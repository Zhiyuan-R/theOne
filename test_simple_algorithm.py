#!/usr/bin/env python3
"""
Test the new simple algorithm
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User
from app.services.ai_matching import ai_matching_service

async def test_simple_algorithm():
    """Test the simple algorithm with existing users"""
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        complete_users = [u for u in users if hasattr(u, 'profile') and u.profile and hasattr(u, 'expectations') and u.expectations]
        
        print(f"Found {len(complete_users)} complete users")
        
        if len(complete_users) < 2:
            print("Need at least 2 complete users to test matching")
            return
        
        # Test with first two users
        user1 = complete_users[0]
        user2 = complete_users[1]
        
        print(f"\nTesting compatibility between:")
        print(f"User 1: {user1.email}")
        print(f"  Profile: {user1.profile.description[:100]}...")
        print(f"  Expectations: {user1.expectations.description[:100]}...")
        
        print(f"\nUser 2: {user2.email}")
        print(f"  Profile: {user2.profile.description[:100]}...")
        print(f"  Expectations: {user2.expectations.description[:100]}...")
        
        # Test simple algorithm
        print(f"\n{'='*50}")
        print("TESTING SIMPLE ALGORITHM")
        print(f"{'='*50}")
        
        compatibility = await ai_matching_service.calculate_simple_compatibility(
            user1, user2, include_reasoning=True
        )
        
        print(f"Simple compatibility score: {compatibility['overall_score']:.3f}")
        print(f"Reasoning: {compatibility.get('reasoning', 'No reasoning')}")
        
        # Test find_daily_matches
        print(f"\n{'='*50}")
        print("TESTING FIND_DAILY_MATCHES")
        print(f"{'='*50}")
        
        matches = await ai_matching_service.find_daily_matches(
            user1, complete_users, limit=5, include_reasoning=False
        )
        
        print(f"Found {len(matches)} matches for {user1.email}:")
        for i, match in enumerate(matches, 1):
            matched_user = next(u for u in complete_users if u.id == match["user_id"])
            print(f"{i}. {matched_user.email} - Score: {match['compatibility_score']:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_simple_algorithm())
