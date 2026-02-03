# Deployment Guide

This guide covers various deployment options for the PowerPoint Search Platform.

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker

1. **Build the Docker image:**
```bash
docker build -t ppt-search-platform .
```

2. **Run the container:**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/slides:/app/slides \
  -v $(pwd)/ppt_search.db:/app/ppt_search.db \
  --name ppt-search \
  ppt-search-platform
```

3. **Access the application:**
Open `http://localhost:8000` in your browser.

### Using Docker Compose

1. **Start all services:**
```bash
docker-compose up -d
```

2. **View logs:**
```bash
docker-compose logs -f
```

3. **Stop services:**
```bash
docker-compose down
```

4. **Rebuild after changes:**
```bash
docker-compose up -d --build
```

## 🌐 Production Deployment

### Option 1: Traditional VPS (Ubuntu/Debian)

1. **Install dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

2. **Clone and setup:**
```bash
cd /opt
sudo git clone <your-repo> ppt-search
cd ppt-search
sudo chown -R $USER:$USER .

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend (for production build)
cd frontend
npm install
npm run build
```

3. **Configure systemd service:**

Create `/etc/systemd/system/ppt-search.service`:
```ini
[Unit]
Description=PowerPoint Search Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ppt-search
Environment="PATH=/opt/ppt-search/venv/bin"
ExecStart=/opt/ppt-search/venv/bin/python backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ppt-search
sudo systemctl start ppt-search
sudo systemctl status ppt-search
```

5. **Configure Nginx:**

Create `/etc/nginx/sites-available/ppt-search`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /slides {
        alias /opt/ppt-search/slides;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ppt-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Setup SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Option 2: Heroku Deployment

1. **Create `Procfile`:**
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy:**
```bash
heroku create your-app-name
git push heroku main
heroku open
```

3. **Add PostgreSQL (optional):**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Option 3: AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04)
2. **Configure security group** (allow ports 80, 443, 22)
3. **Follow VPS deployment steps above**
4. **Use AWS RDS** for database (optional)
5. **Use S3** for file storage (optional)

### Option 4: Google Cloud Run

1. **Build and push image:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ppt-search
```

2. **Deploy:**
```bash
gcloud run deploy ppt-search \
  --image gcr.io/PROJECT_ID/ppt-search \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔒 Security Checklist for Production

- [ ] Change default SECRET_KEY
- [ ] Restrict CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Configure file upload limits
- [ ] Set up logging
- [ ] Enable monitoring
- [ ] Regular backups
- [ ] Keep dependencies updated
- [ ] Use environment variables
- [ ] Disable debug mode

## 🔧 Production Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
# Production settings
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/pptdb
MAX_UPLOAD_SIZE=100
```

### Database Migration (SQLite to PostgreSQL)

1. **Install PostgreSQL driver:**
```bash
pip install psycopg2-binary
```

2. **Update DATABASE_URL in backend/database.py**

3. **Migrate data:**
```bash
# Export from SQLite
sqlite3 ppt_search.db .dump > backup.sql

# Import to PostgreSQL
psql -U user -d pptdb -f backup.sql
```

## 📊 Monitoring

### Setup Logging

Add to `backend/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check Endpoint

Already included at `/` - returns 200 OK

### Monitoring Tools
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Papertrail, Loggly
- **Performance**: New Relic, Datadog
- **Errors**: Sentry

## 🔄 CI/CD Pipeline

Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t ppt-search .
      
      - name: Deploy to server
        run: |
          # Your deployment commands here
          # e.g., push to registry, SSH to server, etc.
```

## 💾 Backup Strategy

### Automated Backups

Create backup script (`backup.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
cp ppt_search.db "$BACKUP_DIR/ppt_search_$DATE.db"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/ppt-search/backup.sh
```

## 🚀 Performance Optimization

### Backend
- Use Redis for caching
- Enable gzip compression
- Optimize database queries
- Use connection pooling
- Implement pagination

### Frontend
- Enable build optimization
- Use CDN for assets
- Implement lazy loading
- Add service worker
- Optimize images

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Check firewall rules
5. Review nginx/proxy configuration

---

**Happy Deploying! 🚀**

