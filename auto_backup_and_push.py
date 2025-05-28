#!/usr/bin/env python3
"""
Auto-backup and push script for theOne dating app
Automatically backs up database before git operations
"""
import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def backup_before_push():
    """Create backup before pushing code"""
    print("🗄️ theOne Auto-Backup and Push Tool")
    print("=" * 50)
    
    # 1. Check if database exists
    if not os.path.exists("theone_production.db"):
        print("⚠️ No database found - skipping backup")
    else:
        # 2. Create backup
        print("📦 Creating backup before push...")
        backup_success = run_command("python3 backup_database.py", "Database backup")
        
        if not backup_success:
            print("❌ Backup failed! Aborting push to prevent data loss.")
            return False
    
    # 3. Git operations
    print("\n🔄 Performing git operations...")
    
    # Add all changes
    if not run_command("git add .", "Adding changes to git"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("ℹ️ No changes to commit")
        return True
    
    # Get commit message
    commit_message = input("\n💬 Enter commit message (or press Enter for auto-message): ").strip()
    if not commit_message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Auto-commit: {timestamp}"
    
    # Commit changes
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_command(commit_cmd, "Committing changes"):
        return False
    
    # Push to remote
    if not run_command("git push origin main", "Pushing to remote repository"):
        return False
    
    print("\n🎉 Backup and push completed successfully!")
    print("💡 Your data is safely backed up in the 'backups/' directory")
    print("🔄 If you need to restore data later, run: python3 restore_database.py")
    
    return True

def main():
    """Main function"""
    try:
        success = backup_before_push()
        if not success:
            print("\n❌ Operation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
