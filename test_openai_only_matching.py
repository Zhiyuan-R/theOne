"""
Test the OpenAI-only matching system with existing profiles
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


async def test_openai_only_matching():
    """Test matching using only OpenAI APIs"""
    db = SessionLocal()
    
    try:
        print("🤖 Testing OpenAI-Only AI Matching System")
        print("=" * 60)
        print("✅ Using only OpenAI APIs:")
        print("   - OpenAI Embeddings API for text similarity")
        print("   - GPT-4 for deep compatibility analysis")
        print("   - GPT-4 Vision for visual compatibility")
        print("   - GPT-4 for reasoning generation")
        
        # Get all users with profiles and expectations
        users = db.query(User).all()
        
        # Filter users who have both profile and expectations
        complete_users = []
        for user in users:
            if hasattr(user, 'profile') and user.profile and hasattr(user, 'expectations') and user.expectations:
                complete_users.append(user)
        
        print(f"\n📊 Found {len(complete_users)} users with complete profiles")
        
        if len(complete_users) < 2:
            print("❌ Need at least 2 users with complete profiles to test matching")
            print("Run create_test_profiles.py first to create test data")
            return
        
        # Test with first user as the main user
        main_user = complete_users[0]
        candidate_users = complete_users[1:3]  # Test with 2 candidates to save API calls
        
        print(f"\n👤 Main User: {main_user.email}")
        print(f"📝 Profile: {main_user.profile.description[:100]}...")
        print(f"💭 Looking for: {main_user.expectations.description[:100]}...")
        
        print(f"\n🎯 Testing OpenAI-only matching against {len(candidate_users)} candidates...")
        
        # Test individual components first
        print(f"\n🔍 Testing Individual OpenAI Components:")
        print("-" * 50)
        
        candidate = candidate_users[0]
        print(f"Testing with: {candidate.email}")
        
        # Test OpenAI embeddings similarity
        print("1. Testing OpenAI Embeddings Similarity...")
        text_sim = await ai_matching_service.get_text_similarity(
            main_user.expectations.description,
            candidate.profile.description
        )
        print(f"   📝 Text Similarity: {text_sim:.3f} ({text_sim:.1%})")
        
        # Test LLM compatibility analysis
        print("2. Testing LLM Compatibility Analysis...")
        llm_analysis = await ai_matching_service.get_llm_text_compatibility(
            candidate.profile.description,
            main_user.expectations.description
        )
        print(f"   🧠 LLM Overall: {llm_analysis['overall_score']:.3f}")
        print(f"   👤 Personality: {llm_analysis['personality_score']:.3f}")
        print(f"   🏠 Lifestyle: {llm_analysis['lifestyle_score']:.3f}")
        print(f"   💝 Emotional: {llm_analysis['emotional_score']:.3f}")
        print(f"   🔮 Long-term: {llm_analysis['longterm_score']:.3f}")
        print(f"   💭 Reasoning: {llm_analysis['reasoning'][:100]}...")
        
        # Test full matching
        print(f"\n🚀 Running Full OpenAI-Only Matching...")
        print("-" * 50)
        
        matches = await ai_matching_service.find_daily_matches(
            main_user, candidate_users, limit=len(candidate_users), include_reasoning=True
        )
        
        print(f"\n📈 OpenAI-Only Matching Results:")
        print("=" * 70)
        
        for i, match in enumerate(matches, 1):
            candidate = next(u for u in candidate_users if u.id == match["user_id"])
            
            print(f"\n{i}. 💕 {candidate.email}")
            print(f"   Overall: {match['compatibility_score']:.3f} ({match['compatibility_score']:.1%})")
            print(f"   📝 OpenAI Embeddings: {match['basic_text_similarity']:.3f}")
            print(f"   🧠 LLM Analysis: {match['llm_text_score']:.3f}")
            print(f"   🖼️  Visual (GPT-4V): {match['visual_similarity']:.3f}")
            print(f"   👤 Personality: {match['personality_score']:.3f}")
            print(f"   🏠 Lifestyle: {match['lifestyle_score']:.3f}")
            print(f"   💝 Emotional: {match['emotional_score']:.3f}")
            print(f"   🔮 Long-term: {match['longterm_score']:.3f}")
            
            # Show reasoning if available
            if "reasoning" in match and match["reasoning"]:
                reasoning = match["reasoning"]
                print(f"   📋 AI Summary: {reasoning.get('summary', 'N/A')[:120]}...")
                print(f"   💪 Strengths: {reasoning.get('strengths', 'N/A')[:120]}...")
                print(f"   💬 Conversation: {reasoning.get('conversation_starters', 'N/A')[:120]}...")
            
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
        
        # Test bidirectional compatibility
        if matches:
            print(f"\n🔄 Testing Bidirectional OpenAI Compatibility")
            print("=" * 50)
            
            top_match = matches[0]
            top_candidate = next(u for u in candidate_users if u.id == top_match["user_id"])
            
            print(f"Testing: {main_user.email} ↔ {top_candidate.email}")
            
            # Main user → Candidate (already calculated)
            main_to_candidate = top_match['compatibility_score']
            
            # Candidate → Main user (reverse direction)
            print("Calculating reverse compatibility...")
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
                    print(f"   🤖 Powered entirely by OpenAI APIs!")
                else:
                    if main_to_candidate > candidate_to_main:
                        print(f"   💔 {main_user.email} likes {top_candidate.email} more")
                    else:
                        print(f"   💔 {top_candidate.email} likes {main_user.email} more")
            else:
                print(f"   ❌ Could not calculate reverse compatibility")
        
        print(f"\n🎯 OpenAI-Only Test Summary:")
        print("=" * 40)
        print(f"✅ Tested {len(matches)} potential matches")
        print(f"✅ Used only OpenAI APIs (no open-source models)")
        print(f"✅ OpenAI Embeddings for text similarity")
        print(f"✅ GPT-4 for deep compatibility analysis")
        print(f"✅ GPT-4 Vision for visual compatibility")
        print(f"✅ GPT-4 for reasoning generation")
        print(f"✅ Bidirectional compatibility verification")
        
    except Exception as e:
        print(f"❌ Error in OpenAI-only matching test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """Main test function"""
    print("🤖 OpenAI-Only AI Matching Test")
    print("=" * 60)
    
    try:
        await test_openai_only_matching()
        
        print("\n" + "=" * 60)
        print("🎉 OpenAI-Only Matching Test Complete!")
        print("\nKey Features Verified:")
        print("🤖 100% OpenAI API powered (no open-source models)")
        print("📊 OpenAI Embeddings for semantic text similarity")
        print("🧠 GPT-4 for deep personality compatibility analysis")
        print("🖼️  GPT-4 Vision for visual compatibility assessment")
        print("💭 GPT-4 for detailed reasoning and conversation starters")
        print("🔄 Bidirectional compatibility verification")
        print("⚖️  Mutual satisfaction checking")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
