#!/bin/bash
# Monitoring and maintenance script for TMMi Assessment Tracker

APP_DIR="/opt/tmmi-tracker"
SERVICE_NAME="tmmi-tracker"

echo "📊 TMMi Assessment Tracker - Server Status"
echo "=========================================="

# Check service status
echo "🔧 Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "💾 Database Status:"
if [ -f "$APP_DIR/data/assessments.db" ]; then
    echo "✅ Database file exists"
    DB_SIZE=$(du -h "$APP_DIR/data/assessments.db" | cut -f1)
    echo "📊 Database size: $DB_SIZE"
else
    echo "❌ Database file not found"
fi

echo ""
echo "📁 Disk Usage:"
df -h $APP_DIR

echo ""
echo "🔍 Recent Logs (last 20 lines):"
sudo journalctl -u $SERVICE_NAME -n 20 --no-pager

echo ""
echo "🌐 Nginx Status:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "🔐 SSL Certificate Status:"
sudo certbot certificates

echo ""
echo "📈 System Resources:"
echo "Memory usage:"
free -h
echo ""
echo "CPU usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//'

echo ""
echo "🔧 Useful Commands:"
echo "- Restart app: sudo systemctl restart $SERVICE_NAME"
echo "- View live logs: sudo journalctl -u $SERVICE_NAME -f"
echo "- Update app: cd $APP_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
echo "- Backup database: cp $APP_DIR/data/assessments.db $APP_DIR/data/assessments.db.backup"