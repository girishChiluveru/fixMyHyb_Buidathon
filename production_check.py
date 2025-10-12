#!/usr/bin/env python3
"""
FixMyHyd - Production Ready Startup Script
This script prepares the application for production deployment.
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import PIL
        import dotenv
        import google.generativeai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🔍 Environment Check:")
    
    # Check API keys
    api_keys = [
        'GOOGLE_API_KEY_IMAGE',
        'GOOGLE_API_KEY_AUDIO', 
        'GOOGLE_API_KEY_TEXT',
        'GOOGLE_API_KEY_REPORT'
    ]
    
    missing_keys = []
    for key in api_keys:
        value = os.getenv(key)
        if value and len(value) > 10:
            print(f"✅ {key}: Configured")
        else:
            print(f"❌ {key}: Not configured")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Get your Google AI API key from: https://aistudio.google.com/")
        print("Add them to your .env file")
        return False
    
    return True

def create_temp_directories():
    """Create necessary directories"""
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print(f"✅ Created temp directory: {temp_dir}")

def test_database():
    """Test database connection"""
    try:
        from app import init_database, get_db_connection
        init_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM admins")
        admin_count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database initialized. Admin users: {admin_count}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main startup sequence"""
    print("🚀 FixMyHyd Production Startup Check")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n💡 For production deployment on Render:")
        print("   1. Set environment variables in Render dashboard")
        print("   2. Use the same Google AI API key for all variables")
        print("   3. Let Render generate the SECRET_KEY")
    
    # Create directories
    create_temp_directories()
    
    # Test database
    if not test_database():
        sys.exit(1)
    
    print("\n✅ Production readiness check complete!")
    print("\n🌐 Ready for Render deployment:")
    print("   1. Push code to GitHub")
    print("   2. Create new Web Service on Render")
    print("   3. Configure environment variables")
    print("   4. Deploy!")
    
    print("\n📚 See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()