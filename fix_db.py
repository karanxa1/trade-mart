from trade_mart.app import app, db, init_db
import os
import time

if __name__ == '__main__':
    with app.app_context():
        # First check if database file exists and delete it to ensure clean slate
        db_path = 'trade_mart/trade_mart.db'
        if os.path.exists(db_path):
            try:
                print(f"Removing existing database at {db_path}")
                os.remove(db_path)
                # Small delay to ensure file is completely removed
                time.sleep(1)
                print("Database file removed successfully")
            except Exception as e:
                print(f"Warning: Could not remove database: {e}")
        
        try:
            print("Creating all tables...")
            db.create_all()
            print("Database schema created successfully!")
            
            # Initialize with sample data
            print("Initializing database with sample data...")
            init_db()
            print("Database initialization complete!")
            
            # Verify the Product table structure using SQLAlchemy
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('product')
            
            print("\nProduct table columns:")
            for column in columns:
                print(f"  {column['name']} ({column['type']})")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc() 