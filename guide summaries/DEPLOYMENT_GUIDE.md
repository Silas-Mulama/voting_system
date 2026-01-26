# eVoting System - Deployment Guide

## Quick Start for Production

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Nginx or Apache
- SSL Certificate (Let's Encrypt)
- Linux server (Ubuntu 20.04+ recommended)

---

## Step 1: Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib nginx supervisor

# Create application user
sudo useradd -m -d /home/evoting evoting
sudo su - evoting
```

---

## Step 2: Application Setup

```bash
# Clone repository
cd /home/evoting
git clone <repository-url> evoting_system
cd evoting_system

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-new-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/evoting
DJANGO_LOG_LEVEL=INFO
EOF

# Load environment variables
export $(cat .env | xargs)
```

---

## Step 3: Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE evoting;"
sudo -u postgres psql -c "CREATE USER evoting_user WITH PASSWORD 'strong-password';"
sudo -u postgres psql -c "ALTER ROLE evoting_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE evoting_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE evoting_user SET default_transaction_deferrable TO on;"
sudo -u postgres psql -c "ALTER ROLE evoting_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE evoting TO evoting_user;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Verify setup
python manage.py check --deploy
```

---

## Step 4: Gunicorn Configuration

Create `/home/evoting/evoting_system/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = False
daemon = False
accesslog = "/home/evoting/evoting_system/logs/access.log"
errorlog = "/home/evoting/evoting_system/logs/error.log"
loglevel = "info"
```

---

## Step 5: Supervisor Configuration

Create `/etc/supervisor/conf.d/evoting.conf`:

```ini
[program:evoting]
directory=/home/evoting/evoting_system
command=/home/evoting/evoting_system/.venv/bin/gunicorn \
    --config /home/evoting/evoting_system/gunicorn_config.py \
    evoting_system.wsgi:application
user=evoting
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/evoting/evoting_system/logs/supervisor.log
environment=PATH="/home/evoting/evoting_system/.venv/bin",\
    HOME="/home/evoting"
```

```bash
# Create logs directory
mkdir -p /home/evoting/evoting_system/logs
chown evoting:evoting /home/evoting/evoting_system/logs

# Start supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start evoting
```

---

## Step 6: Nginx Configuration

Create `/etc/nginx/sites-available/evoting`:

```nginx
upstream evoting_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/evoting_access.log;
    error_log /var/log/nginx/evoting_error.log;

    # Client size limit
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/evoting/evoting_system/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /home/evoting/evoting_system/media/;
        expires 7d;
    }

    # Application
    location / {
        proxy_pass http://evoting_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/evoting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 7: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Step 8: Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Step 9: Backup Configuration

Create `/home/evoting/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/evoting/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump evoting > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/evoting/evoting_system/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed at $DATE"
```

```bash
# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/evoting/backup.sh") | crontab -
```

---

## Step 10: Monitoring & Alerts

```bash
# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Check application status
sudo supervisorctl status evoting

# View logs
tail -f /home/evoting/evoting_system/logs/error.log
tail -f /var/log/nginx/evoting_error.log
```

---

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo supervisorctl tail evoting stderr
python manage.py runserver  # Test locally
```

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx
```

### Database connection issues
```bash
psql -U evoting_user -d evoting -h localhost
# Test connection from application directory
```

### High CPU/Memory usage
```bash
# Adjust gunicorn workers
# Check for slow queries
python manage.py dbshell
```

---

## Post-Deployment

1. **Test the system**
   - Admin login
   - Student registration
   - Create election
   - Test voting

2. **Monitor for 24 hours**
   - Check error logs
   - Monitor performance
   - Verify backups

3. **Document any issues**
   - Create fixes
   - Update documentation

---

## Emergency Procedures

### Restore from Backup
```bash
sudo -u postgres psql evoting < /home/evoting/backups/db_backup.sql
```

### Restart Application
```bash
sudo supervisorctl restart evoting
```

### Rollback Deployment
```bash
git revert HEAD
python manage.py migrate
sudo supervisorctl restart evoting
```

---

**Deployment completed successfully! 🎉**
