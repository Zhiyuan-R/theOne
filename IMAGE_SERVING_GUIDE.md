# Image Serving Troubleshooting Guide

## Problem: Images show locally but not on DigitalOcean

### Quick Diagnosis

1. **Run diagnostic script:**
   ```bash
   python debug_image_serving.py
   ```

2. **Check health endpoint:**
   ```bash
   curl https://your-app-url.ondigitalocean.app/health
   ```

3. **Test image URL directly:**
   ```bash
   curl -I https://your-app-url.ondigitalocean.app/uploads/profiles/some-image.jpg
   ```

### Common Issues & Solutions

#### Issue 1: File paths in database don't match production structure

**Symptoms:**
- Images work locally but 404 in production
- Database has paths like `static/uploads/...` but production expects `/app/data/uploads/...`

**Solution:**
```bash
python fix_image_paths.py
```

#### Issue 2: Upload directory not mounted correctly

**Symptoms:**
- `/health` endpoint shows upload directory doesn't exist
- Files uploaded but immediately disappear

**Check:**
- DigitalOcean App Platform volumes are configured correctly
- Environment variable `UPLOADS_PATH=/app/data/uploads` is set

#### Issue 3: Static file mounting issue

**Symptoms:**
- FastAPI not serving files from `/uploads/` route

**Check in main.py:**
```python
# Should be present:
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
```

#### Issue 4: URL generation problems

**Symptoms:**
- URLs generated incorrectly (localhost references in production)

**Fixed in main.py:**
- Removed hardcoded localhost references
- Added debug logging to trace URL generation

### Environment Configuration

**Local Development (.env):**
```env
DEBUG=True
UPLOADS_PATH=./static/uploads
```

**Production (DigitalOcean):**
```env
DEBUG=False
UPLOADS_PATH=/app/data/uploads
```

### File Structure

**Local Development:**
```
theOne/
├── static/
│   └── uploads/
│       ├── profiles/
│       ├── ideal_partners/
│       ├── expectations/
│       └── audio/
```

**Production (DigitalOcean):**
```
/app/
├── data/
│   └── uploads/          # Mounted volume
│       ├── profiles/
│       ├── ideal_partners/
│       ├── expectations/
│       └── audio/
```

### Testing Steps

1. **Upload a test image locally:**
   - Verify it appears in `static/uploads/profiles/`
   - Check database path with `debug_image_serving.py`

2. **Deploy to DigitalOcean:**
   - Check `/health` endpoint for upload directory status
   - Run `fix_image_paths.py` if needed
   - Test image URL directly

3. **Verify URL generation:**
   - Check browser developer tools for 404 errors
   - Verify URLs don't contain localhost references

### Manual Fixes

**If files are in wrong location:**
```bash
# Copy from development to production location
cp -r ./static/uploads/* /app/data/uploads/
```

**If database paths are wrong:**
```sql
-- Update profile photos
UPDATE photos SET file_path = REPLACE(file_path, 'static/uploads/', '/app/data/uploads/');

-- Update ideal partner photos  
UPDATE ideal_partner_photos SET file_path = REPLACE(file_path, 'static/uploads/', '/app/data/uploads/');
```

### Monitoring

**Check logs for image serving errors:**
```bash
# DigitalOcean App Platform logs
doctl apps logs <app-id>

# Look for 404 errors on /uploads/ routes
```

**Health check includes:**
- Upload directory existence
- Subdirectory file counts
- Write permissions
- Debug mode status

### Prevention

1. **Always use environment-aware paths:**
   ```python
   upload_dir = settings.get_upload_dir()  # Not hardcoded paths
   ```

2. **Test image serving in staging:**
   - Deploy to staging environment first
   - Verify image uploads and display work

3. **Use consistent URL generation:**
   - Always use `get_photo_url()` function
   - Never hardcode localhost or domain names

### Quick Fix Commands

```bash
# 1. Diagnose the issue
python debug_image_serving.py

# 2. Fix database paths
python fix_image_paths.py

# 3. Check health status
curl https://your-app.ondigitalocean.app/health

# 4. Test specific image
curl -I https://your-app.ondigitalocean.app/uploads/profiles/test.jpg
```
