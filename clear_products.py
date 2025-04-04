from trade_mart.app import app, db, Product

with app.app_context():
    try:
        # Get count of products before deletion
        count_before = Product.query.count()
        print(f"Found {count_before} products in the database")
        
        # Delete all products
        if count_before > 0:
            Product.query.delete()
            db.session.commit()
            print(f"Successfully deleted all {count_before} products")
        else:
            print("No products to delete")
        
        # Verify deletion
        count_after = Product.query.count()
        print(f"Products remaining in database: {count_after}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback() 