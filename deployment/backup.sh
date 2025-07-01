#!/bin/bash
# Backup Script for Audio Frequency Game
# Run this as root or with sudo

APP_DIR="/var/www/audio-game"
BACKUP_DIR="/var/backups/audio-game"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Creating backup for Audio Frequency Game..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup archive
tar -czf $BACKUP_DIR/audio-game-backup-$DATE.tar.gz \
    -C $APP_DIR \
    instance/ \
    audio/ \
    .env \
    logs/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "audio-game-backup-*.tar.gz" -mtime +7 -delete

echo "✅ Backup created: audio-game-backup-$DATE.tar.gz"
echo "📁 Backup location: $BACKUP_DIR"

# Optional: Upload to cloud storage (uncomment and configure)
# aws s3 cp $BACKUP_DIR/audio-game-backup-$DATE.tar.gz s3://your-bucket/backups/
# or
# gsutil cp $BACKUP_DIR/audio-game-backup-$DATE.tar.gz gs://your-bucket/backups/ 