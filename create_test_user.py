#!/usr/bin/env python3
"""
Create a test user to test the simple algorithm
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo
from passlib.context import CryptContext
import uuid

def create_test_user():
    """Create a test user for matching"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists")
            return
        
        # Create test user
        user = User(
            email="test@example.com",
            hashed_password=pwd_context.hash(str(uuid.uuid4())),
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            description="I'm a 25-year-old software engineer who loves hiking, reading, and trying new restaurants. I'm looking for someone who shares my passion for adventure and intellectual conversations."
        )
        db.add(profile)
        db.flush()
        
        # Create expectations
        expectation = Expectation(
            user_id=user.id,
            description="Looking for someone between 22-30 years old who is kind, intelligent, and has a good sense of humor. I value honesty and communication in relationships."
        )
        db.add(expectation)
        db.flush()
        
        db.commit()
        print(f"Created test user: {user.email} (ID: {user.id})")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
