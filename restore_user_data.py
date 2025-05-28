#!/usr/bin/env python3
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
