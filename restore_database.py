#!/usr/bin/env python3
"""
Database restore script for theOne dating app
Restores database and uploaded files from backup
"""
import os
import shutil
import json
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def list_backups():
    """List available backups"""
    if not os.path.exists("backups"):
        print("❌ No backups directory found")
        return []
    
    backups = []
    for item in os.listdir("backups"):
        backup_path = os.path.join("backups", item)
        if os.path.isdir(backup_path) and item.startswith("backup_"):
            summary_file = os.path.join(backup_path, "backup_summary.json")
            if os.path.exists(summary_file):
                try:
                    with open(summary_file, "r") as f:
                        summary = json.load(f)
                    backups.append({
                        "directory": item,
                        "path": backup_path,
                        "summary": summary
                    })
                except:
                    pass
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x["summary"]["backup_timestamp"], reverse=True)
    return backups

def restore_database(backup_path):
    """Restore database from backup"""
    
    print(f"🔄 Restoring from backup: {backup_path}")
    
    try:
        # 1. Backup current data (if exists)
        if os.path.exists("theone_production.db"):
            current_backup = f"theone_production_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("theone_production.db", current_backup)
            print(f"📦 Current database backed up as: {current_backup}")
        
        # 2. Restore database file
        backup_db_path = os.path.join(backup_path, "theone_production.db")
        if os.path.exists(backup_db_path):
            shutil.copy2(backup_db_path, "theone_production.db")
            print("✅ Database file restored")
        else:
            print("⚠️ No database file in backup")
        
        # 3. Restore uploaded files
        backup_uploads_path = os.path.join(backup_path, "static", "uploads")
        if os.path.exists(backup_uploads_path):
            # Backup current uploads if they exist
            if os.path.exists("static/uploads"):
                current_uploads_backup = f"static/uploads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move("static/uploads", current_uploads_backup)
                print(f"📦 Current uploads backed up as: {current_uploads_backup}")
            
            # Restore uploads
            os.makedirs("static", exist_ok=True)
            shutil.copytree(backup_uploads_path, "static/uploads")
            print("✅ Uploaded files restored")
        else:
            print("⚠️ No uploads directory in backup")
        
        # 4. Show restore summary
        summary_file = os.path.join(backup_path, "backup_summary.json")
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                summary = json.load(f)
            
            print(f"📊 Restored Data Summary:")
            print(f"   👥 Users: {summary.get('total_users', 0)}")
            print(f"   📝 Profiles: {summary.get('total_profiles', 0)}")
            print(f"   💭 Expectations: {summary.get('total_expectations', 0)}")
            print(f"   📸 Photos: {summary.get('total_photos', 0)}")
            print(f"   💕 Ideal Photos: {summary.get('total_ideal_photos', 0)}")
            print(f"   🎯 Matches: {summary.get('total_matches', 0)}")
        
        print("✅ Restore completed successfully!")
        print("🔄 Please restart your server to use the restored database")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main restore function with interactive selection"""
    print("🗄️ theOne Database Restore Tool")
    print("=" * 40)
    
    backups = list_backups()
    
    if not backups:
        print("❌ No backups found!")
        print("💡 Run 'python3 backup_database.py' to create a backup first")
        return
    
    print(f"📋 Found {len(backups)} backup(s):")
    print()
    
    for i, backup in enumerate(backups, 1):
        summary = backup["summary"]
        timestamp = summary["backup_timestamp"]
        # Format timestamp for display
        try:
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = timestamp
        
        print(f"{i}. {formatted_time}")
        print(f"   📁 {backup['directory']}")
        print(f"   👥 {summary.get('total_users', 0)} users, "
              f"📸 {summary.get('total_photos', 0)} photos, "
              f"💕 {summary.get('total_ideal_photos', 0)} ideal photos")
        print()
    
    # Get user selection
    try:
        choice = input(f"Select backup to restore (1-{len(backups)}) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("👋 Restore cancelled")
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(backups):
            selected_backup = backups[choice_num - 1]
            
            # Confirm restore
            print(f"\n⚠️ This will replace your current database and files!")
            confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
            
            if confirm in ['yes', 'y']:
                restore_database(selected_backup["path"])
            else:
                print("👋 Restore cancelled")
        else:
            print("❌ Invalid selection")
            
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Restore cancelled")

if __name__ == "__main__":
    main()
