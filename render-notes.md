# Render deployment configuration for FixMyHyd
# This file configures the deployment settings for Render.com

# Using standard Python environment
# Render automatically handles most dependencies

# Key changes for compatibility:
# 1. Using Python 3.12 for better compatibility
# 2. Updated package versions
# 3. Simplified build process
# 4. No custom build scripts needed

# Environment variables to set in Render Dashboard:
# - SECRET_KEY (auto-generate)
# - FLASK_ENV=production
# - GOOGLE_API_KEY_IMAGE=your-api-key
# - GOOGLE_API_KEY_AUDIO=your-api-key
# - GOOGLE_API_KEY_TEXT=your-api-key
# - GOOGLE_API_KEY_REPORT=your-api-key