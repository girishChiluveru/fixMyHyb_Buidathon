#!/usr/bin/env python3
"""
FixMyHyd - Complete Application Startup Script
Ensures all components are connected and fully functional
"""

import os
import sys
import subprocess
import time
from app import app, init_database

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    required_packages = ['flask', 'PIL', 'dotenv', 'google.generativeai']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("Dependencies installed successfully!")
    else:
        print("All dependencies are available!")

def setup_environment():
    """Set up environment configuration"""
    print("Setting up environment...")
    
    if not os.path.exists('.env'):
        if os.path.exists('env.template'):
            print("Creating .env file from template...")
            with open('env.template', 'r') as template:
                with open('.env', 'w') as env_file:
                    env_file.write(template.read())
            print("Environment file created! Please edit .env with your API keys.")
        else:
            print("Creating basic .env file...")
            with open('.env', 'w') as env_file:
                env_file.write("""SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY_IMAGE=your-google-api-key-here
GOOGLE_API_KEY_AUDIO=your-google-api-key-here
GOOGLE_API_KEY_TEXT=your-google-api-key-here
GOOGLE_API_KEY_REPORT=your-google-api-key-here
DEBUG=True
PORT=5001
""")
            print("Basic environment file created! Please add your Google AI API keys.")
    else:
        print("Environment file already exists!")

def initialize_database():
    """Initialize the database with required tables"""
    print("Initializing database...")
    try:
        init_database()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def test_application():
    """Run basic application tests"""
    print("Testing application...")
    try:
        # Test if app can be imported and basic routes work
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("Home page: OK")
            else:
                print(f"Home page failed: {response.status_code}")
                return False
            
            # Test static files
            response = client.get('/static/css/style.css')
            if response.status_code == 200:
                print("CSS files: OK")
            else:
                print(f"CSS files failed: {response.status_code}")
                return False
            
            # Test JavaScript files
            response = client.get('/static/js/main.js')
            if response.status_code == 200:
                print("JavaScript files: OK")
            else:
                print(f"JavaScript files failed: {response.status_code}")
                return False
        
        print("Application tests passed!")
        return True
    except Exception as e:
        print(f"Application test failed: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print("Starting FixMyHyd application...")
    print("=" * 60)
    print("Application will be available at:")
    print("  http://localhost:5001")
    print("  http://127.0.0.1:5001")
    print("")
    print("Default admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("")
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        app.run(debug=True, port=5001, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error starting application: {e}")

def main():
    """Main startup function"""
    print("FixMyHyd - AI-Powered Civic Issue Reporting System")
    print("Complete Application Startup")
    print("=" * 60)
    
    # Step 1: Check dependencies
    check_dependencies()
    print()
    
    # Step 2: Setup environment
    setup_environment()
    print()
    
    # Step 3: Initialize database
    if not initialize_database():
        print("Failed to initialize database. Exiting.")
        return False
    print()
    
    # Step 4: Test application
    if not test_application():
        print("Application tests failed. Please check the errors above.")
        return False
    print()
    
    # Step 5: Start application
    start_application()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nStartup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Startup failed: {e}")
        sys.exit(1)
