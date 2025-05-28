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

    # Handle different path formats and ensure absolute URLs
    if file_path.startswith('/app/data/uploads/'):
        # Production path - use /uploads/ mount
        relative_path = file_path.replace('/app/data/uploads/', '')
        # Use double slash to ensure it's treated as absolute
        return f"//localhost:8000/uploads/{quote(relative_path)}" if settings.debug else f"/uploads/{quote(relative_path)}"
    elif file_path.startswith('static/uploads/'):
        # Development path - use /uploads/ mount
        relative_path = file_path.replace('static/uploads/', '')
        # Use double slash to ensure it's treated as absolute
        return f"//localhost:8000/uploads/{quote(relative_path)}" if settings.debug else f"/uploads/{quote(relative_path)}"
    elif file_path.startswith('static/'):
        # Other static files
        return f"//localhost:8000/{quote(file_path)}" if settings.debug else f"/{quote(file_path)}"
    else:
        # Assume it's a relative path in uploads
        return f"//localhost:8000/uploads/{quote(file_path)}" if settings.debug else f"/uploads/{quote(file_path)}"

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
    """Health check endpoint"""
    return {"status": "healthy"}


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

        # Get AI matches - get more to filter for high compatibility
        matches = await ai_matching_service.find_daily_matches(
            user, complete_users, limit=len(complete_users), include_reasoning=False
        )

        # STRICT MATCHING: Only show very high compatibility (>= 0.7 = 70%)
        high_compatibility_matches = [m for m in matches if m["compatibility_score"] >= 0.7]

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
