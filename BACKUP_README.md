# 🗄️ theOne Database Backup System

This backup system ensures your user data is never lost when pushing code updates.

## 📋 Quick Start

### 🔄 Before Pushing Code (Recommended)
```bash
# Auto-backup and push (safest option)
python3 auto_backup_and_push.py
```

### 📦 Manual Backup
```bash
# Create a backup
python3 backup_database.py

# Quick backup with minimal output
python3 quick_backup.py
```

### 🔄 Restore Data
```bash
# Interactive restore (shows all available backups)
python3 restore_database.py
```

## 🛠️ How It Works

### 1. **Persistent Database**
- Database file (`theone_production.db`) is now preserved between code updates
- Only creates new database if none exists
- No more data loss on server restart!

### 2. **Complete Backup System**
Each backup includes:
- ✅ **SQLite Database** - Complete database file
- ✅ **Uploaded Files** - All user photos and ideal partner photos
- ✅ **JSON Export** - Human-readable data export
- ✅ **Backup Summary** - Statistics and metadata

### 3. **Smart Restore**
- Lists all available backups with timestamps
- Shows user counts and photo counts
- Backs up current data before restoring
- Interactive selection process

## 📁 Backup Structure

```
backups/
├── backup_20241201_143022/
│   ├── theone_production.db      # Database file
│   ├── static/uploads/           # All uploaded files
│   ├── data_backup.json          # JSON export
│   └── backup_summary.json       # Backup metadata
└── backup_20241201_150315/
    └── ...
```

## 🚀 Usage Examples

### Before Major Code Changes
```bash
# Create backup before making changes
python3 quick_backup.py

# Make your code changes...
# Test everything...

# Push with auto-backup
python3 auto_backup_and_push.py
```

### After Deployment Issues
```bash
# List and restore from backup
python3 restore_database.py

# Select backup from list
# Restart server
python3 main.py
```

### Regular Maintenance
```bash
# Create daily backup
python3 backup_database.py

# Check backup status
ls -la backups/
```

## 🔒 Data Protection

### What's Protected:
- ✅ User accounts and profiles
- ✅ Profile photos and ideal partner photos
- ✅ Expectations and descriptions
- ✅ AI matching scores and history
- ✅ All uploaded files

### What's Excluded:
- ❌ Temporary files
- ❌ Log files
- ❌ Cache files
- ❌ Development databases

## 🎯 Best Practices

1. **Always backup before pushing code**
   ```bash
   python3 auto_backup_and_push.py
   ```

2. **Create backups before major changes**
   ```bash
   python3 quick_backup.py
   ```

3. **Test restore process periodically**
   ```bash
   python3 restore_database.py
   ```

4. **Keep multiple backups** (automatic - each backup is timestamped)

5. **Monitor backup sizes** (check `backups/` directory)

## 🆘 Emergency Recovery

If you lose data:

1. **Stop the server** (Ctrl+C)
2. **Run restore script**:
   ```bash
   python3 restore_database.py
   ```
3. **Select the most recent backup**
4. **Restart the server**:
   ```bash
   python3 main.py
   ```

## 📊 Backup Statistics

Each backup shows:
- 👥 Total users
- 📝 Total profiles  
- 💭 Total expectations
- 📸 Total photos
- 💕 Total ideal partner photos
- 🎯 Total matches

## 🔧 Troubleshooting

### "No backups found"
```bash
# Create your first backup
python3 backup_database.py
```

### "Database file not found"
```bash
# Start the server to create database
python3 main.py
# Then create backup
python3 backup_database.py
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x *.py
```

## 🎉 Success!

Your data is now protected! The backup system ensures:
- ✅ No data loss during code updates
- ✅ Easy recovery from any backup
- ✅ Complete file and database protection
- ✅ Automated backup workflows
