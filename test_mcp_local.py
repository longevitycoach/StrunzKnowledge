#!/usr/bin/env python3
"""Test MCP server locally"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp.enhanced_server import main

if __name__ == "__main__":
    # FastMCP automatically handles stdio when run as main
    app = main()
    
    # Check if FastMCP has run_stdio method
    if hasattr(app, 'run_stdio'):
        app.run_stdio()
    elif hasattr(app, 'serve'):
        app.serve()
    else:
        print(f"Available methods: {dir(app)}")
        print("FastMCP app created but no stdio runner found")