#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base - Main Entry Point

This is the main entry point for the Dr. Strunz Knowledge Base MCP Server.
For production deployment, use the scripts in src/scripts/deployment/

Environment Variables:
- RAILWAY_PUBLIC_DOMAIN: Public domain for Railway deployment (default: strunz.up.railway.app)
- RAILWAY_PRIVATE_DOMAIN: Private domain for Railway internal (default: strunz.railway.internal)
- PORT: Server port (default: 8000)
- LOG_LEVEL: Logging level (default: INFO)
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set default Railway domains
os.environ.setdefault('RAILWAY_PUBLIC_DOMAIN', 'strunz.up.railway.app')
os.environ.setdefault('RAILWAY_PRIVATE_DOMAIN', 'strunz.railway.internal')
os.environ.setdefault('PORT', '8000')
os.environ.setdefault('LOG_LEVEL', 'INFO')

def main():
    """Main entry point - determines which server to run."""
    
    # Check environment
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    
    if is_railway and is_production:
        # Production Railway deployment with enhanced server
        print("Starting production Railway deployment with enhanced server...")
        from src.scripts.deployment.railway_production_server import main as run_server
    elif is_railway:
        # Non-production Railway deployment
        print("Starting Railway deployment...")
        from src.scripts.deployment.railway_mcp_server import main as run_server
    else:
        # Local development
        print("Starting local development server...")
        from src.mcp.enhanced_server import main as run_server
    
    # Run the appropriate server
    if is_railway and is_production:
        # Direct function call for production (no asyncio.run)
        run_server()
    else:
        # Use asyncio for other servers
        import asyncio
        asyncio.run(run_server())

if __name__ == "__main__":
    main()