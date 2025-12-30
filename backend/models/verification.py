# Business Verification Model for Firestore
from firebase_admin import firestore
from ..config import db

class BusinessVerificationModel:
    COLLECTION = 'business_verifications'
    
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
        docs = cls.get_collection().where('user_id', '==', str(user_id)).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def get_pending(cls):
        docs = cls.get_collection().where('status', '==', 'pending').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def create(cls, user_id, documents):
        data = {
            'user_id': str(user_id),
            'documents': documents,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(data)
        return doc_ref.id
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)

class ReviewModel:
    COLLECTION = 'reviews'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def get_by_seller(cls, seller_id):
        docs = cls.get_collection().where('seller_id', '==', str(seller_id)).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_seller_stats(cls, seller_id):
        reviews = cls.get_by_seller(seller_id)
        if not reviews:
            return {'avg_rating': 0, 'count': 0}
        total = sum(r.get('rating', 0) for r in reviews)
        return {'avg_rating': total / len(reviews), 'count': len(reviews)}
    
    @classmethod
    def create_review(cls, reviewer_id, seller_id, rating, comment=None):
        review_data = {
            'reviewer_id': str(reviewer_id),
            'seller_id': str(seller_id),
            'rating': int(rating),
            'comment': comment,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(review_data)
        return doc_ref.id
