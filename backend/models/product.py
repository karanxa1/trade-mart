from datetime import datetime
from functools import lru_cache
from firebase_admin import firestore
from ..config import db

class CategoryModel:
    COLLECTION = 'categories'
    
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
    @lru_cache(maxsize=1)
    def get_all(cls):
        return [{'id': doc.id, **doc.to_dict()} for doc in cls.get_collection().stream()]
    
    @classmethod
    def get_by_name(cls, name):
        docs = cls.get_collection().where('name', '==', name).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def initialize_categories(cls):
        categories = ['Electronics', 'Books', 'Furniture', 'Tools', 'Vehicles', 'Toys', 'Clothing', 'Home & Garden']
        for i, name in enumerate(categories, 1):
            existing = cls.get_by_name(name)
            if not existing:
                cls.get_collection().document(str(i)).set({'name': name})

class ConditionModel:
    COLLECTION = 'conditions'
    
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
    @lru_cache(maxsize=1)
    def get_all(cls):
        return [{'id': doc.id, **doc.to_dict()} for doc in cls.get_collection().stream()]
    
    @classmethod
    def get_by_name(cls, name):
        docs = cls.get_collection().where('name', '==', name).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def initialize_conditions(cls):
        conditions = ['New', 'Like New', 'Good', 'Fair', 'Poor']
        for i, name in enumerate(conditions, 1):
            existing = cls.get_by_name(name)
            if not existing:
                cls.get_collection().document(str(i)).set({'name': name})

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
        query = cls.get_collection().where('status', '==', 'available')
        
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
