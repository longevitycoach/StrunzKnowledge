#!/usr/bin/env python3
"""
Production server starter for Railway deployment
Ensures the SSE-enabled MCP server is started in production mode
"""
import os
import sys

# Force production mode for Railway
os.environ['RAILWAY_ENVIRONMENT'] = 'production'

# Import and run main
from main import main

if __name__ == "__main__":
    print("Starting production server with SSE support...")
    main()