#!/bin/bash
# Application Setup Script
# Run this as the audioapp user

echo "🎵 Setting up Audio Frequency Game application..."

# Navigate to app directory
cd /var/www/audio-game

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create production config
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///instance/audio_game.db
EOF

# Create necessary directories
mkdir -p instance logs audio/uploads

# Set proper permissions
chmod 755 /var/www/audio-game
chmod 644 .env

# Initialize database
python scripts/init_db.py

# Create admin user
python scripts/create_admin.py

echo "✅ Application setup complete!"
echo "📝 Next steps:"
echo "1. Configure systemd service"
echo "2. Set up Nginx configuration"
echo "3. Test the application" 