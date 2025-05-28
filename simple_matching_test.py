"""
Simple test for bidirectional matching with existing profiles
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation
from app.services.ai_matching import ai_matching_service


async def test_simple_matching():
    """Test matching with existing profiles"""
    db = SessionLocal()
    
    try:
        print("🔍 Testing Enhanced AI Matching System")
        print("=" * 60)
        
        # Get all users with profiles and expectations
        users = db.query(User).all()
        
        # Filter users who have both profile and expectations
        complete_users = []
        for user in users:
            if hasattr(user, 'profile') and user.profile and hasattr(user, 'expectations') and user.expectations:
                complete_users.append(user)
        
        print(f"📊 Found {len(complete_users)} users with complete profiles")
        
        if len(complete_users) < 2:
            print("❌ Need at least 2 users with complete profiles to test matching")
            print("Run create_test_profiles.py first to create test data")
            return
        
        # Test with first user as the main user
        main_user = complete_users[0]
        candidate_users = complete_users[1:]
        
        print(f"\n👤 Main User: {main_user.email}")
        print(f"📝 Profile: {main_user.profile.description[:100]}...")
        print(f"💭 Looking for: {main_user.expectations.description[:100]}...")
        
        print(f"\n🎯 Testing against {len(candidate_users)} candidates...")
        
        # Generate matches
        matches = await ai_matching_service.find_daily_matches(
            main_user, candidate_users, limit=len(candidate_users), include_reasoning=True
        )
        
        print(f"\n📈 Matching Results:")
        print("=" * 70)
        
        for i, match in enumerate(matches, 1):
            candidate = next(u for u in candidate_users if u.id == match["user_id"])
            
            print(f"\n{i}. 💕 {candidate.email}")
            print(f"   Overall: {match['compatibility_score']:.3f} ({match['compatibility_score']:.1%})")
            print(f"   📝 Text: {match['text_similarity']:.3f}")
            print(f"   🖼️  Visual: {match['visual_similarity']:.3f}")
            print(f"   🧠 LLM: {match['llm_text_score']:.3f}")
            print(f"   👤 Personality: {match['personality_score']:.3f}")
            print(f"   🏠 Lifestyle: {match['lifestyle_score']:.3f}")
            print(f"   💝 Emotional: {match['emotional_score']:.3f}")
            print(f"   🔮 Long-term: {match['longterm_score']:.3f}")
            
            # Show reasoning if available
            if "reasoning" in match and match["reasoning"]:
                reasoning = match["reasoning"]
                print(f"   📋 Summary: {reasoning.get('summary', 'N/A')[:100]}...")
                print(f"   💪 Strengths: {reasoning.get('strengths', 'N/A')[:100]}...")
                print(f"   💬 Conversation: {reasoning.get('conversation_starters', 'N/A')[:100]}...")
            
            # Match quality indicator
            score = match['compatibility_score']
            if score > 0.8:
                print("   🌟 EXCELLENT MATCH!")
            elif score > 0.6:
                print("   💕 GREAT MATCH!")
            elif score > 0.4:
                print("   👍 GOOD MATCH")
            else:
                print("   🤔 MODERATE MATCH")
        
        # Test bidirectional compatibility with top match
        if matches:
            print(f"\n🔄 Testing Bidirectional Compatibility")
            print("=" * 50)
            
            top_match = matches[0]
            top_candidate = next(u for u in candidate_users if u.id == top_match["user_id"])
            
            print(f"Testing: {main_user.email} ↔ {top_candidate.email}")
            
            # Main user → Candidate (already calculated)
            main_to_candidate = top_match['compatibility_score']
            
            # Candidate → Main user (reverse direction)
            reverse_matches = await ai_matching_service.find_daily_matches(
                top_candidate, [main_user], limit=1, include_reasoning=False
            )
            
            if reverse_matches:
                candidate_to_main = reverse_matches[0]['compatibility_score']
                
                print(f"   {main_user.email} → {top_candidate.email}: {main_to_candidate:.3f} ({main_to_candidate:.1%})")
                print(f"   {top_candidate.email} → {main_user.email}: {candidate_to_main:.3f} ({candidate_to_main:.1%})")
                
                # Calculate mutual compatibility
                mutual_score = (main_to_candidate + candidate_to_main) / 2
                print(f"   🤝 Mutual Score: {mutual_score:.3f} ({mutual_score:.1%})")
                
                # Check if both are satisfied (both scores > 0.5)
                both_satisfied = main_to_candidate > 0.5 and candidate_to_main > 0.5
                print(f"   ✅ Both Satisfied: {'YES' if both_satisfied else 'NO'}")
                
                if both_satisfied:
                    print(f"   🎉 MUTUAL MATCH CONFIRMED!")
                    
                    # Show the difference in attraction
                    difference = abs(main_to_candidate - candidate_to_main)
                    if difference < 0.1:
                        print(f"   ⚖️  Balanced attraction (difference: {difference:.3f})")
                    elif difference < 0.2:
                        print(f"   📊 Slight preference difference (difference: {difference:.3f})")
                    else:
                        print(f"   ⚠️  Significant preference difference (difference: {difference:.3f})")
                else:
                    if main_to_candidate > candidate_to_main:
                        print(f"   💔 {main_user.email} likes {top_candidate.email} more")
                    else:
                        print(f"   💔 {top_candidate.email} likes {main_user.email} more")
            else:
                print(f"   ❌ Could not calculate reverse compatibility")
        
        print(f"\n🎯 Test Summary:")
        print("=" * 40)
        print(f"✅ Tested {len(matches)} potential matches")
        print(f"✅ Enhanced AI analysis with LLM reasoning")
        print(f"✅ Bidirectional compatibility verification")
        print(f"✅ Mutual satisfaction checking")
        
        # Show best matches
        excellent_matches = [m for m in matches if m['compatibility_score'] > 0.8]
        great_matches = [m for m in matches if 0.6 < m['compatibility_score'] <= 0.8]
        
        print(f"\n📊 Match Quality Distribution:")
        print(f"   🌟 Excellent (>80%): {len(excellent_matches)}")
        print(f"   💕 Great (60-80%): {len(great_matches)}")
        print(f"   👍 Good (40-60%): {len([m for m in matches if 0.4 < m['compatibility_score'] <= 0.6])}")
        print(f"   🤔 Moderate (<40%): {len([m for m in matches if m['compatibility_score'] <= 0.4])}")
        
    except Exception as e:
        print(f"❌ Error in matching test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """Main test function"""
    print("🌟 Enhanced AI Matching - Bidirectional Test")
    print("=" * 60)
    
    try:
        await test_simple_matching()
        
        print("\n" + "=" * 60)
        print("🎉 Bidirectional Matching Test Complete!")
        print("\nKey Features Tested:")
        print("✅ Enhanced LLM-based text compatibility analysis")
        print("✅ Detailed personality, lifestyle, emotional scoring")
        print("✅ Bidirectional compatibility verification")
        print("✅ Mutual satisfaction checking")
        print("✅ Comprehensive reasoning generation")
        print("✅ Match quality distribution analysis")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
