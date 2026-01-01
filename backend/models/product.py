from datetime import datetime
from functools import lru_cache
from firebase_admin import firestore
from ..config import db

# In-memory cache for categories and conditions (small, static data)
_categories_cache = None
_conditions_cache = None
_cache_timestamp = None
CACHE_TTL = 300  # 5 minutes

def _get_categories_cached():
    global _categories_cache, _cache_timestamp
    import time
    now = time.time()
    if _categories_cache is None or _cache_timestamp is None or (now - _cache_timestamp) > CACHE_TTL:
        docs = db.collection('categories').stream()
        _categories_cache = {doc.id: {'id': doc.id, **doc.to_dict()} for doc in docs}
        _cache_timestamp = now
    return _categories_cache

def _get_conditions_cached():
    global _conditions_cache, _cache_timestamp
    import time
    now = time.time()
    if _conditions_cache is None or _cache_timestamp is None or (now - _cache_timestamp) > CACHE_TTL:
        docs = db.collection('conditions').stream()
        _conditions_cache = {doc.id: {'id': doc.id, **doc.to_dict()} for doc in docs}
        _cache_timestamp = now
    return _conditions_cache


class CategoryModel:
    COLLECTION = 'categories'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def get_by_id(cls, doc_id):
        cache = _get_categories_cached()
        return cache.get(str(doc_id))
    
    @classmethod
    def get_all(cls):
        cache = _get_categories_cached()
        return list(cache.values())
    
    @classmethod
    def get_by_name(cls, name):
        cache = _get_categories_cached()
        for cat in cache.values():
            if cat.get('name') == name:
                return cat
        return None
    
    @classmethod
    def initialize_categories(cls):
        global _categories_cache
        _categories_cache = None  # Clear cache
        categories = ['Electronics', 'Books', 'Furniture', 'Tools', 'Vehicles', 'Toys', 'Clothing', 'Home & Garden']
        for i, name in enumerate(categories, 1):
            existing = cls.get_by_name(name)
            if not existing:
                cls.get_collection().document(str(i)).set({'name': name})
        _categories_cache = None  # Clear cache again after init


class ConditionModel:
    COLLECTION = 'conditions'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def get_by_id(cls, doc_id):
        cache = _get_conditions_cached()
        return cache.get(str(doc_id))
    
    @classmethod
    def get_all(cls):
        cache = _get_conditions_cached()
        return list(cache.values())
    
    @classmethod
    def get_by_name(cls, name):
        cache = _get_conditions_cached()
        for cond in cache.values():
            if cond.get('name') == name:
                return cond
        return None
    
    @classmethod
    def initialize_conditions(cls):
        global _conditions_cache
        _conditions_cache = None  # Clear cache
        conditions = ['New', 'Like New', 'Good', 'Fair', 'Poor']
        for i, name in enumerate(conditions, 1):
            existing = cls.get_by_name(name)
            if not existing:
                cls.get_collection().document(str(i)).set({'name': name})
        _conditions_cache = None  # Clear cache again after init

class ProductModel:
    COLLECTION = 'products'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def get_by_id(cls, doc_id):
        doc = cls.get_collection().document(str(doc_id)).get()
        if doc.exists:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def get_available_products(cls, limit=None, category_id=None, condition_id=None, 
                               seller_id=None, min_price=None, max_price=None,
                               search_query=None, sort_by='newest'):
        # Only show approved products to public
        query = cls.get_collection().where('status', '==', 'available').where('approval_status', '==', 'approved')
        
        if category_id:
            query = query.where('category_id', '==', str(category_id))
        if condition_id:
            query = query.where('condition_id', '==', str(condition_id))
        if seller_id:
            query = query.where('seller_id', '==', str(seller_id))
        
        docs = query.stream()
        products = []
        
        for doc in docs:
            product = {'id': doc.id, **doc.to_dict()}
            
            if min_price and product.get('price', 0) < min_price:
                continue
            if max_price and product.get('price', 0) > max_price:
                continue
            if search_query:
                name = product.get('name', '').lower()
                desc = product.get('description', '').lower()
                if search_query.lower() not in name and search_query.lower() not in desc:
                    continue
            
            products.append(product)
        
        if sort_by == 'price_low':
            products.sort(key=lambda x: x.get('price', 0))
        elif sort_by == 'price_high':
            products.sort(key=lambda x: x.get('price', 0), reverse=True)
        else:
            products.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        if limit:
            products = products[:limit]
        
        return products
    
    @classmethod
    def get_by_seller(cls, seller_id):
        docs = cls.get_collection().where('seller_id', '==', str(seller_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def create_product(cls, name, description, price, negotiable, condition_id, 
                       image, category_id, seller_id):
        product_data = {
            'name': name,
            'description': description,
            'price': float(price),
            'negotiable': negotiable,
            'condition_id': str(condition_id),
            'image': image,
            'category_id': str(category_id),
            'seller_id': str(seller_id),
            'status': 'available',
            'approval_status': 'pending',
            'approved_by': None,
            'approved_at': None,
            'rejection_reason': None,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(product_data)
        return doc_ref.id
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)
    
    @classmethod
    def delete(cls, doc_id):
        cls.get_collection().document(str(doc_id)).delete()
    
    @classmethod
    def get_pending_products(cls):
        """Get all products pending approval"""
        docs = cls.get_collection().where('approval_status', '==', 'pending').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_all_products_with_approval_status(cls, seller_id=None):
        """Get all products regardless of approval status (for seller/admin view)"""
        if seller_id:
            docs = cls.get_collection().where('seller_id', '==', str(seller_id)).stream()
        else:
            docs = cls.get_collection().stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def approve_product(cls, product_id, gov_employee_id):
        """Approve a product"""
        cls.get_collection().document(str(product_id)).update({
            'approval_status': 'approved',
            'approved_by': str(gov_employee_id),
            'approved_at': firestore.SERVER_TIMESTAMP,
            'rejection_reason': None
        })
    
    @classmethod
    def reject_product(cls, product_id: str, gov_employee_id: str, reason: str):
        """Reject a product"""
        cls.get_collection().document(str(product_id)).update({
            'approval_status': 'rejected',
            'approved_by': str(gov_employee_id),
            'approved_at': firestore.SERVER_TIMESTAMP,
            'rejection_reason': reason
        })
    
    @classmethod
    def delete_by_government(cls, product_id: str, gov_employee_id: str, reason: str):
        """Delete a product by government employee"""
        cls.get_collection().document(str(product_id)).update({
            'status': 'deleted',
            'deleted_by_govt': True,
            'deleted_by': str(gov_employee_id),
            'deleted_at': firestore.SERVER_TIMESTAMP,
            'deletion_reason': reason
        })
