# Firebase Configuration for Trade-Mart Backend
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_PATH = os.environ.get(
    'FIREBASE_SERVICE_ACCOUNT_PATH', 
    os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
)

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCo2sY-LTnbe48lM089nxNSmvA9AHA3FIM",
    "authDomain": "collegehack.firebaseapp.com",
    "projectId": "collegehack",
    "storageBucket": "collegehack.firebasestorage.app",
    "messagingSenderId": "502238961650",
    "appId": "1:502238961650:web:0005ef459f59440b9e556b",
    "measurementId": "G-TVDRCZEL4M"
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'trademartkey123supersecret')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

def init_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        if os.path.exists(SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    return firebase_admin.get_app()

init_firebase()

db = firestore.client()
firebase_auth = auth
