# 🚀 Deploy theOne Dating App to DigitalOcean

## 📋 Prerequisites

1. **DigitalOcean Account** - Sign up at https://digitalocean.com
2. **Domain Name** (optional but recommended)
3. **OpenAI API Key** - Your existing key

## 🖥️ Step 1: Create DigitalOcean Droplet

### Create Droplet
1. **Log into DigitalOcean** → Create → Droplets
2. **Choose Image**: Ubuntu 22.04 LTS
3. **Choose Size**: 
   - **Basic Plan**: $12/month (2GB RAM, 1 CPU) - Recommended for testing
   - **Basic Plan**: $24/month (4GB RAM, 2 CPU) - Recommended for production
4. **Choose Region**: Closest to your users
5. **Authentication**: SSH Key (recommended) or Password
6. **Hostname**: `theone-dating-app`
7. **Click Create Droplet**

### Get Droplet IP
```bash
# Note your droplet's IP address (e.g., 164.90.XXX.XXX)
```

## 🔧 Step 2: Connect and Setup Server

### Connect via SSH
```bash
# Replace YOUR_DROPLET_IP with actual IP
ssh root@YOUR_DROPLET_IP
```

### Update System
```bash
apt update && apt upgrade -y
```

### Install Python and Dependencies
```bash
# Install Python 3.9+
apt install python3 python3-pip python3-venv nginx supervisor git -y

# Install Node.js (for any future frontend needs)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs
```

## 📁 Step 3: Deploy Application

### Create Application Directory
```bash
mkdir -p /var/www/theone
cd /var/www/theone
```

### Upload Your Code
**Option A: Git (Recommended)**
```bash
# If you have a Git repository
git clone YOUR_REPOSITORY_URL .

# Or create the files manually (see below)
```

**Option B: Manual Upload**
```bash
# Create the directory structure
mkdir -p app/{api,core,db,models,services} templates static/uploads/{profiles,expectations}

# You'll need to upload your files via SCP or create them manually
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python Dependencies
```bash
pip install fastapi uvicorn sqlalchemy sqlite3 openai python-multipart pillow passlib bcrypt python-jose cryptography pydantic-settings jinja2
```

## 🔐 Step 4: Environment Configuration

### Create Production Environment File
```bash
cat > .env << 'EOF'
# Production Environment
DEBUG=False
APP_NAME="theOne - AI Dating"
SECRET_KEY="your-super-secret-key-change-this-in-production"

# Database
DATABASE_URL="sqlite:///./theone_production.db"

# OpenAI Configuration
OPENAI_API_KEY="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"
GPT_MODEL="gpt-4o-mini"
EMBEDDING_MODEL="text-embedding-3-small"

# Security
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
EOF
```

### Set Proper Permissions
```bash
chown -R www-data:www-data /var/www/theone
chmod -R 755 /var/www/theone
chmod 600 /var/www/theone/.env
```

## 🗄️ Step 5: Database Setup

### Initialize Production Database
```bash
cd /var/www/theone
source venv/bin/activate

# Create database and tables
python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
print('✅ Production database initialized!')
"

# Create initial test data (optional)
python3 create_test_profiles.py
python3 create_alternative_lifestyle_profiles.py
```

## 🌐 Step 6: Nginx Configuration

### Create Nginx Config
```bash
cat > /etc/nginx/sites-available/theone << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    client_max_body_size 10M;

    # Serve static files
    location /static/ {
        alias /var/www/theone/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF
```

### Enable Site
```bash
# Replace YOUR_DOMAIN_OR_IP with your actual domain or IP
sed -i 's/YOUR_DOMAIN_OR_IP/YOUR_ACTUAL_DOMAIN_OR_IP/g' /etc/nginx/sites-available/theone

# Enable the site
ln -s /etc/nginx/sites-available/theone /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx
```

## 🔄 Step 7: Process Management with Supervisor

### Create Supervisor Config
```bash
cat > /etc/supervisor/conf.d/theone.conf << 'EOF'
[program:theone]
command=/var/www/theone/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
directory=/var/www/theone
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/theone.log
environment=PATH="/var/www/theone/venv/bin"
EOF
```

### Start Application
```bash
supervisorctl reread
supervisorctl update
supervisorctl start theone
supervisorctl status
```

## 🔒 Step 8: SSL Certificate (Recommended)

### Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
# Replace with your actual domain
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
certbot renew --dry-run
```

## 🔥 Step 9: Firewall Setup

### Configure UFW Firewall
```bash
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable
ufw status
```

## 📊 Step 10: Monitoring and Logs

### View Application Logs
```bash
# Application logs
tail -f /var/log/theone.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u nginx -f
```

### Monitor Application
```bash
# Check if app is running
supervisorctl status theone

# Restart if needed
supervisorctl restart theone

# Check processes
ps aux | grep uvicorn
```

## 🚀 Step 11: Test Deployment

### Test Your App
```bash
# Test locally on server
curl http://localhost:8000/health

# Test externally
curl http://YOUR_DOMAIN_OR_IP/health
```

### Visit Your App
- **HTTP**: http://YOUR_DOMAIN_OR_IP
- **HTTPS**: https://YOUR_DOMAIN_OR_IP (if SSL configured)

## 🔄 Step 12: Deployment Script for Updates

### Create Update Script
```bash
cat > /var/www/theone/deploy.sh << 'EOF'
#!/bin/bash
cd /var/www/theone

# Pull latest changes (if using Git)
# git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations if needed
# python3 migrate.py

# Restart application
supervisorctl restart theone

echo "✅ Deployment complete!"
EOF

chmod +x /var/www/theone/deploy.sh
```

## 💰 Cost Estimation

### DigitalOcean Costs
- **Droplet**: $12-24/month (2-4GB RAM)
- **Domain**: $10-15/year (optional)
- **Backups**: $2-5/month (recommended)

### OpenAI API Costs
- **GPT-4o-mini**: ~$0.15 per 1M input tokens
- **Embeddings**: ~$0.02 per 1M tokens
- **Estimated**: $10-50/month depending on usage

## 🛡️ Security Best Practices

### Additional Security
```bash
# Change SSH port (optional)
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
systemctl restart ssh

# Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban

# Regular updates
echo "0 2 * * * apt update && apt upgrade -y" | crontab -
```

## 🎯 Quick Deployment Checklist

- [ ] Create DigitalOcean droplet
- [ ] Connect via SSH
- [ ] Install dependencies
- [ ] Upload/create application files
- [ ] Configure environment variables
- [ ] Setup database
- [ ] Configure Nginx
- [ ] Setup Supervisor
- [ ] Configure SSL (optional)
- [ ] Setup firewall
- [ ] Test application
- [ ] Monitor logs

## 🆘 Troubleshooting

### Common Issues
```bash
# App not starting
supervisorctl status theone
tail -f /var/log/theone.log

# Nginx issues
nginx -t
systemctl status nginx

# Permission issues
chown -R www-data:www-data /var/www/theone

# Database issues
ls -la theone_production.db
```

Your BDSM dating app will be live at your domain/IP! 🌟
