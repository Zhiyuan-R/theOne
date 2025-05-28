#!/usr/bin/env python3
"""
Remote monitoring script for theOne dating app on DigitalOcean
Monitor user registrations from your local machine
"""

import requests
import json
import time
import os
from datetime import datetime

class RemoteMonitor:
    def __init__(self, server_ip, server_port=80):
        self.base_url = f"http://{server_ip}:{server_port}"
        self.last_check = None
        
    def get_user_stats(self):
        """Get user statistics from remote server"""
        try:
            # Try to get admin page (we'll parse HTML for now)
            response = requests.get(f"{self.base_url}/admin", timeout=10)
            
            if response.status_code == 200:
                # Simple HTML parsing to extract user count
                html = response.text
                
                # Look for user count in the HTML
                import re
                
                # Extract total users
                total_match = re.search(r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">Total Users</div>', html)
                total_users = int(total_match.group(1)) if total_match else 0
                
                # Extract complete profiles
                complete_match = re.search(r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">Complete Profiles</div>', html)
                complete_profiles = int(complete_match.group(1)) if complete_match else 0
                
                return {
                    'status': 'success',
                    'total_users': total_users,
                    'complete_profiles': complete_profiles,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'status': 'error',
                    'message': f"HTTP {response.status_code}",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def check_health(self):
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def monitor_once(self):
        """Single monitoring check"""
        print(f"🔍 Checking server at {self.base_url}")
        print("=" * 50)
        
        # Check health first
        if not self.check_health():
            print("❌ Server is not responding")
            print("   Check if your DigitalOcean app is running")
            return
        
        print("✅ Server is healthy")
        
        # Get user stats
        stats = self.get_user_stats()
        
        if stats['status'] == 'success':
            print(f"📊 User Statistics ({stats['timestamp']}):")
            print(f"   👥 Total Users: {stats['total_users']}")
            print(f"   ✅ Complete Profiles: {stats['complete_profiles']}")
            
            if stats['total_users'] > 0:
                completion_rate = (stats['complete_profiles'] / stats['total_users']) * 100
                print(f"   📈 Completion Rate: {completion_rate:.1f}%")
            
            # Check for new users
            if self.last_check and stats['total_users'] > self.last_check.get('total_users', 0):
                new_users = stats['total_users'] - self.last_check.get('total_users', 0)
                print(f"🎉 {new_users} new user(s) since last check!")
            
            self.last_check = stats
            
        else:
            print(f"❌ Error getting stats: {stats['message']}")
        
        print()
    
    def monitor_continuous(self, interval=30):
        """Continuous monitoring with specified interval"""
        print(f"🚀 Starting continuous monitoring of {self.base_url}")
        print(f"⏰ Checking every {interval} seconds")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                self.monitor_once()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("👋 Monitoring stopped")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 remote_monitor.py <server_ip>                    - Single check")
        print("  python3 remote_monitor.py <server_ip> continuous [interval] - Continuous monitoring")
        print()
        print("Examples:")
        print("  python3 remote_monitor.py 164.90.123.456")
        print("  python3 remote_monitor.py 164.90.123.456 continuous")
        print("  python3 remote_monitor.py 164.90.123.456 continuous 60")
        return
    
    server_ip = sys.argv[1]
    monitor = RemoteMonitor(server_ip)
    
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'continuous':
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        monitor.monitor_continuous(interval)
    else:
        monitor.monitor_once()

if __name__ == "__main__":
    main()
