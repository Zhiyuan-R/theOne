"""
Expectations/preferences API endpoints
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, Expectation, ExampleImage, IdealPartnerPhoto
from app.schemas.user import ExpectationCreate, ExpectationResponse, ExpectationUpdate

router = APIRouter(prefix="/expectations", tags=["expectations"])


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


@router.post("/", response_model=ExpectationResponse)
async def create_expectations(
    description: str = Form(...),
    example_images: List[UploadFile] = File(default=[]),
    ideal_partner_photos: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create user expectations with example images and ideal partner photos"""
    # Check if expectations already exist
    existing_expectations = db.query(Expectation).filter(Expectation.user_id == current_user.id).first()
    if existing_expectations:
        raise HTTPException(status_code=400, detail="Expectations already exist")

    # Validate example images (optional)
    if example_images and len(example_images) > 5:
        raise HTTPException(status_code=400, detail="Must upload at most 5 example images")

    # Validate ideal partner photos (optional)
    if ideal_partner_photos and len(ideal_partner_photos) > 5:
        raise HTTPException(status_code=400, detail="Must upload at most 5 ideal partner photos")

    # Validate all image formats
    all_images = (example_images or []) + (ideal_partner_photos or [])
    for image in all_images:
        if image.filename and not any(image.filename.lower().endswith(ext) for ext in settings.allowed_image_extensions):
            raise HTTPException(status_code=400, detail=f"Invalid image format: {image.filename}")

    # Create expectations
    db_expectation = Expectation(
        user_id=current_user.id,
        description=description
    )

    db.add(db_expectation)
    db.commit()
    db.refresh(db_expectation)

    # Save example images
    if example_images:
        for image in example_images:
            if image.filename:  # Check if file was actually uploaded
                image_path = save_uploaded_file(image, "expectations")
                db_image = ExampleImage(
                    expectation_id=db_expectation.id,
                    file_path=image_path
                )
                db.add(db_image)

    # Save ideal partner photos
    if ideal_partner_photos:
        for i, photo in enumerate(ideal_partner_photos):
            if photo.filename:  # Check if file was actually uploaded
                photo_path = save_uploaded_file(photo, "ideal_partners")
                db_photo = IdealPartnerPhoto(
                    expectation_id=db_expectation.id,
                    file_path=photo_path,
                    order_index=i
                )
                db.add(db_photo)

    db.commit()
    db.refresh(db_expectation)

    return db_expectation


@router.get("/me", response_model=ExpectationResponse)
def get_my_expectations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's expectations"""
    expectations = db.query(Expectation).filter(Expectation.user_id == current_user.id).first()
    if not expectations:
        raise HTTPException(status_code=404, detail="Expectations not found")

    return expectations


@router.put("/me", response_model=ExpectationResponse)
def update_my_expectations(
    expectation_update: ExpectationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's expectations"""
    expectations = db.query(Expectation).filter(Expectation.user_id == current_user.id).first()
    if not expectations:
        raise HTTPException(status_code=404, detail="Expectations not found")

    if expectation_update.description is not None:
        expectations.description = expectation_update.description

    db.commit()
    db.refresh(expectations)

    return expectations
