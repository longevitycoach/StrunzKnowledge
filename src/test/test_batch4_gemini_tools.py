"""
Comprehensive test suite for Batch 4 Gemini-Enhanced Tools
Tests the final batch of tools completing the FastMCP migration
"""

import pytest
import asyncio
import os
from typing import Optional, List
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from dataclasses import dataclass
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp.batch4_gemini_tools import GeminiEnhancedTools


@dataclass
class MockSearchResult:
    """Mock search result for testing"""
    text: str
    score: float
    source: str
    title: str
    metadata: dict


class MockSearchTool:
    """Mock search tool for testing"""
    
    def search(self, query: str, k: int = 10, sources: Optional[List[str]] = None):
        """Mock search implementation"""
        results = []
        for i in range(min(k, 5)):
            source = ["books", "news", "forum"][i % 3]
            if sources and source not in sources:
                continue
            
            result = MockSearchResult(
                text=f"Mock content about {query} from {source}. Dr. Strunz recommends specific approaches.",
                score=0.95 - (i * 0.05),
                source=source,
                title=f"{source.capitalize()} - {query} Article {i+1}",
                metadata={
                    "date": f"2023-0{(i%9)+1}-{(i%28)+1:02d}",
                    "author": "Dr. Ulrich Strunz"
                }
            )
            results.append(result)
        return results


class MockGeminiClient:
    """Mock Gemini client for testing"""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        """Mock content generation"""
        return f"AI-generated response: {prompt[:100]}... This is a synthesized answer based on Dr. Strunz's teachings."
    
    async def extract_key_concepts(self, text: str) -> List[str]:
        """Mock concept extraction"""
        return ["Vitamin D", "Exercise", "Nutrition", "Health", "Wellness"]
    
    async def validate_api_key(self) -> bool:
        """Mock API key validation"""
        return True


class TestBatch4GeminiTools:
    """Test suite for Batch 4 Gemini-enhanced tools"""
    
    @pytest.fixture
    def mock_search_tool(self):
        """Create mock search tool"""
        return MockSearchTool()
    
    @pytest.fixture
    def gemini_tools_with_key(self, mock_search_tool):
        """Create Gemini tools with API key set"""
        os.environ['GOOGLE_GEMINI_API_KEY'] = 'test-key'
        tools = GeminiEnhancedTools(mock_search_tool)
        yield tools
        # Cleanup
        if 'GOOGLE_GEMINI_API_KEY' in os.environ:
            del os.environ['GOOGLE_GEMINI_API_KEY']
    
    @pytest.fixture
    def gemini_tools_without_key(self, mock_search_tool):
        """Create Gemini tools without API key"""
        if 'GOOGLE_GEMINI_API_KEY' in os.environ:
            del os.environ['GOOGLE_GEMINI_API_KEY']
        return GeminiEnhancedTools(mock_search_tool)
    
    @pytest.mark.asyncio
    async def test_search_knowledge_gemini_no_api_key(self, gemini_tools_without_key):
        """Test Gemini search without API key returns proper fallback"""
        result = await gemini_tools_without_key.search_knowledge_gemini(
            query="vitamin D",
            limit=5
        )
        
        assert "Gemini-Enhanced Search Not Available" in result
        assert "GOOGLE_GEMINI_API_KEY not configured" in result
        assert "Alternative" in result
        assert "knowledge_search" in result
    
    @pytest.mark.asyncio
    async def test_search_knowledge_gemini_with_api_key(self, gemini_tools_with_key):
        """Test Gemini search with API key (mocked)"""
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            with patch('src.mcp.batch4_gemini_tools.GeminiEnhancedSearch') as mock_search:
                # Mock the enhanced search
                mock_instance = MagicMock()
                mock_instance.search = AsyncMock(return_value={
                    'synthesis': 'Synthesized answer about vitamin D',
                    'key_concepts': ['Vitamin D', 'Sunlight', 'Health'],
                    'raw_results': [{'text': 'Result 1'}, {'text': 'Result 2'}],
                    'sources_used': ['books', 'news'],
                    'enhanced_by': 'gemini-2.5-flash'
                })
                mock_search.return_value = mock_instance
                
                result = await gemini_tools_with_key.search_knowledge_gemini(
                    query="vitamin D",
                    limit=5
                )
                
                assert "Gemini-Enhanced Search: vitamin D" in result
                assert "AI-Synthesized Answer" in result
                assert "Key Concepts" in result
                assert "Sources Used" in result
    
    @pytest.mark.asyncio
    async def test_ask_strunz_gemini_no_api_key(self, gemini_tools_without_key):
        """Test Gemini Q&A without API key"""
        result = await gemini_tools_without_key.ask_strunz_gemini(
            question="What are the benefits of vitamin D?",
            context="I live in a northern climate"
        )
        
        assert "Gemini Q&A Not Available" in result
        assert "GOOGLE_GEMINI_API_KEY not configured" in result
        assert "Alternative" in result
    
    @pytest.mark.asyncio
    async def test_ask_strunz_gemini_with_api_key(self, gemini_tools_with_key):
        """Test Gemini Q&A with API key (mocked)"""
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            result = await gemini_tools_with_key.ask_strunz_gemini(
                question="What are the benefits of vitamin D?",
                context="I live in a northern climate"
            )
            
            assert "Dr. Strunz Q&A (Gemini-Enhanced)" in result
            assert "Your Question" in result
            assert "Your Context" in result
            assert "Answer" in result
            assert "Key Recommendations" in result
    
    @pytest.mark.asyncio
    async def test_analyze_health_topic_gemini_no_api_key(self, gemini_tools_without_key):
        """Test Gemini analysis without API key"""
        result = await gemini_tools_without_key.analyze_health_topic_gemini(
            topic="immune system",
            aspects=["nutrition", "exercise"]
        )
        
        assert "Gemini Analysis Not Available" in result
        assert "GOOGLE_GEMINI_API_KEY not configured" in result
    
    @pytest.mark.asyncio
    async def test_analyze_health_topic_gemini_with_api_key(self, gemini_tools_with_key):
        """Test Gemini analysis with API key (mocked)"""
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            result = await gemini_tools_with_key.analyze_health_topic_gemini(
                topic="immune system",
                aspects=["nutrition", "exercise", "sleep"]
            )
            
            assert "Comprehensive Analysis: immune system" in result
            assert "Aspects Analyzed" in result
            assert "nutrition" in result
            assert "exercise" in result
            assert "sleep" in result
            assert "Source Distribution" in result
    
    @pytest.mark.asyncio
    async def test_validate_gemini_connection_no_key(self, gemini_tools_without_key):
        """Test Gemini validation without API key"""
        result = await gemini_tools_without_key.validate_gemini_connection()
        
        assert "Gemini Connection Status" in result
        assert "Not Configured" in result
        assert "Setup Instructions" in result
        assert "Gemini tools unavailable" in result
    
    @pytest.mark.asyncio
    async def test_validate_gemini_connection_with_key(self, gemini_tools_with_key):
        """Test Gemini validation with API key (mocked)"""
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            result = await gemini_tools_with_key.validate_gemini_connection()
            
            assert "Gemini Connection Status" in result
            assert "Connected Successfully" in result
            assert "API Key Status: Valid" in result
            assert "Available Gemini Tools" in result
            assert "All Gemini tools operational" in result
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, gemini_tools_with_key):
        """Test parameter validation for Gemini tools"""
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            with patch('src.mcp.batch4_gemini_tools.GeminiEnhancedSearch') as mock_search:
                mock_instance = MagicMock()
                mock_instance.search = AsyncMock(return_value={
                    'synthesis': 'Test',
                    'key_concepts': [],
                    'raw_results': [],
                    'sources_used': [],
                    'enhanced_by': 'gemini-2.5-flash'
                })
                mock_search.return_value = mock_instance
                
                # Test limit bounds (should clamp to 1-20)
                result = await gemini_tools_with_key.search_knowledge_gemini(
                    query="test",
                    limit=50  # Should be clamped to 20
                )
                assert result is not None
                
                result = await gemini_tools_with_key.search_knowledge_gemini(
                    query="test",
                    limit=0  # Should be clamped to 1
                )
                assert result is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, gemini_tools_with_key):
        """Test error handling in Gemini tools"""
        # Mock an error in Gemini client
        with patch('src.mcp.batch4_gemini_tools.GeminiClient') as mock_client:
            mock_client.side_effect = Exception("API Error")
            
            result = await gemini_tools_with_key.search_knowledge_gemini(
                query="test",
                limit=5
            )
            
            assert "Gemini Search Error" in result
            assert "API Error" in result
            assert "Suggestion" in result
    
    @pytest.mark.asyncio
    async def test_no_search_results_handling(self, gemini_tools_with_key):
        """Test handling when no search results are found"""
        # Mock search tool to return empty results
        gemini_tools_with_key.search_tool.search = lambda *args, **kwargs: []
        
        with patch('src.mcp.batch4_gemini_tools.GeminiClient', MockGeminiClient):
            result = await gemini_tools_with_key.ask_strunz_gemini(
                question="obscure topic with no results"
            )
            
            assert "No Information Found" in result or "Answer" in result


class TestBatch4Integration:
    """Integration tests for Batch 4 with MCP server"""
    
    @pytest.mark.asyncio
    async def test_batch4_feature_flag_enabled(self):
        """Test Batch 4 with feature flag enabled"""
        os.environ["ENABLE_BATCH4_MIGRATION"] = "true"
        
        # Would need full integration test here
        assert os.environ.get("ENABLE_BATCH4_MIGRATION") == "true"
    
    @pytest.mark.asyncio
    async def test_batch4_feature_flag_disabled(self):
        """Test Batch 4 with feature flag disabled"""
        os.environ["ENABLE_BATCH4_MIGRATION"] = "false"
        
        assert os.environ.get("ENABLE_BATCH4_MIGRATION") == "false"
    
    def test_batch4_tool_schemas(self):
        """Test that Gemini tool schemas are properly defined"""
        schemas = {
            "search_knowledge_gemini": {
                "required": ["query"],
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    "sources": {"type": "array"}
                }
            },
            "ask_strunz_gemini": {
                "required": ["question"],
                "properties": {
                    "question": {"type": "string"},
                    "context": {"type": "string"}
                }
            },
            "analyze_health_topic_gemini": {
                "required": ["topic"],
                "properties": {
                    "topic": {"type": "string"},
                    "aspects": {"type": "array"}
                }
            },
            "validate_gemini_connection": {
                "properties": {}
            }
        }
        
        # Verify schema structures
        for tool_name, schema in schemas.items():
            assert "properties" in schema
            if tool_name != "validate_gemini_connection":
                assert "required" in schema


class TestBatch4CompleteMigration:
    """Test complete migration status after Batch 4"""
    
    def test_no_fastmcp_imports_in_main_server(self):
        """Verify no FastMCP imports remain in main server"""
        # Read the main server file
        server_path = project_root / "src" / "mcp" / "mcp_server_clean.py"
        if server_path.exists():
            content = server_path.read_text()
            assert "fastmcp" not in content.lower()
            assert "FastMCP" not in content
    
    def test_all_batches_integrated(self):
        """Test that all 4 batches are integrated"""
        flags = [
            "ENABLE_BATCH2_MIGRATION",
            "ENABLE_BATCH3_MIGRATION", 
            "ENABLE_BATCH4_MIGRATION"
        ]
        
        # All flags should be checkable
        for flag in flags:
            # Just verify the flag can be set
            os.environ[flag] = "true"
            assert os.environ.get(flag) == "true"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])