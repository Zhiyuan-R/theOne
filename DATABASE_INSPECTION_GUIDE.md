# 🗄️ Database Inspection Guide - theOne Dating App

## 🚀 Quick Database Check

### **Method 1: Python Script (Recommended)**
```bash
# View all database content
python3 check_database.py

# Clear all data
python3 check_database.py clear

# Show table structure
python3 check_database.py tables
```

### **Method 2: SQLite Command Line**
```bash
# Open database
sqlite3 theone_production.db

# Show all tables
.tables

# Count users
SELECT COUNT(*) FROM users;

# View all users
SELECT id, email, is_active, created_at FROM users;

# View profiles with users
SELECT u.email, p.description 
FROM users u 
LEFT JOIN profiles p ON u.id = p.user_id;

# View expectations
SELECT u.email, e.description 
FROM users u 
LEFT JOIN expectations e ON u.id = e.user_id;

# View photos
SELECT u.email, ph.file_path 
FROM users u 
JOIN profiles p ON u.id = p.user_id 
JOIN photos ph ON p.id = ph.profile_id;

# Exit
.quit
```

### **Method 3: SQLite Browser (GUI)**
```bash
# Install SQLite Browser (macOS)
brew install --cask db-browser-for-sqlite

# Open database file
# File → Open Database → select theone_production.db
```

## 📊 Database Schema

### **Tables Structure:**
```
users
├── id (Primary Key)
├── email (Unique)
├── hashed_password
├── is_active
└── created_at

profiles
├── id (Primary Key)
├── user_id (Foreign Key → users.id)
├── description
├── audio_clip_path
├── created_at
└── updated_at

expectations
├── id (Primary Key)
├── user_id (Foreign Key → users.id)
├── description
├── created_at
└── updated_at

photos
├── id (Primary Key)
├── profile_id (Foreign Key → profiles.id)
├── file_path
└── order_index

example_images
├── id (Primary Key)
├── expectation_id (Foreign Key → expectations.id)
└── file_path
```

## 🔍 Common Database Queries

### **Check User Data:**
```sql
-- All users with complete profiles
SELECT 
    u.email,
    p.description as profile,
    e.description as expectations,
    COUNT(ph.id) as photo_count
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN expectations e ON u.id = e.user_id
LEFT JOIN photos ph ON p.id = ph.profile_id
GROUP BY u.id;

-- Users ready for matching (have profile + expectations)
SELECT u.email
FROM users u
JOIN profiles p ON u.id = p.user_id
JOIN expectations e ON u.id = e.user_id;

-- Photo file paths
SELECT u.email, ph.file_path
FROM users u
JOIN profiles p ON u.id = p.user_id
JOIN photos ph ON p.id = ph.profile_id
ORDER BY u.email;
```

### **Database Maintenance:**
```sql
-- Clear all user data
DELETE FROM example_images;
DELETE FROM photos;
DELETE FROM expectations;
DELETE FROM profiles;
DELETE FROM users;

-- Reset auto-increment
DELETE FROM sqlite_sequence;

-- Vacuum database (reclaim space)
VACUUM;
```

## 🛠️ Database Management Commands

### **Backup Database:**
```bash
# Create backup
cp theone_production.db theone_backup_$(date +%Y%m%d).db

# Restore from backup
cp theone_backup_20250528.db theone_production.db
```

### **Database File Locations:**
```bash
# Development database
./theone.db

# Production database
./theone_production.db

# Check which database is being used
grep DATABASE_URL .env
```

### **Reset Database:**
```bash
# Remove database files
rm -f theone.db theone_production.db

# Recreate tables
python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
print('✅ Database recreated!')
"

# Add test data
python3 create_test_profiles.py
python3 create_alternative_lifestyle_profiles.py
```

## 📈 Monitoring Database Growth

### **Check Database Size:**
```bash
# File sizes
ls -lh *.db

# Detailed info
python3 check_database.py
```

### **Performance Queries:**
```sql
-- Table sizes
SELECT 
    name,
    COUNT(*) as row_count
FROM sqlite_master 
WHERE type='table' 
AND name NOT LIKE 'sqlite_%';

-- Database info
PRAGMA database_list;
PRAGMA table_info(users);
```

## 🔧 Troubleshooting

### **Database Locked Error:**
```bash
# Check for running processes
ps aux | grep python
ps aux | grep uvicorn

# Kill if needed
pkill -f uvicorn
pkill -f python

# Then try again
python3 check_database.py
```

### **Permission Issues:**
```bash
# Fix permissions
chmod 644 *.db
chown $USER:$USER *.db
```

### **Corrupted Database:**
```bash
# Check integrity
sqlite3 theone_production.db "PRAGMA integrity_check;"

# Repair if needed
sqlite3 theone_production.db ".dump" | sqlite3 theone_repaired.db
mv theone_repaired.db theone_production.db
```

## 🎯 Quick Commands Reference

```bash
# View database content
python3 check_database.py

# Clear all data
python3 check_database.py clear

# Add test data
python3 create_alternative_lifestyle_profiles.py

# Check file size
ls -lh *.db

# Open in SQLite
sqlite3 theone_production.db

# Backup database
cp theone_production.db backup_$(date +%Y%m%d).db
```

Your database is now easy to inspect and manage! 🗄️✨
