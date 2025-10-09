import psycopg2
from psycopg2 import OperationalError
import os
import sqlite3
from urllib.parse import urlparse

# Render Database Configuration for "machine learning" database
RENDER_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'dpg-d3jt9rm3jp1c73aj5g1g-a'),
    'database': os.getenv('DB_NAME', 'david_qqd7'),  # Your database name
    'user': os.getenv('DB_USER', 'david_qqd7_user'),
    'password': os.getenv('DB_PASSWORD', '9HTJrak7tr5H1Or00thypxCgwnmBMpo8'),
    'port': os.getenv('DB_PORT', '5432')
}

# Render typically provides DATABASE_URL environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
#postgresql://david_qqd7_user:9HTJrak7tr5H1Or00thypxCgwnmBMpo8@dpg-d3jt9rm3jp1c73aj5g1g-a.oregon-postgres.render.com/david_qqd7

# SQLite fallback for local development
SQLITE_DB = 'david_qqd7'

def create_sqlite_table():
    """Create SQLite table if it doesn't exist (fallback)"""
    try:
        conn = sqlite3.connect(SQLITE_DB)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                gene1 REAL NOT NULL,
                gene2 REAL NOT NULL,
                gene3 REAL NOT NULL,
                gene4 REAL NOT NULL,
                gene5 REAL NOT NULL,
                prediction_numeric INTEGER NOT NULL,
                prediction_label TEXT NOT NULL,
                true_label TEXT
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✓ SQLite table created/verified")
    except Exception as e:
        print(f"✗ Error creating SQLite table: {e}")

def create_postgres_table(conn):
    """Create PostgreSQL table if it doesn't exist"""
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                gene1 REAL NOT NULL,
                gene2 REAL NOT NULL,
                gene3 REAL NOT NULL,
                gene4 REAL NOT NULL,
                gene5 REAL NOT NULL,
                prediction_numeric INTEGER NOT NULL,
                prediction_label VARCHAR(20) NOT NULL,
                true_label VARCHAR(20)
            )
        ''')
        conn.commit()
        cur.close()
        print("✓ PostgreSQL table created/verified")
    except Exception as e:
        print(f"✗ Error creating PostgreSQL table: {e}")
        raise e

def get_db_connection():
    """Get database connection - Render PostgreSQL with SQLite fallback"""
    try:
        if DATABASE_URL:
            # Parse DATABASE_URL provided by Render
            print("🔗 Attempting connection using DATABASE_URL...")
            url = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                host=url.hostname,
                database=url.path[1:],  # Remove leading slash
                user=url.username,
                password=url.password,
                port=url.port or 5432,
                sslmode='require',  # Render requires SSL
                connect_timeout=10
            )
        else:
            # Use individual environment variables
            print("🔗 Attempting connection using individual environment variables...")
            conn = psycopg2.connect(
                host=RENDER_DB_CONFIG['host'],
                database=RENDER_DB_CONFIG['database'],
                user=RENDER_DB_CONFIG['user'],
                password=RENDER_DB_CONFIG['password'],
                port=RENDER_DB_CONFIG['port'],
                sslmode='require',
                connect_timeout=10
            )
        
        # Test connection and create table
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        
        # Create table if it doesn't exist
        create_postgres_table(conn)
        
        print("✅ Successfully connected to Render PostgreSQL database: 'machine learning'")
        return conn, 'postgresql'
        
    except (OperationalError, Exception) as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("🔄 Falling back to SQLite database for local development...")
        
        # Fallback to SQLite for local development
        try:
            create_sqlite_table()
            conn = sqlite3.connect(SQLITE_DB, timeout=10)
            conn.row_factory = sqlite3.Row
            print("✅ Connected to SQLite database (fallback)")
            return conn, 'sqlite'
        except Exception as sqlite_error:
            print(f"❌ SQLite fallback also failed: {sqlite_error}")
            raise sqlite_error

def execute_query(query, params=None, fetch=False):
    """Execute query with automatic connection handling and database compatibility"""
    conn, db_type = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Convert PostgreSQL queries to SQLite if needed
        if db_type == 'sqlite':
            # Replace PostgreSQL syntax with SQLite equivalents
            query = query.replace('%s', '?')
            query = query.replace('NOW()', "datetime('now')")
            query = query.replace("INTERVAL '1 day'", "'-1 day'")
            query = query.replace('CURRENT_TIMESTAMP', "datetime('now')")
            query = query.replace('SERIAL', 'INTEGER')
            query = query.replace('VARCHAR(20)', 'TEXT')
            query = query.replace('REAL', 'REAL')
        
        # Execute query
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        # Fetch results if requested
        if fetch:
            if db_type == 'sqlite':
                result = cur.fetchall()
            else:
                result = cur.fetchall()
        else:
            result = None
            
        conn.commit()
        return result
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Query execution failed: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        raise e
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def test_connection():
    """Test database connection and display information"""
    try:
        print("🧪 Testing database connection...")
        conn, db_type = get_db_connection()
        
        cur = conn.cursor()
        if db_type == 'postgresql':
            # Get PostgreSQL version and database info
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            print(f"✅ PostgreSQL Connection Successful!")
            print(f"   Database: {db_name}")
            print(f"   Version: {version.split(',')[0]}")
            
            # Test table existence
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'predictions'
                );
            """)
            table_exists = cur.fetchone()[0]
            print(f"   Predictions table exists: {table_exists}")
            
        else:
            # SQLite version
            cur.execute("SELECT sqlite_version();")
            version = cur.fetchone()[0]
            print(f"✅ SQLite Connection Successful!")
            print(f"   Database file: {SQLITE_DB}")
            print(f"   Version: {version}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def get_connection_info():
    """Get connection information for debugging"""
    info = {
        'database_url_provided': bool(DATABASE_URL),
        'database_name': RENDER_DB_CONFIG['database'],
        'host': RENDER_DB_CONFIG['host'],
        'port': RENDER_DB_CONFIG['port'],
        'user': RENDER_DB_CONFIG['user'],
        'password_set': bool(RENDER_DB_CONFIG['password']),
        'sqlite_fallback': SQLITE_DB
    }
    return info

if __name__ == "__main__":
    print("🧬 GenePredict Database Configuration")
    print("=" * 50)
    
    # Show connection info
    info = get_connection_info()
    print("Connection Information:")
    for key, value in info.items():
        if 'password' in key.lower():
            print(f"  {key}: {'Set' if value else 'Not Set'}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Test connection
    test_connection()
