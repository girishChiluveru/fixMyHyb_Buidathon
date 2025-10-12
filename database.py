# Database migration to PostgreSQL for Render deployment
# This fixes the SQLite persistence issue on Render's free tier

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get PostgreSQL connection for production or SQLite for development"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql'):
        # Production: Use PostgreSQL
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    else:
        # Development: Use SQLite
        import sqlite3
        conn = sqlite3.connect('fixmyhyd.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_database():
    """Initialize database tables for PostgreSQL or SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we're using PostgreSQL or SQLite
    database_url = os.getenv('DATABASE_URL')
    is_postgres = database_url and database_url.startswith('postgresql')
    
    if is_postgres:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id SERIAL PRIMARY KEY,
                ghmc_id VARCHAR(255) UNIQUE NOT NULL,
                category VARCHAR(100) NOT NULL,
                priority VARCHAR(20) DEFAULT 'Medium',
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                zone VARCHAR(100),
                gps_lat DECIMAL(10, 8),
                gps_lng DECIMAL(11, 8),
                status VARCHAR(50) DEFAULT 'Submitted',
                submitted_by VARCHAR(100) DEFAULT 'Citizen',
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id SERIAL PRIMARY KEY,
                complaint_id INTEGER REFERENCES complaints(id),
                old_status VARCHAR(50),
                new_status VARCHAR(50),
                changed_by VARCHAR(100),
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    else:
        # SQLite syntax (for local development)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ghmc_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                zone TEXT,
                gps_lat REAL,
                gps_lng REAL,
                status TEXT DEFAULT 'Submitted',
                submitted_by TEXT DEFAULT 'Citizen',
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id INTEGER,
                old_status TEXT,
                new_status TEXT,
                changed_by TEXT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (complaint_id) REFERENCES complaints (id)
            )
        ''')
    
    # Create default admin if none exists
    cursor.execute('SELECT COUNT(*) FROM admins')
    result = cursor.fetchone()
    admin_count = result[0] if is_postgres else result[0]
    
    if admin_count == 0:
        from app import hash_password  # Import from main app
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, name)
            VALUES (%s, %s, %s)
        ''' if is_postgres else '''
            INSERT INTO admins (username, password_hash, name)
            VALUES (?, ?, ?)
        ''', ('admin', admin_password, 'System Administrator'))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")