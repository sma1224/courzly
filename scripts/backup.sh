#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="courzly_backup_$TIMESTAMP"

echo "🗄️ Starting backup process..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Load environment variables
source .env

# Backup PostgreSQL database
echo "📊 Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U courzly courzly > "$BACKUP_DIR/${BACKUP_NAME}_postgres.sql"

# Backup Redis data
echo "💾 Backing up Redis data..."
docker-compose exec -T redis redis-cli --rdb - > "$BACKUP_DIR/${BACKUP_NAME}_redis.rdb"

# Backup uploaded files
echo "📁 Backing up uploaded files..."
if [ -d "./uploads" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz" -C . uploads/
fi

# Backup configuration files
echo "⚙️ Backing up configuration..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" \
    .env \
    docker-compose.yml \
    configs/ \
    --exclude=configs/ssl/

# Create combined backup archive
echo "📦 Creating combined backup archive..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz" \
    -C $BACKUP_DIR \
    "${BACKUP_NAME}_postgres.sql" \
    "${BACKUP_NAME}_redis.rdb" \
    "${BACKUP_NAME}_uploads.tar.gz" \
    "${BACKUP_NAME}_config.tar.gz"

# Cleanup individual files
rm -f "$BACKUP_DIR/${BACKUP_NAME}_postgres.sql"
rm -f "$BACKUP_DIR/${BACKUP_NAME}_redis.rdb"
rm -f "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz"
rm -f "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz"

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "courzly_backup_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_NAME}_complete.tar.gz"
echo "📊 Backup size: $(du -h "$BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz" | cut -f1)"