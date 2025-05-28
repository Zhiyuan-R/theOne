"""
Pydantic schemas for user-related API requests and responses
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Profile schemas
class PhotoResponse(BaseModel):
    id: int
    file_path: str
    order_index: int
    
    class Config:
        from_attributes = True


class ProfileCreate(BaseModel):
    description: str


class ProfileUpdate(BaseModel):
    description: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    description: str
    audio_clip_path: Optional[str] = None
    photos: List[PhotoResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Expectation schemas
class ExampleImageResponse(BaseModel):
    id: int
    file_path: str
    
    class Config:
        from_attributes = True


class ExpectationCreate(BaseModel):
    description: str


class ExpectationUpdate(BaseModel):
    description: Optional[str] = None


class ExpectationResponse(BaseModel):
    id: int
    description: str
    example_images: List[ExampleImageResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Match schemas
class MatchResponse(BaseModel):
    id: int
    matched_user_id: int
    compatibility_score: float
    text_similarity_score: float
    visual_similarity_score: float
    is_viewed: bool
    created_at: datetime
    matched_user_profile: Optional[ProfileResponse] = None
    
    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
