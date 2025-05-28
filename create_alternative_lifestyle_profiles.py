"""
Create test profiles including BDSM and alternative lifestyle users
"""
import sys
import os
from passlib.context import CryptContext

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo, ExampleImage
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_alternative_lifestyle_profiles():
    """Create diverse profiles including BDSM and alternative lifestyles"""
    db = SessionLocal()
    
    try:
        print("🌈 Creating Alternative Lifestyle Test Profiles")
        print("=" * 60)
        
        alternative_profiles = [
            {
                "email": "dom.master@test.com",
                "password": "testpass123",
                "profile_description": "Experienced Dom in the BDSM community with 8+ years of practice. I value trust, communication, and consent above all. I enjoy rope bondage, impact play, and psychological dominance. Outside the lifestyle, I'm a software architect who loves hiking and cooking. Looking for a meaningful D/s relationship built on mutual respect and growth.",
                "expectation_description": "Seeking a submissive partner who is curious, communicative, and eager to explore. Must understand the importance of safe words, aftercare, and ongoing consent. I value intelligence, emotional maturity, and someone who can challenge me intellectually while submitting physically. New to BDSM? That's okay - I love teaching and guiding the right person.",
                "photos": ["static/uploads/profiles/dom_1.jpg", "static/uploads/profiles/dom_2.jpg"],
                "example_images": ["static/uploads/expectations/dom_ideal_1.jpg"]
            },
            {
                "email": "sub.kitten@test.com",
                "password": "testpass123",
                "profile_description": "Submissive exploring my desires in a safe, consensual environment. I'm drawn to service submission, rope play, and the psychological aspects of power exchange. I'm a graphic designer by day, cat mom by night. I value aftercare, communication, and building deep trust with the right Dom. Looking for someone who understands that submission is a gift, not a given.",
                "expectation_description": "Looking for an experienced, patient Dom who prioritizes my safety and growth. Must be excellent at communication, understand consent and boundaries, and provide proper aftercare. I want someone who appreciates my submission while helping me explore new aspects of myself. Emotional connection is just as important as physical compatibility.",
                "photos": ["static/uploads/profiles/sub_1.jpg", "static/uploads/profiles/sub_2.jpg"],
                "example_images": ["static/uploads/expectations/sub_ideal_1.jpg"]
            },
            {
                "email": "poly.explorer@test.com",
                "password": "testpass123",
                "profile_description": "Polyamorous relationship anarchist who believes love isn't finite. I have two existing partners and we practice ethical non-monogamy with full transparency. I'm passionate about social justice, environmental activism, and building intentional communities. I love deep conversations, music festivals, and exploring different relationship dynamics.",
                "expectation_description": "Seeking someone who understands and embraces polyamory. Must be comfortable with my existing relationships and interested in building something unique together. I value honesty, compersion, and excellent communication skills. Looking for someone who wants to explore what relationship anarchy can offer - freedom, authenticity, and genuine connection.",
                "photos": ["static/uploads/profiles/poly_1.jpg", "static/uploads/profiles/poly_2.jpg"],
                "example_images": ["static/uploads/expectations/poly_ideal_1.jpg"]
            },
            {
                "email": "kink.switch@test.com",
                "password": "testpass123",
                "profile_description": "Versatile switch in the kink community - I enjoy both dominant and submissive roles depending on the dynamic and partner. I'm into impact play, sensory deprivation, and role play. I'm also a professional dancer and yoga instructor. I believe in exploring sexuality without shame and building connections based on authentic desire and mutual exploration.",
                "expectation_description": "Looking for another switch or someone open to exploring power dynamics from both sides. Must be sex-positive, kink-aware, and excellent at negotiating scenes. I want someone who can match my energy whether I'm topping or bottoming. Emotional intelligence and creativity in the bedroom are huge turn-ons.",
                "photos": ["static/uploads/profiles/switch_1.jpg", "static/uploads/profiles/switch_2.jpg"],
                "example_images": ["static/uploads/expectations/switch_ideal_1.jpg"]
            },
            {
                "email": "queer.artist@test.com",
                "password": "testpass123",
                "profile_description": "Non-binary queer artist exploring gender expression through performance and visual art. I use they/them pronouns and am attracted to people regardless of gender. I'm passionate about LGBTQ+ rights, creating inclusive spaces, and challenging societal norms. I love underground music, poetry slams, and collaborative art projects.",
                "expectation_description": "Seeking someone who celebrates queerness and understands gender fluidity. Must be respectful of pronouns, supportive of my art, and interested in social justice. I want a partner who can appreciate both my masculine and feminine energy. Bonus points if you're also involved in the arts or activism.",
                "photos": ["static/uploads/profiles/queer_1.jpg", "static/uploads/profiles/queer_2.jpg"],
                "example_images": ["static/uploads/expectations/queer_ideal_1.jpg"]
            },
            {
                "email": "age.gap@test.com",
                "password": "testpass123",
                "profile_description": "Mature 45-year-old professional who has always been attracted to younger partners (25-35). I'm financially stable, emotionally mature, and looking for someone who appreciates experience and wisdom. I enjoy mentoring, traveling, fine dining, and intellectual conversations. I believe age is just a number when there's genuine connection and mutual respect.",
                "expectation_description": "Looking for a younger partner who is attracted to maturity and stability. Must be emotionally intelligent, ambitious, and not interested in me just for financial security. I want someone who can teach me new perspectives while appreciating what I bring to the relationship. Age gap relationships require extra communication - are you up for that?",
                "photos": ["static/uploads/profiles/mature_1.jpg", "static/uploads/profiles/mature_2.jpg"],
                "example_images": ["static/uploads/expectations/mature_ideal_1.jpg"]
            }
        ]
        
        created_users = []
        
        for i, profile_data in enumerate(alternative_profiles, 1):
            print(f"👤 Creating alternative lifestyle user {i}: {profile_data['email']}")
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == profile_data["email"]).first()
            if existing_user:
                print(f"   User already exists, updating profile...")
                user = existing_user
                # Delete existing profile and expectations
                if user.profile:
                    for photo in user.profile.photos:
                        db.delete(photo)
                    db.delete(user.profile)
                if user.expectations:
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
                db.flush()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                description=profile_data["profile_description"]
            )
            db.add(profile)
            db.flush()
            
            # Create expectations
            expectation = Expectation(
                user_id=user.id,
                description=profile_data["expectation_description"]
            )
            db.add(expectation)
            db.flush()
            
            # Create fake photos
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
        print(f"✅ Successfully created {len(created_users)} alternative lifestyle profiles!")
        
        # Create placeholder images
        create_placeholder_images_alternative()
        
        return created_users
        
    except Exception as e:
        print(f"❌ Error creating alternative lifestyle profiles: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_placeholder_images_alternative():
    """Create placeholder images for alternative lifestyle profiles"""
    import os
    from PIL import Image, ImageDraw, ImageFont
    
    # Create directories
    os.makedirs("static/uploads/profiles", exist_ok=True)
    os.makedirs("static/uploads/expectations", exist_ok=True)
    
    # Create simple placeholder images
    profiles = ["dom", "sub", "poly", "switch", "queer", "mature"]
    colors = [
        (120, 50, 150),   # dom - purple
        (200, 100, 150),  # sub - pink
        (100, 200, 100),  # poly - green
        (200, 150, 50),   # switch - orange
        (150, 100, 200),  # queer - lavender
        (100, 100, 150)   # mature - blue
    ]
    
    for i, profile in enumerate(profiles):
        color = colors[i]
        
        for j in range(1, 3):  # 2 photos per profile
            img = Image.new('RGB', (400, 400), color=color)
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            text = f"{profile.title()}\nPhoto {j}"
            draw.text((50, 150), text, fill=(255, 255, 255), font=font)
            
            img.save(f"static/uploads/profiles/{profile}_{j}.jpg")
        
        # Create expectation image
        img = Image.new('RGB', (400, 400), color=tuple(c + 30 for c in color))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 25)
        except:
            font = ImageFont.load_default()
        
        text = f"{profile.title()}'s\nIdeal Match"
        draw.text((50, 150), text, fill=(255, 255, 255), font=font)
        
        img.save(f"static/uploads/expectations/{profile}_ideal_1.jpg")
    
    print("✅ Created placeholder images for alternative lifestyles")


if __name__ == "__main__":
    print("🌈 Creating Alternative Lifestyle Test Profiles")
    print("=" * 60)
    
    try:
        users = create_alternative_lifestyle_profiles()
        print("\n📊 Alternative Lifestyle Profiles Created:")
        print("-" * 50)
        print("1. Dom/Master - BDSM Dominant")
        print("2. Submissive - BDSM Submissive") 
        print("3. Polyamorous - Ethical Non-Monogamy")
        print("4. Switch - Versatile Kink")
        print("5. Queer/Non-Binary - LGBTQ+")
        print("6. Age Gap - Mature/Younger Dynamic")
        
        print("\n🎯 Ready for Alternative Lifestyle Matching!")
        print("The AI system can now handle:")
        print("✅ BDSM and kink relationships")
        print("✅ Polyamorous and open relationships")
        print("✅ LGBTQ+ and gender-diverse users")
        print("✅ Age gap relationships")
        print("✅ Alternative relationship structures")
        print("✅ All consensual adult lifestyle preferences")
        
    except Exception as e:
        print(f"❌ Failed to create alternative lifestyle profiles: {e}")
        import traceback
        traceback.print_exc()
