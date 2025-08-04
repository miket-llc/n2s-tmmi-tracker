# N2S TMMi Tracker - Production Deployment Guide

## Database Persistence Setup

### Environment Variables

Set the following environment variables in your production environment:

```bash
# Database path - should point to persistent storage
export TMMI_DB_PATH="/app/persistent_data/assessments.db"

# Backup directory - should also be on persistent storage
export TMMI_BACKUP_DIR="/app/persistent_data/backups"

# Questions file path
export TMMI_QUESTIONS_PATH="/app/persistent_data/tmmi_questions.json"
```

### Docker Deployment

1. **Build and run with Docker Compose**:
```bash
docker-compose up -d
```

2. **Manual Docker setup**:
```bash
# Build image
docker build -t n2s-tmmi-tracker .

# Run with persistent volumes
docker run -d \
  --name n2s-tmmi-tracker \
  -p 8501:8501 \
  -v tmmi_data:/app/persistent_data \
  -v tmmi_logs:/app/logs \
  -e TMMI_DB_PATH=/app/persistent_data/assessments.db \
  -e TMMI_BACKUP_DIR=/app/persistent_data/backups \
  n2s-tmmi-tracker
```

### Traditional Server Deployment

1. **Set up environment variables** in your deployment script or server environment:
```bash
export TMMI_DB_PATH="/var/lib/tmmi/assessments.db"
export TMMI_BACKUP_DIR="/var/lib/tmmi/backups"
```

2. **Create directories**:
```bash
sudo mkdir -p /var/lib/tmmi/backups
sudo chown -R $USER:$USER /var/lib/tmmi
```

3. **Run the application**:
```bash
./run_app.sh
```

## GitHub Actions Integration

### Environment Setup

Add these secrets to your GitHub repository:

- `PRODUCTION_SERVER_HOST`: Your server hostname/IP
- `PRODUCTION_SERVER_USER`: SSH username
- `PRODUCTION_SERVER_KEY`: SSH private key
- `TMMI_DB_PATH`: Production database path
- `TMMI_BACKUP_DIR`: Production backup directory

### Sample GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy N2S TMMi Tracker

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Create backup before deployment
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.PRODUCTION_SERVER_HOST }}
        username: ${{ secrets.PRODUCTION_SERVER_USER }}
        key: ${{ secrets.PRODUCTION_SERVER_KEY }}
        script: |
          cd /app/tmmi-tracker
          # Create pre-deployment backup
          if [ -f "${{ secrets.TMMI_DB_PATH }}" ]; then
            cp "${{ secrets.TMMI_DB_PATH }}" "${{ secrets.TMMI_BACKUP_DIR }}/pre_deploy_$(date +%Y%m%d_%H%M%S).db"
          fi
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.PRODUCTION_SERVER_HOST }}
        username: ${{ secrets.PRODUCTION_SERVER_USER }}
        key: ${{ secrets.PRODUCTION_SERVER_KEY }}
        script: |
          cd /app/tmmi-tracker
          git pull origin main
          
          # Set environment variables
          export TMMI_DB_PATH="${{ secrets.TMMI_DB_PATH }}"
          export TMMI_BACKUP_DIR="${{ secrets.TMMI_BACKUP_DIR }}"
          
          # Restart application
          pkill -f "streamlit run app.py" || true
          nohup ./run_app.sh > deploy.log 2>&1 &
          
          # Wait for application to start
          sleep 10
          
          # Health check
          curl -f http://localhost:8501/_stcore/health || exit 1
```

## Data Migration and Backup

### Initial Data Setup

1. **Copy existing data to persistent location**:
```bash
# If you have existing data/assessments.db
mkdir -p $TMMI_BACKUP_DIR
cp data/assessments.db $TMMI_DB_PATH
cp data/tmmi_questions.json $TMMI_QUESTIONS_PATH
```

2. **Verify the setup**:
```bash
# Check if database is accessible
python3 -c "
from src.models.database import TMMiDatabase
db = TMMiDatabase()
print('Database path:', db.db_path)
print('Health check:', db.verify_database_integrity())
print('Stats:', db.get_database_stats())
"
```

### Automated Backups

Add to your crontab for regular backups:

```bash
# Backup every 6 hours
0 */6 * * * /usr/bin/python3 -c "
import os
os.environ['TMMI_DB_PATH'] = '/var/lib/tmmi/assessments.db'
os.environ['TMMI_BACKUP_DIR'] = '/var/lib/tmmi/backups'
from src.models.database import TMMiDatabase
db = TMMiDatabase()
backup_path = db.backup_database()
print(f'Backup created: {backup_path}')
" >> /var/log/tmmi_backup.log 2>&1
```

## Monitoring and Health Checks

### Application Health

The application includes built-in health monitoring accessible through the "Database Admin" page:

- Database integrity checks
- Connection monitoring
- Backup status
- Performance metrics

### Log Monitoring

Monitor these log files:

- `logs/app.log`: Application logs
- `deploy.log`: Deployment logs (if using GitHub Actions)
- `/var/log/tmmi_backup.log`: Backup operation logs

### Resource Monitoring

Monitor these resources:

- Disk space for database and backups
- Database file size growth
- Application memory usage
- Response times

## Troubleshooting

### Database Issues

1. **Database file not found**:
```bash
# Check environment variables
echo $TMMI_DB_PATH
ls -la $(dirname $TMMI_DB_PATH)

# Initialize if needed
python3 -c "from src.models.database import TMMiDatabase; TMMiDatabase()"
```

2. **Backup restore**:
```bash
# List available backups
ls -la $TMMI_BACKUP_DIR/*.db

# Restore from backup (through admin interface or manually)
cp $TMMI_BACKUP_DIR/backup_file.db $TMMI_DB_PATH
```

3. **Database corruption**:
```bash
# Check integrity
sqlite3 $TMMI_DB_PATH "PRAGMA integrity_check;"

# Recover if possible
sqlite3 $TMMI_DB_PATH ".backup backup.db"
mv backup.db $TMMI_DB_PATH
```

### Permission Issues

```bash
# Fix permissions
sudo chown -R $USER:$USER $(dirname $TMMI_DB_PATH)
chmod 755 $(dirname $TMMI_DB_PATH)
chmod 644 $TMMI_DB_PATH
```

### Performance Issues

1. **Database size**: Monitor using the Database Admin interface
2. **Vacuum database**: Use the "Vacuum Database" option in admin interface
3. **Clean old backups**: Regularly clean old backup files

## Security Considerations

1. **File Permissions**: Ensure database files are not publicly accessible
2. **Backup Security**: Store backups in secure, encrypted storage
3. **Network Security**: Use HTTPS in production
4. **Access Control**: Implement proper authentication if needed

## Scaling Considerations

For larger deployments, consider:

1. **Database Migration**: Move to PostgreSQL for better concurrent access
2. **Load Balancing**: Multiple Streamlit instances behind a load balancer
3. **Backup Strategy**: Implement incremental backups
4. **Monitoring**: Use proper APM tools for production monitoring