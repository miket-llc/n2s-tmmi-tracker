#!/bin/bash
# SSL Certificate Setup with Let's Encrypt
# Run this after the basic server setup

echo "🔐 Setting up SSL Certificate for motoko.hopto.org"
echo "================================================="

# Install certbot if not already installed
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
echo "📜 Obtaining SSL certificate..."
sudo certbot --nginx -d motoko.hopto.org --non-interactive --agree-tos --email your-email@example.com

# Set up automatic renewal
echo "🔄 Setting up automatic renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
echo "🧪 Testing certificate renewal..."
sudo certbot renew --dry-run

echo "✅ SSL setup complete!"
echo "🌐 Your app is now available at: https://motoko.hopto.org"
echo ""
echo "🔧 Certificate management:"
echo "- Check status: sudo certbot certificates"
echo "- Renew manually: sudo certbot renew"
echo "- Check auto-renewal: sudo systemctl status certbot.timer"