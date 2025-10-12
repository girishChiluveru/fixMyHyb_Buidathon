# FixMyHyd - Render Deployment Guide

## 🎯 Complete Step-by-Step Guide to Deploy on Render

### 📋 Prerequisites
- GitHub account
- Render account (free tier available)
- Google AI API keys from Google AI Studio
- Your local FixMyHyd project ready

---

## 🔧 Step 1: Prepare Your Application for Production

### 1.1 Create Production Configuration Files

First, we need to create configuration files for Render deployment.

#### Create `render.yaml` (Render Configuration)
```yaml
services:
  - type: web
    name: fixmyhyd
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
```

#### Update `requirements.txt` for Production
```txt
Flask==2.3.3
Pillow==10.0.1
python-dotenv==1.0.0
google-generativeai==0.3.2
Werkzeug==2.3.7
gunicorn==21.2.0
```

#### Create `runtime.txt` (Python Version)
```txt
python-3.11.0
```

### 1.2 Modify Application for Production

#### Update `app.py` for Production Deployment
- Change the final run section to support Render's port configuration
- Update database path for persistent storage
- Add production-ready configurations

---

## 🌐 Step 2: Prepare for Render Deployment

### 2.1 Update Application Configuration

You'll need to modify your `app.py` file to work with Render's environment:

1. **Port Configuration**: Use Render's PORT environment variable
2. **Database Path**: Use absolute path for database
3. **Temp Directory**: Create proper temp directory handling
4. **CORS and Security**: Add production security settings

### 2.2 Environment Variables Setup

Create a production `.env` file structure that will be configured in Render dashboard:

```env
# Production Environment Variables for Render
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
GOOGLE_API_KEY_IMAGE=your-google-api-key
GOOGLE_API_KEY_AUDIO=your-google-api-key  
GOOGLE_API_KEY_TEXT=your-google-api-key
GOOGLE_API_KEY_REPORT=your-google-api-key
DATABASE_URL=sqlite:///opt/render/project/src/fixmyhyd.db
PORT=10000
```

---

## 🚀 Step 3: Deploy to Render

### 3.1 Repository Setup

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Ensure all files are committed**:
   - Updated `requirements.txt` with gunicorn
   - Modified `app.py` for production
   - `render.yaml` configuration
   - `runtime.txt` for Python version

### 3.2 Render Dashboard Setup

1. **Create New Web Service**:
   - Go to [Render Dashboard](https://render.com/dashboard)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your FixMyHyd repository

2. **Configure Build & Deploy Settings**:
   ```
   Name: fixmyhyd-app
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

3. **Add Environment Variables** in Render Dashboard:
   ```
   SECRET_KEY = [Generate Random Key]
   FLASK_ENV = production
   GOOGLE_API_KEY_IMAGE = [Your Google AI API Key]
   GOOGLE_API_KEY_AUDIO = [Your Google AI API Key]
   GOOGLE_API_KEY_TEXT = [Your Google AI API Key]
   GOOGLE_API_KEY_REPORT = [Your Google AI API Key]
   PYTHON_VERSION = 3.11.0
   ```

---

## 🔐 Step 4: Configure Environment Variables in Render

### 4.1 Required Environment Variables

Navigate to your service → Environment tab and add:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SECRET_KEY` | Use "Generate" button | Flask session security |
| `FLASK_ENV` | `production` | Production mode |
| `GOOGLE_API_KEY_IMAGE` | Your API key | Image analysis |
| `GOOGLE_API_KEY_AUDIO` | Your API key | Audio transcription |
| `GOOGLE_API_KEY_TEXT` | Your API key | Text analysis |
| `GOOGLE_API_KEY_REPORT` | Your API key | Report generation |
| `PYTHON_VERSION` | `3.11.0` | Python runtime |

### 4.2 Get Google AI API Keys

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the key and paste it into all four GOOGLE_API_KEY_* variables in Render
4. **Important**: You can use the same API key for all four variables

---

## 📝 Step 5: Code Modifications for Production

### 5.1 Update Database Configuration

The current SQLite database will work on Render, but you need to ensure proper path handling:

### 5.2 Update Port Configuration

The app currently runs on port 5001, but Render assigns a dynamic port.

### 5.3 Update Temp Directory Handling

Render has specific requirements for temporary file storage.

---

## ✅ Step 6: Deploy and Test

### 6.1 Initial Deployment

1. **Deploy**: Click "Deploy Latest Commit" in Render dashboard
2. **Monitor Logs**: Watch the build and deploy logs for any errors
3. **Wait**: First deployment takes 5-10 minutes

### 6.2 Access Your Application

Once deployed, Render provides:
- **Your App URL**: `https://your-app-name.onrender.com`
- **Admin Login**: `/admin/login` (admin/admin123)
- **User Registration**: `/user/register`

### 6.3 Test Core Features

1. **Home Page**: Verify it loads correctly
2. **User Registration**: Create a test account
3. **Admin Dashboard**: Login with admin credentials
4. **Report Issue**: Test the complete workflow
5. **AI Features**: Ensure API keys work correctly

---

## 🔧 Step 7: Production Optimizations

### 7.1 Database Persistence

Render's free tier has ephemeral storage. For production:
- Consider upgrading to a paid plan for persistent storage
- Or migrate to PostgreSQL using Render's database service

### 7.2 File Upload Optimization

For production, consider:
- Using cloud storage (AWS S3, Google Cloud Storage)
- Implementing file size limits
- Adding file validation

### 7.3 Performance Optimizations

- Enable gzip compression
- Add caching headers
- Optimize database queries
- Consider using Redis for sessions

---

## 🚨 Troubleshooting Common Issues

### Build Failures
- Check `requirements.txt` for correct package versions
- Ensure Python version compatibility
- Review build logs for specific errors

### Runtime Errors
- Verify all environment variables are set
- Check API key validity
- Review application logs in Render dashboard

### Database Issues
- Ensure database initialization runs on startup
- Check file permissions
- Verify database path configuration

### API Key Issues
- Confirm Google AI API keys are valid
- Check quota limits
- Verify API is enabled in Google Cloud Console

---

## 📊 Step 8: Production Monitoring

### 8.1 Render Dashboard Monitoring
- Monitor application logs
- Check resource usage
- Set up alerts for downtime

### 8.2 Application Health Checks
- Implement health check endpoints
- Monitor database connectivity
- Track API response times

---

## 🎉 Step 9: Go Live!

### 9.1 Final Verification
1. **All Features Working**: Test complete user journey
2. **Admin Functions**: Verify admin dashboard and controls
3. **AI Integration**: Confirm all AI features operational
4. **Mobile Responsive**: Test on mobile devices

### 9.2 Share Your Application
- **Production URL**: `https://your-app-name.onrender.com`
- **Admin Access**: Share admin credentials securely
- **User Guide**: Provide user documentation

---

## 🔄 Step 10: Updates and Maintenance

### 10.1 Continuous Deployment
- Push updates to GitHub main branch
- Render automatically deploys changes
- Monitor deployment success

### 10.2 Backup Strategy
- Regular database exports
- Source code version control
- Environment variable backup

### 10.3 Scaling Considerations
- Monitor usage patterns
- Plan for increased load
- Consider upgrading Render plan

---

## 📞 Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Google AI Documentation**: [ai.google.dev](https://ai.google.dev)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---

## 🎯 Success Metrics

After deployment, your FixMyHyd application will be:
- ✅ Accessible globally via HTTPS
- ✅ Scalable and production-ready
- ✅ Integrated with Google AI services
- ✅ Mobile-responsive and user-friendly
- ✅ Secure with proper authentication

**Your AI-powered civic issue reporting system is now live and ready to make Hyderabad a better place!** 🏙️✨