#!/usr/bin/env python3
"""
Test API key loading
"""
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def test_api_key():
    """Test if API key is loaded correctly"""
    print("Environment variables:")
    print(f"OPENAI_API_KEY from os.getenv: {os.getenv('OPENAI_API_KEY')}")
    print(f"Settings openai_api_key: {settings.openai_api_key}")
    
    # Try loading .env manually
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print(f"After load_dotenv - OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    except ImportError:
        print("python-dotenv not installed")

if __name__ == "__main__":
    test_api_key()
