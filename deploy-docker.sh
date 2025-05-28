#!/bin/bash

# theOne Dating App - Docker Deployment Script for DigitalOcean
# This script sets up the complete Docker environment

set -e  # Exit on any error

echo "🚀 theOne Dating App - Docker Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_status "Step 1: Updating system packages"
apt update && apt upgrade -y

print_status "Step 2: Installing Docker and Docker Compose"

# Install Docker
if ! command -v docker &> /dev/null; then
    print_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add current user to docker group
    usermod -aG docker $USER
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_info "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

print_status "Step 3: Setting up application directory"
APP_DIR="/opt/theone"
mkdir -p $APP_DIR
cd $APP_DIR

print_status "Step 4: Cloning application repository"
if [ -d ".git" ]; then
    print_info "Repository already exists, pulling latest changes..."
    git pull
else
    print_info "Cloning repository..."
    # Replace with your actual repository URL
    git clone https://github.com/yourusername/theone-dating-app.git .
fi

print_status "Step 5: Setting up environment file"
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate a secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your_secret_key_here/$SECRET_KEY/" .env
    
    print_warning "Created .env file with secure secret key"
    print_warning "IMPORTANT: Please update the following in .env:"
    print_warning "  - OPENAI_API_KEY=your_actual_openai_api_key"
    print_warning "  - CORS_ORIGINS=https://yourdomain.com"
else
    print_status ".env file already exists"
fi

print_status "Step 6: Creating necessary directories"
mkdir -p data logs ssl
mkdir -p static/uploads/{profiles,expectations}

# Create .gitkeep files for empty directories
touch static/uploads/profiles/.gitkeep
touch static/uploads/expectations/.gitkeep

print_status "Step 7: Setting up firewall"
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

print_status "Step 8: Building and starting Docker containers"
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

print_status "Step 9: Waiting for services to start"
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_status "Services are running successfully"
else
    print_error "Some services failed to start"
    docker-compose logs
    exit 1
fi

print_status "Step 10: Initializing database"
docker-compose exec -T theone-app python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized!')
"

print_status "Step 11: Creating test data"
docker-compose exec -T theone-app python3 create_test_profiles.py
docker-compose exec -T theone-app python3 create_alternative_lifestyle_profiles.py

print_status "Step 12: Testing deployment"
sleep 10

# Test health endpoint
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_status "Health check passed"
else
    print_warning "Health check failed, but app might still be starting"
fi

print_status "Deployment completed successfully! 🎉"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
print_info "1. Update your OpenAI API key:"
echo "   nano $APP_DIR/.env"
echo "   # Update OPENAI_API_KEY=your_actual_key"
echo ""
print_info "2. Update CORS origins for your domain:"
echo "   # Update CORS_ORIGINS=https://yourdomain.com"
echo ""
print_info "3. Restart services after updating .env:"
echo "   cd $APP_DIR && docker-compose restart"
echo ""
print_info "4. Setup SSL certificate (if you have a domain):"
echo "   docker run --rm -v $APP_DIR/ssl:/etc/letsencrypt certbot/certbot certonly --standalone -d yourdomain.com"
echo ""
print_info "5. Monitor logs:"
echo "   docker-compose logs -f"
echo ""
print_info "6. Manage services:"
echo "   docker-compose stop    # Stop services"
echo "   docker-compose start   # Start services"
echo "   docker-compose restart # Restart services"
echo ""
echo "🌐 Your app is available at:"
echo "   HTTP:  http://$(curl -s ifconfig.me)"
echo "   Local: http://localhost"
echo ""
print_warning "Important Security Notes:"
echo "- Update OPENAI_API_KEY in .env file"
echo "- Setup SSL certificate for production"
echo "- Configure proper CORS origins"
echo "- Monitor logs regularly"
echo ""
print_status "theOne Dating App is now running with Docker! 💕"
