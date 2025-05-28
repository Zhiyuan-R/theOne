"""
Startup script for theOne dating app
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from example...")
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created! Please update it with your API keys.")
        else:
            print("❌ .env.example not found!")
            return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("Starting FastAPI backend...")
    try:
        subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        print("✅ Backend started at http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("Starting Streamlit frontend...")
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py", "--server.port", "8501"])
        print("✅ Frontend started at http://localhost:8501")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🌟 Starting theOne - AI-Powered Dating App")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    print("\n📋 Setup Instructions:")
    print("1. Update your .env file with your OpenAI API key")
    print("2. The backend will start at http://localhost:8000")
    print("3. The frontend will start at http://localhost:8501")
    print("4. API documentation will be available at http://localhost:8000/docs")
    print("\n🚀 Starting services...")
    
    # Start backend
    if start_backend():
        import time
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        start_frontend()
        
        print("\n✅ Both services are starting!")
        print("📖 Visit http://localhost:8501 to use the app")
        print("📚 Visit http://localhost:8000/docs for API documentation")
        print("\n⚠️  Make sure to set your OPENAI_API_KEY in the .env file!")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()
