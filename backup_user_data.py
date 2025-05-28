#!/usr/bin/env python3
"""
Backup all user data (database + files) to GitHub repository
This prevents data loss during deployments
"""
import os
import sys
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def backup_database():
    """Export database to JSON format"""
    print("📊 Backing up database...")
    
    try:
        # Import database modules
        sys.path.append('.')
        from app.db.database import SessionLocal
        from app.models.user import User, Profile, Photo, Expectation, IdealPartnerPhoto
        
        db = SessionLocal()
        
        # Get all users with their data
        users = db.query(User).all()
        
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "total_users": len(users),
            "users": []
        }
        
        for user in users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "profile": None,
                "expectations": None
            }
            
            # Get profile data
            if hasattr(user, 'profile') and user.profile:
                profile_photos = []
                for photo in user.profile.photos:
                    profile_photos.append({
                        "id": photo.id,
                        "file_path": photo.file_path,
                        "order_index": photo.order_index,
                        "created_at": photo.created_at.isoformat() if photo.created_at else None
                    })
                
                user_data["profile"] = {
                    "id": user.profile.id,
                    "description": user.profile.description,
                    "audio_clip_path": user.profile.audio_clip_path,
                    "created_at": user.profile.created_at.isoformat() if user.profile.created_at else None,
                    "updated_at": user.profile.updated_at.isoformat() if user.profile.updated_at else None,
                    "photos": profile_photos
                }
            
            # Get expectations data
            if hasattr(user, 'expectations') and user.expectations:
                ideal_partner_photos = []
                for photo in user.expectations.ideal_partner_photos:
                    ideal_partner_photos.append({
                        "id": photo.id,
                        "file_path": photo.file_path,
                        "order_index": photo.order_index,
                        "created_at": photo.created_at.isoformat() if photo.created_at else None
                    })
                
                user_data["expectations"] = {
                    "id": user.expectations.id,
                    "description": user.expectations.description,
                    "created_at": user.expectations.created_at.isoformat() if user.expectations.created_at else None,
                    "updated_at": user.expectations.updated_at.isoformat() if user.expectations.updated_at else None,
                    "ideal_partner_photos": ideal_partner_photos
                }
            
            backup_data["users"].append(user_data)
        
        db.close()
        
        # Save to JSON file
        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/database_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Database backed up to: {backup_file}")
        print(f"   Users: {len(users)}")
        
        # Also create a latest backup
        latest_backup = "backups/database_backup_latest.json"
        shutil.copy2(backup_file, latest_backup)
        print(f"✅ Latest backup: {latest_backup}")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ Error backing up database: {e}")
        return None

def backup_files():
    """Copy all uploaded files to backup directory"""
    print("📁 Backing up uploaded files...")
    
    # Find upload directories
    possible_upload_dirs = [
        "./static/uploads",
        "/app/data/uploads",
        "./data/uploads"
    ]
    
    upload_dir = None
    for dir_path in possible_upload_dirs:
        if os.path.exists(dir_path):
            upload_dir = dir_path
            break
    
    if not upload_dir:
        print("❌ No upload directory found")
        return False
    
    print(f"📂 Found upload directory: {upload_dir}")
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/files_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy all files
    copied_count = 0
    try:
        for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
            source_dir = os.path.join(upload_dir, subdir)
            target_dir = os.path.join(backup_dir, subdir)
            
            if os.path.exists(source_dir):
                os.makedirs(target_dir, exist_ok=True)
                for filename in os.listdir(source_dir):
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_dir, filename)
                    
                    if os.path.isfile(source_file):
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
        
        print(f"✅ Files backed up to: {backup_dir}")
        print(f"   Files copied: {copied_count}")
        
        # Also create a latest backup
        latest_backup_dir = "backups/files_latest"
        if os.path.exists(latest_backup_dir):
            shutil.rmtree(latest_backup_dir)
        shutil.copytree(backup_dir, latest_backup_dir)
        print(f"✅ Latest files backup: {latest_backup_dir}")
        
        return backup_dir
        
    except Exception as e:
        print(f"❌ Error backing up files: {e}")
        return None

def create_restore_script():
    """Create a script to restore data from backup"""
    restore_script = """#!/usr/bin/env python3
'''
Restore user data from backup
Usage: python restore_user_data.py [backup_file]
'''
import os
import sys
import json
import shutil
from datetime import datetime

def restore_database(backup_file):
    '''Restore database from JSON backup'''
    print(f"🔄 Restoring database from {backup_file}")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Import database modules
        sys.path.append('.')
        from app.db.database import SessionLocal, create_tables
        from app.models.user import User, Profile, Photo, Expectation, IdealPartnerPhoto
        from passlib.context import CryptContext
        import uuid
        
        # Create tables if they don't exist
        create_tables()
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        db = SessionLocal()
        
        restored_count = 0
        
        for user_data in backup_data["users"]:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"  ⚠️  User {user_data['email']} already exists, skipping")
                continue
            
            # Create user
            user = User(
                email=user_data["email"],
                hashed_password=pwd_context.hash(str(uuid.uuid4())),  # Random password
                is_active=user_data["is_active"]
            )
            db.add(user)
            db.flush()
            
            # Restore profile
            if user_data["profile"]:
                profile = Profile(
                    user_id=user.id,
                    description=user_data["profile"]["description"],
                    audio_clip_path=user_data["profile"]["audio_clip_path"]
                )
                db.add(profile)
                db.flush()
                
                # Restore photos
                for photo_data in user_data["profile"]["photos"]:
                    photo = Photo(
                        profile_id=profile.id,
                        file_path=photo_data["file_path"],
                        order_index=photo_data["order_index"]
                    )
                    db.add(photo)
            
            # Restore expectations
            if user_data["expectations"]:
                expectation = Expectation(
                    user_id=user.id,
                    description=user_data["expectations"]["description"]
                )
                db.add(expectation)
                db.flush()
                
                # Restore ideal partner photos
                for photo_data in user_data["expectations"]["ideal_partner_photos"]:
                    photo = IdealPartnerPhoto(
                        expectation_id=expectation.id,
                        file_path=photo_data["file_path"],
                        order_index=photo_data["order_index"]
                    )
                    db.add(photo)
            
            restored_count += 1
        
        db.commit()
        db.close()
        
        print(f"✅ Restored {restored_count} users")
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")

def restore_files(backup_dir):
    '''Restore files from backup'''
    print(f"📁 Restoring files from {backup_dir}")
    
    # Determine target directory
    target_dirs = ["./static/uploads", "/app/data/uploads"]
    target_dir = None
    
    for dir_path in target_dirs:
        if os.path.exists(os.path.dirname(dir_path)):
            target_dir = dir_path
            break
    
    if not target_dir:
        print("❌ Cannot determine target upload directory")
        return
    
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy files
    copied_count = 0
    for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
        source_dir = os.path.join(backup_dir, subdir)
        target_subdir = os.path.join(target_dir, subdir)
        
        if os.path.exists(source_dir):
            os.makedirs(target_subdir, exist_ok=True)
            for filename in os.listdir(source_dir):
                source_file = os.path.join(source_dir, filename)
                target_file = os.path.join(target_subdir, filename)
                
                if os.path.isfile(source_file):
                    shutil.copy2(source_file, target_file)
                    copied_count += 1
    
    print(f"✅ Restored {copied_count} files to {target_dir}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        backup_file = sys.argv[1]
    else:
        backup_file = "backups/database_backup_latest.json"
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        sys.exit(1)
    
    print("🔄 Restoring user data from backup...")
    restore_database(backup_file)
    
    # Try to restore files
    files_backup = "backups/files_latest"
    if os.path.exists(files_backup):
        restore_files(files_backup)
    
    print("✅ Restore complete!")
"""
    
    with open("restore_user_data.py", "w") as f:
        f.write(restore_script)
    
    os.chmod("restore_user_data.py", 0o755)
    print("✅ Created restore script: restore_user_data.py")

def main():
    """Main backup function"""
    print("💾 theOne Dating App - User Data Backup")
    print("=" * 40)
    print()
    
    # Create backups directory
    os.makedirs("backups", exist_ok=True)
    
    # Backup database
    db_backup = backup_database()
    
    # Backup files
    files_backup = backup_files()
    
    # Create restore script
    create_restore_script()
    
    print()
    print("=" * 40)
    print("✅ Backup complete!")
    print()
    print("📋 What was backed up:")
    if db_backup:
        print(f"   📊 Database: {db_backup}")
    if files_backup:
        print(f"   📁 Files: {files_backup}")
    print("   🔄 Restore script: restore_user_data.py")
    print()
    print("💡 To commit to GitHub:")
    print("   git add backups/")
    print("   git commit -m 'Backup user data'")
    print("   git push origin main")

if __name__ == "__main__":
    main()
