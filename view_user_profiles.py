#!/usr/bin/env python3
"""
View user profiles created through the website
Shows all user data submitted via the web interface
"""

from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo
import os
from datetime import datetime

def view_all_profiles():
    """View all user profiles submitted through the website"""
    
    print("👥 theOne Dating App - User Profiles Viewer")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("📭 No users found in database")
            print("   Users will appear here after they submit the form on your website")
            return
        
        print(f"📊 Found {len(users)} user(s) in database")
        print()
        
        for i, user in enumerate(users, 1):
            print(f"👤 User #{i}")
            print("=" * 40)
            print(f"📧 Email: {user.email}")
            print(f"🆔 User ID: {user.id}")
            print(f"📅 Joined: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"✅ Active: {user.is_active}")
            
            # Show profile information
            if hasattr(user, 'profile') and user.profile:
                profile = user.profile
                print(f"\n📝 Profile Description:")
                print(f"   {profile.description}")
                print(f"   Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show photos
                if profile.photos:
                    print(f"\n📸 Uploaded Photos ({len(profile.photos)}):")
                    for j, photo in enumerate(profile.photos, 1):
                        photo_path = photo.file_path
                        if os.path.exists(photo_path):
                            size = os.path.getsize(photo_path)
                            print(f"   {j}. {photo_path} ({size:,} bytes)")
                        else:
                            print(f"   {j}. {photo_path} (FILE MISSING)")
                else:
                    print(f"\n📸 Photos: None uploaded")
            else:
                print(f"\n📝 Profile: Not created")
            
            # Show expectations
            if hasattr(user, 'expectations') and user.expectations:
                expectations = user.expectations
                print(f"\n💭 Expectations:")
                print(f"   {expectations.description}")
                print(f"   Created: {expectations.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"\n💭 Expectations: Not provided")
            
            # Check if user is ready for matching
            has_profile = hasattr(user, 'profile') and user.profile
            has_expectations = hasattr(user, 'expectations') and user.expectations
            has_photo = has_profile and user.profile.photos
            
            print(f"\n🎯 Matching Status:")
            print(f"   Profile: {'✅' if has_profile else '❌'}")
            print(f"   Expectations: {'✅' if has_expectations else '❌'}")
            print(f"   Photo: {'✅' if has_photo else '❌'}")
            
            if has_profile and has_expectations:
                print(f"   🚀 Ready for AI matching!")
            else:
                print(f"   ⏳ Incomplete profile")
            
            print("\n" + "-" * 60 + "\n")
    
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    
    finally:
        db.close()

def view_user_by_email(email):
    """View specific user by email"""
    
    print(f"🔍 Looking for user: {email}")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return
        
        print(f"✅ Found user!")
        print(f"📧 Email: {user.email}")
        print(f"🆔 ID: {user.id}")
        print(f"📅 Joined: {user.created_at}")
        
        # Show detailed profile
        if hasattr(user, 'profile') and user.profile:
            print(f"\n📝 Profile:")
            print(f"   Description: {user.profile.description}")
            
            if user.profile.photos:
                print(f"\n📸 Photos:")
                for photo in user.profile.photos:
                    print(f"   - {photo.file_path}")
        
        if hasattr(user, 'expectations') and user.expectations:
            print(f"\n💭 Expectations:")
            print(f"   {user.expectations.description}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

def view_recent_users(limit=5):
    """View most recent users"""
    
    print(f"🕒 Most Recent {limit} Users")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
        
        if not users:
            print("📭 No users found")
            return
        
        for i, user in enumerate(users, 1):
            print(f"{i}. 📧 {user.email}")
            print(f"   📅 {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Quick status
            has_profile = hasattr(user, 'profile') and user.profile
            has_expectations = hasattr(user, 'expectations') and user.expectations
            has_photo = has_profile and user.profile.photos
            
            status = []
            if has_profile: status.append("Profile")
            if has_expectations: status.append("Expectations") 
            if has_photo: status.append("Photo")
            
            print(f"   📊 Has: {', '.join(status) if status else 'Nothing yet'}")
            print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

def view_uploaded_files():
    """View all uploaded files"""
    
    print("📁 Uploaded Files")
    print("=" * 40)
    
    upload_dirs = ['static/uploads/profiles', 'static/uploads/expectations']
    
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            if files:
                print(f"\n📂 {upload_dir}:")
                for file in sorted(files):
                    if file != '.gitkeep':
                        file_path = os.path.join(upload_dir, file)
                        size = os.path.getsize(file_path)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        print(f"   📄 {file} ({size:,} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"\n📂 {upload_dir}: Empty")
        else:
            print(f"\n📂 {upload_dir}: Directory not found")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "email" and len(sys.argv) > 2:
            email = sys.argv[2]
            view_user_by_email(email)
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            view_recent_users(limit)
        elif command == "files":
            view_uploaded_files()
        elif command == "help":
            print("Usage:")
            print("  python view_user_profiles.py              - View all profiles")
            print("  python view_user_profiles.py email <email> - View specific user")
            print("  python view_user_profiles.py recent [N]   - View N recent users")
            print("  python view_user_profiles.py files        - View uploaded files")
        else:
            print("Unknown command. Use 'help' for usage.")
    else:
        view_all_profiles()
