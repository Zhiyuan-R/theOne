"""
Demo script to showcase theOne AI matching capabilities
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_matching import AIMatchingService


async def demo_text_matching():
    """Demo text similarity matching"""
    print("🧠 AI Text Matching Demo")
    print("=" * 40)
    
    ai_service = AIMatchingService()
    
    # Sample user descriptions and expectations
    test_cases = [
        {
            "user_description": "I'm an introverted bookworm who loves rainy cafes and deep talks about philosophy and life.",
            "expectation": "Someone warm, thoughtful, who enjoys quiet moments and meaningful conversations.",
            "expected_score": "High"
        },
        {
            "user_description": "Adventure seeker, love hiking, rock climbing, and exploring new places. Always up for spontaneous trips!",
            "expectation": "Looking for someone who loves the outdoors and isn't afraid to take risks.",
            "expected_score": "High"
        },
        {
            "user_description": "Tech enthusiast, spend most of my time coding and playing video games. Love sci-fi movies.",
            "expectation": "Someone warm, adventurous, who loves dogs and slow mornings.",
            "expected_score": "Low"
        },
        {
            "user_description": "Artist and creative soul, love painting, music, and expressing myself through art.",
            "expectation": "Someone creative, passionate about art, who understands the artistic temperament.",
            "expected_score": "High"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i} (Expected: {case['expected_score']} compatibility)")
        print("-" * 50)
        print(f"User: {case['user_description']}")
        print(f"Looking for: {case['expectation']}")
        
        similarity = ai_service.get_text_similarity(
            case['user_description'], 
            case['expectation']
        )
        
        print(f"🎯 Compatibility Score: {similarity:.3f} ({similarity:.1%})")
        
        if similarity > 0.7:
            print("💕 Excellent match!")
        elif similarity > 0.5:
            print("👍 Good match!")
        elif similarity > 0.3:
            print("🤔 Moderate match")
        else:
            print("❌ Poor match")


def demo_without_openai():
    """Demo the text matching without requiring OpenAI API"""
    print("\n🌟 theOne AI Dating App - Text Matching Demo")
    print("=" * 60)
    print("Note: This demo shows text similarity matching.")
    print("Visual matching requires OpenAI API key configuration.")
    print("=" * 60)
    
    # Run the text matching demo
    asyncio.run(demo_text_matching())
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\nTo experience the full AI matching with visual analysis:")
    print("1. Get an OpenAI API key from https://platform.openai.com/")
    print("2. Add it to your .env file: OPENAI_API_KEY=your_key_here")
    print("3. Use the web interface at http://localhost:8501")
    print("\n📚 API Documentation: http://localhost:8000/docs")


def main():
    """Main demo function"""
    try:
        demo_without_openai()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure you've installed all requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
