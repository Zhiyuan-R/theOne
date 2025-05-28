# 🐳 Docker Deployment Guide - theOne Dating App

## 🚀 Quick Docker Deployment to DigitalOcean

### Prerequisites
- DigitalOcean account
- GitHub repository with your code
- OpenAI API key

## 📋 Step-by-Step Deployment

### 1. Create DigitalOcean Droplet (5 minutes)
```bash
# Create droplet via DigitalOcean dashboard:
# - Image: Ubuntu 22.04 LTS
# - Size: $24/month (4GB RAM, 2 CPU) - Recommended for Docker
# - Region: Choose closest to your users
# - Authentication: SSH Key (recommended)
# - Hostname: theone-dating-app
```

### 2. Setup GitHub Repository (2 minutes)
```bash
# 1. Create new repository on GitHub
# 2. Push your code:
git init
git add .
git commit -m "Initial commit - theOne Dating App"
git branch -M main
git remote add origin https://github.com/yourusername/theone-dating-app.git
git push -u origin main
```

### 3. Deploy with Docker (10 minutes)
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Download and run deployment script
curl -sSL https://raw.githubusercontent.com/yourusername/theone-dating-app/main/deploy-docker.sh -o deploy-docker.sh
chmod +x deploy-docker.sh
./deploy-docker.sh
```

### 4. Configure Environment (3 minutes)
```bash
# Update environment variables
cd /opt/theone
nano .env

# Update these critical values:
OPENAI_API_KEY=your_actual_openai_api_key_here
CORS_ORIGINS=https://yourdomain.com,http://YOUR_SERVER_IP
SECRET_KEY=automatically_generated_secure_key

# Restart services
docker-compose restart
```

### 5. Test Deployment (1 minute)
```bash
# Check services
docker-compose ps

# Test health endpoint
curl http://YOUR_SERVER_IP/health

# View logs
docker-compose logs -f
```

## 🌐 Your App is Live!

Visit: `http://YOUR_SERVER_IP`

## 🔒 Optional: Setup SSL Certificate

### For Custom Domain
```bash
# 1. Point your domain to your server IP
# 2. Install SSL certificate
cd /opt/theone
docker run --rm -v $(pwd)/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d yourdomain.com

# 3. Update nginx.conf to enable HTTPS
# 4. Restart nginx
docker-compose restart nginx
```

## 📊 Docker Services

Your deployment includes:

### theone-app
- **FastAPI application** with GPT-4o-mini
- **Port**: 8000 (internal)
- **Features**: AI matching, photo upload, BDSM support

### nginx
- **Reverse proxy** and load balancer
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Features**: Rate limiting, static file serving, SSL

## 🛠️ Management Commands

### View Services
```bash
cd /opt/theone
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f theone-app
docker-compose logs -f nginx
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart theone-app
```

### Update Application
```bash
cd /opt/theone
git pull origin main
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

### Database Management
```bash
# Access database
docker-compose exec theone-app python3 -c "
from app.db.database import SessionLocal
from app.models.user import User
db = SessionLocal()
print(f'Users: {db.query(User).count()}')
"

# Backup database
docker-compose exec theone-app cp theone_production.db /app/data/backup_$(date +%Y%m%d).db
```

## 📈 Monitoring

### Check Resource Usage
```bash
# Docker stats
docker stats

# System resources
htop
df -h
free -h
```

### Health Checks
```bash
# Application health
curl http://localhost/health

# Service status
docker-compose ps
```

## 🔧 Troubleshooting

### App Not Starting
```bash
# Check logs
docker-compose logs theone-app

# Check environment
docker-compose exec theone-app env | grep OPENAI

# Restart service
docker-compose restart theone-app
```

### Nginx Issues
```bash
# Check nginx config
docker-compose exec nginx nginx -t

# Check logs
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx
```

### Database Issues
```bash
# Check database file
docker-compose exec theone-app ls -la *.db

# Reinitialize database
docker-compose exec theone-app python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
"
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Scale services (if needed)
docker-compose up -d --scale theone-app=2
```

## 💰 Cost Optimization

### DigitalOcean Droplet Sizes
- **$12/month (2GB)**: Development/testing
- **$24/month (4GB)**: Production (recommended)
- **$48/month (8GB)**: High traffic

### OpenAI API Optimization
- **GPT-4o-mini**: 90% cheaper than GPT-4
- **Caching**: Implemented for repeated queries
- **Rate limiting**: Prevents API abuse

## 🔄 CI/CD with GitHub Actions

Your repository includes automated deployment:

1. **Push to main branch** → Triggers deployment
2. **Tests run** → Ensures code quality
3. **Docker image builds** → Creates container
4. **Deploys to server** → Updates production

### Setup GitHub Secrets
```bash
# In your GitHub repository settings, add:
DIGITALOCEAN_HOST=your_server_ip
DIGITALOCEAN_USERNAME=root
DIGITALOCEAN_SSH_KEY=your_private_ssh_key
```

## 🎉 Success!

Your BDSM-friendly dating app is now:
- ✅ **Running on Docker** with professional setup
- ✅ **Auto-scaling** with nginx load balancing
- ✅ **Monitoring** with health checks
- ✅ **Secure** with rate limiting and SSL-ready
- ✅ **Cost-optimized** with GPT-4o-mini
- ✅ **CI/CD ready** with GitHub Actions

**Total setup time**: ~20 minutes
**Monthly cost**: ~$35-75 (server + API)

Your dating app is production-ready! 🌟💕
