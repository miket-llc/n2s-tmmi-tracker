# TMMi Assessment Tracker - Self-Hosted Deployment

Deploy the TMMi Assessment Tracker on your own Linux server at `motoko.hopto.org`.

## 🚀 Quick Start

### 1. Initial Server Setup
```bash
# Copy setup script to your server
scp deploy/server_setup.sh motoko.hopto.org:~/

# SSH to your server and run setup
ssh motoko.hopto.org
chmod +x server_setup.sh
./server_setup.sh
```

### 2. Setup SSL Certificate
```bash
# Copy SSL setup script
scp deploy/ssl_setup.sh motoko.hopto.org:~/

# Run SSL setup (update email in script first)
ssh motoko.hopto.org
chmod +x ssl_setup.sh
./ssl_setup.sh
```

### 3. Deploy Updates
```bash
# From your local machine, deploy updates
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 📊 Monitoring

### Check Status
```bash
# Copy monitoring script
scp deploy/monitor.sh motoko.hopto.org:~/

# Run monitoring
ssh motoko.hopto.org
chmod +x monitor.sh
./monitor.sh
```

### Common Commands
```bash
# SSH to server
ssh motoko.hopto.org

# Check service status
sudo systemctl status tmmi-tracker

# View live logs
sudo journalctl -u tmmi-tracker -f

# Restart application
sudo systemctl restart tmmi-tracker

# Update application
cd /opt/tmmi-tracker
git pull
sudo systemctl restart tmmi-tracker

# Backup database
cp /opt/tmmi-tracker/data/assessments.db /opt/tmmi-tracker/data/backup-$(date +%Y%m%d).db
```

## 🔧 Architecture

```
Internet → Nginx (Port 80/443) → Streamlit App (Port 8501)
                                      ↓
                               SQLite Database (Persistent)
```

## 📁 File Structure on Server

```
/opt/tmmi-tracker/
├── app.py                 # Main Streamlit app
├── src/                   # Source code
├── data/                  # SQLite database (PERSISTENT)
│   └── assessments.db
├── logs/                  # Application logs
├── venv/                  # Python virtual environment
└── requirements.txt       # Python dependencies
```

## 🔐 Security Features

- ✅ **SSL/TLS encryption** with Let's Encrypt
- ✅ **Reverse proxy** with Nginx
- ✅ **Systemd service** for automatic restart
- ✅ **Automatic certificate renewal**
- ✅ **Local SQLite** (no external database exposure)

## 📊 Benefits of Self-Hosting

1. **Data Persistence** - SQLite database stays on your server
2. **Full Control** - No external service limitations
3. **Custom Domain** - Your own `motoko.hopto.org`
4. **Performance** - No cold starts, always available
5. **Privacy** - All data stays on your server
6. **Cost** - No per-user or usage fees

## 🔄 Deployment Workflow

1. **Develop locally** - Test changes on your machine
2. **Push to GitHub** - Commit and push changes
3. **Deploy to server** - Run `./deploy/deploy.sh`
4. **Monitor** - Check status with `./deploy/monitor.sh`

## 🆘 Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u tmmi-tracker -f

# Check port availability
sudo netstat -tlnp | grep :8501

# Restart service
sudo systemctl restart tmmi-tracker
```

### Database Issues
```bash
# Check database file
ls -la /opt/tmmi-tracker/data/

# Check permissions
sudo chown -R $USER:$USER /opt/tmmi-tracker/data/

# Backup database
cp /opt/tmmi-tracker/data/assessments.db ~/backup-$(date +%Y%m%d).db
```

### Nginx Issues
```bash
# Check nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 📈 Scaling

- **Backup strategy** - Regular database backups
- **Resource monitoring** - CPU/Memory usage
- **Log rotation** - Automatic log cleanup
- **Updates** - Automated deployment process

Your TMMi Assessment Tracker will be running at:
**https://motoko.hopto.org** 🎉