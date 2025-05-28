# 👥 User Profile Monitoring Guide

## 🌐 **Method 1: Web Admin Dashboard (Recommended)**

### **Start Admin Dashboard:**
```bash
# In your local project directory
python3 admin_dashboard.py
```

### **Access Dashboard:**
- **URL**: http://localhost:8001/admin
- **Features**:
  - ✅ Beautiful web interface
  - ✅ View all user profiles at a glance
  - ✅ See photos, descriptions, expectations
  - ✅ Check profile completion status
  - ✅ Click to view detailed user info

### **Dashboard Features:**
- **📊 Statistics**: Total users, complete profiles, completion rate
- **👤 User Cards**: Each user shown with status badges
- **📸 Photo Previews**: Thumbnail images of uploaded photos
- **🔍 Detailed View**: Click "View Details" for full user info

---

## 💻 **Method 2: Command Line Scripts**

### **View All Profiles:**
```bash
python3 view_user_profiles.py
```

### **View Specific User:**
```bash
python3 view_user_profiles.py email user@example.com
```

### **View Recent Users:**
```bash
python3 view_user_profiles.py recent 10
```

### **View Uploaded Files:**
```bash
python3 view_user_profiles.py files
```

---

## 🗄️ **Method 3: Database Direct Access**

### **Quick Database Check:**
```bash
python3 check_database.py
```

### **SQLite Command Line:**
```bash
# Open database
sqlite3 theone_production.db

# View all users
SELECT email, created_at FROM users ORDER BY created_at DESC;

# View complete profiles
SELECT u.email, p.description, e.description 
FROM users u 
JOIN profiles p ON u.id = p.user_id 
JOIN expectations e ON u.id = e.user_id;

# Exit
.quit
```

---

## 📊 **What You'll See After Users Submit Forms**

### **User Profile Data:**
```
👤 User #1
==========================================
📧 Email: sarah@example.com
🆔 User ID: 1
📅 Joined: 2025-05-28 10:30:15
✅ Active: True

📝 Profile Description:
   I'm a 28-year-old submissive looking for a caring Dom...
   Created: 2025-05-28 10:30:15

📸 Uploaded Photos (1):
   1. static/uploads/profiles/1_photo.jpg (245,678 bytes)

💭 Expectations:
   Looking for someone who understands BDSM dynamics...
   Created: 2025-05-28 10:30:15

🎯 Matching Status:
   Profile: ✅
   Expectations: ✅
   Photo: ✅
   🚀 Ready for AI matching!
```

---

## 🔍 **Real-Time Monitoring**

### **Monitor New Submissions:**
```bash
# Watch for new users (refresh every 5 seconds)
watch -n 5 "python3 view_user_profiles.py recent 5"

# Monitor file uploads
watch -n 5 "ls -la static/uploads/profiles/"
```

### **Check Database Growth:**
```bash
# Monitor database size
watch -n 10 "ls -lh *.db"
```

---

## 📱 **Mobile-Friendly Admin**

The web admin dashboard works great on mobile:
- **📱 Responsive design**
- **👆 Touch-friendly interface**
- **🔄 Auto-refresh** (refresh page to see new users)

---

## 🚨 **Monitoring Alerts**

### **Check for Issues:**
```bash
# Find users with missing data
python3 -c "
from app.db.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).all()
for user in users:
    issues = []
    if not (hasattr(user, 'profile') and user.profile):
        issues.append('No Profile')
    if not (hasattr(user, 'expectations') and user.expectations):
        issues.append('No Expectations')
    if hasattr(user, 'profile') and user.profile and not user.profile.photos:
        issues.append('No Photos')
    if issues:
        print(f'{user.email}: {', '.join(issues)}')
db.close()
"
```

### **Check Upload Directory:**
```bash
# Verify upload directories exist
ls -la static/uploads/
ls -la static/uploads/profiles/
ls -la static/uploads/expectations/
```

---

## 📈 **Analytics Queries**

### **User Statistics:**
```sql
-- Users by day
SELECT DATE(created_at) as date, COUNT(*) as users
FROM users 
GROUP BY DATE(created_at) 
ORDER BY date DESC;

-- Profile completion rate
SELECT 
    COUNT(*) as total_users,
    COUNT(p.id) as users_with_profiles,
    COUNT(e.id) as users_with_expectations,
    ROUND(COUNT(p.id) * 100.0 / COUNT(*), 2) as profile_completion_rate
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN expectations e ON u.id = e.user_id;
```

---

## 🎯 **Quick Commands Reference**

```bash
# Start web admin dashboard
python3 admin_dashboard.py
# Then visit: http://localhost:8001/admin

# View all profiles (command line)
python3 view_user_profiles.py

# Check database status
python3 check_database.py

# View recent users
python3 view_user_profiles.py recent

# Clear all data (if needed)
python3 check_database.py clear
```

---

## 🌟 **Pro Tips**

1. **📊 Use Web Dashboard**: Most user-friendly way to monitor
2. **🔄 Refresh Regularly**: New users appear immediately after form submission
3. **📸 Check Photos**: Verify uploaded images are displaying correctly
4. **💾 Monitor Database Size**: Keep track of storage usage
5. **🚨 Watch for Errors**: Check logs if users report submission issues

Your user monitoring system is now ready! You'll be able to see every profile, photo, and expectation submitted through your dating app website. 👥💕
