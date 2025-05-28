#!/usr/bin/env python3
"""
Quick start script for the BDSM dating app server
"""
import subprocess
import sys
import webbrowser
import time
import requests
from threading import Timer


def check_server_ready(url, max_attempts=30):
    """Check if server is ready to accept connections"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def open_browser_delayed(url, delay=3):
    """Open browser after a delay"""
    def open_browser():
        print(f"🌐 Opening browser to {url}")
        webbrowser.open(url)
    
    Timer(delay, open_browser).start()


def main():
    """Start the server and optionally open browser"""
    print("🚀 Starting BDSM Dating App Server")
    print("=" * 50)
    
    server_url = "http://localhost:8000"
    docs_url = f"{server_url}/docs"
    
    print(f"📍 Server URL: {server_url}")
    print(f"📖 API Docs: {docs_url}")
    print(f"💚 Health Check: {server_url}/health")
    print("\n🔧 Starting FastAPI server...")
    print("Press Ctrl+C to stop")
    
    # Schedule browser opening
    open_browser_delayed(docs_url, delay=3)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    main()
