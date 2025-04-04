from trade_mart.app import app, db, init_db
import os

def initialize_database():
    with app.app_context():
        # Check if we need to create tables
        try:
            print("Creating all tables if they don't exist...")
            db.create_all()
            print("Database schema created successfully!")
            
            # Initialize with sample data
            print("Initializing database with sample data...")
            init_db()
            print("Database initialization complete!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()

# This function can be imported and called when needed
if __name__ == "__main__":
    initialize_database()