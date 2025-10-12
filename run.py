#!/usr/bin/env python3
"""
FixMyHyd - AI-Powered Civic Issue Reporting System
Startup script for the application
"""

import os
import sys
from app import app, init_database

def main():
    """Main startup function"""
    print("FixMyHyd - AI-Powered Civic Issue Reporting System")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found!")
        print("   Please copy env.template to .env and configure your API keys")
        print("   cp env.template .env")
        print()
    
    # Create tmp directory if it doesn't exist
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
        print("Created /tmp directory")
    
    # Initialize database
    print("Initializing database...")
    init_database()
    print("Database initialized successfully")
    
    # Check for required environment variables
    required_vars = [
        'GOOGLE_API_KEY_IMAGE',
        'GOOGLE_API_KEY_AUDIO', 
        'GOOGLE_API_KEY_TEXT',
        'GOOGLE_API_KEY_REPORT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("   Please configure these in your .env file")
        print()
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting server on http://localhost:{port}")
    print("Access the application in your browser")
    print("Default admin: admin / admin123")
    print("=" * 60)
    
    try:
        app.run(debug=debug, port=port, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\nShutting down FixMyHyd...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
