#!/usr/bin/env python3
"""
Stdio server for Claude Desktop - properly handles FastMCP
"""

import sys
import os

# No print statements to stdout! They break JSON-RPC
# All debug output must go to stderr

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Suppress all stdout prints from imports
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

try:
    # Import after redirecting stdout
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    
    # Restore stdout for JSON-RPC communication
    sys.stdout = old_stdout
    
    # Create server
    server = StrunzKnowledgeMCP()
    
    # Debug to stderr only
    print("FastMCP server created", file=sys.stderr)
    print(f"Server type: {type(server.app)}", file=sys.stderr)
    
    # Run in stdio mode
    # FastMCP has run() method that defaults to stdio
    print("Running FastMCP in stdio mode", file=sys.stderr)
    server.app.run()
        
except Exception as e:
    # Restore stdout to report error
    sys.stdout = old_stdout
    
    # Log error to stderr
    import traceback
    print(f"Server error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Send error response in JSON-RPC format
    import json
    error_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32603,
            "message": f"Server initialization failed: {str(e)}"
        },
        "id": None
    }
    print(json.dumps(error_response))
    sys.exit(1)