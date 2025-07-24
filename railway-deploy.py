#!/usr/bin/env python3
"""
Railway deployment entry point for production

This script is specifically designed for Railway.app deployment.
It imports and runs the unified main entry point with HTTP transport.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

# Set Railway environment
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ.setdefault('RAILWAY_PUBLIC_DOMAIN', 'strunz.up.railway.app')
os.environ.setdefault('RAILWAY_PRIVATE_DOMAIN', 'strunz.railway.internal')
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('LOG_LEVEL', 'INFO')

# Force HTTP transport for Railway
os.environ['TRANSPORT'] = 'http'

# Import and run the unified main entry point
from main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Railway deployment error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)