import sqlite3
import os
from urllib.parse import urlparse

try:
    import pymysql
    from dotenv import load_dotenv
except ImportError:
    print("❌ ERROR: Missing required packages.")
    print("👉 Please run: pip install pymysql python-dotenv")
    exit()

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
print("--- 🚀 Starting SQLite to MySQL Migration ---")

# Get MySQL connection details from DATABASE_URL in .env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ ERROR: DATABASE_URL not found in your .env file.")
    print("👉 Please run 'python setup_env.py' first to create the .env file.")
    exit()

# Parse the database URL
try:
    # Replace 'mysql+pymysql' with 'mysql' for standard parsing
    if db_url.startswith("mysql+pymysql://"):
        temp_url = db_url.replace("mysql+pymysql://", "mysql://")
    else:
        temp_url = db_url
        
    parsed_url = urlparse(temp_url)
    
    MYSQL_HOST = parsed_url.hostname
    MYSQL_USER = parsed_url.username
    MYSQL_PASSWORD = parsed_url.password
    MYSQL_DB = parsed_url.path.lstrip('/')
    
    if not all([MYSQL_HOST, MYSQL_USER, MYSQL_DB]):
        raise ValueError("URL is missing host, user, or database name.")

except Exception as e:
    print(f"❌ ERROR: Could not parse DATABASE_URL '{db_url}'. Please check its format in .env. Error: {e}")
    exit()

# --- Migration Logic ---
sqlite_conn = None
mysql_conn = None
try:
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("crm.db")
    sqlite_cursor = sqlite_conn.cursor()
    print("✅ Connected to SQLite (crm.db)")

    # Connect to MySQL
    print(f"⏳ Connecting to MySQL on '{MYSQL_HOST}'...")
    mysql_conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    mysql_cursor = mysql_conn.cursor()
    print(f"✅ Connected to MySQL database '{MYSQL_DB}'")

except pymysql.err.OperationalError as e:
    print(f"\n❌ MYSQL CONNECTION FAILED: {e}")
    print("\n--- Troubleshooting ---")
    print("1. Is your MySQL server (like XAMPP or WAMP) running?")
    print(f"2. Is the password in your .env file correct for the user '{MYSQL_USER}'?")
    print(f"3. Does the database '{MYSQL_DB}' exist? (Run 'CREATE DATABASE {MYSQL_DB};' in MySQL if not)")
    exit()
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")
    exit()


# Connect to SQLite
sqlite_conn = sqlite3.connect("crm.db")
sqlite_cursor = sqlite_conn.cursor()

# Get SQLite tables
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for table in tables:
    table_name = table[0]
 
    if table_name == "sqlite_sequence":
        continue
 
    print(f"\nMigrating table: {table_name}")
 
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
 
    if rows:
        placeholders = ",".join(["%s"] * len(rows[0]))
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        column_names = [info[1] for info in sqlite_cursor.fetchall()]
        columns_str = ",".join(f"`{col}`" for col in column_names)
        
        insert_query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
 
        try:
            print(f"  -> Inserting {len(rows)} rows...")
            mysql_cursor.executemany(insert_query, rows)
            mysql_conn.commit()
            print(f"  -> ✅ Successfully migrated {table_name}")
        except Exception as e:
            print(f"  -> ❌ Error migrating data for {table_name}: {e}")
            if mysql_conn:
                mysql_conn.rollback()
    else:
        print("  -> Skipping empty table.")
 
print("\n🎉 Migration Completed Successfully!")
 
if sqlite_conn:
    sqlite_conn.close()
if mysql_conn:
    mysql_conn.close()