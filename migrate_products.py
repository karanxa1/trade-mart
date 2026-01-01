#!/usr/bin/env python3
"""
Migration script to update existing products with approval status.
This sets all existing products to 'approved' status so they remain visible.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('backend/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def migrate_products():
    """Update all products to add approval_status field"""
    products_ref = db.collection('products')
    products = products_ref.stream()
    
    updated_count = 0
    for product in products:
        product_data = product.to_dict()
        
        # Check if approval_status already exists
        if 'approval_status' not in product_data:
            # Set existing products to approved
            products_ref.document(product.id).update({
                'approval_status': 'approved',
                'approved_by': None,
                'approved_at': datetime.utcnow(),
                'rejection_reason': None
            })
            updated_count += 1
            print(f"✅ Updated product: {product_data.get('name', product.id)}")
    
    print(f"\n🎉 Migration complete! Updated {updated_count} products.")
    if updated_count == 0:
        print("All products already have approval status.")

if __name__ == '__main__':
    print("Starting product approval migration...")
    print("This will set all existing products to 'approved' status.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_products()
    else:
        print("Migration cancelled.")
