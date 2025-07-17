#!/usr/bin/env python3
"""
Local proxy for Claude Desktop to connect to the Strunz Knowledge MCP server.
This script runs the enhanced server in stdio mode for Claude Desktop.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the enhanced server
from src.mcp.enhanced_server import main

if __name__ == "__main__":
    # Set environment to ensure stdio mode
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    # Run the server
    main()