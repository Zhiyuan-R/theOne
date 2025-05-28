#!/bin/bash

# Upload theOne Dating App to DigitalOcean Server
# Usage: ./upload_to_server.sh YOUR_SERVER_IP

if [ $# -eq 0 ]; then
    echo "Usage: $0 <server_ip>"
    echo "Example: $0 164.90.123.456"
    exit 1
fi

SERVER_IP=$1
SERVER_USER="root"
APP_DIR="/var/www/theone"

echo "🚀 Uploading theOne Dating App to $SERVER_IP"
echo "============================================="

# Create a temporary directory with only the files we need
echo "📦 Preparing files for upload..."
mkdir -p temp_upload

# Copy application files
cp -r app temp_upload/
cp -r templates temp_upload/
cp -r static temp_upload/
cp main.py temp_upload/
cp requirements.txt temp_upload/
cp .env.production temp_upload/.env
cp create_test_profiles.py temp_upload/
cp create_alternative_lifestyle_profiles.py temp_upload/

# Create any missing directories
mkdir -p temp_upload/static/uploads/{profiles,expectations}

echo "📤 Uploading files to server..."

# Upload files
scp -r temp_upload/* $SERVER_USER@$SERVER_IP:$APP_DIR/

echo "🔧 Setting up application on server..."

# Run setup commands on server
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/theone

# Set permissions
chown -R www-data:www-data /var/www/theone
chmod -R 755 /var/www/theone
chmod 600 /var/www/theone/.env

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized!')
"

# Create test data
python3 create_test_profiles.py
python3 create_alternative_lifestyle_profiles.py

# Restart application
supervisorctl restart theone

echo "✅ Application setup complete!"
EOF

# Clean up
rm -rf temp_upload

echo ""
echo "🎉 Upload completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your server: ssh $SERVER_USER@$SERVER_IP"
echo "2. Update your OpenAI API key in /var/www/theone/.env"
echo "3. Update domain in nginx config: /etc/nginx/sites-available/theone"
echo "4. Restart nginx: systemctl restart nginx"
echo "5. Check application status: supervisorctl status theone"
echo "6. Test your app: curl http://$SERVER_IP/health"
echo ""
echo "🌐 Your app should be available at: http://$SERVER_IP"
