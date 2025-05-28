#!/bin/bash

# theOne Dating App - DigitalOcean Deployment Script
# Run this script on your DigitalOcean droplet

set -e  # Exit on any error

echo "🚀 Starting theOne Dating App Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/theone"
APP_USER="www-data"
DOMAIN="your-domain.com"  # Change this to your domain

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_status "Step 1: Updating system packages"
apt update && apt upgrade -y

print_status "Step 2: Installing required packages"
apt install -y python3 python3-pip python3-venv nginx supervisor git curl

print_status "Step 3: Creating application directory"
mkdir -p $APP_DIR
cd $APP_DIR

print_status "Step 4: Setting up Python virtual environment"
python3 -m venv venv
source venv/bin/activate

print_status "Step 5: Installing Python dependencies"
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy openai python-multipart pillow passlib python-jose pydantic-settings jinja2 python-dotenv

print_status "Step 6: Creating directory structure"
mkdir -p app/{api,core,db,models,services}
mkdir -p templates static/uploads/{profiles,expectations}
mkdir -p logs

print_status "Step 7: Setting up environment file"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Production Environment
DEBUG=False
APP_NAME="theOne - AI Dating"
SECRET_KEY="$(openssl rand -hex 32)"

# Database
DATABASE_URL="sqlite:///./theone_production.db"

# OpenAI Configuration - UPDATE THIS WITH YOUR KEY
OPENAI_API_KEY="your-openai-api-key-here"
GPT_MODEL="gpt-4o-mini"
EMBEDDING_MODEL="text-embedding-3-small"

# Security
CORS_ORIGINS="*"
EOF
    print_warning "Created .env file - PLEASE UPDATE OPENAI_API_KEY!"
else
    print_status ".env file already exists"
fi

print_status "Step 8: Setting up Nginx configuration"
cat > /etc/nginx/sites-available/theone << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 10M;

    # Serve static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/theone /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t
systemctl restart nginx
systemctl enable nginx

print_status "Step 9: Setting up Supervisor configuration"
cat > /etc/supervisor/conf.d/theone.conf << EOF
[program:theone]
command=$APP_DIR/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/theone.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="$APP_DIR/venv/bin"
EOF

print_status "Step 10: Setting permissions"
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod 600 $APP_DIR/.env

print_status "Step 11: Setting up firewall"
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

print_status "Step 12: Starting services"
supervisorctl reread
supervisorctl update

print_status "Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Upload your application files to $APP_DIR"
echo "2. Update the OpenAI API key in $APP_DIR/.env"
echo "3. Update the domain name in /etc/nginx/sites-available/theone"
echo "4. Initialize the database:"
echo "   cd $APP_DIR && source venv/bin/activate"
echo "   python3 -c \"from app.db.database import engine; from app.models.user import Base; Base.metadata.create_all(bind=engine)\""
echo "5. Start the application:"
echo "   supervisorctl start theone"
echo "6. Check status:"
echo "   supervisorctl status"
echo "   curl http://localhost:8000/health"
echo ""
echo "🌐 Your app will be available at: http://$DOMAIN"
echo ""
print_warning "Don't forget to:"
echo "- Update OPENAI_API_KEY in .env"
echo "- Update domain name in nginx config"
echo "- Setup SSL certificate with: certbot --nginx -d $DOMAIN"
echo ""
print_status "Deployment script completed successfully! 🎉"
