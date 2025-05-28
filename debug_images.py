#!/usr/bin/env python3
"""
Debug script to check image paths and URLs in the database
Run this to diagnose image display issues
"""

from app.db.database import SessionLocal
from app.models.user import User, Profile, Photo
import os

def debug_images():
    """Debug image paths and check if files exist"""
    
    print("🔍 theOne Dating App - Image Debug Tool")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Get all users with photos
        users = db.query(User).all()
        
        if not users:
            print("📭 No users found in database")
            return
        
        total_photos = 0
        missing_photos = 0
        
        for user in users:
            if hasattr(user, 'profile') and user.profile and user.profile.photos:
                print(f"\n👤 User: {user.email}")
                print(f"📸 Photos ({len(user.profile.photos)}):")
                
                for i, photo in enumerate(user.profile.photos, 1):
                    total_photos += 1
                    file_path = photo.file_path
                    
                    # Check if file exists
                    file_exists = os.path.exists(file_path)
                    if not file_exists:
                        missing_photos += 1
                    
                    # Generate different URL formats
                    url1 = f"/{file_path}"  # Direct path
                    url2 = f"/static/{file_path}" if not file_path.startswith('static/') else f"/{file_path}"
                    
                    print(f"   {i}. File Path: {file_path}")
                    print(f"      File Exists: {'✅' if file_exists else '❌'}")
                    print(f"      URL Option 1: {url1}")
                    print(f"      URL Option 2: {url2}")
                    
                    if file_exists:
                        file_size = os.path.getsize(file_path)
                        print(f"      File Size: {file_size:,} bytes")
                    print()
        
        print("📊 Summary:")
        print(f"   Total Photos: {total_photos}")
        print(f"   Missing Files: {missing_photos}")
        print(f"   Success Rate: {((total_photos - missing_photos) / total_photos * 100) if total_photos > 0 else 0:.1f}%")
        
        # Check upload directories
        print("\n📁 Upload Directories:")
        upload_dirs = ['static/uploads', 'static/uploads/profiles', 'static/uploads/expectations']
        
        for dir_path in upload_dirs:
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if not f.startswith('.')]
                print(f"   {dir_path}: {len(files)} files")
                
                # Show first few files
                for file in files[:3]:
                    file_path = os.path.join(dir_path, file)
                    size = os.path.getsize(file_path)
                    print(f"      - {file} ({size:,} bytes)")
                
                if len(files) > 3:
                    print(f"      ... and {len(files) - 3} more")
            else:
                print(f"   {dir_path}: ❌ Directory not found")
        
        # Test static file serving
        print("\n🌐 Static File Serving Test:")
        print("   Static files are mounted at: /static")
        print("   Directory: static/")
        print("   Example URLs:")
        print("   - /static/uploads/profiles/1_photo.jpg")
        print("   - /static/uploads/profiles/2_image.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

def fix_image_paths():
    """Fix image paths in database if needed"""
    
    print("🔧 Fixing image paths in database...")
    
    db = SessionLocal()
    
    try:
        photos = db.query(Photo).all()
        fixed_count = 0
        
        for photo in photos:
            old_path = photo.file_path
            
            # Fix path if it doesn't start with static/
            if not old_path.startswith('static/') and not old_path.startswith('/'):
                if 'uploads/' in old_path:
                    # Extract the uploads part
                    uploads_index = old_path.find('uploads/')
                    new_path = f"static/{old_path[uploads_index:]}"
                else:
                    new_path = f"static/uploads/profiles/{old_path}"
                
                print(f"   Fixing: {old_path} → {new_path}")
                photo.file_path = new_path
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"✅ Fixed {fixed_count} image paths")
        else:
            print("✅ All image paths are correct")
    
    except Exception as e:
        print(f"❌ Error fixing paths: {e}")
        db.rollback()
    
    finally:
        db.close()

def test_image_urls():
    """Test different image URL formats"""
    
    print("🧪 Testing Image URL Formats")
    print("=" * 30)
    
    db = SessionLocal()
    
    try:
        # Get first user with photos
        user = db.query(User).filter(User.profile.has()).filter(User.profile.has(Profile.photos.any())).first()
        
        if not user or not user.profile.photos:
            print("❌ No users with photos found for testing")
            return
        
        photo = user.profile.photos[0]
        file_path = photo.file_path
        
        print(f"📸 Testing photo: {file_path}")
        print(f"👤 User: {user.email}")
        print()
        
        # Test different URL formats
        url_formats = [
            f"/{file_path}",
            f"/static/{file_path}",
            f"/{file_path.replace('static/', '')}",
            f"/static/{file_path.replace('static/', '')}"
        ]
        
        print("🔗 URL Format Options:")
        for i, url in enumerate(url_formats, 1):
            print(f"   {i}. {url}")
        
        print("\n💡 Recommended URL format:")
        if file_path.startswith('static/'):
            recommended = f"/{file_path}"
        else:
            recommended = f"/static/{file_path}"
        
        print(f"   {recommended}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "fix":
            fix_image_paths()
        elif command == "test":
            test_image_urls()
        elif command == "help":
            print("Usage:")
            print("  python3 debug_images.py        - Debug image paths and files")
            print("  python3 debug_images.py fix    - Fix incorrect image paths")
            print("  python3 debug_images.py test   - Test image URL formats")
        else:
            print("Unknown command. Use 'help' for usage.")
    else:
        debug_images()
