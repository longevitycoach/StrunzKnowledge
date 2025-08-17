#!/usr/bin/env python3
"""
Test script to verify frontend changes
"""
import subprocess
import time
import requests
import webbrowser
import signal
import sys

def signal_handler(sig, frame):
    print('\nShutting down test server...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("Starting test server on http://localhost:8080")
print("Press Ctrl+C to stop\n")

# Start the server
server = subprocess.Popen(['python', '-m', 'http.server', '8080'], 
                         cwd='frontend',
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

time.sleep(2)

print("Server started. Testing endpoints...")

try:
    # Test if server is running
    response = requests.get('http://localhost:8080/')
    print(f"✅ Server responding: {response.status_code}")
    
    # Open in browser
    print("\n📌 Opening http://localhost:8080 in your browser...")
    print("📌 Please test the following:")
    print("   1. Check if the welcome message is compact")
    print("   2. Type 'help' and press Enter") 
    print("   3. Verify the help output is compact")
    print("\n⚠️  Clear browser cache (Cmd+Shift+R) if you see old content!")
    
    webbrowser.open('http://localhost:8080')
    
    print("\nServer is running. Press Ctrl+C to stop.")
    server.wait()
    
except KeyboardInterrupt:
    print("\nShutting down...")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.terminate()
    server.wait()