#!/usr/bin/env python3
"""
Simple admin dashboard to view user profiles through web browser
Run this script and visit http://localhost:8001/admin
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.db.database import SessionLocal
from app.models.user import User, Profile, Expectation, Photo
import uvicorn
import os
from datetime import datetime

app = FastAPI(title="theOne Admin Dashboard")
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard to view all user profiles"""
    
    db = SessionLocal()
    
    try:
        # Get all users with their data
        users = db.query(User).all()
        
        user_data = []
        for user in users:
            # Get profile info
            profile_desc = ""
            photo_count = 0
            photo_urls = []
            
            if hasattr(user, 'profile') and user.profile:
                profile_desc = user.profile.description
                photo_count = len(user.profile.photos)
                photo_urls = [f"/{photo.file_path}" for photo in user.profile.photos]
            
            # Get expectations
            expectations_desc = ""
            if hasattr(user, 'expectations') and user.expectations:
                expectations_desc = user.expectations.description
            
            # Check completeness
            has_profile = bool(profile_desc)
            has_expectations = bool(expectations_desc)
            has_photo = photo_count > 0
            is_complete = has_profile and has_expectations and has_photo
            
            user_data.append({
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': user.is_active,
                'profile_description': profile_desc,
                'expectations_description': expectations_desc,
                'photo_count': photo_count,
                'photo_urls': photo_urls,
                'has_profile': has_profile,
                'has_expectations': has_expectations,
                'has_photo': has_photo,
                'is_complete': is_complete
            })
        
        # Sort by creation date (newest first)
        user_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "users": user_data,
            "total_users": len(user_data),
            "complete_profiles": sum(1 for u in user_data if u['is_complete'])
        })
    
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>")
    
    finally:
        db.close()

@app.get("/admin/user/{user_id}", response_class=HTMLResponse)
async def view_user_detail(request: Request, user_id: int):
    """View detailed user profile"""
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return HTMLResponse("<h1>User not found</h1>")
        
        # Get all user data
        profile_data = None
        if hasattr(user, 'profile') and user.profile:
            profile_data = {
                'description': user.profile.description,
                'created_at': user.profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'photos': [{'path': photo.file_path, 'url': f"/{photo.file_path}"} for photo in user.profile.photos]
            }
        
        expectations_data = None
        if hasattr(user, 'expectations') and user.expectations:
            expectations_data = {
                'description': user.expectations.description,
                'created_at': user.expectations.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return templates.TemplateResponse("user_detail.html", {
            "request": request,
            "user": {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': user.is_active
            },
            "profile": profile_data,
            "expectations": expectations_data
        })
    
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting theOne Admin Dashboard")
    print("📊 Visit: http://localhost:8001/admin")
    print("🔍 View user profiles submitted through your website")
    print()
    
    uvicorn.run(
        "admin_dashboard:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
