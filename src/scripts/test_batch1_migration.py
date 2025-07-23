#!/usr/bin/env python3
"""
Test script for Batch 1 migration validation
Tests all 6 simple tools migrated from FastMCP to Official SDK
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp.mcp_sdk_clean import StrunzKnowledgeServer
import mcp.types as types

class Batch1MigrationTest:
    def __init__(self):
        self.server = StrunzKnowledgeServer()
        self.results = {}
        
    async def test_tool(self, tool_name: str, arguments: dict) -> Dict:
        """Test a single tool and measure performance"""
        start_time = time.time()
        
        try:
            # Access the decorated handler directly
            handler = None
            for attr_name in dir(self.server):
                attr = getattr(self.server, attr_name)
                if hasattr(attr, '__wrapped__') and hasattr(attr.__wrapped__, '__name__'):
                    if attr.__wrapped__.__name__ == 'call_tool':
                        handler = attr.__wrapped__
                        break
            
            if not handler:
                # Fallback: call the handler methods directly
                handler_method = getattr(self.server, f"_handle_{tool_name}", None)
                if handler_method:
                    result = await handler_method(arguments)
                else:
                    raise ValueError(f"No handler found for tool: {tool_name}")
            else:
                # Call through the decorated handler
                result = await handler(tool_name, arguments)
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return {
                "tool_name": tool_name,
                "status": "success",
                "response_time_ms": response_time_ms,
                "result_preview": str(result[0].text)[:200] if result else "No result",
                "arguments": arguments
            }
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return {
                "tool_name": tool_name,
                "status": "error",
                "error": str(e),
                "response_time_ms": response_time_ms,
                "arguments": arguments
            }
    
    async def run_batch1_tests(self):
        """Run all Batch 1 tool tests"""
        print("🧪 Testing Batch 1 Migration - Simple Tools")
        print("=" * 60)
        
        # Define test cases for each tool
        test_cases = [
            ("knowledge_search", {"query": "vitamin D deficiency symptoms"}),
            ("summarize_posts", {"category": "nutrition", "limit": 5}),
            ("get_health_assessment_questions", {"user_role": "patient", "assessment_depth": "basic"}),
            ("get_dr_strunz_biography", {"include_achievements": True, "include_philosophy": True}),
            ("get_mcp_server_purpose", {}),
            ("get_vector_db_analysis", {})
        ]
        
        # Expected baseline times from Phase 1
        baseline_times = {
            "knowledge_search": 155.4,
            "summarize_posts": 100.6,
            "get_health_assessment_questions": 54.0,
            "get_dr_strunz_biography": 75.2,
            "get_mcp_server_purpose": 29.3,
            "get_vector_db_analysis": 105.1
        }
        
        print(f"Testing {len(test_cases)} tools...\n")
        
        all_passed = True
        
        for tool_name, arguments in test_cases:
            print(f"Testing {tool_name}...")
            result = await self.test_tool(tool_name, arguments)
            self.results[tool_name] = result
            
            if result["status"] == "success":
                baseline = baseline_times.get(tool_name, 100)
                regression_percent = ((result["response_time_ms"] - baseline) / baseline) * 100
                
                # Check for >50% regression
                if regression_percent > 50:
                    print(f"  ❌ FAIL - Performance regression: {regression_percent:.1f}%")
                    print(f"     Baseline: {baseline:.1f}ms, Current: {result['response_time_ms']:.1f}ms")
                    all_passed = False
                else:
                    print(f"  ✅ PASS - {result['response_time_ms']:.1f}ms (vs baseline {baseline:.1f}ms)")
                    print(f"     Performance: {regression_percent:+.1f}%")
            else:
                print(f"  ❌ FAIL - Error: {result['error']}")
                all_passed = False
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 Batch 1 Migration Test Summary")
        print(f"{'='*60}")
        
        successful = sum(1 for r in self.results.values() if r["status"] == "success")
        failed = len(self.results) - successful
        
        print(f"Total Tools Tested: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            avg_time = sum(r["response_time_ms"] for r in self.results.values() if r["status"] == "success") / successful
            print(f"Average Response Time: {avg_time:.1f}ms")
        
        print(f"\nOverall Result: {'✅ ALL TESTS PASS' if all_passed else '❌ SOME TESTS FAILED'}")
        
        # Save detailed results
        results_file = project_root / "docs" / "validation_results" / f"batch1_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                "test_date": time.strftime('%Y-%m-%d %H:%M:%S'),
                "batch": "Batch 1 - Simple Tools",
                "tools_tested": len(self.results),
                "successful": successful,
                "failed": failed,
                "all_passed": all_passed,
                "results": self.results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return all_passed

async def main():
    """Main entry point"""
    tester = Batch1MigrationTest()
    success = await tester.run_batch1_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))