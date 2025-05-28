# 🚀 DigitalOcean Deployment Guide for theOne Dating App

This guide shows you how to deploy your dating app to DigitalOcean with **persistent data storage** that survives code updates.

## 🎯 Problem Solved

✅ **Database persists** across deployments  
✅ **User photos persist** across deployments  
✅ **No data loss** when pushing new code  
✅ **Automatic backups** before deployment  

## 🛠️ Setup Instructions

### 1. **DigitalOcean Account Setup**

1. Create a [DigitalOcean account](https://cloud.digitalocean.com/)
2. Install [doctl CLI](https://docs.digitalocean.com/reference/doctl/how-to/install/)
3. Authenticate: `doctl auth init`

### 2. **Configure Environment Variables**

In your DigitalOcean App Platform dashboard:

```bash
# Required Environment Variables
SECRET_KEY=your-super-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_PATH=/app/data/database/theone_production.db
UPLOADS_PATH=/app/data/uploads
BACKUPS_PATH=/app/data/backups
```

### 3. **Deploy Using Script**

```bash
# One-command deployment with backup
python3 deploy_to_digitalocean.py
```

Or manually:
```bash
# Create backup first
python3 backup_database.py

# Push to trigger deployment
git add .
git commit -m "Deploy to production"
git push origin main
```

## 📁 Persistent Storage Structure

Your app uses persistent volumes that survive deployments:

```
/app/data/
├── database/
│   └── theone_production.db     # SQLite database
├── uploads/
│   ├── profiles/                # User profile photos
│   ├── expectations/            # Expectation example images
│   └── ideal_partners/          # Ideal partner photos
└── backups/                     # Automatic backups
    ├── backup_20241201_143022/
    └── backup_20241201_150315/
```

## 🔄 How Persistent Storage Works

### **Before (Data Loss Problem):**
```
Deploy → Container Rebuilt → Database Gone → Users Lost 😢
```

### **After (Persistent Storage):**
```
Deploy → Container Rebuilt → Database Persists → Users Safe 🎉
```

### **Volume Mounts:**
- `theone-database` → `/app/data/database` (1GB)
- `theone-uploads` → `/app/data/uploads` (5GB)  
- `theone-backups` → `/app/data/backups` (2GB)

## 🚀 Deployment Workflow

### **Safe Deployment Process:**

1. **Auto-backup** (before deployment)
2. **Code push** (triggers deployment)
3. **Container rebuild** (with new code)
4. **Volume remount** (same data)
5. **App restart** (with persistent data)

### **Commands:**

```bash
# Safe deployment with backup
python3 deploy_to_digitalocean.py

# Quick deployment (if you're confident)
git push origin main

# Emergency restore (if needed)
python3 restore_database.py
```

## 📊 Monitoring Your Deployment

### **Check App Status:**
```bash
doctl apps list
doctl apps get <app-id>
```

### **View Logs:**
```bash
doctl apps logs <app-id>
```

### **Access App:**
- Your app URL: `https://your-app-name.ondigitalocean.app`
- Admin dashboard: `https://your-app-name.ondigitalocean.app/admin`

## 🆘 Troubleshooting

### **"Database not found" after deployment**
```bash
# Check if volumes are mounted correctly
doctl apps get <app-id> --format json | grep volumes
```

### **"Photos not displaying"**
```bash
# Check upload directory permissions
# Verify UPLOADS_PATH environment variable
```

### **"App won't start"**
```bash
# Check logs for errors
doctl apps logs <app-id>

# Verify environment variables
doctl apps get <app-id> --format json | grep envs
```

### **"Need to restore data"**
```bash
# Use backup system (locally)
python3 restore_database.py

# Then redeploy
python3 deploy_to_digitalocean.py
```

## 🔒 Security Best Practices

### **Environment Variables:**
- ✅ Use DigitalOcean's secret management
- ✅ Never commit secrets to git
- ✅ Rotate keys regularly

### **Database Security:**
- ✅ Database is in private volume
- ✅ No external access
- ✅ Regular backups

### **File Upload Security:**
- ✅ File type validation
- ✅ Size limits enforced
- ✅ Secure file paths

## 💰 Cost Optimization

### **App Platform Pricing:**
- **Basic Plan**: $5/month (512MB RAM, 1 vCPU)
- **Professional**: $12/month (1GB RAM, 1 vCPU)

### **Storage Costs:**
- **Volumes**: $0.10/GB/month
- **Total Storage**: ~8GB = $0.80/month

### **Total Monthly Cost:**
- App: $5-12/month
- Storage: $0.80/month
- **Total: ~$6-13/month**

## 🎉 Success Checklist

After deployment, verify:

- [ ] App loads at your DigitalOcean URL
- [ ] Users can register and upload photos
- [ ] Photos display correctly
- [ ] Admin dashboard works
- [ ] Database persists after redeployment
- [ ] Backups are created automatically

## 📞 Support

If you encounter issues:

1. **Check logs**: `doctl apps logs <app-id>`
2. **Verify environment variables** in DigitalOcean dashboard
3. **Test locally** with Docker first
4. **Use backup system** if data is lost

Your data is now safe and persistent across all deployments! 🎉
