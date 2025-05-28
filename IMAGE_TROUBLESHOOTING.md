# 📸 Image Display Troubleshooting Guide

## 🔍 **Quick Diagnosis**

### **Step 1: Check if images exist**
```bash
# Run the debug script
python3 debug_images.py

# Check upload directory
ls -la static/uploads/profiles/
```

### **Step 2: Test image URLs directly**
```bash
# Test in browser or curl
curl -I http://YOUR_SERVER_IP/static/uploads/profiles/1_photo.jpg
```

## 🛠️ **Common Issues & Fixes**

### **Issue 1: Images not showing in admin dashboard**

#### **Symptoms:**
- Admin dashboard shows user cards but no photo thumbnails
- Broken image icons in browser
- Photos exist in filesystem but don't display

#### **Diagnosis:**
```bash
# Check image paths in database
python3 debug_images.py

# Check if files exist
ls -la static/uploads/profiles/
```

#### **Fix A: Incorrect file paths in database**
```bash
# Fix paths automatically
python3 debug_images.py fix
```

#### **Fix B: Static file serving issue**
Check that static files are properly mounted in main.py:
```python
# Should be in main.py
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### **Issue 2: 404 errors for images**

#### **Symptoms:**
- Browser shows 404 Not Found for image URLs
- Images exist in filesystem

#### **Fix: Check URL format**
```bash
# Test different URL formats
python3 debug_images.py test

# Correct format should be:
http://YOUR_SERVER_IP/static/uploads/profiles/1_photo.jpg
```

### **Issue 3: Permission issues (DigitalOcean)**

#### **Symptoms:**
- Images upload but can't be accessed
- 403 Forbidden errors

#### **Fix: Set correct permissions**
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP
cd /opt/theone

# Fix permissions
chmod -R 755 static/uploads/
chown -R www-data:www-data static/uploads/

# Restart Docker containers
docker-compose restart
```

### **Issue 4: Docker volume mounting**

#### **Symptoms:**
- Images disappear after container restart
- Uploads work but don't persist

#### **Fix: Check docker-compose.yml**
```yaml
# Should have volume mounting
services:
  theone-app:
    volumes:
      - ./static/uploads:/app/static/uploads
```

## 🔧 **Manual Fixes**

### **Fix 1: Update image URLs in admin dashboard**

The issue might be in how URLs are generated. Check main.py:

```python
# In admin_dashboard function, ensure correct URL format:
if photo.file_path.startswith('static/'):
    photo_urls.append(f"/{photo.file_path}")
else:
    photo_urls.append(f"/static/{photo.file_path}")
```

### **Fix 2: Add error handling for missing images**

Update admin_dashboard.html to handle missing images:

```html
<!-- Add onerror handler -->
<img src="{{ photo_url }}" 
     alt="User photo" 
     class="photo-thumb"
     onerror="this.src='/static/placeholder.jpg'; this.onerror=null;">
```

### **Fix 3: Create placeholder image**

```bash
# Create a placeholder for missing images
mkdir -p static/
# Add a placeholder.jpg file to static/ directory
```

## 🧪 **Testing Steps**

### **1. Local Testing:**
```bash
# Start local server
python3 -m uvicorn main:app --reload

# Visit admin dashboard
open http://localhost:8000/admin

# Check browser developer tools for image errors
```

### **2. Server Testing:**
```bash
# SSH into server
ssh root@YOUR_SERVER_IP
cd /opt/theone

# Check logs for errors
docker-compose logs theone-app | grep -i error

# Test image access directly
curl -I http://localhost/static/uploads/profiles/1_photo.jpg
```

### **3. Browser Testing:**
```bash
# Open browser developer tools (F12)
# Go to Network tab
# Refresh admin dashboard
# Look for failed image requests (red entries)
```

## 📋 **Debugging Checklist**

- [ ] **Files exist**: `ls -la static/uploads/profiles/`
- [ ] **Correct paths**: `python3 debug_images.py`
- [ ] **Static mounting**: Check `app.mount("/static", ...)` in main.py
- [ ] **URL format**: Should be `/static/uploads/profiles/filename.jpg`
- [ ] **Permissions**: `chmod 755` and correct ownership
- [ ] **Docker volumes**: Check docker-compose.yml volume mounting
- [ ] **Network access**: Test with `curl -I http://SERVER/static/...`

## 🚀 **Quick Fix Commands**

```bash
# Debug images
python3 debug_images.py

# Fix database paths
python3 debug_images.py fix

# Check file permissions
ls -la static/uploads/profiles/

# Test URL access
curl -I http://YOUR_SERVER_IP/static/uploads/profiles/1_photo.jpg

# Restart server (if needed)
docker-compose restart
```

## 💡 **Prevention Tips**

1. **Consistent paths**: Always save images with `static/uploads/profiles/` prefix
2. **Test uploads**: Verify image display immediately after upload
3. **Monitor logs**: Check for file permission or access errors
4. **Backup images**: Ensure Docker volumes are properly configured

## 🆘 **Still Not Working?**

### **Last Resort Fixes:**

1. **Clear and re-upload images**:
```bash
# Clear all images
rm -rf static/uploads/profiles/*
# Have users re-upload through the website
```

2. **Check nginx configuration** (if using):
```bash
# Ensure nginx serves static files correctly
# Check nginx.conf for static file handling
```

3. **Enable debug mode**:
```python
# In main.py, add debug prints
print(f"DEBUG: Photo URL: {photo_url}")
print(f"DEBUG: File exists: {os.path.exists(photo.file_path)}")
```

Your images should now display correctly in the admin dashboard! 📸✨
