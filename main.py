"""
Main FastAPI application for theOne dating app
"""
from typing import List
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.db.database import create_tables
from app.api import auth, profiles, expectations, matches

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Dating App with Multimodal Matching",
    version="1.0.0"
)

# Add CORS middleware
cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files with proper configuration for production
from app.core.config import settings
import os

# Get the actual upload directory (may be different in production)
upload_dir = settings.get_upload_dir()
static_dir = "static"

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount uploads directory separately for better control
if os.path.exists(upload_dir):
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

def get_photo_url(file_path: str) -> str:
    """Generate proper photo URL for both development and production"""
    if not file_path:
        return None

    from urllib.parse import quote

    # Debug logging
    print(f"DEBUG: Converting file_path '{file_path}' to URL")

    # Handle different path formats and ensure absolute URLs
    if file_path.startswith('/app/data/uploads/'):
        # Production path - use /uploads/ mount
        relative_path = file_path.replace('/app/data/uploads/', '')
        url = f"/uploads/{quote(relative_path)}"
        print(f"DEBUG: Production path -> {url}")
        return url
    elif file_path.startswith('static/uploads/'):
        # Development path - use /uploads/ mount
        relative_path = file_path.replace('static/uploads/', '')
        url = f"/uploads/{quote(relative_path)}"
        print(f"DEBUG: Development path -> {url}")
        return url
    elif file_path.startswith('static/'):
        # Other static files
        url = f"/{quote(file_path)}"
        print(f"DEBUG: Static path -> {url}")
        return url
    else:
        # Assume it's a relative path in uploads
        url = f"/uploads/{quote(file_path)}"
        print(f"DEBUG: Relative path -> {url}")
        return url

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(expectations.router, prefix="/api")
app.include_router(matches.router, prefix="/api")


# Initialize database on startup (only if it doesn't exist)
import os
if not os.path.exists("theone_production.db"):
    print("🗄️ Creating new database...")
    create_tables()
else:
    print("🗄️ Using existing database...")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Simple dating app - upload photo, intro, expectations, find matches"""
    return templates.TemplateResponse("simple.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint with image serving status"""
    # Check if upload directory exists and is accessible
    upload_dir = settings.get_upload_dir()
    upload_status = {
        "upload_dir": upload_dir,
        "exists": os.path.exists(upload_dir),
        "writable": os.access(upload_dir, os.W_OK) if os.path.exists(upload_dir) else False
    }

    # Check subdirectories
    subdirs = {}
    for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
        subdir_path = os.path.join(upload_dir, subdir)
        subdirs[subdir] = {
            "exists": os.path.exists(subdir_path),
            "file_count": len(os.listdir(subdir_path)) if os.path.exists(subdir_path) else 0
        }

    return {
        "status": "healthy",
        "uploads": upload_status,
        "subdirectories": subdirs,
        "debug_mode": settings.debug
    }


@app.get("/profiles/{filename:path}")
async def redirect_profiles_to_uploads(filename: str):
    """Redirect /profiles/ requests to /uploads/ (fix for browser URL interpretation)"""
    print(f"DEBUG: Redirecting /profiles/{filename} to /uploads/{filename}")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/uploads/{filename}", status_code=301)


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard to monitor user registrations"""
    from app.db.database import SessionLocal
    from app.models.user import User, Profile, Expectation, Photo

    db = SessionLocal()

    try:
        # Get all users with their data
        users = db.query(User).all()

        user_data = []
        for user in users:
            # Get profile info
            profile_desc = ""
            photo_count = 0
            photo_urls = []

            if hasattr(user, 'profile') and user.profile:
                profile_desc = user.profile.description
                photo_count = len(user.profile.photos)
                # Generate proper photo URLs
                photo_urls = []
                for photo in user.profile.photos:
                    photo_url = get_photo_url(photo.file_path)
                    if photo_url:
                        photo_urls.append(photo_url)

                # Debug: print photo paths to help diagnose
                print(f"DEBUG: User {user.email} photos: {[photo.file_path for photo in user.profile.photos]}")
                print(f"DEBUG: Photo URLs: {photo_urls}")

            # Get expectations and ideal partner photos
            expectations_desc = ""
            ideal_partner_photos = []
            if hasattr(user, 'expectations') and user.expectations:
                expectations_desc = user.expectations.description
                # Get ideal partner photos
                for photo in user.expectations.ideal_partner_photos:
                    photo_url = get_photo_url(photo.file_path)
                    if photo_url:
                        ideal_partner_photos.append(photo_url)

            # Check completeness
            has_profile = bool(profile_desc)
            has_expectations = bool(expectations_desc)
            has_photo = photo_count > 0
            is_complete = has_profile and has_expectations and has_photo

            user_data.append({
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': user.is_active,
                'profile_description': profile_desc,
                'expectations_description': expectations_desc,
                'photo_count': photo_count,
                'photo_urls': photo_urls,
                'ideal_partner_photos': ideal_partner_photos,
                'ideal_partner_count': len(ideal_partner_photos),
                'has_profile': has_profile,
                'has_expectations': has_expectations,
                'has_photo': has_photo,
                'has_ideal_photos': len(ideal_partner_photos) > 0,
                'is_complete': is_complete
            })

        # Sort by creation date (newest first)
        user_data.sort(key=lambda x: x['created_at'], reverse=True)

        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "users": user_data,
            "total_users": len(user_data),
            "complete_profiles": sum(1 for u in user_data if u['is_complete'])
        })

    except Exception as e:
        return HTMLResponse(f"<h1>Admin Error</h1><p>{str(e)}</p>")

    finally:
        db.close()


@app.get("/admin/user/{user_id}", response_class=HTMLResponse)
async def view_user_detail(request: Request, user_id: int):
    """View detailed user profile"""
    from app.db.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return HTMLResponse("<h1>User not found</h1>")

        # Get all user data
        profile_data = None
        if hasattr(user, 'profile') and user.profile:
            # Generate proper photo URLs for user detail view
            photos = []
            for photo in user.profile.photos:
                photo_url = get_photo_url(photo.file_path)
                if photo_url:
                    photos.append({'path': photo.file_path, 'url': photo_url})

            profile_data = {
                'description': user.profile.description,
                'created_at': user.profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'photos': photos
            }

        expectations_data = None
        if hasattr(user, 'expectations') and user.expectations:
            # Get ideal partner photos
            ideal_partner_photos = []
            for photo in user.expectations.ideal_partner_photos:
                photo_url = get_photo_url(photo.file_path)
                if photo_url:
                    ideal_partner_photos.append({'path': photo.file_path, 'url': photo_url})

            expectations_data = {
                'description': user.expectations.description,
                'created_at': user.expectations.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'ideal_partner_photos': ideal_partner_photos
            }

        return templates.TemplateResponse("user_detail.html", {
            "request": request,
            "user": {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': user.is_active
            },
            "profile": profile_data,
            "expectations": expectations_data
        })

    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>")

    finally:
        db.close()


@app.get("/api/stats")
async def get_user_stats():
    """API endpoint for user statistics - useful for monitoring"""
    from app.db.database import SessionLocal
    from app.models.user import User, Profile, Expectation, Photo
    from datetime import datetime

    db = SessionLocal()

    try:
        total_users = db.query(User).count()

        # Count users with complete data
        users_with_profiles = db.query(User).filter(User.profile.has()).count()
        users_with_expectations = db.query(User).filter(User.expectations.has()).count()

        # Count photos
        total_photos = db.query(Photo).count()

        # Get recent users (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_users = db.query(User).filter(User.created_at >= yesterday).count()

        return {
            "total_users": total_users,
            "users_with_profiles": users_with_profiles,
            "users_with_expectations": users_with_expectations,
            "total_photos": total_photos,
            "recent_users_24h": recent_users,
            "completion_rate": round((users_with_profiles / total_users * 100) if total_users > 0 else 0, 1),
            "timestamp": datetime.now().isoformat(),
            "status": "healthy"
        }

    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }

    finally:
        db.close()


@app.post("/api/find-matches")
async def find_matches(
    email: str = Form(...),
    introduction: str = Form(...),
    expectations: str = Form(...),
    photo: UploadFile = File(None),
    ideal_partner_photos: List[UploadFile] = File(default=[])
):
    """Simple endpoint: upload photo + intro + expectations, get matches"""
    from app.db.database import SessionLocal
    from app.models.user import User, Profile, Expectation
    from app.services.ai_matching import ai_matching_service
    from passlib.context import CryptContext
    import uuid

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()

    try:
        # Create or get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create new user
            user = User(
                email=email,
                hashed_password=pwd_context.hash(str(uuid.uuid4())),  # Random password
                is_active=True
            )
            db.add(user)
            db.flush()

        # Handle photo upload
        photo_path = None
        if photo:
            import os
            # Use the configured upload directory
            upload_base = settings.get_upload_dir()
            profiles_dir = f"{upload_base}/profiles"
            os.makedirs(profiles_dir, exist_ok=True)
            photo_path = f"{profiles_dir}/{user.id}_{photo.filename}"
            with open(photo_path, "wb") as buffer:
                content = await photo.read()
                buffer.write(content)

        # Update or create profile
        if hasattr(user, 'profile') and user.profile:
            user.profile.description = introduction
        else:
            profile = Profile(user_id=user.id, description=introduction)
            db.add(profile)
            db.flush()

        # Add photo to profile if uploaded
        if photo_path and hasattr(user, 'profile') and user.profile:
            from app.models.user import Photo
            # Remove old photos
            for old_photo in user.profile.photos:
                db.delete(old_photo)
            # Add new photo
            new_photo = Photo(profile_id=user.profile.id, file_path=photo_path, order_index=0)
            db.add(new_photo)

        # Update or create expectations
        if hasattr(user, 'expectations') and user.expectations:
            user.expectations.description = expectations
        else:
            expectation = Expectation(user_id=user.id, description=expectations)
            db.add(expectation)
            db.flush()

        # Handle ideal partner photos
        if ideal_partner_photos and hasattr(user, 'expectations') and user.expectations:
            from app.models.user import IdealPartnerPhoto
            import os

            # Create directory for ideal partner photos
            upload_base = settings.get_upload_dir()
            ideal_partners_dir = f"{upload_base}/ideal_partners"
            os.makedirs(ideal_partners_dir, exist_ok=True)

            # Remove old ideal partner photos
            for old_photo in user.expectations.ideal_partner_photos:
                db.delete(old_photo)

            # Add new ideal partner photos
            for i, photo in enumerate(ideal_partner_photos):
                if photo.filename:  # Check if file was actually uploaded
                    photo_path = f"{ideal_partners_dir}/{user.id}_{i}_{photo.filename}"
                    with open(photo_path, "wb") as buffer:
                        content = await photo.read()
                        buffer.write(content)

                    new_ideal_photo = IdealPartnerPhoto(
                        expectation_id=user.expectations.id,
                        file_path=photo_path,
                        order_index=i
                    )
                    db.add(new_ideal_photo)

        db.commit()

        # Find matches
        all_users = db.query(User).filter(User.id != user.id).all()
        complete_users = [u for u in all_users if hasattr(u, 'profile') and u.profile and hasattr(u, 'expectations') and u.expectations]

        if not complete_users:
            return []

        # Get AI matches using NEW BIDIRECTIONAL ALGORITHM
        matches = []
        for potential_match in complete_users:
            if potential_match.id == user.id:
                continue  # Skip self

            # Calculate bidirectional compatibility
            compatibility = await ai_matching_service.calculate_bidirectional_compatibility(
                user, potential_match, include_reasoning=False
            )

            # Only include if mutual compatibility is high (>= 0.7 = 70%)
            if compatibility["mutual_compatibility"] >= 0.7:
                matches.append({
                    "user_id": potential_match.id,
                    "compatibility_score": compatibility["mutual_compatibility"],
                    "user_a_score": compatibility["user_a_score"],
                    "user_b_score": compatibility["user_b_score"]
                })

        # Sort by compatibility score (highest first)
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        high_compatibility_matches = matches  # All matches are already high compatibility

        # Format response with photos
        result = []
        for match in high_compatibility_matches[:5]:  # Max 5 high-quality matches
            matched_user = next(u for u in complete_users if u.id == match["user_id"])

            # Get user's photo
            photo_url = None
            if hasattr(matched_user, 'profile') and matched_user.profile and matched_user.profile.photos:
                photo_url = get_photo_url(matched_user.profile.photos[0].file_path)

            result.append({
                "email": matched_user.email,
                "introduction": matched_user.profile.description,
                "expectations": matched_user.expectations.description,
                "photo_url": photo_url,
                "is_high_match": True  # All matches are high compatibility
            })

        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")
    finally:
        db.close()


@app.get("/api/debug/file-paths")
async def debug_file_paths():
    """Debug endpoint to check file paths and directories"""
    import os
    from app.core.config import settings

    upload_dir = settings.get_upload_dir()

    debug_info = {
        "upload_dir": upload_dir,
        "upload_dir_exists": os.path.exists(upload_dir),
        "static_dir_exists": os.path.exists("static"),
        "current_working_directory": os.getcwd(),
        "environment_variables": {
            "DATABASE_PATH": os.getenv("DATABASE_PATH"),
            "UPLOADS_PATH": os.getenv("UPLOADS_PATH"),
        },
        "directory_contents": {}
    }

    # Check directory contents
    for dir_name in [upload_dir, "static", "/app/data/uploads"]:
        if os.path.exists(dir_name):
            try:
                contents = os.listdir(dir_name)
                debug_info["directory_contents"][dir_name] = contents
            except Exception as e:
                debug_info["directory_contents"][dir_name] = f"Error: {str(e)}"
        else:
            debug_info["directory_contents"][dir_name] = "Directory does not exist"

    return debug_info


@app.post("/api/fix-image-paths")
async def fix_image_paths():
    """Fix image paths in database for production environment"""
    from app.db.database import SessionLocal
    from app.models.user import Photo, IdealPartnerPhoto

    db = SessionLocal()
    try:
        fixed_count = 0
        upload_dir = settings.get_upload_dir()

        # Fix profile photos
        photos = db.query(Photo).all()
        for photo in photos:
            old_path = photo.file_path

            # Extract filename
            if '/' in old_path:
                filename = old_path.split('/')[-1]
            else:
                filename = old_path

            # Generate new production path
            new_path = os.path.join(upload_dir, 'profiles', filename)

            if old_path != new_path:
                photo.file_path = new_path
                fixed_count += 1

        # Fix ideal partner photos
        ideal_photos = db.query(IdealPartnerPhoto).all()
        for photo in ideal_photos:
            old_path = photo.file_path

            # Extract filename
            if '/' in old_path:
                filename = old_path.split('/')[-1]
            else:
                filename = old_path

            # Generate new production path
            new_path = os.path.join(upload_dir, 'ideal_partners', filename)

            if old_path != new_path:
                photo.file_path = new_path
                fixed_count += 1

        db.commit()

        return {
            "status": "success",
            "fixed_count": fixed_count,
            "upload_dir": upload_dir,
            "message": f"Fixed {fixed_count} file paths"
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@app.post("/api/copy-files-to-production")
async def copy_files_to_production():
    """Copy files from development location to production location"""
    import shutil

    source_base = "static/uploads"
    target_base = "/app/data/uploads"

    if not os.path.exists(source_base):
        return {"status": "error", "message": "Source directory not found"}

    if not os.path.exists(target_base):
        return {"status": "error", "message": "Target directory not found"}

    copied_count = 0

    try:
        # Copy files from each subdirectory
        for subdir in ['profiles', 'ideal_partners', 'expectations', 'audio']:
            source_dir = os.path.join(source_base, subdir)
            target_dir = os.path.join(target_base, subdir)

            if os.path.exists(source_dir):
                os.makedirs(target_dir, exist_ok=True)
                for filename in os.listdir(source_dir):
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_dir, filename)

                    if os.path.isfile(source_file) and not os.path.exists(target_file):
                        shutil.copy2(source_file, target_file)
                        copied_count += 1

        return {
            "status": "success",
            "copied_count": copied_count,
            "message": f"Copied {copied_count} files to production location"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/backup-user-data")
async def backup_user_data():
    """Backup all user data (database + files) for safekeeping"""
    import subprocess
    from datetime import datetime

    try:
        # Run the backup script
        result = subprocess.run(
            ["python3", "backup_user_data.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            # Check what was created
            backup_info = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "backup_output": result.stdout,
                "files_created": []
            }

            # List backup files
            if os.path.exists("backups"):
                for filename in os.listdir("backups"):
                    if filename.startswith("database_backup_") or filename.startswith("files_"):
                        backup_info["files_created"].append(filename)

            return backup_info
        else:
            return {
                "status": "error",
                "error": result.stderr,
                "output": result.stdout
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Backup process timed out"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/algorithm-version")
async def get_algorithm_version():
    """Check which algorithm version is running"""
    return {
        "algorithm": "bidirectional_compatibility_v2",
        "description": "Using new bidirectional matching with mutual compatibility scoring",
        "threshold": 0.7,
        "timestamp": "2025-01-28"
    }


@app.post("/api/debug-match")
async def debug_specific_match():
    """Debug why two specific users aren't matching"""
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.services.ai_matching import ai_matching_service

    db = SessionLocal()
    try:
        # Get the two users from the screenshot
        user1 = db.query(User).filter(User.email == "a329571438@gmail.com").first()
        user2 = db.query(User).filter(User.email == "renzhiy1@msu.edu").first()

        if not user1 or not user2:
            return {"error": "One or both users not found"}

        if not (user1.profile and user1.expectations and user2.profile and user2.expectations):
            return {"error": "Users missing profile or expectations data"}

        # Test the new bidirectional matching
        compatibility = await ai_matching_service.calculate_bidirectional_compatibility(
            user1, user2, include_reasoning=True
        )

        # Also test individual scores
        user1_scores_user2 = await ai_matching_service.calculate_user_score_for_target(
            user1.profile.description,
            user1.expectations.description,
            [photo.file_path for photo in user1.expectations.ideal_partner_photos],
            user2.profile.description,
            [photo.file_path for photo in user2.profile.photos]
        )

        user2_scores_user1 = await ai_matching_service.calculate_user_score_for_target(
            user2.profile.description,
            user2.expectations.description,
            [photo.file_path for photo in user2.expectations.ideal_partner_photos],
            user1.profile.description,
            [photo.file_path for photo in user1.profile.photos]
        )

        return {
            "user1_email": user1.email,
            "user1_profile": user1.profile.description,
            "user1_expectations": user1.expectations.description,
            "user1_photos": len(user1.profile.photos),
            "user1_ideal_photos": len(user1.expectations.ideal_partner_photos),

            "user2_email": user2.email,
            "user2_profile": user2.profile.description,
            "user2_expectations": user2.expectations.description,
            "user2_photos": len(user2.profile.photos),
            "user2_ideal_photos": len(user2.expectations.ideal_partner_photos),

            "bidirectional_compatibility": compatibility,
            "user1_scores_user2": user1_scores_user2,
            "user2_scores_user1": user2_scores_user1,

            "should_match": compatibility["mutual_compatibility"] >= 0.7,
            "match_threshold": 0.7
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@app.get("/api/get-user/{email}")
async def get_user_data(email: str):
    """Get existing user data for editing"""
    from app.db.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"exists": False}

        # Get user's current data
        photo_url = None
        if hasattr(user, 'profile') and user.profile and user.profile.photos:
            photo_url = get_photo_url(user.profile.photos[0].file_path)

        return {
            "exists": True,
            "introduction": user.profile.description if hasattr(user, 'profile') and user.profile else "",
            "expectations": user.expectations.description if hasattr(user, 'expectations') and user.expectations else "",
            "photo_url": photo_url
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
