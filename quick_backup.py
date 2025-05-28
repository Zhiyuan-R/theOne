#!/usr/bin/env python3
"""
Quick backup script for theOne dating app
Creates a quick backup with minimal output
"""
import os
import sys
from backup_database import backup_database

def main():
    """Quick backup with minimal output"""
    print("🔄 Creating quick backup...")
    
    backup_dir = backup_database()
    
    if backup_dir:
        print(f"✅ Backup created: {backup_dir}")
        
        # Show quick stats
        if os.path.exists(f"{backup_dir}/backup_summary.json"):
            import json
            with open(f"{backup_dir}/backup_summary.json", "r") as f:
                summary = json.load(f)
            print(f"📊 {summary.get('total_users', 0)} users, {summary.get('total_photos', 0)} photos backed up")
    else:
        print("❌ Backup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
