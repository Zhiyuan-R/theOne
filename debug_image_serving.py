#!/usr/bin/env python3
"""
Debug script to diagnose image serving issues in theOne dating app
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Check environment configuration"""
    print("=== ENVIRONMENT CONFIGURATION ===")
    print(f"DEBUG: {os.getenv('DEBUG', 'Not set')}")
    print(f"UPLOADS_PATH: {os.getenv('UPLOADS_PATH', 'Not set')}")
    print(f"UPLOAD_DIR: {os.getenv('UPLOAD_DIR', 'Not set')}")
    print()

def check_directories():
    """Check if upload directories exist and list contents"""
    print("=== DIRECTORY STRUCTURE ===")
    
    # Check possible upload directories
    possible_dirs = [
        "./static/uploads",
        "/app/data/uploads",
        "./data/uploads",
        os.getenv('UPLOADS_PATH', './static/uploads')
    ]
    
    for dir_path in possible_dirs:
        print(f"Checking: {dir_path}")
        if os.path.exists(dir_path):
            print(f"  ✅ EXISTS")
            try:
                # List subdirectories
                for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
                    subdir_path = os.path.join(dir_path, subdir)
                    if os.path.exists(subdir_path):
                        files = os.listdir(subdir_path)
                        print(f"    {subdir}/: {len(files)} files")
                        if files:
                            print(f"      Sample files: {files[:3]}")
                    else:
                        print(f"    {subdir}/: ❌ MISSING")
            except Exception as e:
                print(f"  ❌ ERROR listing contents: {e}")
        else:
            print(f"  ❌ MISSING")
        print()

def check_database_paths():
    """Check file paths stored in database"""
    print("=== DATABASE FILE PATHS ===")
    
    try:
        # Import database modules
        sys.path.append('.')
        from app.db.database import SessionLocal
        from app.models.user import User, Profile, Photo, Expectation, IdealPartnerPhoto
        
        db = SessionLocal()
        
        # Check profile photos
        photos = db.query(Photo).all()
        print(f"Profile photos in database: {len(photos)}")
        for photo in photos[:5]:  # Show first 5
            print(f"  ID {photo.id}: {photo.file_path}")
            if os.path.exists(photo.file_path):
                print(f"    ✅ File exists")
            else:
                print(f"    ❌ File missing")
        
        print()
        
        # Check ideal partner photos
        ideal_photos = db.query(IdealPartnerPhoto).all()
        print(f"Ideal partner photos in database: {len(ideal_photos)}")
        for photo in ideal_photos[:5]:  # Show first 5
            print(f"  ID {photo.id}: {photo.file_path}")
            if os.path.exists(photo.file_path):
                print(f"    ✅ File exists")
            else:
                print(f"    ❌ File missing")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print()

def test_url_generation():
    """Test URL generation function"""
    print("=== URL GENERATION TEST ===")
    
    try:
        sys.path.append('.')
        from main import get_photo_url
        
        test_paths = [
            "static/uploads/profiles/test.jpg",
            "/app/data/uploads/profiles/test.jpg",
            "profiles/test.jpg",
            "static/uploads/ideal_partners/test.jpg",
            "/app/data/uploads/ideal_partners/test.jpg"
        ]
        
        for path in test_paths:
            url = get_photo_url(path)
            print(f"Path: {path}")
            print(f"URL:  {url}")
            print()
            
    except Exception as e:
        print(f"❌ Error testing URL generation: {e}")

def check_fastapi_mounts():
    """Check FastAPI static file mounts"""
    print("=== FASTAPI STATIC MOUNTS ===")
    
    try:
        sys.path.append('.')
        from main import app
        
        print("Mounted routes:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'name'):
                print(f"  {route.path} -> {route.name}")
                
    except Exception as e:
        print(f"❌ Error checking FastAPI mounts: {e}")

def main():
    """Run all diagnostic checks"""
    print("🔍 theOne Dating App - Image Serving Diagnostics")
    print("=" * 50)
    print()
    
    check_environment()
    check_directories()
    check_database_paths()
    test_url_generation()
    check_fastapi_mounts()
    
    print("=" * 50)
    print("✅ Diagnostic complete!")
    print()
    print("💡 TROUBLESHOOTING TIPS:")
    print("1. Ensure UPLOADS_PATH environment variable is set correctly")
    print("2. Check that upload directories exist and have proper permissions")
    print("3. Verify file paths in database match actual file locations")
    print("4. Test image URLs directly in browser")
    print("5. Check server logs for 404 errors")

if __name__ == "__main__":
    main()
