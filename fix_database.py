import sqlite3
import os

# Check both database files
db_paths = [
    'instance/trademart.db',
    'trade_mart/instance/trademart.db'
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"Database file does not exist at {db_path}")
        continue

    print(f"\nChecking database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the product table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product'")
    if not cursor.fetchone():
        print("Product table does not exist in this database")
        conn.close()
        continue

    # Check if the negotiable column already exists
    cursor.execute("PRAGMA table_info(product)")
    columns = cursor.fetchall()
    print("Current Product table schema:")
    column_names = []
    for col in columns:
        column_names.append(col[1])
        print(f"  {col[1]} ({col[2]})")

    if 'negotiable' not in column_names:
        # Add the missing column
        print("\nAdding missing 'negotiable' column to the product table...")
        try:
            cursor.execute("ALTER TABLE product ADD COLUMN negotiable BOOLEAN DEFAULT TRUE")
            conn.commit()
            print("Column added successfully!")
            
            # Verify the modified schema
            cursor.execute("PRAGMA table_info(product)")
            columns = cursor.fetchall()
            print("\nUpdated Product table schema:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("\nThe 'negotiable' column already exists in the product table.")

    conn.close()

print("\nDatabase update complete.") 