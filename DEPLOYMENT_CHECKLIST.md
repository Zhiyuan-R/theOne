# 🚀 theOne Dating App - Quick Deployment Checklist

## 📋 Pre-Deployment Checklist

- [ ] **DigitalOcean Account** created
- [ ] **Domain name** purchased (optional)
- [ ] **OpenAI API Key** ready
- [ ] **SSH Key** generated (recommended)

## 🖥️ DigitalOcean Setup (5 minutes)

### 1. Create Droplet
- [ ] Go to DigitalOcean → Create → Droplets
- [ ] **Image**: Ubuntu 22.04 LTS
- [ ] **Size**: $12/month (2GB RAM) or $24/month (4GB RAM)
- [ ] **Region**: Choose closest to your users
- [ ] **Authentication**: SSH Key or Password
- [ ] **Hostname**: `theone-dating-app`
- [ ] Click **Create Droplet**
- [ ] **Note the IP address** (e.g., 164.90.XXX.XXX)

## 🚀 Quick Deployment (10 minutes)

### Option A: Automated Deployment
```bash
# 1. Upload your app to the server
./upload_to_server.sh YOUR_SERVER_IP

# 2. SSH into server and run deployment script
ssh root@YOUR_SERVER_IP
wget https://raw.githubusercontent.com/your-repo/theone/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual Deployment
```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Run the deployment script
curl -sSL https://raw.githubusercontent.com/your-repo/theone/main/deploy.sh | bash
```

## 🔧 Configuration (5 minutes)

### 1. Update Environment Variables
```bash
ssh root@YOUR_SERVER_IP
cd /var/www/theone
nano .env

# Update these values:
OPENAI_API_KEY="your-actual-openai-api-key"
CORS_ORIGINS="https://yourdomain.com,http://YOUR_SERVER_IP"
```

### 2. Update Domain (if you have one)
```bash
# Update nginx configuration
nano /etc/nginx/sites-available/theone

# Change: server_name your-domain.com;
systemctl restart nginx
```

### 3. Start Application
```bash
cd /var/www/theone
supervisorctl restart theone
supervisorctl status theone
```

## ✅ Testing (2 minutes)

### 1. Health Check
```bash
# On server
curl http://localhost:8000/health

# From your computer
curl http://YOUR_SERVER_IP/health
```

### 2. Web Interface
- [ ] Visit: `http://YOUR_SERVER_IP`
- [ ] Test photo upload
- [ ] Test profile creation
- [ ] Test matching functionality

## 🔒 Security Setup (Optional - 10 minutes)

### 1. SSL Certificate (if you have a domain)
```bash
ssh root@YOUR_SERVER_IP
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

### 2. Firewall
```bash
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable
```

## 📊 Monitoring

### Check Application Status
```bash
# Application logs
tail -f /var/log/theone.log

# Application status
supervisorctl status theone

# Restart if needed
supervisorctl restart theone
```

### Check Server Resources
```bash
# Memory usage
free -h

# Disk usage
df -h

# CPU usage
top
```

## 🎯 Quick Commands Reference

```bash
# Restart application
supervisorctl restart theone

# View logs
tail -f /var/log/theone.log

# Check nginx
systemctl status nginx
nginx -t

# Update application (after code changes)
cd /var/www/theone
git pull  # if using git
supervisorctl restart theone

# Check database
ls -la theone_production.db
```

## 💰 Cost Breakdown

### DigitalOcean
- **Droplet**: $12-24/month
- **Domain**: $10-15/year (optional)
- **Backups**: $2-5/month (recommended)

### OpenAI API
- **GPT-4o-mini**: ~$0.15 per 1M tokens
- **Embeddings**: ~$0.02 per 1M tokens
- **Estimated**: $10-50/month (depends on usage)

**Total**: ~$25-75/month

## 🆘 Troubleshooting

### App Not Starting
```bash
supervisorctl status theone
tail -f /var/log/theone.log
```

### Nginx Issues
```bash
nginx -t
systemctl status nginx
systemctl restart nginx
```

### Database Issues
```bash
cd /var/www/theone
ls -la *.db
python3 -c "from app.db.database import SessionLocal; print('DB OK')"
```

### Permission Issues
```bash
chown -R www-data:www-data /var/www/theone
chmod -R 755 /var/www/theone
```

## 🎉 Success!

Your BDSM dating app should now be live at:
- **HTTP**: `http://YOUR_SERVER_IP`
- **HTTPS**: `https://yourdomain.com` (if SSL configured)

### Features Working:
- ✅ Photo upload and display
- ✅ Profile creation and editing
- ✅ AI-powered matching (GPT-4o-mini)
- ✅ BDSM and alternative lifestyle support
- ✅ Strict high-compatibility matching (70%+)
- ✅ Auto-save and auto-load user data
- ✅ Responsive web interface

## 📞 Support

If you encounter issues:
1. Check the logs: `tail -f /var/log/theone.log`
2. Verify environment variables in `/var/www/theone/.env`
3. Test OpenAI API key: `curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models`
4. Check server resources: `free -h` and `df -h`

Your dating app is now live and ready to match people! 🌟💕
