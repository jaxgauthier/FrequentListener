# 🚂 Railway Deployment Guide

## Prerequisites
- **Railway account** (sign up at [railway.app](https://railway.app))
- **GitHub account** with your code repository
- **Domain name** (optional, Railway provides free subdomain)

## Step 1: Prepare Your Repository

### 1.1 Push Your Code to GitHub
```bash
# If you haven't already, push your code to GitHub
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 1.2 Verify Required Files
Make sure these files are in your repository:
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `app/__init__.py` - App factory
- ✅ `app/config.py` - Configuration

## Step 2: Deploy to Railway

### 2.1 Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### 2.2 Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```bash
# Required
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://... (Railway will provide this)

# Optional
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
LOG_LEVEL=INFO
```

### 2.3 Add PostgreSQL Database
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable

### 2.4 Deploy
1. Railway will automatically detect your Python app
2. It will use the `Procfile` to start your application
3. Deployment will begin automatically

## Step 3: Initialize Database

### 3.1 Access Railway Console
1. Go to your project in Railway dashboard
2. Click on your web service
3. Go to "Settings" tab
4. Click "Open Console"

### 3.2 Run Database Initialization
```bash
# In the Railway console
python scripts/init_db.py
python scripts/create_admin.py
```

## Step 4: Configure Custom Domain (Optional)

### 4.1 Add Custom Domain
1. In Railway dashboard, go to your web service
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update your DNS records as instructed

### 4.2 SSL Certificate
Railway automatically provides SSL certificates for all domains.

## Step 5: Verify Deployment

### 5.1 Check Health Endpoint
Visit: `https://your-app-name.railway.app/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "database": "healthy",
  "version": "1.0.0"
}
```

### 5.2 Test Main Application
Visit: `https://your-app-name.railway.app`

### 5.3 Test Admin Panel
Visit: `https://your-app-name.railway.app/admin`
- Username: `admin`
- Password: `MadJax195`

## Step 6: Monitor and Maintain

### 6.1 View Logs
In Railway dashboard:
- Go to your web service
- Click "Logs" tab
- View real-time application logs

### 6.2 Monitor Performance
Railway provides:
- Request metrics
- Error rates
- Response times
- Resource usage

### 6.3 Automatic Deployments
Railway automatically deploys when you push to your main branch.

## Troubleshooting

### App Won't Start
1. Check logs in Railway dashboard
2. Verify environment variables are set
3. Check `Procfile` syntax
4. Ensure all dependencies are in `requirements.txt`

### Database Connection Issues
1. Verify `DATABASE_URL` is set correctly
2. Check if PostgreSQL service is running
3. Ensure database is initialized

### Static Files Not Loading
1. Check if `whitenoise` is in `requirements.txt`
2. Verify static files are in `app/static/`
3. Check Railway logs for errors

### Audio Files Not Playing
1. Ensure audio files are committed to repository
2. Check file paths in `app/config.py`
3. Verify audio file permissions

## Railway-Specific Features

### Environment Variables
Railway automatically provides:
- `PORT` - Port your app should listen on
- `DATABASE_URL` - PostgreSQL connection string
- `RAILWAY_STATIC_URL` - Static file URL (if configured)

### Scaling
Railway allows you to:
- Scale horizontally (multiple instances)
- Scale vertically (more resources)
- Set up auto-scaling rules

### Monitoring
Railway provides:
- Real-time logs
- Performance metrics
- Error tracking
- Health checks

## Cost Considerations

### Free Tier
- $5/month credit
- Enough for small applications
- PostgreSQL database included

### Paid Plans
- Pay-as-you-go pricing
- More resources available
- Custom domains included

## Best Practices

### 1. Environment Variables
- Never commit secrets to repository
- Use Railway's environment variable system
- Use different values for development/production

### 2. Database
- Use PostgreSQL for production
- Set up automated backups
- Monitor database performance

### 3. Logging
- Use structured logging
- Monitor error rates
- Set up alerts for critical errors

### 4. Security
- Use strong SECRET_KEY
- Enable HTTPS (automatic on Railway)
- Regular security updates

## Support

### Railway Documentation
- [Railway Docs](https://docs.railway.app)
- [Deployment Guide](https://docs.railway.app/deploy/deployments)
- [Environment Variables](https://docs.railway.app/deploy/environment-variables)

### Community
- [Railway Discord](https://discord.gg/railway)
- [GitHub Issues](https://github.com/railwayapp/railway)

## Next Steps

1. **Test all features** on your live Railway app
2. **Set up monitoring** and alerts
3. **Configure custom domain** (optional)
4. **Set up automated backups**
5. **Monitor costs** and usage 