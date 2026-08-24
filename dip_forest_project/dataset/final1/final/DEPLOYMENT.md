# StudySphere Deployment Guide

This guide provides step-by-step instructions for deploying StudySphere to production environments.

## 🚀 Quick Deployment Options

### Option 1: Render (Backend) + Vercel (Frontend) - Recommended
- **Backend**: Render.com (Free tier available)
- **Frontend**: Vercel.com (Free tier available)
- **Database**: Render PostgreSQL (Free tier available)

### Option 2: Railway (Full Stack)
- **Backend & Frontend**: Railway.com
- **Database**: Railway PostgreSQL

### Option 3: Heroku (Legacy)
- **Backend**: Heroku.com
- **Frontend**: Vercel.com
- **Database**: Heroku Postgres

## 📋 Prerequisites

Before deployment, ensure you have:

1. **GitHub Repository**: Push your code to GitHub
2. **Azure OpenAI Account**: For AI features
3. **Domain Name** (optional): For custom domain

## 🎯 Option 1: Render + Vercel Deployment

### Backend Deployment (Render)

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Verify your email

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `studysphere-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app`
   - **Plan**: Free (or choose paid for better performance)

#### Step 3: Environment Variables
Add these environment variables in Render dashboard:

```env
DATABASE_URL=postgresql://username:password@host:port/database
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SECRET_KEY=your-flask-secret-key-change-this-in-production
AZURE_OPENAI_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Step 4: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `studysphere-db`
   - **Database**: `studysphere_db`
   - **User**: `studysphere_user`
3. Copy the connection string to `DATABASE_URL`

#### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Note the service URL (e.g., `https://studysphere-backend.onrender.com`)

### Frontend Deployment (Vercel)

#### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account

#### Step 2: Import Project
1. Click "New Project"
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

#### Step 3: Environment Variables
Add these environment variables:

```env
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

#### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Your app will be available at the provided URL

## 🎯 Option 2: Railway Deployment

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account

### Step 2: Create Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository

### Step 3: Configure Services
Railway will automatically detect your services. Configure:

#### Backend Service
- **Name**: `studysphere-backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn server:app`

#### Frontend Service
- **Name**: `studysphere-frontend`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Start Command**: `cd frontend && npm start`

### Step 4: Add PostgreSQL
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will automatically link it to your services

### Step 5: Environment Variables
Add all required environment variables in Railway dashboard.

### Step 6: Deploy
1. Railway will automatically deploy on every push
2. Access your app through the provided URLs

## 🔧 Environment Variables Reference

### Required Variables
```env
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SECRET_KEY=your-flask-secret-key-change-this-in-production

# Azure OpenAI
AZURE_OPENAI_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Application
FLASK_ENV=production
FLASK_DEBUG=False
```

### Frontend Variables
```env
REACT_APP_API_URL=https://your-backend-url.com
```

## 🔒 Security Checklist

### Before Deployment
- [ ] Change default JWT secret key
- [ ] Change default Flask secret key
- [ ] Use strong passwords for database
- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Set up proper CORS origins
- [ ] Configure Azure OpenAI with proper permissions

### After Deployment
- [ ] Test all authentication flows
- [ ] Verify database connections
- [ ] Test AI suggestions functionality
- [ ] Check file upload security
- [ ] Monitor error logs
- [ ] Set up monitoring/alerting

## 📊 Monitoring & Maintenance

### Health Checks
- **Backend**: `GET /api/health`
- **Database**: Monitor connection pool
- **AI Service**: Test suggestion generation

### Logs
- **Render**: View logs in dashboard
- **Vercel**: Function logs in dashboard
- **Railway**: Real-time logs in terminal

### Performance
- Monitor response times
- Check database query performance
- Track API usage and limits

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
gunicorn server:app --log-level debug

# Verify dependencies
pip list

# Check environment variables
echo $DATABASE_URL
```

#### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL

# Check migrations
flask db upgrade
```

#### Frontend Build Fails
```bash
# Clear cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### CORS Issues
```python
# In server.py, update CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Performance Optimization

#### Backend
```python
# Add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Optimize database queries
# Use select_from() for complex joins
# Add database indexes
```

#### Frontend
```javascript
// Add service worker for caching
// Implement lazy loading
// Optimize bundle size
```

## 🔄 Continuous Deployment

### GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          # Add deployment steps
```

## 📈 Scaling Considerations

### When to Scale
- **Users**: > 1000 active users
- **Data**: > 1GB database
- **Performance**: Response time > 2s

### Scaling Options
1. **Vertical Scaling**: Upgrade plan (Render/Railway)
2. **Horizontal Scaling**: Add more instances
3. **Database**: Read replicas, connection pooling
4. **Caching**: Redis for session storage
5. **CDN**: For static assets

## 🆘 Support

### Deployment Issues
- Check platform-specific documentation
- Review logs for error messages
- Test locally with production settings
- Contact platform support

### Application Issues
- Review application logs
- Check database connectivity
- Verify environment variables
- Test API endpoints individually

---

**Need Help?** Create an issue in the GitHub repository or check the platform-specific documentation. 