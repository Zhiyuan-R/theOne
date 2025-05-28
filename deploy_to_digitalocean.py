#!/usr/bin/env python3
"""
Deployment script for DigitalOcean with data backup
"""
import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description, check=True):
    """Run a shell command"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def backup_before_deploy():
    """Create backup before deployment"""
    print("📦 Creating backup before deployment...")
    
    if not os.path.exists("theone_production.db"):
        print("⚠️ No local database found - skipping backup")
        return True
    
    return run_command("python3 backup_database.py", "Creating backup", check=False)

def deploy_to_digitalocean():
    """Deploy to DigitalOcean App Platform"""
    print("🚀 theOne DigitalOcean Deployment Tool")
    print("=" * 50)
    
    # 1. Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check if doctl is installed
    if not run_command("doctl version", "Checking doctl installation", check=False):
        print("❌ doctl is not installed!")
        print("💡 Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/")
        return False
    
    # Check if authenticated
    if not run_command("doctl auth list", "Checking authentication", check=False):
        print("❌ Not authenticated with DigitalOcean!")
        print("💡 Run: doctl auth init")
        return False
    
    # 2. Create backup
    if not backup_before_deploy():
        print("⚠️ Backup failed, but continuing with deployment...")
    
    # 3. Prepare for deployment
    print("\n🔄 Preparing for deployment...")
    
    # Add all changes
    if not run_command("git add .", "Adding changes to git"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode != 0:
        # Get commit message
        commit_message = input("\n💬 Enter commit message (or press Enter for auto-message): ").strip()
        if not commit_message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Deploy to DigitalOcean: {timestamp}"
        
        # Commit changes
        if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
            return False
    
    # 4. Push to GitHub (triggers DigitalOcean deployment)
    print("\n🚀 Deploying to DigitalOcean...")
    if not run_command("git push origin main", "Pushing to GitHub (triggers deployment)"):
        return False
    
    # 5. Check app status (optional)
    print("\n📊 Checking app status...")
    run_command("doctl apps list", "Listing apps", check=False)
    
    print("\n🎉 Deployment initiated successfully!")
    print("📱 Your app will be available at your DigitalOcean App Platform URL")
    print("🔄 Deployment may take a few minutes to complete")
    print("📊 Monitor deployment: https://cloud.digitalocean.com/apps")
    
    return True

def main():
    """Main deployment function"""
    try:
        success = deploy_to_digitalocean()
        if not success:
            print("\n❌ Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
