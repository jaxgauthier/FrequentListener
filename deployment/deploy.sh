#!/bin/bash
# Complete Deployment Script for Audio Frequency Game
# Run this as root

DOMAIN="yourdomain.com"  # CHANGE THIS TO YOUR DOMAIN
APP_DIR="/var/www/audio-game"

echo "🚀 Starting deployment of Audio Frequency Game..."
echo "📍 Domain: $DOMAIN"
echo "📁 App directory: $APP_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root or with sudo"
    exit 1
fi

# Step 1: Server setup
echo "📦 Setting up server packages..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# Create application user if it doesn't exist
if ! id "audioapp" &>/dev/null; then
    useradd -m -s /bin/bash audioapp
    usermod -aG sudo audioapp
fi

# Create application directory
mkdir -p $APP_DIR
chown audioapp:audioapp $APP_DIR

# Step 2: Copy application files
echo "📁 Setting up application..."
if [ -d "app" ]; then
    # If running from project directory
    cp -r . $APP_DIR/
    chown -R audioapp:audioapp $APP_DIR
else
    echo "❌ Please run this script from your project directory"
    exit 1
fi

# Step 3: Application setup (as audioapp user)
echo "🐍 Setting up Python environment..."
sudo -u audioapp bash << EOF
cd $APP_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create production config
cat > .env << EOL
FLASK_ENV=production
SECRET_KEY=\$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///instance/audio_game.db
EOL

# Create necessary directories
mkdir -p instance logs audio/uploads

# Set proper permissions
chmod 755 $APP_DIR
chmod 644 .env

# Initialize database
python scripts/init_db.py

# Create admin user
python scripts/create_admin.py
EOF

# Step 4: Configure systemd service
echo "⚙️ Configuring systemd service..."
cp deployment/audio-game.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable audio-game

# Step 5: Configure Nginx
echo "🌐 Configuring Nginx..."
# Update domain in nginx config
sed -i "s/yourdomain.com/$DOMAIN/g" deployment/nginx-audio-game
cp deployment/nginx-audio-game /etc/nginx/sites-available/audio-game
ln -sf /etc/nginx/sites-available/audio-game /etc/nginx/sites-enabled/

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Step 6: Set up firewall
echo "🔥 Configuring firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Step 7: Start the application
echo "🎵 Starting the application..."
systemctl start audio-game
systemctl status audio-game --no-pager

# Step 8: SSL Certificate
echo "🔒 Setting up SSL certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Step 9: Final status check
echo "✅ Deployment complete!"
echo ""
echo "📊 Status:"
systemctl status audio-game --no-pager
systemctl status nginx --no-pager

echo ""
echo "🌐 Your app should now be available at:"
echo "   http://$DOMAIN"
echo "   https://$DOMAIN"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status audio-game    # Check app status"
echo "   sudo systemctl restart audio-game   # Restart app"
echo "   sudo journalctl -u audio-game -f    # View app logs"
echo "   sudo nginx -t                       # Test nginx config"
echo "   sudo systemctl reload nginx         # Reload nginx"
echo ""
echo "📝 Next steps:"
echo "1. Test your website at https://$DOMAIN"
echo "2. Set up automated backups"
echo "3. Configure monitoring (optional)"
echo "4. Update your DNS records to point to this server" 