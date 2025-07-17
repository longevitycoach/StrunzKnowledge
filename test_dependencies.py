#!/usr/bin/env python3
"""
Test script to verify that the main dependencies can be imported successfully.
"""

import sys
import importlib

def test_import(package_name, description=""):
    """Test importing a package and return success status."""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} {description}")
        return True
    except ImportError as e:
        print(f"❌ {package_name} {description}: {e}")
        return False

def main():
    """Test all critical dependencies."""
    print("Testing critical dependencies...")
    
    success_count = 0
    total_count = 0
    
    # Core dependencies
    dependencies = [
        ("requests", "- HTTP requests"),
        ("beautifulsoup4", "- HTML parsing"),
        ("lxml", "- XML/HTML parser"),
        ("selenium", "- Web automation"),
        ("pandas", "- Data processing"),
        ("numpy", "- Numerical computing"),
        ("faiss", "- Vector search"),
        ("sentence_transformers", "- Text embeddings"),
        ("fastapi", "- Web framework"),
        ("uvicorn", "- ASGI server"),
        ("fastmcp", "- MCP framework"),
        ("langchain", "- LLM framework"),
        ("langchain_community", "- LLM extensions"),
        ("tiktoken", "- Token counting"),
        ("pydantic", "- Data validation"),
        ("loguru", "- Logging"),
    ]
    
    for package, description in dependencies:
        total_count += 1
        if test_import(package, description):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{total_count} dependencies imported successfully")
    
    if success_count == total_count:
        print("🎉 All dependencies are working correctly!")
        return 0
    else:
        print("⚠️  Some dependencies are missing or incompatible")
        return 1

if __name__ == "__main__":
    sys.exit(main())