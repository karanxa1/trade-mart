# User Model for Firestore
from datetime import datetime, timedelta
from firebase_admin import firestore
from ..config import db
import hashlib
import random

class UserModel:
    COLLECTION = 'users'
    
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
    def get_by_ids(cls, doc_ids):
        if not doc_ids:
            return []
        
        # Firestore 'in' query supports up to 10 values preferably, but we can also use getAll
        # Ideally, we use db.get_all(refs)
        refs = [cls.get_collection().document(str(uid)) for uid in set(doc_ids) if uid]
        if not refs:
            return []
            
        docs = db.get_all(refs)
        users = []
        for doc in docs:
            if doc.exists:
                users.append({'id': doc.id, **doc.to_dict()})
        return users
    
    @classmethod
    def get_by_username(cls, username):
        docs = cls.get_collection().where('username', '==', username).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def get_by_email(cls, email):
        docs = cls.get_collection().where('email', '==', email).limit(1).stream()
        for doc in docs:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    @classmethod
    def create_user(cls, uid, username, email, phone, address, user_type, password_hash=None):
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user_data = {
            'username': username,
            'email': email,
            'phone': phone,
            'address': address,
            'user_type': user_type,
            'is_verified': False,
            'verification_code': verification_code,
            'verification_code_expires': datetime.utcnow() + timedelta(hours=24),
            'identity_verified': False,
            'id_document': None,
            'selfie_document': None,
            'avg_rating': 0.0,
            'total_ratings': 0,
            'is_suspended': False,
            'suspend_reason': None,
            'suspended_at': None,
            'suspended_by': None,
            'created_at': firestore.SERVER_TIMESTAMP,
            'password_hash': password_hash
        }
        cls.get_collection().document(uid).set(user_data)
        return {'id': uid, **user_data, 'verification_code': verification_code}
    
    @classmethod
    def update(cls, doc_id, data):
        cls.get_collection().document(str(doc_id)).update(data)
    
    @classmethod
    def get_verified_sellers(cls):
        docs = cls.get_collection().where('user_type', '==', 'seller').where('is_verified', '==', True).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    def get_all_sellers(cls):
        docs = cls.get_collection().where('user_type', '==', 'seller').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, password_hash):
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
