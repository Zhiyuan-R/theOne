# 🚀 Local Testing Guide - BDSM Dating App

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Make sure you're in the project directory
cd /Users/tencentintern/Documents/start_up/theOne

# Verify Python environment
python3 --version  # Should be 3.9+

# Check if virtual environment is activated (optional but recommended)
# python -m venv venv
# source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies
```bash
# Install required packages
pip install fastapi uvicorn sqlalchemy sqlite3 openai python-multipart pillow passlib bcrypt python-jose cryptography pydantic-settings

# Or if you have requirements.txt:
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Verify .env file exists with correct settings
cat .env

# Should contain:
# OPENAI_API_KEY=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
# GPT_MODEL=gpt-4o-mini
# EMBEDDING_MODEL=text-embedding-3-small
```

## 🗄️ Database Setup

### 1. Initialize Database
```bash
# Create database and tables
python3 -c "
from app.db.database import engine
from app.models.user import Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized!')
"
```

### 2. Create Test Profiles
```bash
# Create traditional dating profiles
python3 create_test_profiles.py

# Create BDSM and alternative lifestyle profiles
python3 create_alternative_lifestyle_profiles.py
```

### 3. Verify Database Content
```bash
# Check database contents
sqlite3 theone.db "
SELECT 'Users:' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Profiles:', COUNT(*) FROM profiles
UNION ALL
SELECT 'Expectations:', COUNT(*) FROM expectations;
"
```

## 🧪 Testing Components

### 1. Test Individual AI Components
```bash
# Test OpenAI embeddings and GPT-4o-mini
python3 test_gpt4o_mini_bdsm.py
```

### 2. Test BDSM Matching
```bash
# Test BDSM Dom/Sub compatibility
python3 test_alternative_lifestyle_matching.py
```

### 3. Test Bidirectional Matching
```bash
# Test mutual compatibility verification
python3 final_bidirectional_test.py
```

## 🌐 Web Server Testing

### 1. Start FastAPI Server
```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at: http://localhost:8000
```

### 2. Test API Endpoints
```bash
# Test health check
curl http://localhost:8000/health

# Test user registration
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Test user login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

### 3. Test Matching API
```bash
# Get daily matches (requires authentication token)
curl -X GET "http://localhost:8000/matching/daily-matches" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Interactive Testing

### 1. API Documentation
```bash
# Start server and visit:
# http://localhost:8000/docs
# 
# This provides interactive API documentation where you can:
# - Test all endpoints
# - See request/response schemas
# - Try authentication flows
```

### 2. Database Browser
```bash
# Install DB Browser for SQLite (optional)
# Download from: https://sqlitebrowser.org/
# Open theone.db to browse data visually
```

## 🔍 Specific Test Scenarios

### 1. BDSM Dom/Sub Matching Test
```bash
# Run comprehensive BDSM test
python3 -c "
import asyncio
from test_gpt4o_mini_bdsm import main
asyncio.run(main())
"
```

### 2. Cross-Lifestyle Compatibility
```bash
# Test different lifestyle combinations
python3 -c "
import asyncio
from test_alternative_lifestyle_matching import main
asyncio.run(main())
"
```

### 3. Performance Testing
```bash
# Test with multiple users
python3 -c "
import asyncio
import time
from app.services.ai_matching import ai_matching_service
from app.db.database import SessionLocal
from app.models.user import User

async def performance_test():
    db = SessionLocal()
    users = db.query(User).limit(10).all()
    
    start_time = time.time()
    
    # Test matching speed
    if len(users) >= 2:
        matches = await ai_matching_service.find_daily_matches(
            users[0], users[1:], limit=5
        )
        
    end_time = time.time()
    print(f'⏱️  Matching took {end_time - start_time:.2f} seconds')
    print(f'📊 Found {len(matches)} matches')
    
    db.close()

asyncio.run(performance_test())
"
```

## 🐛 Debugging & Troubleshooting

### 1. Common Issues

#### OpenAI API Errors
```bash
# Test API key
python3 -c "
import openai
from app.core.config import settings
client = openai.OpenAI(api_key=settings.openai_api_key)
try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('✅ OpenAI API working!')
    print(f'Response: {response.choices[0].message.content}')
except Exception as e:
    print(f'❌ OpenAI API error: {e}')
"
```

#### Database Issues
```bash
# Reset database
rm theone.db
python3 create_test_profiles.py
python3 create_alternative_lifestyle_profiles.py
```

#### Import Errors
```bash
# Check Python path
python3 -c "
import sys
print('Python path:')
for path in sys.path:
    print(f'  {path}')
"

# Test imports
python3 -c "
try:
    from app.services.ai_matching import ai_matching_service
    print('✅ AI matching service imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
"
```

### 2. Logging & Monitoring
```bash
# Enable debug logging
export DEBUG=True

# Run with verbose output
python3 test_gpt4o_mini_bdsm.py 2>&1 | tee test_output.log
```

## 📊 Test Results Validation

### Expected Results
- **BDSM Dom/Sub Match**: ~50-70% compatibility
- **Cross-lifestyle**: Variable based on preferences
- **Traditional matches**: ~40-80% range
- **API Response Time**: <5 seconds per match
- **Database Operations**: <1 second

### Success Indicators
```
✅ GPT-4o-mini successfully handles BDSM content
✅ Non-judgmental analysis of kink relationships
✅ Focus on consent, communication, and safety
✅ Detailed Dom/Sub compatibility assessment
✅ Bidirectional BDSM matching verification
✅ Cost-efficient alternative to GPT-4
```

## 🚀 Quick Start Commands

```bash
# Complete local test sequence
cd /Users/tencentintern/Documents/start_up/theOne

# 1. Setup database and profiles
python3 create_test_profiles.py
python3 create_alternative_lifestyle_profiles.py

# 2. Test BDSM matching
python3 test_gpt4o_mini_bdsm.py

# 3. Start web server
uvicorn app.main:app --reload --port 8000

# 4. Open browser to test API
open http://localhost:8000/docs
```

## 🎯 Production Testing Checklist

Before deploying:
- [ ] All tests pass locally
- [ ] API endpoints respond correctly
- [ ] BDSM matching works appropriately
- [ ] Database operations are fast
- [ ] OpenAI API calls succeed
- [ ] Error handling works
- [ ] Authentication flows work
- [ ] File uploads function (if implemented)
- [ ] CORS settings configured
- [ ] Environment variables set correctly

Your BDSM dating app is ready for local testing! 🌟
