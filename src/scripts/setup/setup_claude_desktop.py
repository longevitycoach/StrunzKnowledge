#!/usr/bin/env python3
"""
Setup script for Claude Desktop integration with Strunz Knowledge MCP Server
"""

import json
import os
import sys
from pathlib import Path

def get_claude_config_path():
    """Get Claude Desktop configuration path"""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"

def setup_claude_desktop():
    """Setup Claude Desktop configuration"""
    print("=== Claude Desktop Setup for Strunz Knowledge MCP Server ===")
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    proxy_script = current_dir / "claude_desktop_local_proxy.py"
    
    if not proxy_script.exists():
        print(f"✗ Proxy script not found: {proxy_script}")
        return False
    
    # Get Claude config path
    config_path = get_claude_config_path()
    print(f"Claude config path: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}
    
    # Add MCP server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["strunz-knowledge"] = {
        "command": "python",
        "args": [str(proxy_script)],
        "env": {}
    }
    
    # Write config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Configuration written to {config_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to write configuration: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n=== Testing Setup ===")
    
    # Test proxy script
    proxy_script = Path(__file__).parent / "claude_desktop_local_proxy.py"
    if not proxy_script.exists():
        print("✗ Proxy script not found")
        return False
    
    print("✓ Proxy script found")
    
    # Test Python execution
    import subprocess
    try:
        result = subprocess.run([sys.executable, str(proxy_script)], 
                              capture_output=True, text=True, timeout=5)
        if "✓ Remote server is accessible" in result.stderr:
            print("✓ Proxy can connect to remote server")
        else:
            print("✗ Proxy cannot connect to remote server")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✓ Proxy started successfully (timeout expected)")
    except Exception as e:
        print(f"✗ Proxy test failed: {e}")
        return False
    
    return True

def print_instructions():
    """Print setup instructions"""
    print("\n=== Setup Complete ===")
    print("📋 Instructions:")
    print("1. Restart Claude Desktop application")
    print("2. The 'Strunz Knowledge' MCP server should appear in your available tools")
    print("3. You can now ask Claude about Dr. Strunz's health recommendations")
    print()
    print("🔧 Available tools:")
    print("  - knowledge_search: Search Dr. Strunz's knowledge base")
    print("  - create_health_protocol: Create personalized health protocols")
    print("  - analyze_supplement_stack: Analyze supplement combinations")
    print("  - nutrition_calculator: Calculate nutrition recommendations")
    print("  - get_dr_strunz_biography: Get Dr. Strunz's background")
    print("  - trace_topic_evolution: Track health topic evolution")
    print("  - get_optimal_diagnostic_values: Get optimal lab values")
    print("  - And 12 more specialized tools...")
    print()
    print("💡 Example usage:")
    print("  'Create a health protocol for vitamin D deficiency'")
    print("  'What are Dr. Strunz's recommendations for immune support?'")
    print("  'Analyze my supplement stack: Vitamin D, Magnesium, Omega-3'")

def main():
    """Main setup function"""
    print("Starting Claude Desktop setup...\n")
    
    # Setup configuration
    if not setup_claude_desktop():
        print("❌ Setup failed!")
        return 1
    
    # Test setup
    if not test_setup():
        print("❌ Setup test failed!")
        return 1
    
    # Print instructions
    print_instructions()
    
    print("\n✅ Claude Desktop setup completed successfully!")
    print("🚀 You can now use the Strunz Knowledge MCP server with Claude Desktop!")
    
    return 0

if __name__ == "__main__":
    exit(main())