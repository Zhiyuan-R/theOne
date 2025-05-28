# 📸 Photo Display Troubleshooting Guide

## 🔧 **Photo Display Fix for DigitalOcean**

### **Problem:**
Photos not displaying in DigitalOcean App Platform deployment.

### **Root Cause:**
- Static file serving not configured properly for production
- File paths different between development and production
- Volume mounts not accessible via web server

### **Solution Implemented:**

1. **✅ Separate Upload Mount**
   ```
   /uploads/ → serves files from persistent volume
   /static/ → serves static assets (CSS, JS)
   ```

2. **✅ Smart Photo URL Generation**
   ```python
   def get_photo_url(file_path: str) -> str:
       if file_path.startswith('/app/data/uploads/'):
           return file_path.replace('/app/data/uploads/', '/uploads/')
       elif file_path.startswith('static/uploads/'):
           return file_path.replace('static/uploads/', '/uploads/')
       # ... more cases
   ```

3. **✅ Production-Ready File Upload**
   ```python
   upload_base = settings.get_upload_dir()  # /app/data/uploads in production
   profiles_dir = f"{upload_base}/profiles"
   ```

## 🔍 **Debugging Steps**

### **1. Check Debug Endpoint**
Visit: `https://your-app.ondigitalocean.app/api/debug/file-paths`

This will show:
- Upload directory paths
- Directory existence
- Environment variables
- Directory contents

### **2. Check Environment Variables**
In DigitalOcean dashboard, verify:
```bash
DATABASE_PATH=/app/data/database/theone_production.db
UPLOADS_PATH=/app/data/uploads
```

### **3. Check Volume Mounts**
In DigitalOcean App Platform:
- `theone-uploads` → `/app/data/uploads` (5GB)
- `theone-database` → `/app/data/database` (1GB)

### **4. Test Photo Upload**
1. Go to your app homepage
2. Upload a photo
3. Check admin dashboard
4. Verify photo displays

## 🚨 **Common Issues & Fixes**

### **Issue: "404 Not Found" for photos**
**Cause:** Volume not mounted or wrong path
**Fix:** 
1. Check DigitalOcean App Platform volumes
2. Verify environment variables
3. Restart the app

### **Issue: Photos upload but don't display**
**Cause:** URL generation incorrect
**Fix:**
1. Check debug endpoint: `/api/debug/file-paths`
2. Verify file paths in database
3. Check if `/uploads/` mount is working

### **Issue: "Permission denied" errors**
**Cause:** File permissions in container
**Fix:**
1. Check Dockerfile user permissions
2. Verify volume mount permissions
3. Restart deployment

### **Issue: Old photos still showing wrong URLs**
**Cause:** Database has old file paths
**Fix:**
1. Use backup/restore to clean data
2. Re-upload photos
3. Check photo URL generation

## 🔧 **Manual Fixes**

### **Force Photo Re-upload**
```bash
# Delete user and re-register
# This will create new photos with correct paths
```

### **Check File System in Production**
```bash
# Use DigitalOcean console access (if available)
ls -la /app/data/uploads/
ls -la /app/data/uploads/profiles/
ls -la /app/data/uploads/ideal_partners/
```

### **Verify URL Generation**
Test these URLs in browser:
- `https://your-app.ondigitalocean.app/uploads/profiles/1_photo.jpg`
- `https://your-app.ondigitalocean.app/static/css/style.css`

## ✅ **Verification Checklist**

After deployment, verify:

- [ ] Debug endpoint shows correct paths
- [ ] Environment variables are set
- [ ] Volumes are mounted
- [ ] Photo upload works
- [ ] Photos display in admin dashboard
- [ ] Photos display in matches
- [ ] Ideal partner photos work
- [ ] No 404 errors in browser console

## 🎯 **Expected Behavior**

### **Development (Local):**
```
File Path: static/uploads/profiles/1_photo.jpg
URL: /uploads/profiles/1_photo.jpg
Served by: FastAPI StaticFiles mount
```

### **Production (DigitalOcean):**
```
File Path: /app/data/uploads/profiles/1_photo.jpg
URL: /uploads/profiles/1_photo.jpg
Served by: FastAPI StaticFiles mount
Storage: Persistent volume
```

## 📞 **Still Having Issues?**

1. **Check logs:**
   ```bash
   doctl apps logs <app-id>
   ```

2. **Test debug endpoint:**
   ```
   https://your-app.ondigitalocean.app/api/debug/file-paths
   ```

3. **Verify admin dashboard:**
   ```
   https://your-app.ondigitalocean.app/admin
   ```

4. **Check browser console** for 404 errors

5. **Restart the app** in DigitalOcean dashboard

Your photos should now display correctly in production! 🎉
