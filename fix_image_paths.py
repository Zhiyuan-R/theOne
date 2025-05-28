#!/usr/bin/env python3
"""
Fix image paths in database to match production environment
"""
import os
import sys

def fix_database_paths():
    """Fix file paths in database to match production environment"""
    print("🔧 Fixing image paths in database...")
    
    try:
        # Import database modules
        sys.path.append('.')
        from app.db.database import SessionLocal
        from app.models.user import User, Profile, Photo, Expectation, IdealPartnerPhoto
        
        db = SessionLocal()
        
        # Get current upload directory
        uploads_path = os.getenv('UPLOADS_PATH', './static/uploads')
        print(f"Target uploads path: {uploads_path}")
        
        # Fix profile photos
        photos = db.query(Photo).all()
        print(f"Checking {len(photos)} profile photos...")
        
        fixed_count = 0
        for photo in photos:
            old_path = photo.file_path
            
            # Extract filename from current path
            if '/' in old_path:
                filename = old_path.split('/')[-1]
            else:
                filename = old_path
            
            # Generate new path
            new_path = os.path.join(uploads_path, 'profiles', filename)
            
            # Update if different and new file exists
            if old_path != new_path:
                if os.path.exists(new_path):
                    print(f"  Updating: {old_path} -> {new_path}")
                    photo.file_path = new_path
                    fixed_count += 1
                else:
                    print(f"  ⚠️  File not found: {new_path}")
        
        # Fix ideal partner photos
        ideal_photos = db.query(IdealPartnerPhoto).all()
        print(f"Checking {len(ideal_photos)} ideal partner photos...")
        
        for photo in ideal_photos:
            old_path = photo.file_path
            
            # Extract filename from current path
            if '/' in old_path:
                filename = old_path.split('/')[-1]
            else:
                filename = old_path
            
            # Generate new path
            new_path = os.path.join(uploads_path, 'ideal_partners', filename)
            
            # Update if different and new file exists
            if old_path != new_path:
                if os.path.exists(new_path):
                    print(f"  Updating: {old_path} -> {new_path}")
                    photo.file_path = new_path
                    fixed_count += 1
                else:
                    print(f"  ⚠️  File not found: {new_path}")
        
        # Commit changes
        if fixed_count > 0:
            db.commit()
            print(f"✅ Fixed {fixed_count} file paths")
        else:
            print("ℹ️  No paths needed fixing")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error fixing paths: {e}")

def copy_files_to_production_location():
    """Copy files from development location to production location"""
    print("📁 Copying files to production location...")
    
    import shutil
    
    source_base = "./static/uploads"
    target_base = "/app/data/uploads"
    
    if not os.path.exists(source_base):
        print(f"❌ Source directory not found: {source_base}")
        return
    
    # Create target directories
    os.makedirs(target_base, exist_ok=True)
    os.makedirs(f"{target_base}/profiles", exist_ok=True)
    os.makedirs(f"{target_base}/ideal_partners", exist_ok=True)
    os.makedirs(f"{target_base}/expectations", exist_ok=True)
    os.makedirs(f"{target_base}/audio", exist_ok=True)
    
    copied_count = 0
    
    # Copy files from each subdirectory
    for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
        source_dir = os.path.join(source_base, subdir)
        target_dir = os.path.join(target_base, subdir)
        
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                source_file = os.path.join(source_dir, filename)
                target_file = os.path.join(target_dir, filename)
                
                if os.path.isfile(source_file) and not os.path.exists(target_file):
                    try:
                        shutil.copy2(source_file, target_file)
                        print(f"  Copied: {source_file} -> {target_file}")
                        copied_count += 1
                    except Exception as e:
                        print(f"  ❌ Error copying {source_file}: {e}")
    
    print(f"✅ Copied {copied_count} files")

def main():
    """Main function"""
    print("🔧 theOne Dating App - Image Path Fixer")
    print("=" * 40)
    print()
    
    # Check if we're in production environment
    is_production = os.getenv('UPLOADS_PATH') == '/app/data/uploads'
    
    if is_production:
        print("🏭 Production environment detected")
        copy_files_to_production_location()
    else:
        print("🛠️  Development environment detected")
    
    fix_database_paths()
    
    print()
    print("✅ Path fixing complete!")
    print("💡 Run debug_image_serving.py to verify the fixes")

if __name__ == "__main__":
    main()
