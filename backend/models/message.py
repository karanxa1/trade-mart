# Message Model for Firestore
from datetime import datetime
from firebase_admin import firestore
from ..config import db

class MessageModel:
    COLLECTION = 'messages'
    
    @classmethod
    def get_collection(cls):
        return db.collection(cls.COLLECTION)
    
    @classmethod
    def get_conversation(cls, user1_id, user2_id):
        all_messages = []
        
        docs1 = cls.get_collection().where('sender_id', '==', str(user1_id)).where('receiver_id', '==', str(user2_id)).stream()
        all_messages.extend([{'id': doc.id, **doc.to_dict()} for doc in docs1])
        
        docs2 = cls.get_collection().where('sender_id', '==', str(user2_id)).where('receiver_id', '==', str(user1_id)).stream()
        all_messages.extend([{'id': doc.id, **doc.to_dict()} for doc in docs2])
        
        all_messages.sort(key=lambda x: x.get('created_at', datetime.min))
        return all_messages
    
    @classmethod
    def get_unread_count(cls, user_id, sender_id=None):
        query = cls.get_collection().where('receiver_id', '==', str(user_id)).where('read', '==', False)
        if sender_id:
            query = query.where('sender_id', '==', str(sender_id))
        return len(list(query.stream()))
    
    @classmethod
    def mark_as_read(cls, user_id, sender_id):
        docs = cls.get_collection().where('receiver_id', '==', str(user_id)).where('sender_id', '==', str(sender_id)).where('read', '==', False).stream()
        batch = db.batch()
        for doc in docs:
            batch.update(doc.reference, {'read': True})
        batch.commit()
    
    @classmethod
    def get_conversation_partners(cls, user_id):
        partners = {}
        
        sent_to_me = cls.get_collection().where('receiver_id', '==', str(user_id)).stream()
        for doc in sent_to_me:
            data = doc.to_dict()
            sender_id = data.get('sender_id')
            if sender_id:
                partners[sender_id] = True
        
        sent_by_me = cls.get_collection().where('sender_id', '==', str(user_id)).stream()
        for doc in sent_by_me:
            data = doc.to_dict()
            receiver_id = data.get('receiver_id')
            if receiver_id:
                partners[receiver_id] = True
        
        return list(partners.keys())
    
    @classmethod
    def send_message(cls, sender_id, receiver_id, content, product_id=None):
        message_data = {
            'sender_id': str(sender_id),
            'receiver_id': str(receiver_id),
            'content': content,
            'product_id': str(product_id) if product_id else None,
            'read': False,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = cls.get_collection().document()
        doc_ref.set(message_data)
        return doc_ref.id
