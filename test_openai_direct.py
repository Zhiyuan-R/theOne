#!/usr/bin/env python3
"""
Test OpenAI API directly
"""
import os
import sys
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
import openai

async def test_openai():
    """Test OpenAI API directly"""
    try:
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
        response = await client.chat.completions.create(
            model=settings.gpt_model,
            messages=[{"role": "user", "content": "Hello, just testing the API. Please respond with 'API works!'"}],
            max_tokens=10
        )
        
        print(f"OpenAI API Response: {response.choices[0].message.content}")
        print("✅ API key is working!")
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        print(f"API Key (first 20 chars): {settings.openai_api_key[:20]}...")
        print(f"Model: {settings.gpt_model}")

if __name__ == "__main__":
    asyncio.run(test_openai())
