#!/usr/bin/env python3
"""
Database backup script for theOne dating app
Creates a backup of the database and uploaded files
"""
import os
import shutil
import sqlite3
import json
from datetime import datetime
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo, ExampleImage, IdealPartnerPhoto, Match

def backup_database():
    """Create a complete backup of the database and files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    
    print(f"🔄 Creating backup: {backup_dir}")
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(f"{backup_dir}/static", exist_ok=True)
    
    try:
        # 1. Backup SQLite database file
        if os.path.exists("theone_production.db"):
            shutil.copy2("theone_production.db", f"{backup_dir}/theone_production.db")
            print("✅ Database file backed up")
        else:
            print("⚠️ No database file found")
        
        # 2. Backup uploaded files
        if os.path.exists("static/uploads"):
            shutil.copytree("static/uploads", f"{backup_dir}/static/uploads")
            print("✅ Uploaded files backed up")
        else:
            print("⚠️ No uploads directory found")
        
        # 3. Export data as JSON (human-readable backup)
        db = SessionLocal()
        try:
            backup_data = {
                "backup_timestamp": timestamp,
                "users": [],
                "profiles": [],
                "expectations": [],
                "photos": [],
                "example_images": [],
                "ideal_partner_photos": [],
                "matches": []
            }
            
            # Export users
            users = db.query(User).all()
            for user in users:
                backup_data["users"].append({
                    "id": user.id,
                    "email": user.email,
                    "hashed_password": user.hashed_password,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                })
            
            # Export profiles
            profiles = db.query(Profile).all()
            for profile in profiles:
                backup_data["profiles"].append({
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "description": profile.description,
                    "audio_clip_path": profile.audio_clip_path,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                    "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
                })
            
            # Export expectations
            expectations = db.query(Expectation).all()
            for expectation in expectations:
                backup_data["expectations"].append({
                    "id": expectation.id,
                    "user_id": expectation.user_id,
                    "description": expectation.description,
                    "created_at": expectation.created_at.isoformat() if expectation.created_at else None,
                    "updated_at": expectation.updated_at.isoformat() if expectation.updated_at else None
                })
            
            # Export photos
            photos = db.query(Photo).all()
            for photo in photos:
                backup_data["photos"].append({
                    "id": photo.id,
                    "profile_id": photo.profile_id,
                    "file_path": photo.file_path,
                    "order_index": photo.order_index,
                    "created_at": photo.created_at.isoformat() if photo.created_at else None
                })
            
            # Export example images
            example_images = db.query(ExampleImage).all()
            for img in example_images:
                backup_data["example_images"].append({
                    "id": img.id,
                    "expectation_id": img.expectation_id,
                    "file_path": img.file_path,
                    "created_at": img.created_at.isoformat() if img.created_at else None
                })
            
            # Export ideal partner photos
            ideal_photos = db.query(IdealPartnerPhoto).all()
            for photo in ideal_photos:
                backup_data["ideal_partner_photos"].append({
                    "id": photo.id,
                    "expectation_id": photo.expectation_id,
                    "file_path": photo.file_path,
                    "order_index": photo.order_index,
                    "created_at": photo.created_at.isoformat() if photo.created_at else None
                })
            
            # Export matches
            matches = db.query(Match).all()
            for match in matches:
                backup_data["matches"].append({
                    "id": match.id,
                    "user_id": match.user_id,
                    "matched_user_id": match.matched_user_id,
                    "compatibility_score": match.compatibility_score,
                    "text_similarity_score": match.text_similarity_score,
                    "visual_similarity_score": match.visual_similarity_score,
                    "basic_text_similarity": match.basic_text_similarity,
                    "llm_text_score": match.llm_text_score,
                    "personality_score": match.personality_score,
                    "lifestyle_score": match.lifestyle_score,
                    "emotional_score": match.emotional_score,
                    "longterm_score": match.longterm_score,
                    "ideal_partner_score": match.ideal_partner_score,
                    "expectation_visual_score": match.expectation_visual_score,
                    "is_viewed": match.is_viewed,
                    "created_at": match.created_at.isoformat() if match.created_at else None
                })
            
            # Save JSON backup
            with open(f"{backup_dir}/data_backup.json", "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print("✅ JSON data export completed")
            
            # Create backup summary
            summary = {
                "backup_timestamp": timestamp,
                "backup_directory": backup_dir,
                "total_users": len(backup_data["users"]),
                "total_profiles": len(backup_data["profiles"]),
                "total_expectations": len(backup_data["expectations"]),
                "total_photos": len(backup_data["photos"]),
                "total_ideal_photos": len(backup_data["ideal_partner_photos"]),
                "total_matches": len(backup_data["matches"])
            }
            
            with open(f"{backup_dir}/backup_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            print(f"📊 Backup Summary:")
            print(f"   👥 Users: {summary['total_users']}")
            print(f"   📝 Profiles: {summary['total_profiles']}")
            print(f"   💭 Expectations: {summary['total_expectations']}")
            print(f"   📸 Photos: {summary['total_photos']}")
            print(f"   💕 Ideal Photos: {summary['total_ideal_photos']}")
            print(f"   🎯 Matches: {summary['total_matches']}")
            
        finally:
            db.close()
        
        print(f"✅ Backup completed successfully!")
        print(f"📁 Backup location: {backup_dir}")
        
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    backup_database()
