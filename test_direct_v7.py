#!/usr/bin/env python3
"""
Test v7 directly to see startup logs
"""

import subprocess
import time
import sys
import os

# Kill any existing servers
os.system("lsof -ti:8080 | xargs kill -9 2>/dev/null || true")
time.sleep(1)

# Start the server
print("🚀 Starting v7 server with visible logs...")
env = os.environ.copy()
env['PORT'] = '8080'

process = subprocess.Popen(
    [sys.executable, 'src/mcp/sse_server_v7.py'],
    cwd='/Users/ma3u/projects/StrunzKnowledge',
    env=env
)

try:
    # Let it run for 30 seconds
    time.sleep(30)
except KeyboardInterrupt:
    pass
finally:
    process.terminate()
    print("\nServer stopped")