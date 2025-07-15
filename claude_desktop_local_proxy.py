#!/usr/bin/env python3
"""
Claude Desktop Local Proxy for Strunz Knowledge MCP Server
Uses FastMCP to create a local STDIO proxy to the remote Railway server
"""

import requests
import json
from fastmcp import FastMCP

# Create FastMCP app for Claude Desktop
app = FastMCP("Strunz Knowledge Proxy")

# Railway server URL
REMOTE_URL = "https://strunz.up.railway.app"

def make_remote_request(method: str, params: dict = None) -> dict:
    """Make request to remote MCP server"""
    request_data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1
    }
    
    try:
        response = requests.post(f"{REMOTE_URL}/mcp", json=request_data)
        if response.status_code == 200:
            return response.json().get("result", {})
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Define all MCP tools as proxies
@app.tool()
def knowledge_search(query: str, sources: list = None, limit: int = 10) -> dict:
    """Search Dr. Strunz knowledge base"""
    return make_remote_request("tools/call", {
        "name": "knowledge_search",
        "arguments": {"query": query, "sources": sources, "limit": limit}
    })

@app.tool()
def get_mcp_server_purpose() -> dict:
    """Get information about the MCP server"""
    return make_remote_request("tools/call", {
        "name": "get_mcp_server_purpose",
        "arguments": {}
    })

@app.tool()
def get_dr_strunz_biography(include_achievements: bool = True, include_philosophy: bool = True) -> dict:
    """Get Dr. Strunz biography"""
    return make_remote_request("tools/call", {
        "name": "get_dr_strunz_biography",
        "arguments": {"include_achievements": include_achievements, "include_philosophy": include_philosophy}
    })

@app.tool()
def create_health_protocol(condition: str, user_profile: dict = None, severity: str = "moderate") -> dict:
    """Create health protocol"""
    return make_remote_request("tools/call", {
        "name": "create_health_protocol",
        "arguments": {"condition": condition, "user_profile": user_profile, "severity": severity}
    })

@app.tool()
def analyze_supplement_stack(supplements: list, health_goals: list, check_interactions: bool = True) -> dict:
    """Analyze supplement stack"""
    return make_remote_request("tools/call", {
        "name": "analyze_supplement_stack",
        "arguments": {"supplements": supplements, "health_goals": health_goals, "check_interactions": check_interactions}
    })

@app.tool()
def nutrition_calculator(age: int, gender: str, weight: float, height: float, activity_level: str, health_goals: list) -> dict:
    """Calculate nutrition recommendations"""
    return make_remote_request("tools/call", {
        "name": "nutrition_calculator",
        "arguments": {
            "age": age, "gender": gender, "weight": weight, "height": height,
            "activity_level": activity_level, "health_goals": health_goals
        }
    })

@app.tool()
def find_contradictions(topic: str, include_reasoning: bool = True) -> dict:
    """Find contradictions in health topics"""
    return make_remote_request("tools/call", {
        "name": "find_contradictions",
        "arguments": {"topic": topic, "include_reasoning": include_reasoning}
    })

@app.tool()
def trace_topic_evolution(topic: str, start_year: int = None, end_year: int = None) -> dict:
    """Trace topic evolution over time"""
    return make_remote_request("tools/call", {
        "name": "trace_topic_evolution",
        "arguments": {"topic": topic, "start_year": start_year, "end_year": end_year}
    })

@app.tool()
def get_vector_db_analysis() -> dict:
    """Get vector database analysis"""
    return make_remote_request("tools/call", {
        "name": "get_vector_db_analysis",
        "arguments": {}
    })

@app.tool()
def get_optimal_diagnostic_values(age: int, gender: str, weight: float = None, height: float = None, athlete: bool = False) -> dict:
    """Get optimal diagnostic values"""
    return make_remote_request("tools/call", {
        "name": "get_optimal_diagnostic_values",
        "arguments": {"age": age, "gender": gender, "weight": weight, "height": height, "athlete": athlete}
    })

if __name__ == "__main__":
    # Test connection to remote server
    import sys
    print("Testing connection to remote server...", file=sys.stderr)
    try:
        response = requests.get(f"{REMOTE_URL}/")
        if response.status_code == 200:
            print("✓ Remote server is accessible", file=sys.stderr)
            print(f"  Server: {response.json()['server']}", file=sys.stderr)
            print(f"  Version: {response.json()['version']}", file=sys.stderr)
        else:
            print(f"✗ Remote server not accessible: {response.status_code}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"✗ Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\nStarting FastMCP proxy for Claude Desktop...", file=sys.stderr)
    print("Use this with Claude Desktop via STDIO transport", file=sys.stderr)
    app.run()  # STDIO transport for Claude Desktop