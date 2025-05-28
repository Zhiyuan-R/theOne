#!/usr/bin/env python3
"""
Database inspection script for theOne dating app
Shows all users, profiles, expectations, and photos in the database
"""

from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo, ExampleImage
from sqlalchemy import text
import os

def check_database():
    """Check and display all data in the database"""
    
    # Check if database file exists
    db_files = ['theone.db', 'theone_production.db']
    existing_dbs = [db for db in db_files if os.path.exists(db)]
    
    print("🗄️  theOne Dating App - Database Inspector")
    print("=" * 50)
    
    if not existing_dbs:
        print("❌ No database files found!")
        print("   Looking for: theone.db, theone_production.db")
        return
    
    print(f"📁 Found database files: {', '.join(existing_dbs)}")
    print()
    
    db = SessionLocal()
    
    try:
        # Get table counts
        user_count = db.query(User).count()
        profile_count = db.query(Profile).count()
        expectation_count = db.query(Expectation).count()
        photo_count = db.query(Photo).count()
        
        print("📊 Database Summary:")
        print(f"   👥 Users: {user_count}")
        print(f"   📝 Profiles: {profile_count}")
        print(f"   💭 Expectations: {expectation_count}")
        print(f"   📸 Photos: {photo_count}")
        print()
        
        if user_count == 0:
            print("✨ Database is empty - ready for fresh start!")
            return
        
        # Show all users with their data
        print("👥 All Users:")
        print("-" * 40)
        
        users = db.query(User).all()
        for i, user in enumerate(users, 1):
            print(f"{i}. 📧 Email: {user.email}")
            print(f"   🆔 ID: {user.id}")
            print(f"   ✅ Active: {user.is_active}")
            print(f"   📅 Created: {user.created_at}")
            
            # Check if user has profile
            if hasattr(user, 'profile') and user.profile:
                print(f"   📝 Profile: {user.profile.description[:100]}...")
                
                # Check photos
                if user.profile.photos:
                    print(f"   📸 Photos: {len(user.profile.photos)} uploaded")
                    for photo in user.profile.photos:
                        print(f"      - {photo.file_path}")
                else:
                    print(f"   📸 Photos: None")
            else:
                print(f"   📝 Profile: None")
            
            # Check expectations
            if hasattr(user, 'expectations') and user.expectations:
                print(f"   💭 Expectations: {user.expectations.description[:100]}...")
            else:
                print(f"   💭 Expectations: None")
            
            print()
        
        # Show database file info
        print("📁 Database File Info:")
        print("-" * 40)
        for db_file in existing_dbs:
            size = os.path.getsize(db_file)
            print(f"   {db_file}: {size:,} bytes ({size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    
    finally:
        db.close()

def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing all data from database...")
    
    db = SessionLocal()
    try:
        # Delete in correct order (foreign key constraints)
        db.query(ExampleImage).delete()
        db.query(Photo).delete()
        db.query(Expectation).delete()
        db.query(Profile).delete()
        db.query(User).delete()
        db.commit()
        
        print("✅ All data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

def show_tables():
    """Show all tables in the database"""
    print("📋 Database Tables:")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        # Get table names
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':
                # Get row count
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = count_result.fetchone()[0]
                print(f"   📊 {table_name}: {count} rows")
        
    except Exception as e:
        print(f"❌ Error reading tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_database()
        elif command == "tables":
            show_tables()
        elif command == "help":
            print("Usage:")
            print("  python check_database.py        - View all data")
            print("  python check_database.py clear  - Clear all data")
            print("  python check_database.py tables - Show table info")
        else:
            print("Unknown command. Use 'help' for usage.")
    else:
        check_database()
