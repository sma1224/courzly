#!/bin/bash
set -e

DOMAIN=${1:-localhost}
EMAIL=${2:-admin@example.com}

echo "🔐 Setting up SSL certificates for domain: $DOMAIN"

if [ "$DOMAIN" = "localhost" ]; then
    echo "📝 Creating self-signed certificates for local development..."
    
    # Create SSL directory
    mkdir -p configs/ssl
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout configs/ssl/key.pem \
        -out configs/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    echo "✅ Self-signed certificates created in configs/ssl/"
    
else
    echo "🌐 Setting up Let's Encrypt certificates for production..."
    
    # Install certbot for Ubuntu 24.04
    sudo apt-get update -y
    sudo snap install core; sudo snap refresh core
    sudo snap install --classic certbot
    sudo ln -sf /snap/bin/certbot /usr/bin/certbot
    
    # Stop nginx if running
    sudo systemctl stop nginx 2>/dev/null || true
    sudo docker-compose down 2>/dev/null || true
    
    # Get certificate
    sudo certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        -d $DOMAIN
    
    # Copy certificates to configs directory
    sudo mkdir -p configs/ssl
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem configs/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem configs/ssl/key.pem
    sudo chown $USER:$USER configs/ssl/*.pem
    
    # Setup auto-renewal
    echo "0 12 * * * /snap/bin/certbot renew --quiet && docker-compose restart nginx" | sudo crontab -
    
    echo "✅ Let's Encrypt certificates configured!"
    echo "📅 Auto-renewal scheduled via cron"
fi

echo "🔒 SSL setup complete!"