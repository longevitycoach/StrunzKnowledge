# Claude Integration Guide

## Overview

This guide explains how to integrate the Strunz Knowledge MCP server with Claude Desktop and Claude.ai.

## Important: Transport Limitations

⚠️ **Claude Desktop and Claude.ai do NOT support direct HTTP-SSE transport for MCP servers.**

### What Works:
- ✅ **Local STDIO transport** (Claude Desktop only)
- ✅ **Remote servers via Settings > Connectors** (certain plans only, requires OAuth)
- ✅ **Railway deployment** (for API access, not Claude Desktop)

### What Doesn't Work:
- ❌ Direct HTTP-SSE connections from Claude Desktop
- ❌ Adding SSE URLs to claude_desktop_config.json
- ❌ Unauthenticated remote servers

## Setup Options

### Option 1: Local Proxy (Recommended)

For Claude Desktop users who want to connect to the Railway deployment:

1. **Install dependencies**:
   ```bash
   pip install fastmcp requests
   ```

2. **Run the setup script**:
   ```bash
   python setup_claude_desktop.py
   ```

3. **Restart Claude Desktop**

4. The proxy will automatically connect to the Railway deployment at https://strunz.up.railway.app

### Option 2: Direct Local Installation

Run the MCP server locally without Railway:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/longevitycoach/StrunzKnowledge.git
   cd StrunzKnowledge
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop**:
   Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "strunz-knowledge": {
         "command": "python",
         "args": ["/path/to/StrunzKnowledge/src/mcp/enhanced_server.py"],
         "env": {}
       }
     }
   }
   ```

4. **Restart Claude Desktop**

### Option 3: Remote Server (Future)

When Claude adds full remote server support:

1. The Railway deployment will be directly accessible
2. OAuth authentication will be implemented
3. No local proxy will be needed

## Troubleshooting

### Common Issues

1. **"MCP error -32000: Connection closed"**
   - This means Claude is trying to connect via HTTP-SSE
   - Use the local proxy instead

2. **"Failed to connect to remote MCP server"**
   - Claude.ai doesn't support custom remote servers yet
   - Use Claude Desktop with local proxy

3. **"No vector store available"**
   - The FAISS indices need to be loaded
   - Check Railway logs for reconstruction errors

### Testing the Server

1. **Test Railway deployment**:
   ```bash
   curl https://strunz.up.railway.app/
   ```

2. **Test local proxy**:
   ```bash
   python test_with_fast_agent.py
   ```

3. **Test MCP tools**:
   ```bash
   python test_mcp_inspector.py
   ```

## Available Tools

Once connected, you'll have access to 19 MCP tools:

- `knowledge_search` - Search Dr. Strunz's knowledge base
- `create_health_protocol` - Create personalized health protocols
- `analyze_supplement_stack` - Analyze supplement combinations
- `nutrition_calculator` - Calculate nutrition recommendations
- `find_contradictions` - Find evolving viewpoints
- `trace_topic_evolution` - Track topic changes over time
- `get_optimal_diagnostic_values` - Get optimal lab values
- And 12 more specialized tools...

## Example Usage

After setup, you can ask Claude:

- "Create a health protocol for vitamin D deficiency"
- "What are Dr. Strunz's recommendations for immune support?"
- "Analyze my supplement stack: Vitamin D, Magnesium, Omega-3"
- "Show me how Dr. Strunz's views on cholesterol evolved"

## Technical Details

- **Protocol**: Model Context Protocol (MCP)
- **Transport**: STDIO (local), HTTP-SSE (Railway)
- **Framework**: FastMCP
- **Vector DB**: FAISS with sentence-transformers
- **Deployment**: Railway (https://strunz.up.railway.app)