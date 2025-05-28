#!/usr/bin/env python3
"""
Test the new algorithm with fallback
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User
from app.services.ai_matching import ai_matching_service

async def test_new_algorithm():
    """Test the new algorithm"""
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
        print(f"User 2: {user2.email}")
        
        # Test new algorithm with timeout
        print(f"\n{'='*50}")
        print("TESTING NEW ALGORITHM")
        print(f"{'='*50}")
        
        try:
            compatibility = await asyncio.wait_for(
                ai_matching_service.calculate_simple_compatibility(
                    user1, user2, include_reasoning=True
                ),
                timeout=10.0  # 10 second timeout
            )
            
            print(f"Compatibility score: {compatibility['overall_score']:.3f}")
            print(f"Reasoning: {compatibility.get('reasoning', 'No reasoning')}")
            
        except asyncio.TimeoutError:
            print("Algorithm timed out - likely API issue")
        except Exception as e:
            print(f"Error in algorithm: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_new_algorithm())
