# MongoDB Atlas integration for FixMyHyd
# Alternative to PostgreSQL for cloud database

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import hashlib
import secrets

class MongoDatabase:
    def __init__(self):
        self.mongo_uri = os.getenv('MONGODB_URI')
        if self.mongo_uri:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.fixmyhyd
        else:
            self.client = None
            self.db = None
    
    def get_collection(self, name):
        """Get MongoDB collection"""
        if self.db:
            return self.db[name]
        return None
    
    def init_database(self):
        """Initialize MongoDB collections and create admin user"""
        if not self.db:
            print("MongoDB not configured")
            return False
        
        # Create collections if they don't exist
        collections = ['complaints', 'users', 'admins', 'status_history']
        for collection in collections:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
        
        # Create default admin if none exists
        admins = self.db.admins
        if admins.count_documents({}) == 0:
            admin_password = self.hash_password('admin123')
            admins.insert_one({
                'username': 'admin',
                'password_hash': admin_password,
                'name': 'System Administrator',
                'created_at': datetime.now()
            })
        
        print("MongoDB initialized successfully")
        return True
    
    def hash_password(self, password):
        """Hash password for MongoDB storage"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False

# Usage example:
# mongo_db = MongoDatabase()
# mongo_db.init_database()

# Requirements to add to requirements.txt:
# pymongo==4.5.0
# dnspython==2.4.2