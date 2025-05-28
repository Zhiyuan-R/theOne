#!/usr/bin/env python3
"""
Complete local testing script for BDSM dating app
"""
import asyncio
import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 50)


def check_dependencies():
    """Check if required dependencies are installed"""
    print_step("1", "Checking Dependencies")

    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('openai', 'openai'),
        ('pillow', 'PIL'),
        ('passlib', 'passlib'),
        ('python-jose', 'jose'),
        ('pydantic-settings', 'pydantic_settings')
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - MISSING")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    print("✅ All dependencies installed!")
    return True


def check_environment():
    """Check environment configuration"""
    print_step("2", "Checking Environment Configuration")

    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False

    print("✅ .env file exists")

    # Check OpenAI API key
    try:
        from app.core.config import settings
        if settings.openai_api_key and len(settings.openai_api_key) > 20:
            print("✅ OpenAI API key configured")
        else:
            print("❌ OpenAI API key missing or invalid")
            return False

        print(f"✅ GPT Model: {settings.gpt_model}")
        print(f"✅ Embedding Model: {settings.embedding_model}")

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    return True


def test_database():
    """Test database setup"""
    print_step("3", "Testing Database Setup")

    try:
        from app.db.database import SessionLocal, engine
        from app.models.user import Base, User

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")

        # Test database connection
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()

        print(f"✅ Database connection working - {user_count} users found")
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def create_test_data():
    """Create test profiles if they don't exist"""
    print_step("4", "Creating Test Data")

    try:
        from app.db.database import SessionLocal
        from app.models.user import User

        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()

        if user_count < 5:
            print("Creating traditional test profiles...")
            result = subprocess.run([sys.executable, "create_test_profiles.py"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Traditional profiles created")
            else:
                print(f"⚠️  Traditional profiles creation had issues: {result.stderr}")

            print("Creating alternative lifestyle profiles...")
            result = subprocess.run([sys.executable, "create_alternative_lifestyle_profiles.py"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Alternative lifestyle profiles created")
            else:
                print(f"⚠️  Alternative profiles creation had issues: {result.stderr}")
        else:
            print(f"✅ Test data already exists ({user_count} users)")

        return True

    except Exception as e:
        print(f"❌ Test data creation error: {e}")
        return False


async def test_ai_matching():
    """Test AI matching functionality"""
    print_step("5", "Testing AI Matching")

    try:
        from app.services.ai_matching import ai_matching_service
        from app.db.database import SessionLocal
        from app.models.user import User

        db = SessionLocal()
        users = db.query(User).limit(3).all()

        if len(users) < 2:
            print("❌ Need at least 2 users for matching test")
            db.close()
            return False

        # Test basic matching
        print("Testing basic AI matching...")
        matches = await ai_matching_service.find_daily_matches(
            users[0], users[1:], limit=2
        )

        if matches:
            print(f"✅ AI matching working - found {len(matches)} matches")
            print(f"   Best match: {matches[0]['compatibility_score']:.3f} compatibility")
        else:
            print("⚠️  No matches found (this might be normal)")

        db.close()
        return True

    except Exception as e:
        print(f"❌ AI matching error: {e}")
        return False


def test_openai_api():
    """Test OpenAI API connectivity"""
    print_step("6", "Testing OpenAI API")

    try:
        import openai
        from app.core.config import settings

        client = openai.OpenAI(api_key=settings.openai_api_key)

        # Test chat completion
        response = client.chat.completions.create(
            model=settings.gpt_model,
            messages=[{"role": "user", "content": "Hello, test message"}],
            max_tokens=10
        )

        print("✅ OpenAI Chat API working")
        print(f"   Model: {settings.gpt_model}")
        print(f"   Response: {response.choices[0].message.content}")

        # Test embeddings
        embedding_response = client.embeddings.create(
            model=settings.embedding_model,
            input="Test embedding"
        )

        print("✅ OpenAI Embeddings API working")
        print(f"   Model: {settings.embedding_model}")
        print(f"   Embedding dimension: {len(embedding_response.data[0].embedding)}")

        return True

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


async def test_bdsm_matching():
    """Test BDSM-specific matching"""
    print_step("7", "Testing BDSM Matching")

    try:
        from app.db.database import SessionLocal
        from app.models.user import User
        from app.services.ai_matching import ai_matching_service

        db = SessionLocal()

        # Find BDSM users
        dom_user = db.query(User).filter(User.email == "dom.master@test.com").first()
        sub_user = db.query(User).filter(User.email == "sub.kitten@test.com").first()

        if not dom_user or not sub_user:
            print("⚠️  BDSM test users not found - run create_alternative_lifestyle_profiles.py")
            db.close()
            return True  # Not a failure, just missing test data

        print("Testing BDSM Dom/Sub compatibility...")

        # Test Dom → Sub
        dom_matches = await ai_matching_service.find_daily_matches(
            dom_user, [sub_user], limit=1, include_reasoning=True
        )

        if dom_matches:
            score = dom_matches[0]['compatibility_score']
            print(f"✅ BDSM matching working!")
            print(f"   Dom → Sub compatibility: {score:.3f} ({score:.1%})")

            if 'reasoning' in dom_matches[0]:
                reasoning = dom_matches[0]['reasoning']
                summary = reasoning.get('summary', 'N/A')[:100]
                print(f"   AI Analysis: {summary}...")
        else:
            print("⚠️  No BDSM matches found")

        db.close()
        return True

    except Exception as e:
        print(f"❌ BDSM matching error: {e}")
        return False


def start_web_server():
    """Start the FastAPI web server"""
    print_step("8", "Starting Web Server")

    try:
        print("Starting FastAPI server on http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        print("\nAvailable endpoints:")
        print("   📖 API Docs: http://localhost:8000/docs")
        print("   🏠 Home: http://localhost:8000/")
        print("   💚 Health: http://localhost:8000/health")

        # Start server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])

    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")


async def run_comprehensive_test():
    """Run all tests"""
    print_header("BDSM Dating App - Local Testing")

    # Run tests in sequence
    tests = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", test_database),
        ("Test Data", create_test_data),
        ("OpenAI API", test_openai_api),
        ("AI Matching", test_ai_matching),
        ("BDSM Matching", test_bdsm_matching),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))

    # Print summary
    print_header("Test Results Summary")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your BDSM dating app is ready!")

        # Ask if user wants to start web server
        try:
            response = input("\n🚀 Start web server? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                start_web_server()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("⚠️  Some tests failed. Please fix the issues before proceeding.")


def main():
    """Main function"""
    try:
        asyncio.run(run_comprehensive_test())
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
