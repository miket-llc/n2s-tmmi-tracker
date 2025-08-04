#!/bin/bash
# Quick deployment script for updates
# Run this to deploy updates to your server

set -e

SERVER="motoko.hopto.org"
APP_DIR="/opt/tmmi-tracker"

echo "🚀 Deploying TMMi Assessment Tracker to $SERVER"
echo "=============================================="

echo "📡 Connecting to server and updating..."

ssh $SERVER << 'ENDSSH'
    # Navigate to app directory
    cd /opt/tmmi-tracker
    
    # Pull latest changes
    echo "📥 Pulling latest code..."
    git pull
    
    # Activate virtual environment and update dependencies
    echo "📚 Updating dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt --upgrade
    
    # Restart the service
    echo "🔄 Restarting application service..."
    sudo systemctl restart tmmi-tracker
    
    # Check service status
    echo "✅ Service status:"
    sudo systemctl is-active tmmi-tracker
    
    echo "🎉 Deployment complete!"
    echo "App is running at: https://motoko.hopto.org"
ENDSSH

echo "✅ Deployment finished!"
echo "🌐 Your app is available at: https://motoko.hopto.org"