#!/usr/bin/env python3
"""
MCP Server compatible with MCP Inspector
Uses the standard stdio transport that Inspector expects
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Use your existing MCP SDK server which supports stdio
from src.mcp.mcp_sdk_clean import main
import asyncio

if __name__ == "__main__":
    # The MCP SDK server already supports stdio transport
    # which is what the Inspector expects
    asyncio.run(main())