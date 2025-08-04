#!/bin/bash
# TMMi Assessment Tracker - Linux Server Setup Script
# Run this on your motoko.hopto.org server

set -e

echo "🚀 Setting up TMMi Assessment Tracker on Linux Server"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# Create application directory
APP_DIR="/opt/tmmi-tracker"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository (you'll need to update this with your repo URL)
echo "📥 Cloning repository..."
cd /opt
if [ -d "tmmi-tracker" ]; then
    echo "Directory exists, pulling latest changes..."
    cd tmmi-tracker
    git pull
else
    git clone https://github.com/miket-llc/n2s-tmmi-tracker.git tmmi-tracker
    cd tmmi-tracker
fi

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory with proper permissions
echo "💾 Setting up data directory..."
mkdir -p data
mkdir -p logs
chmod 755 data logs

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/tmmi-tracker.service > /dev/null <<EOF
[Unit]
Description=TMMi Assessment Tracker Streamlit App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "🔄 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable tmmi-tracker
sudo systemctl start tmmi-tracker

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/tmmi-tracker > /dev/null <<EOF
server {
    listen 80;
    server_name motoko.hopto.org;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;
    }
    
    # Handle static files
    location /_stcore/static/ {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host \$host;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/tmmi-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Basic setup complete!"
echo ""
echo "🔐 Next steps:"
echo "1. Set up SSL certificate: sudo certbot --nginx -d motoko.hopto.org"
echo "2. Check service status: sudo systemctl status tmmi-tracker"
echo "3. View logs: sudo journalctl -u tmmi-tracker -f"
echo "4. Your app should be available at: http://motoko.hopto.org"
echo ""
echo "🔧 Useful commands:"
echo "- Restart app: sudo systemctl restart tmmi-tracker"
echo "- Update code: cd $APP_DIR && git pull && sudo systemctl restart tmmi-tracker"
echo "- View app logs: sudo journalctl -u tmmi-tracker -f"
echo "- Check nginx: sudo nginx -t && sudo systemctl reload nginx"