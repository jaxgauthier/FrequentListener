#!/bin/bash
# Server Setup Script for Audio Frequency Game
# Run this as root or with sudo

echo "🚀 Setting up server for Audio Frequency Game..."

# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

# Create application user
useradd -m -s /bin/bash audioapp
usermod -aG sudo audioapp

# Create application directory
mkdir -p /var/www/audio-game
chown audioapp:audioapp /var/www/audio-game

# Set up firewall
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

echo "✅ Server setup complete!"
echo "📝 Next steps:"
echo "1. Upload your code to /var/www/audio-game"
echo "2. Run the application setup script"
echo "3. Configure Nginx"
echo "4. Set up SSL certificate" 