# 🚀 Quick Start: Deploy Audio Frequency Game Publicly

## Prerequisites
- **Domain name** (e.g., `yourdomain.com`)
- **VPS/Server** (Ubuntu/Debian recommended)
- **Root/sudo access** to the server

## Step 1: Prepare Your Domain
1. **Buy a domain** (Namecheap, GoDaddy, etc.)
2. **Point DNS** to your server's IP address:
   - Create an A record: `yourdomain.com` → `YOUR_SERVER_IP`
   - Create an A record: `www.yourdomain.com` → `YOUR_SERVER_IP`

## Step 2: Upload Your Code
```bash
# On your local machine, upload the project
scp -r /path/to/your/DFT user@YOUR_SERVER_IP:/tmp/
```

## Step 3: Deploy on Server
```bash
# SSH into your server
ssh user@YOUR_SERVER_IP

# Move to root and run deployment
sudo su -
cd /tmp/DFT
nano deployment/deploy.sh  # Edit DOMAIN="yourdomain.com"
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

## Step 4: Verify Deployment
```bash
# Check services
sudo systemctl status audio-game
sudo systemctl status nginx

# Test website
curl -I https://yourdomain.com
```

## Step 5: Set Up Backups
```bash
# Add to crontab for daily backups
sudo crontab -e
# Add: 0 2 * * * /var/www/audio-game/deployment/backup.sh
```

## Your Website is Live! 🎉

**URLs:**
- Main site: `https://yourdomain.com`
- Admin panel: `https://yourdomain.com/admin`
- Health check: `https://yourdomain.com/health`

**Default Admin Credentials:**
- Username: `admin`
- Password: `MadJax195`

## Useful Commands

### Check Status
```bash
sudo systemctl status audio-game    # App status
sudo systemctl status nginx         # Web server status
sudo journalctl -u audio-game -f    # View app logs
```

### Restart Services
```bash
sudo systemctl restart audio-game   # Restart app
sudo systemctl reload nginx         # Reload web server
```

### Update Application
```bash
cd /var/www/audio-game
sudo -u audioapp git pull
sudo systemctl restart audio-game
```

### SSL Certificate Renewal
```bash
sudo certbot renew --dry-run        # Test renewal
sudo certbot renew                  # Renew certificates
```

## Troubleshooting

### App Won't Start
```bash
sudo journalctl -u audio-game -n 50
sudo systemctl status audio-game
```

### Nginx Issues
```bash
sudo nginx -t                       # Test config
sudo systemctl status nginx
```

### Database Issues
```bash
cd /var/www/audio-game
sudo -u audioapp python scripts/init_db.py
```

### Permission Issues
```bash
sudo chown -R audioapp:audioapp /var/www/audio-game
sudo chmod -R 755 /var/www/audio-game
```

## Security Notes
- ✅ Firewall enabled (SSH + HTTP/HTTPS only)
- ✅ SSL certificate installed
- ✅ Sensitive files protected
- ✅ Application runs as non-root user
- ✅ Regular backups configured

## Next Steps
1. **Test all features** on your live site
2. **Change default passwords**
3. **Set up monitoring** (optional)
4. **Configure email** for admin notifications
5. **Set up CDN** for better performance (optional)

## Support
If you encounter issues:
1. Check the logs: `sudo journalctl -u audio-game -f`
2. Verify DNS propagation: `nslookup yourdomain.com`
3. Test SSL: `curl -I https://yourdomain.com`
4. Check firewall: `sudo ufw status` 