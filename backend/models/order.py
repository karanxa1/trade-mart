# Order Models for Firestore
from datetime import datetime, timedelta
from firebase_admin import firestore
from ..config import db
import random

class OrderModel:
    COLLECTION = 'orders'
    
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
    def create_order(cls, user_id, total_amount, delivery_address, payment_method='cash_on_delivery'):
        tracking_id = f"TM{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        order_data = {
            'user_id': str(user_id),
            'order_date': firestore.SERVER_TIMESTAMP,
            'status': 'pending',
            'tracking_status': 'order_placed',
            'tracking_id': tracking_id,
            'tracking_updates': [{
                'status': 'order_placed',
                'timestamp': datetime.utcnow().isoformat(),
                'description': 'Order has been placed successfully'
            }],
            'estimated_delivery': (datetime.utcnow() + timedelta(days=5)).isoformat(),
            'delivery_address': delivery_address,
            'payment_method': payment_method,
            'total_amount': float(total_amount)
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(order_data)
        return doc_ref.id
    
    @classmethod
    def get_by_user(cls, user_id):
        docs = cls.get_collection().where('user_id', '==', str(user_id)).order_by('order_date', direction=firestore.Query.DESCENDING).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_by_tracking_id(cls, tracking_id):
        docs = cls.get_collection().where('tracking_id', '==', tracking_id).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)

class OrderItemModel:
    COLLECTION = 'order_items'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def create_item(cls, order_id, product_id, quantity, price):
        item_data = {
            'order_id': str(order_id),
            'product_id': str(product_id),
            'quantity': int(quantity),
            'price': float(price)
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(item_data)
        return doc_ref.id
    
    @classmethod
    def get_by_order(cls, order_id):
        docs = cls.get_collection().where('order_id', '==', str(order_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_by_product(cls, product_id):
        docs = cls.get_collection().where('product_id', '==', str(product_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
