"""
Test script for enhanced AI matching with LLM-based text analysis and reasoning
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_matching import AIMatchingService
from app.core.config import settings


async def test_llm_text_compatibility():
    """Test the new LLM-based text compatibility analysis"""
    print("🧠 Enhanced LLM Text Compatibility Analysis")
    print("=" * 60)
    
    ai_service = AIMatchingService()
    
    # Test cases
    test_cases = [
        {
            "profile": "I'm a software engineer who loves hiking, reading sci-fi novels, and cooking. I value deep conversations, honesty, and personal growth. I'm looking for someone to explore life's adventures with.",
            "expectation": "Looking for someone who shares my love for outdoor activities and intellectual discussions. Must be ambitious, kind, and have a good sense of humor. Bonus points if you love books!",
            "expected": "High compatibility"
        },
        {
            "profile": "Party animal who loves nightlife, social media, and shopping. I'm all about living in the moment and having fun. Work hard, play harder!",
            "expectation": "Seeking a quiet, introverted partner who enjoys staying home, reading books, and having deep philosophical conversations about life.",
            "expected": "Low compatibility"
        },
        {
            "profile": "Yoga instructor passionate about mindfulness, healthy living, and spiritual growth. I love nature, meditation, and helping others find inner peace.",
            "expectation": "Looking for someone who values wellness, personal development, and has a calm, centered approach to life. Must love nature and healthy living.",
            "expected": "High compatibility"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i} (Expected: {case['expected']})")
        print("-" * 50)
        print(f"Profile: {case['profile'][:100]}...")
        print(f"Looking for: {case['expectation'][:100]}...")
        
        try:
            result = await ai_service.get_llm_text_compatibility(
                case['profile'], 
                case['expectation']
            )
            
            print(f"\n🎯 LLM Analysis Results:")
            print(f"   Overall Score: {result['overall_score']:.3f} ({result['overall_score']:.1%})")
            print(f"   Personality: {result['personality_score']:.3f}")
            print(f"   Lifestyle: {result['lifestyle_score']:.3f}")
            print(f"   Emotional: {result['emotional_score']:.3f}")
            print(f"   Long-term: {result['longterm_score']:.3f}")
            print(f"   Reasoning: {result['reasoning']}")
            
            if result['overall_score'] > 0.7:
                print("💕 Excellent match!")
            elif result['overall_score'] > 0.5:
                print("👍 Good match!")
            elif result['overall_score'] > 0.3:
                print("🤔 Moderate match")
            else:
                print("❌ Poor match")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_compatibility_reasoning():
    """Test the compatibility reasoning generation"""
    print("\n\n🎭 Compatibility Reasoning Generation")
    print("=" * 60)
    
    ai_service = AIMatchingService()
    
    # Mock profile and expectation objects
    class MockProfile:
        def __init__(self, description):
            self.description = description
    
    class MockExpectation:
        def __init__(self, description):
            self.description = description
    
    user_profile = MockProfile("Creative writer and coffee enthusiast who loves exploring new cities, trying different cuisines, and having meaningful conversations. I value authenticity, creativity, and emotional intelligence.")
    
    target_profile = MockProfile("Freelance photographer with a passion for travel and storytelling. I love capturing moments, exploring cultures, and connecting with people from all walks of life.")
    
    user_expectations = MockExpectation("Looking for someone creative, adventurous, and emotionally mature. Must love travel, good food, and deep conversations about life, art, and dreams.")
    
    target_expectations = MockExpectation("Seeking a partner who appreciates art, loves to explore, and values genuine connections. Someone who can be my adventure buddy and creative collaborator.")
    
    # Mock compatibility scores
    scores = {
        "overall_score": 0.85,
        "text_similarity": 0.82,
        "visual_similarity": 0.75,
        "personality_score": 0.88,
        "lifestyle_score": 0.85,
        "emotional_score": 0.83,
        "longterm_score": 0.87
    }
    
    try:
        reasoning = await ai_service.generate_compatibility_reasoning(
            user_profile, target_profile, user_expectations, target_expectations, scores
        )
        
        print("🎯 Detailed Compatibility Analysis:")
        print("-" * 40)
        print(f"Summary: {reasoning['summary']}")
        print(f"\nStrengths: {reasoning['strengths']}")
        print(f"\nShared Interests: {reasoning['shared_interests']}")
        print(f"\nConversation Starters: {reasoning['conversation_starters']}")
        print(f"\nGrowth Potential: {reasoning['growth_potential']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main test function"""
    print("🌟 Enhanced AI Matching System Test")
    print("=" * 60)
    
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured!")
        print("Please set your OPENAI_API_KEY in the .env file")
        return
    
    print(f"✅ OpenAI API key configured")
    print(f"✅ Using model: {settings.gpt_model}")
    
    try:
        await test_llm_text_compatibility()
        await test_compatibility_reasoning()
        
        print("\n" + "=" * 60)
        print("🎉 Enhanced AI Matching Test Complete!")
        print("\nNew Features Added:")
        print("✅ LLM-based text compatibility analysis")
        print("✅ Detailed personality, lifestyle, emotional, and long-term scoring")
        print("✅ Comprehensive compatibility reasoning generation")
        print("✅ Enhanced database schema with new score fields")
        print("✅ New API endpoint for detailed match analysis")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
