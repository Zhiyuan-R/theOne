"""
User and profile related database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    expectations = relationship("Expectation", back_populates="user", uselist=False)
    sent_matches = relationship("Match", foreign_keys="Match.user_id", back_populates="user")
    received_matches = relationship("Match", foreign_keys="Match.matched_user_id", back_populates="matched_user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    audio_clip_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")
    photos = relationship("Photo", back_populates="profile", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    file_path = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("Profile", back_populates="photos")


class Expectation(Base):
    __tablename__ = "expectations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="expectations")
    example_images = relationship("ExampleImage", back_populates="expectation", cascade="all, delete-orphan")


class ExampleImage(Base):
    __tablename__ = "example_images"

    id = Column(Integer, primary_key=True, index=True)
    expectation_id = Column(Integer, ForeignKey("expectations.id"), nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    expectation = relationship("Expectation", back_populates="example_images")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    matched_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    text_similarity_score = Column(Float, nullable=False)
    visual_similarity_score = Column(Float, nullable=False)

    # Enhanced LLM-based compatibility scores
    basic_text_similarity = Column(Float, nullable=True)
    llm_text_score = Column(Float, nullable=True)
    personality_score = Column(Float, nullable=True)
    lifestyle_score = Column(Float, nullable=True)
    emotional_score = Column(Float, nullable=True)
    longterm_score = Column(Float, nullable=True)

    # Match metadata
    is_viewed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="sent_matches")
    matched_user = relationship("User", foreign_keys=[matched_user_id], back_populates="received_matches")
