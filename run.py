from trade_mart.app import app, db, init_db
import os
import sqlite3
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
            
            # Verify the Product table structure
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(product)")
                columns = cursor.fetchall()
                print("\nProduct table structure:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                conn.close()
            except Exception as e:
                print(f"Error checking table structure: {e}")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0') 