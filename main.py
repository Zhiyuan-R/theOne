"""
Main FastAPI application for theOne dating app
"""
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(expectations.router, prefix="/api")
app.include_router(matches.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_tables()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Simple dating app - upload photo, intro, expectations, find matches"""
    return templates.TemplateResponse("simple.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/find-matches")
async def find_matches(
    email: str = Form(...),
    introduction: str = Form(...),
    expectations: str = Form(...),
    photo: UploadFile = File(None)
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
            os.makedirs("static/uploads/profiles", exist_ok=True)
            photo_path = f"static/uploads/profiles/{user.id}_{photo.filename}"
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
                photo_url = f"/{matched_user.profile.photos[0].file_path}"

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
            photo_url = f"/{user.profile.photos[0].file_path}"

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
