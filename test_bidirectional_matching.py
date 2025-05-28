"""
Test bidirectional matching with a new user against existing fake profiles
"""
import asyncio
import sys
import os
from datetime import datetime
from passlib.context import CryptContext

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo, ExampleImage, Match
from app.services.ai_matching import ai_matching_service
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_user():
    """Create a new test user with profile and expectations"""
    db = SessionLocal()

    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "testuser@example.com").first()
        if existing_user:
            print("🔄 Test user already exists, updating profile...")
            # Delete existing profile and expectations
            if existing_user.profile:
                db.delete(existing_user.profile)
            if existing_user.expectations:
                db.delete(existing_user.expectations)
            db.commit()
            user = existing_user
        else:
            print("👤 Creating new test user...")
            hashed_password = pwd_context.hash("testpass123")
            user = User(
                email="testuser@example.com",
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(user)
            db.flush()

        # Create profile - someone who would match well with Alex (tech) and Sarah (creative)
        profile = Profile(
            user_id=user.id,
            description="Full-stack developer with a passion for creative problem-solving and photography. I love building innovative apps, exploring new technologies, and capturing beautiful moments through my camera. When I'm not coding, you'll find me hiking, reading about AI advancements, or experimenting with new cooking recipes. I believe technology should bring people together and make life more meaningful."
        )
        db.add(profile)
        db.flush()

        # Create expectations - looking for someone creative, tech-savvy, and adventurous
        expectation = Expectation(
            user_id=user.id,
            description="Looking for an intelligent, creative partner who shares my passion for technology and innovation. Must be curious about the world, love learning new things, and enjoy both outdoor adventures and cozy nights discussing ideas. I value authenticity, emotional intelligence, and someone who can challenge me intellectually while being supportive and kind."
        )
        db.add(expectation)
        db.flush()

        # Create placeholder photos
        from PIL import Image, ImageDraw, ImageFont
        import os

        os.makedirs("static/uploads/profiles", exist_ok=True)
        os.makedirs("static/uploads/expectations", exist_ok=True)

        # Create test user photos
        for i in range(1, 3):
            img = Image.new('RGB', (400, 400), color=(50, 100, 200))
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            text = f"Test User\nPhoto {i}"
            draw.text((50, 150), text, fill=(255, 255, 255), font=font)

            photo_path = f"static/uploads/profiles/testuser_{i}.jpg"
            img.save(photo_path)

            photo = Photo(
                profile_id=profile.id,
                file_path=photo_path,
                order_index=i-1
            )
            db.add(photo)

        # Create expectation image
        img = Image.new('RGB', (400, 400), color=(200, 50, 100))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        text = "Test User's\nIdeal Match"
        draw.text((50, 150), text, fill=(255, 255, 255), font=font)

        expectation_path = "static/uploads/expectations/testuser_ideal_1.jpg"
        img.save(expectation_path)

        example_image = ExampleImage(
            expectation_id=expectation.id,
            file_path=expectation_path
        )
        db.add(example_image)

        db.commit()
        print(f"✅ Test user created: {user.email}")
        return user

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def test_bidirectional_matching():
    """Test bidirectional matching between test user and existing profiles"""
    db = SessionLocal()

    try:
        print("\n🔍 Testing Bidirectional Matching")
        print("=" * 50)

        # Get test user with full profile
        test_user = db.query(User).options(
            joinedload(User.profile).joinedload(Profile.photos),
            joinedload(User.expectations).joinedload(Expectation.example_images)
        ).filter(User.email == "testuser@example.com").first()

        if not test_user or not test_user.profile or not test_user.expectations:
            print("❌ Test user not found or incomplete profile")
            return

        print(f"👤 Test User: {test_user.email}")
        print(f"📝 Profile: {test_user.profile.description[:100]}...")
        print(f"💭 Looking for: {test_user.expectations.description[:100]}...")

        # Get all other users (fake profiles)
        candidate_users = db.query(User).options(
            joinedload(User.profile).joinedload(Profile.photos),
            joinedload(User.expectations).joinedload(Expectation.example_images)
        ).filter(
            User.id != test_user.id,
            User.profile.isnot(None),
            User.expectations.isnot(None)
        ).all()

        print(f"\n🎯 Found {len(candidate_users)} potential matches")

        if not candidate_users:
            print("❌ No candidate users found. Run create_test_profiles.py first!")
            return

        # Test matching with enhanced analysis
        print("\n🧠 Running Enhanced AI Matching Analysis...")
        print("-" * 50)

        matches = await ai_matching_service.find_daily_matches(
            test_user, candidate_users, limit=len(candidate_users), include_reasoning=True
        )

        print(f"\n📊 Matching Results (Top {len(matches)} candidates):")
        print("=" * 70)

        for i, match in enumerate(matches, 1):
            candidate = next(u for u in candidate_users if u.id == match["user_id"])

            print(f"\n{i}. {candidate.email}")
            print(f"   Overall Compatibility: {match['compatibility_score']:.3f} ({match['compatibility_score']:.1%})")
            print(f"   📝 Text Similarity: {match['text_similarity']:.3f}")
            print(f"   🖼️  Visual Similarity: {match['visual_similarity']:.3f}")
            print(f"   🧠 LLM Text Score: {match['llm_text_score']:.3f}")
            print(f"   👤 Personality: {match['personality_score']:.3f}")
            print(f"   🏠 Lifestyle: {match['lifestyle_score']:.3f}")
            print(f"   💝 Emotional: {match['emotional_score']:.3f}")
            print(f"   🔮 Long-term: {match['longterm_score']:.3f}")

            if "reasoning" in match:
                reasoning = match["reasoning"]
                print(f"   📋 Analysis:")
                print(f"      Summary: {reasoning.get('summary', 'N/A')}")
                print(f"      Strengths: {reasoning.get('strengths', 'N/A')}")
                print(f"      Conversation Starters: {reasoning.get('conversation_starters', 'N/A')}")

            # Determine match quality
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
        print(f"\n🔄 Testing Bidirectional Compatibility")
        print("=" * 50)

        # Test with top 3 matches
        top_matches = matches[:3]

        for match in top_matches:
            candidate = next(u for u in candidate_users if u.id == match["user_id"])

            print(f"\n🔍 Bidirectional Test: Test User ↔ {candidate.email}")
            print("-" * 40)

            # Test User → Candidate (already calculated above)
            test_to_candidate = match['compatibility_score']

            # Candidate → Test User (reverse direction)
            reverse_matches = await ai_matching_service.find_daily_matches(
                candidate, [test_user], limit=1, include_reasoning=False
            )

            if reverse_matches:
                candidate_to_test = reverse_matches[0]['compatibility_score']

                print(f"   Test User → {candidate.email}: {test_to_candidate:.3f} ({test_to_candidate:.1%})")
                print(f"   {candidate.email} → Test User: {candidate_to_test:.3f} ({candidate_to_test:.1%})")

                # Calculate mutual compatibility
                mutual_score = (test_to_candidate + candidate_to_test) / 2
                print(f"   🤝 Mutual Compatibility: {mutual_score:.3f} ({mutual_score:.1%})")

                # Check if both are satisfied (both scores > 0.5)
                both_satisfied = test_to_candidate > 0.5 and candidate_to_test > 0.5
                print(f"   ✅ Both Satisfied: {'YES' if both_satisfied else 'NO'}")

                if both_satisfied:
                    print(f"   🎉 MUTUAL MATCH FOUND!")
                else:
                    print(f"   ⚠️  One-sided attraction")
            else:
                print(f"   ❌ Could not calculate reverse compatibility")

        print(f"\n🎯 Bidirectional Matching Test Complete!")

    except Exception as e:
        print(f"❌ Error in matching test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """Main test function"""
    print("🌟 Bidirectional AI Matching Test")
    print("=" * 60)

    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API key not configured - using fallback scores")
    else:
        print("✅ OpenAI API key configured")

    try:
        # Step 1: Create test user
        test_user = create_test_user()

        # Step 2: Test bidirectional matching
        await test_bidirectional_matching()

        print("\n" + "=" * 60)
        print("🎉 Test Complete!")
        print("\nWhat was tested:")
        print("✅ Created new test user with profile and expectations")
        print("✅ Generated compatibility scores with all existing users")
        print("✅ Tested bidirectional matching (both directions)")
        print("✅ Identified mutual matches where both users are satisfied")
        print("✅ Provided detailed reasoning and conversation starters")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
