#!/usr/bin/env python3
"""Quick script to check product approval status"""
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate('backend/serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Get the specific product
product_id = '3ZGDq2suC9h7XRl7cY6g'
product = db.collection('products').document(product_id).get()

if product.exists:
    data = product.to_dict()
    print(f"Product: {data.get('name')}")
    print(f"Approval Status: {data.get('approval_status', 'NOT SET')}")
    print(f"Status: {data.get('status')}")
    print(f"Seller ID: {data.get('seller_id')}")
    print(f"\nFull data:")
    for key, value in data.items():
        print(f"  {key}: {value}")
else:
    print("Product not found!")

# Also check all pending products
print("\n\n=== ALL PENDING PRODUCTS ===")
pending = db.collection('products').where('approval_status', '==', 'pending').stream()
count = 0
for p in pending:
    count += 1
    pdata = p.to_dict()
    print(f"{count}. {pdata.get('name')} - ID: {p.id}")
    
if count == 0:
    print("No pending products found!")
