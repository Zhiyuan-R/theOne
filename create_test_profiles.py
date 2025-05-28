"""
Create fake profiles for testing the enhanced AI matching system
"""
import sys
import os
from datetime import datetime
from passlib.context import CryptContext

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.user import User, Profile, Expectation, Photo, ExampleImage
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_fake_profiles():
    """Create comprehensive fake profiles for testing"""
    db = SessionLocal()

    try:
        # Clear existing data (optional - comment out if you want to keep existing users)
        print("🧹 Clearing existing test data...")
        db.query(Photo).delete()
        db.query(ExampleImage).delete()
        db.query(Profile).delete()
        db.query(Expectation).delete()
        # Keep existing users but clear their profiles

        fake_profiles = [
            {
                "email": "alex.chen@test.com",
                "password": "testpass123",
                "profile_description": "Software engineer passionate about AI and machine learning. I love hiking on weekends, experimenting with new recipes, and reading sci-fi novels. I value deep conversations, personal growth, and building meaningful connections. Looking for someone who shares my curiosity about technology and life.",
                "expectation_description": "Seeking an intelligent, ambitious partner who loves learning and exploring new ideas. Must be kind, emotionally mature, and share my passion for outdoor adventures. Bonus points if you're into tech, books, or cooking!",
                "photos": ["static/uploads/profiles/alex_1.jpg", "static/uploads/profiles/alex_2.jpg"],
                "example_images": ["static/uploads/expectations/alex_ideal_1.jpg"]
            },
            {
                "email": "sarah.martinez@test.com",
                "password": "testpass123",
                "profile_description": "Creative photographer and travel enthusiast. I capture stories through my lens and believe every person has a unique tale to tell. Love exploring new cultures, trying exotic foods, and having philosophical discussions under the stars. Life is an adventure meant to be shared.",
                "expectation_description": "Looking for a creative soul who appreciates art, loves to travel, and values authentic connections. Someone who can be my adventure buddy and creative collaborator. Must be open-minded, emotionally intelligent, and ready for life's beautiful chaos.",
                "photos": ["static/uploads/profiles/sarah_1.jpg", "static/uploads/profiles/sarah_2.jpg"],
                "example_images": ["static/uploads/expectations/sarah_ideal_1.jpg"]
            },
            {
                "email": "mike.johnson@test.com",
                "password": "testpass123",
                "profile_description": "Fitness trainer and outdoor enthusiast who believes in living life to the fullest. I love rock climbing, surfing, and helping others achieve their health goals. When I'm not at the gym, you'll find me planning my next adventure or cooking healthy meals.",
                "expectation_description": "Seeking an active, health-conscious partner who loves outdoor activities and adventure. Must be positive, motivated, and ready to explore the world together. Looking for someone who values fitness, personal growth, and living an active lifestyle.",
                "photos": ["static/uploads/profiles/mike_1.jpg", "static/uploads/profiles/mike_2.jpg"],
                "example_images": ["static/uploads/expectations/mike_ideal_1.jpg"]
            },
            {
                "email": "emma.wilson@test.com",
                "password": "testpass123",
                "profile_description": "Yoga instructor and mindfulness coach passionate about wellness and spiritual growth. I love meditation, nature walks, and helping others find inner peace. I believe in the power of positive energy and authentic connections.",
                "expectation_description": "Looking for a calm, centered partner who values wellness, personal development, and spiritual growth. Must be emotionally mature, kind-hearted, and interested in mindful living. Someone who appreciates quiet moments and deep conversations.",
                "photos": ["static/uploads/profiles/emma_1.jpg", "static/uploads/profiles/emma_2.jpg"],
                "example_images": ["static/uploads/expectations/emma_ideal_1.jpg"]
            },
            {
                "email": "david.kim@test.com",
                "password": "testpass123",
                "profile_description": "Musician and music producer who lives and breathes creativity. I play guitar, produce electronic music, and love discovering new artists. Music is my language for expressing emotions and connecting with others. Always working on my next creative project.",
                "expectation_description": "Seeking a creative, artistic partner who appreciates music and the arts. Must be passionate, expressive, and open to new experiences. Looking for someone who can inspire me creatively and share in my artistic journey.",
                "photos": ["static/uploads/profiles/david_1.jpg", "static/uploads/profiles/david_2.jpg"],
                "example_images": ["static/uploads/expectations/david_ideal_1.jpg"]
            },
            {
                "email": "lisa.brown@test.com",
                "password": "testpass123",
                "profile_description": "Marketing professional with a passion for storytelling and human psychology. I love analyzing consumer behavior, creating compelling campaigns, and understanding what makes people tick. In my free time, I enjoy wine tasting, art galleries, and weekend getaways.",
                "expectation_description": "Looking for an intelligent, ambitious professional who values career growth and intellectual stimulation. Must be sophisticated, well-traveled, and enjoy the finer things in life. Someone who can engage in stimulating conversations about business, psychology, and life.",
                "photos": ["static/uploads/profiles/lisa_1.jpg", "static/uploads/profiles/lisa_2.jpg"],
                "example_images": ["static/uploads/expectations/lisa_ideal_1.jpg"]
            }
        ]

        created_users = []

        for i, profile_data in enumerate(fake_profiles, 1):
            print(f"👤 Processing user {i}: {profile_data['email']}")

            # Check if user already exists
            existing_user = db.query(User).filter(User.email == profile_data["email"]).first()
            if existing_user:
                print(f"   User already exists, updating profile...")
                user = existing_user
                # Delete existing profile and expectations
                if user.profile:
                    # Delete photos first
                    for photo in user.profile.photos:
                        db.delete(photo)
                    db.delete(user.profile)
                if user.expectations:
                    # Delete example images first
                    for img in user.expectations.example_images:
                        db.delete(img)
                    db.delete(user.expectations)
                db.flush()
            else:
                # Create new user
                hashed_password = pwd_context.hash(profile_data["password"])
                user = User(
                    email=profile_data["email"],
                    hashed_password=hashed_password,
                    is_active=True
                )
                db.add(user)
                db.flush()  # Get the user ID

            # Create profile
            profile = Profile(
                user_id=user.id,
                description=profile_data["profile_description"]
            )
            db.add(profile)
            db.flush()  # Get the profile ID

            # Create expectations
            expectation = Expectation(
                user_id=user.id,
                description=profile_data["expectation_description"]
            )
            db.add(expectation)
            db.flush()  # Get the expectation ID

            # Create fake photos (we'll create placeholder files)
            for j, photo_path in enumerate(profile_data["photos"]):
                photo = Photo(
                    profile_id=profile.id,
                    file_path=photo_path,
                    order_index=j
                )
                db.add(photo)

            # Create fake example images
            for example_path in profile_data["example_images"]:
                example_image = ExampleImage(
                    expectation_id=expectation.id,
                    file_path=example_path
                )
                db.add(example_image)

            created_users.append({
                "user": user,
                "profile": profile,
                "expectation": expectation
            })

        db.commit()
        print(f"✅ Successfully created {len(created_users)} test profiles!")

        # Create placeholder image files
        create_placeholder_images()

        return created_users

    except Exception as e:
        print(f"❌ Error creating profiles: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_placeholder_images():
    """Create placeholder image files for testing"""
    import os
    from PIL import Image, ImageDraw, ImageFont

    # Create directories
    os.makedirs("static/uploads/profiles", exist_ok=True)
    os.makedirs("static/uploads/expectations", exist_ok=True)

    # Create simple placeholder images
    profiles = ["alex", "sarah", "mike", "emma", "david", "lisa"]

    for profile in profiles:
        for i in range(1, 3):  # 2 photos per profile
            img = Image.new('RGB', (400, 400), color=(100, 150, 200))
            draw = ImageDraw.Draw(img)

            # Add text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            text = f"{profile.title()}\nPhoto {i}"
            draw.text((50, 150), text, fill=(255, 255, 255), font=font)

            img.save(f"static/uploads/profiles/{profile}_{i}.jpg")

        # Create expectation image
        img = Image.new('RGB', (400, 400), color=(200, 100, 150))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        text = f"{profile.title()}'s\nIdeal Match"
        draw.text((50, 150), text, fill=(255, 255, 255), font=font)

        img.save(f"static/uploads/expectations/{profile}_ideal_1.jpg")

    print("✅ Created placeholder images")


if __name__ == "__main__":
    print("🌟 Creating Test Profiles for Enhanced AI Matching")
    print("=" * 60)

    try:
        users = create_fake_profiles()
        print("\n📊 Test Profiles Created:")
        print("-" * 40)
        for i, user_data in enumerate(users, 1):
            print(f"{i}. {user_data['user'].email}")
            print(f"   Profile: {user_data['profile'].description[:100]}...")
            print(f"   Looking for: {user_data['expectation'].description[:100]}...")
            print()

        print("🎯 Ready for testing!")
        print("You can now:")
        print("1. Register a new user through the app")
        print("2. Create their profile and expectations")
        print("3. Generate matches to see the enhanced AI analysis")
        print("4. Use /matches/detailed/{match_id} for full reasoning")

    except Exception as e:
        print(f"❌ Failed to create test profiles: {e}")
        import traceback
        traceback.print_exc()
