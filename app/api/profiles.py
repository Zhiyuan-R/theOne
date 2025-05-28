"""
Profile management API endpoints
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, Profile, Photo
from app.schemas.user import ProfileCreate, ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def save_uploaded_file(file: UploadFile, subfolder: str) -> str:
    """Save uploaded file and return the file path"""
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create full path
    file_path = os.path.join(settings.upload_dir, subfolder, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return file_path


@router.post("/", response_model=ProfileResponse)
async def create_profile(
    description: str = Form(...),
    photos: List[UploadFile] = File(...),
    audio_clip: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create user profile with photos and optional audio clip"""
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    # Validate photos
    if len(photos) < 1 or len(photos) > 5:
        raise HTTPException(status_code=400, detail="Must upload 1-5 photos")
    
    for photo in photos:
        if not any(photo.filename.lower().endswith(ext) for ext in settings.allowed_image_extensions):
            raise HTTPException(status_code=400, detail=f"Invalid image format: {photo.filename}")
    
    # Create profile
    db_profile = Profile(
        user_id=current_user.id,
        description=description
    )
    
    # Handle audio clip if provided
    if audio_clip and audio_clip.filename:
        if not any(audio_clip.filename.lower().endswith(ext) for ext in settings.allowed_audio_extensions):
            raise HTTPException(status_code=400, detail=f"Invalid audio format: {audio_clip.filename}")
        
        audio_path = save_uploaded_file(audio_clip, "audio")
        db_profile.audio_clip_path = audio_path
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Save photos
    for i, photo in enumerate(photos):
        photo_path = save_uploaded_file(photo, "profiles")
        db_photo = Photo(
            profile_id=db_profile.id,
            file_path=photo_path,
            order_index=i
        )
        db.add(db_photo)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile_update.description is not None:
        profile.description = profile_update.description
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/{user_id}", response_model=ProfileResponse)
def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get another user's profile"""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile
