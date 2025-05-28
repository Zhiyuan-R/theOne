#!/bin/bash

# Deploy theOne dating app to DigitalOcean with image serving fixes
# This script ensures images work correctly in production

echo "🚀 Deploying theOne Dating App with Image Serving Fixes"
echo "======================================================="

# Check if we have the necessary files
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Run this script from the project root."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it first."
    exit 1
fi

# Commit and push changes
echo "📝 Committing image serving fixes..."
git add .
git commit -m "Fix image serving for DigitalOcean deployment

- Updated get_photo_url() function to work correctly in production
- Added UPLOADS_PATH environment variable for production
- Created diagnostic and fix scripts for troubleshooting
- Enhanced health check endpoint with upload directory status
- Added comprehensive troubleshooting guide"

echo "📤 Pushing to GitHub..."
git push origin main

echo "⏳ Waiting for DigitalOcean deployment to complete..."
echo "   This may take 2-3 minutes..."

# Wait for deployment
sleep 30

echo "🔍 Getting app URL..."
# You'll need to replace this with your actual app URL
APP_URL="https://theone-dating-app-xxxxx.ondigitalocean.app"

echo "📋 Post-deployment checks:"
echo "=========================="

echo "1. Checking health endpoint..."
curl -s "$APP_URL/health" | python3 -m json.tool

echo ""
echo "2. Testing image serving..."
# This will show if the uploads directory is properly mounted
curl -I "$APP_URL/uploads/" 2>/dev/null | head -1

echo ""
echo "3. Manual steps to complete:"
echo "   a) SSH into your DigitalOcean app (if possible) or use the console"
echo "   b) Run: python3 debug_image_serving.py"
echo "   c) Run: python3 fix_image_paths.py"
echo "   d) Test image URLs in browser"

echo ""
echo "🔗 Useful URLs:"
echo "   App: $APP_URL"
echo "   Admin: $APP_URL/admin"
echo "   Health: $APP_URL/health"

echo ""
echo "🛠️  If images still don't work:"
echo "   1. Check the troubleshooting guide: IMAGE_SERVING_GUIDE.md"
echo "   2. Run diagnostic script on the server"
echo "   3. Verify DigitalOcean volume mounts are working"
echo "   4. Check that UPLOADS_PATH environment variable is set"

echo ""
echo "✅ Deployment script complete!"
echo "   Monitor the DigitalOcean dashboard for deployment status."
