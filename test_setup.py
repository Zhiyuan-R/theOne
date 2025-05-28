"""
Simple test script to verify the setup
"""
import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'openai',
        'sentence_transformers',
        'numpy',
        'sklearn',
        'PIL',
        'streamlit',
        'passlib',
        'jose',
        'requests'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run 'pip install -r requirements.txt' to install missing packages")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_app_structure():
    """Test if the app structure is correct"""
    import os
    
    required_files = [
        'main.py',
        'requirements.txt',
        '.env.example',
        'app/__init__.py',
        'app/core/config.py',
        'app/core/auth.py',
        'app/db/database.py',
        'app/models/user.py',
        'app/schemas/user.py',
        'app/services/ai_matching.py',
        'app/api/auth.py',
        'app/api/profiles.py',
        'app/api/expectations.py',
        'app/api/matches.py',
        'frontend/streamlit_app.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

def test_database_models():
    """Test if database models can be imported and created"""
    try:
        from app.db.database import create_tables, Base
        from app.models.user import User, Profile, Photo, Expectation, ExampleImage, Match
        
        print("✅ Database models imported successfully")
        
        # Test table creation (in memory)
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing theOne App Setup")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("App Structure", test_app_structure),
        ("Database Models", test_database_models)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        print("-" * 30)
        
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run 'python start.py' to start the application.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
