# Cart Model for Firestore
from ..config import db

class CartModel:
    COLLECTION = 'carts'
    
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
    def get_by_user(cls, user_id):
        docs = cls.get_collection().where('user_id', '==', str(user_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_user_product_cart(cls, user_id, product_id):
        docs = cls.get_collection().where('user_id', '==', str(user_id)).where('product_id', '==', str(product_id)).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def add_to_cart(cls, user_id, product_id, quantity=1):
        existing = cls.get_user_product_cart(user_id, product_id)
        if existing:
            new_quantity = existing.get('quantity', 0) + quantity
            cls.update(existing['id'], {'quantity': new_quantity})
            return existing['id']
        else:
            cart_data = {
                'user_id': str(user_id),
                'product_id': str(product_id),
                'quantity': quantity
            }
            doc_ref = cls.get_collection().document()
            doc_ref.set(cart_data)
            return doc_ref.id
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)
    
    @classmethod
    def delete(cls, doc_id):
        cls.get_collection().document(str(doc_id)).delete()
    
    @classmethod
    def clear_user_cart(cls, user_id):
        cart_items = cls.get_by_user(user_id)
        batch = db.batch()
        for item in cart_items:
            batch.delete(cls.get_collection().document(item['id']))
        batch.commit()
