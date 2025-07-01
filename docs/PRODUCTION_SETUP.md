# Production Setup Guide

This guide covers setting up the Audio Frequency Game for production deployment.

## 1. Environment Variables

Create a `.env` file in your production environment with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration (PostgreSQL recommended for production)
DATABASE_URL=postgresql://username:password@localhost/database_name

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 2. Database Setup

### PostgreSQL (Recommended for Production)

1. Install PostgreSQL:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. Create database and user:
   ```sql
   CREATE DATABASE audio_frequency_game;
   CREATE USER game_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE audio_frequency_game TO game_user;
   ```

3. Update your `.env` file:
   ```bash
   DATABASE_URL=postgresql://game_user:your_password@localhost/audio_frequency_game
   ```

### SQLite (Development Only)
For development, you can use SQLite:
```bash
DATABASE_URL=sqlite:///data/game.db
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Database Migration

Run the migration script to create tables:
```bash
python scripts/migrate_db.py
```

## 5. Logging Setup

The application automatically creates a `logs/` directory and configures logging. Logs will be written to:
- `logs/app.log` - Application logs
- Console output - For containerized deployments

## 6. Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique `SECRET_KEY` values
- Rotate API keys regularly

### Database Security
- Use strong database passwords
- Restrict database access to application servers only
- Enable SSL for database connections in production

### Application Security
- The application automatically adds security headers in production
- Ensure HTTPS is enabled in your web server configuration
- Regularly update dependencies

## 7. Deployment Options

### Option 1: Gunicorn (Recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Option 2: Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p logs

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Option 3: Vercel/Heroku
- Set environment variables in your deployment platform
- Use the provided `runtime.txt` for Python version
- Ensure `gunicorn` is in requirements.txt

## 8. Monitoring and Maintenance

### Log Monitoring
- Monitor `logs/app.log` for errors
- Set up log rotation to prevent disk space issues
- Consider using external logging services (e.g., Sentry, Loggly)

### Database Maintenance
- Regular backups of your database
- Monitor database performance
- Consider connection pooling for high traffic

### Application Health
- Set up health check endpoints
- Monitor application performance
- Regular dependency updates

## 9. Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` is correct
   - Check database server is running
   - Ensure database user has proper permissions

2. **Permission Errors**
   - Ensure `logs/` directory is writable
   - Check file permissions for upload directories

3. **Spotify API Errors**
   - Verify `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
   - Check Spotify API rate limits

### Debug Mode
For troubleshooting, temporarily enable debug mode:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
```

**Note:** Never use debug mode in production! 