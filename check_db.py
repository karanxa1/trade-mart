import sqlite3
import os

# Possible database paths
db_paths = [
    'trade_mart/trade_mart.db',
    'trade_mart.db',
    'instance/trade_mart.db',
    os.path.join(os.getcwd(), 'trade_mart/trade_mart.db'),
    os.path.join(os.getcwd(), 'trade_mart.db'),
    os.path.join(os.getcwd(), 'instance/trade_mart.db')
]

print("Searching for database files:")
found_db = False

for db_path in db_paths:
    print(f"Checking {os.path.abspath(db_path)}")
    
    if os.path.exists(db_path):
        found_db = True
        print(f"Database file exists at {db_path}, size: {os.path.getsize(db_path)} bytes")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("  Tables in the database:")
            for table in tables:
                print(f"    {table[0]}")
            
            # Get Product table schema
            print("  Product table schema:")
            cursor.execute("PRAGMA table_info(product)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    {col[1]} ({col[2]})")
            
            conn.close()
        except Exception as e:
            print(f"  Error: {e}")
        print("\n")

# Also search for any SQLite files in the current directory
print("Searching for any .db files in the current directory:")
for root, dirs, files in os.walk('.', topdown=True):
    if '.git' in dirs:
        dirs.remove('.git')  # Don't search git directory
    
    for file in files:
        if file.endswith('.db'):
            db_path = os.path.join(root, file)
            print(f"Found database: {db_path}, size: {os.path.getsize(db_path)} bytes")

if not found_db:
    print("No database files found at expected locations.") 