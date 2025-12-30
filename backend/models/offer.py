# Offer Model for Firestore
from firebase_admin import firestore
from ..config import db

class OfferModel:
    COLLECTION = 'offers'
    
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
    def get_by_product(cls, product_id):
        docs = cls.get_collection().where('product_id', '==', str(product_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_pending_by_buyer_product(cls, buyer_id, product_id):
        docs = cls.get_collection().where('product_id', '==', str(product_id)).where('buyer_id', '==', str(buyer_id)).where('status', '==', 'pending').limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def get_by_buyer(cls, buyer_id):
        docs = cls.get_collection().where('buyer_id', '==', str(buyer_id)).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_by_seller(cls, seller_id):
        docs = cls.get_collection().where('seller_id', '==', str(seller_id)).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_pending_count_for_seller(cls, seller_id):
        docs = cls.get_collection().where('seller_id', '==', str(seller_id)).where('status', '==', 'pending').stream()
        return len(list(docs))
    
    @classmethod
    def create_offer(cls, product_id, buyer_id, seller_id, offer_price):
        offer_data = {
            'product_id': str(product_id),
            'buyer_id': str(buyer_id),
            'seller_id': str(seller_id),
            'offer_price': float(offer_price),
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(offer_data)
        return doc_ref.id
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)
