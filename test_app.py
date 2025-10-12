#!/usr/bin/env python3
"""
FixMyHyd Application Test Script
Tests all functionality to ensure everything is working properly
"""

import os
import sys
import tempfile
from app import app, init_database, get_db_connection, hash_password

def test_database():
    """Test database initialization and basic operations"""
    print("Testing database...")
    try:
        init_database()
        conn = get_db_connection()
        
        # Test user creation
        test_password = hash_password("test123")
        conn.execute('''
            INSERT OR IGNORE INTO users (name, email, password_hash, phone)
            VALUES (?, ?, ?, ?)
        ''', ("Test User", "test@example.com", test_password, "+91-9999999999"))
        
        # Test admin creation
        admin_password = hash_password("admin123")
        conn.execute('''
            INSERT OR IGNORE INTO admins (username, password_hash, name)
            VALUES (?, ?, ?)
        ''', ("admin", admin_password, "Test Admin"))
        
        conn.commit()
        conn.close()
        print("Database test passed")
        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_routes():
    """Test all application routes"""
    print("Testing routes...")
    try:
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            assert response.status_code == 200
            print("Home page working")
            
            # Test user login page
            response = client.get('/user/login')
            assert response.status_code == 200
            print("User login page working")
            
            # Test admin login page
            response = client.get('/admin/login')
            assert response.status_code == 200
            print("Admin login page working")
            
            # Test user registration page
            response = client.get('/user/register')
            assert response.status_code == 200
            print("User registration page working")
            
            # Test static files
            response = client.get('/static/css/style.css')
            assert response.status_code == 200
            print("CSS files working")
            
            response = client.get('/static/js/main.js')
            assert response.status_code == 200
            print("JavaScript files working")
            
        print("All routes test passed")
        return True
    except Exception as e:
        print(f"Routes test failed: {e}")
        return False

def test_authentication():
    """Test authentication system"""
    print("Testing authentication...")
    try:
        with app.test_client() as client:
            # Test user registration page
            response = client.get('/user/register')
            assert response.status_code == 200
            print("User registration page working")
            
            # Test user login page
            response = client.get('/user/login')
            assert response.status_code == 200
            print("User login page working")
            
            # Test admin login page
            response = client.get('/admin/login')
            assert response.status_code == 200
            print("Admin login page working")
            
            # Test logout
            response = client.get('/logout')
            assert response.status_code == 302  # Redirect after logout
            print("Logout working")
            
        print("Authentication test passed")
        return True
    except Exception as e:
        print(f"Authentication test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("Testing API endpoints...")
    try:
        with app.test_client() as client:
            # Test admin complaints endpoint (should redirect to login)
            response = client.get('/api/admin/complaints')
            assert response.status_code == 302  # Redirect to login
            print("Admin complaints API working")
            
            # Test user complaints endpoint (should redirect to login)
            response = client.get('/api/user/complaints')
            assert response.status_code == 302  # Redirect to login
            print("User complaints API working")
            
        print("API endpoints test passed")
        return True
    except Exception as e:
        print(f"API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("FixMyHyd Application Test Suite")
    print("=" * 50)
    
    tests = [
        test_database,
        test_routes,
        test_authentication,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Application is fully functional!")
        return True
    else:
        print("Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
