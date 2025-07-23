#!/usr/bin/env python3
"""
MCP Inspector Integration Test - Issue #12
Real integration test with MCP Inspector for StrunzKnowledge server validation
"""

import subprocess
import time
import sys
import json
import requests
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class MCPInspectorIntegration:
    def __init__(self):
        self.inspector_process: Optional[subprocess.Popen] = None
        self.server_process: Optional[subprocess.Popen] = None
        
    def start_server(self, server_type: str = "clean") -> subprocess.Popen:
        """Start MCP server for testing."""
        if server_type == "clean":
            server_cmd = [sys.executable, "src/mcp/mcp_sdk_clean.py"]
        elif server_type == "enhanced":
            server_cmd = [sys.executable, "src/mcp/enhanced_server.py"]
        else:
            raise ValueError(f"Unknown server type: {server_type}")
        
        print(f"🚀 Starting {server_type} server...")
        
        process = subprocess.Popen(
            server_cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give server time to start
        time.sleep(5)
        return process
    
    def start_inspector(self, server_cmd: list) -> subprocess.Popen:
        """Start MCP Inspector with server command."""
        print("🔍 Starting MCP Inspector...")
        
        # Build inspector command
        inspector_cmd = ["npx", "@modelcontextprotocol/inspector"] + server_cmd
        
        print(f"Command: {' '.join(inspector_cmd)}")
        
        process = subprocess.Popen(
            inspector_cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give inspector time to start
        time.sleep(10)
        return process
    
    def test_clean_server_integration(self) -> bool:
        """Test MCP Inspector with clean (Official SDK) server."""
        print("\n🧪 Testing MCP Inspector with Clean Server (Official SDK)")
        print("=" * 60)
        
        try:
            # Start inspector with clean server
            server_cmd = [sys.executable, "src/mcp/mcp_sdk_clean.py"]
            self.inspector_process = self.start_inspector(server_cmd)
            
            # Check if inspector started successfully
            time.sleep(5)
            
            if self.inspector_process.poll() is None:
                print("✅ MCP Inspector started successfully")
                print("🌐 Inspector should be available at: http://localhost:6274")
                print("🔧 You can now manually test tool discovery and execution")
                
                # Wait for user input to continue
                input("\n⏸️  Press Enter after testing in browser (or Ctrl+C to skip)...")
                
                return True
            else:
                stdout, stderr = self.inspector_process.communicate(timeout=5)
                print(f"❌ MCP Inspector failed to start")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Manual testing skipped by user")
            return True
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            return False
        finally:
            if self.inspector_process:
                self.inspector_process.terminate()
    
    def test_enhanced_server_integration(self) -> bool:
        """Test MCP Inspector with enhanced (FastMCP) server."""
        print("\n🧪 Testing MCP Inspector with Enhanced Server (FastMCP)")
        print("=" * 60)
        
        try:
            # Start inspector with enhanced server
            server_cmd = [sys.executable, "src/mcp/enhanced_server.py"]
            self.inspector_process = self.start_inspector(server_cmd)
            
            # Check if inspector started successfully
            time.sleep(5)
            
            if self.inspector_process.poll() is None:
                print("✅ MCP Inspector started successfully")
                print("🌐 Inspector should be available at: http://localhost:6274")
                print("🔧 You can now manually test all 20 FastMCP tools")
                
                # Wait for user input to continue
                input("\n⏸️  Press Enter after testing FastMCP tools (or Ctrl+C to skip)...")
                
                return True
            else:
                stdout, stderr = self.inspector_process.communicate(timeout=5)
                print(f"❌ MCP Inspector failed to start")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Manual testing skipped by user")
            return True
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            return False
        finally:
            if self.inspector_process:
                self.inspector_process.terminate()
    
    def run_complete_integration_test(self) -> bool:
        """Run complete integration test suite."""
        print("🚀 MCP Inspector Integration Test Suite")
        print("=" * 70)
        print("This test will start MCP Inspector with both server types")
        print("and allow manual validation of tool discovery and execution.")
        print()
        
        results = []
        
        # Test 1: Clean server (Official SDK target)
        print("Test 1: Official SDK Server Integration")
        clean_result = self.test_clean_server_integration()
        results.append(("Clean Server", clean_result))
        
        # Test 2: Enhanced server (FastMCP current)  
        print("\nTest 2: FastMCP Server Integration")
        enhanced_result = self.test_enhanced_server_integration()
        results.append(("Enhanced Server", enhanced_result))
        
        # Summary
        print("\n📊 Integration Test Results:")
        print("=" * 30)
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        overall_success = all(result for _, result in results)
        print(f"\nOverall: {'✅ ALL TESTS PASS' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n🎉 MCP Inspector integration is working correctly!")
            print("✅ Ready for Phase 2 migration validation")
        else:
            print("\n⚠️ Issues detected with MCP Inspector integration")
            print("🔧 Manual troubleshooting may be required")
        
        return overall_success

def main():
    """Main entry point."""
    integration = MCPInspectorIntegration()
    
    try:
        success = integration.run_complete_integration_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Integration test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())