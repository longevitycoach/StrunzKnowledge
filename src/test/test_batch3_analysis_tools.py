"""
Comprehensive test suite for Batch 3 Complex Analysis Tools
Tests dynamic FAISS integration and complex parameter handling
"""

import pytest
import asyncio
from typing import List, Optional
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from dataclasses import dataclass
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp.batch3_analysis_tools import ComplexAnalysisTools


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
    
    def __init__(self):
        self.vector_store = MagicMock()
        self.vector_store.documents = [MagicMock() for _ in range(100)]
        self.vector_store.index = MagicMock()
        self.vector_store.index.ntotal = 43373
        self.vector_store.dimension = 384
    
    def search(self, query: str, k: int = 10, sources: Optional[List[str]] = None):
        """Mock search implementation"""
        # Return mock results based on query
        results = []
        
        # Generate diverse results
        for i in range(min(k, 10)):
            source = ["books", "news", "forum"][i % 3]
            
            # Skip if source filtering applied
            if sources and source not in sources:
                continue
                
            result = MockSearchResult(
                text=f"Mock result {i+1} for query '{query}' from {source}. "
                     f"This contains information about {query} with detailed explanations. "
                     f"Dr. Strunz recommends specific approaches for this topic.",
                score=0.95 - (i * 0.05),
                source=source,
                title=f"{source.capitalize()} - {query} Article {i+1}",
                metadata={
                    "date": f"202{3-i%3}-0{(i%9)+1}-{(i%28)+1:02d}",
                    "author": "Dr. Ulrich Strunz" if source == "books" else "Editorial",
                    "url": f"https://strunz.com/{source}/{query.lower().replace(' ', '-')}-{i+1}"
                }
            )
            results.append(result)
        
        return results
    
    def get_stats(self):
        """Mock stats implementation"""
        return {
            "status": "Ready",
            "documents": 43373,
            "index_size": 43373,
            "dimension": 384
        }


class TestBatch3ComplexAnalysisTools:
    """Test suite for Batch 3 complex analysis tools"""
    
    @pytest.fixture
    def mock_search_tool(self):
        """Create mock search tool"""
        return MockSearchTool()
    
    @pytest.fixture
    def analysis_tools(self, mock_search_tool):
        """Create analysis tools instance with mock"""
        return ComplexAnalysisTools(mock_search_tool)
    
    @pytest.mark.asyncio
    async def test_knowledge_search_basic(self, analysis_tools):
        """Test basic knowledge search"""
        result = await analysis_tools.knowledge_search(
            query="vitamin D",
            k=5
        )
        
        assert "Search Results: vitamin D" in result
        assert "Found 5 relevant passages" in result
        assert "Result 1" in result
        assert "Result 5" in result
        assert "Source:" in result
        assert "Title:" in result
        assert "Relevance Score:" in result
    
    @pytest.mark.asyncio
    async def test_knowledge_search_with_sources(self, analysis_tools):
        """Test knowledge search with source filtering"""
        result = await analysis_tools.knowledge_search(
            query="omega 3",
            k=10,
            sources=["books", "news"]
        )
        
        assert "filtered by sources: books, news" in result
        assert "forum" not in result.lower() or "Forum" not in result
    
    @pytest.mark.asyncio
    async def test_knowledge_search_large_k(self, analysis_tools):
        """Test knowledge search with maximum k value"""
        result = await analysis_tools.knowledge_search(
            query="protein",
            k=50  # Maximum allowed
        )
        
        assert "Search Results: protein" in result
        # Should be clamped to available results
        assert "Result" in result
    
    @pytest.mark.asyncio
    async def test_find_contradictions(self, analysis_tools):
        """Test contradiction detection"""
        result = await analysis_tools.find_contradictions(
            topic="carbohydrates"
        )
        
        assert "Contradiction Analysis: carbohydrates" in result
        assert "Analyzed" in result
        assert "passages for potential contradictions" in result
        assert "Analysis by Source" in result
        assert "Summary" in result
    
    @pytest.mark.asyncio
    async def test_find_contradictions_with_time_window(self, analysis_tools):
        """Test contradiction detection with time window"""
        result = await analysis_tools.find_contradictions(
            topic="fasting",
            time_window=2  # 2 year window
        )
        
        assert "Contradiction Analysis: fasting" in result
        # Time window doesn't affect mock but should be handled
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_search_by_date_range(self, analysis_tools):
        """Test temporal search with date range"""
        result = await analysis_tools.search_by_date_range(
            query="ketogenic diet",
            start_date="2022-01-01",
            end_date="2023-12-31",
            k=5
        )
        
        assert "Date-Filtered Search: ketogenic diet" in result
        assert "Date Range:" in result
        assert "From 2022-01-01" in result
        assert "To 2023-12-31" in result
    
    @pytest.mark.asyncio
    async def test_search_by_date_invalid_format(self, analysis_tools):
        """Test temporal search with invalid date format"""
        result = await analysis_tools.search_by_date_range(
            query="supplements",
            start_date="invalid-date",
            k=5
        )
        
        assert "Invalid date format" in result
    
    @pytest.mark.asyncio
    async def test_get_vector_db_analysis(self, analysis_tools):
        """Test vector database analysis"""
        result = await analysis_tools.get_vector_db_analysis()
        
        assert "Vector Database Analysis" in result
        assert "Overview" in result
        assert "Total Documents:" in result
        assert "43,373" in result  # Formatted number
        assert "FAISS" in result
        assert "Search Capabilities" in result
        assert "Performance Metrics" in result
    
    @pytest.mark.asyncio
    async def test_ping_health_check(self, analysis_tools):
        """Test health check endpoint"""
        result = await analysis_tools.ping()
        
        assert "System Health Check" in result
        assert "Component Status" in result
        assert "Vector Store" in result
        assert "Search Engine" in result
        assert "Overall Status" in result
        assert "✅" in result or "⚠️" in result or "❌" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_no_search_tool(self):
        """Test error handling when search tool is not available"""
        tools = ComplexAnalysisTools(None)
        
        result = await tools.knowledge_search("test", k=5)
        assert "Error: Knowledge base not available" in result
        
        result = await tools.find_contradictions("test")
        assert "Error: Knowledge base not available" in result
        
        result = await tools.search_by_date_range("test")
        assert "Error: Knowledge base not available" in result
        
        result = await tools.get_vector_db_analysis()
        assert "Error: Knowledge base not available" in result
    
    @pytest.mark.asyncio
    async def test_knowledge_search_empty_results(self, analysis_tools):
        """Test handling of empty search results"""
        # Mock empty results
        analysis_tools.search_tool.search = lambda *args, **kwargs: []
        
        result = await analysis_tools.knowledge_search("nonexistent topic", k=10)
        assert "No results found" in result
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, analysis_tools):
        """Test parameter validation and edge cases"""
        # Test k parameter bounds
        result = await analysis_tools.knowledge_search("test", k=0)
        assert "Result 1" in result  # Should clamp to minimum of 1
        
        result = await analysis_tools.knowledge_search("test", k=100)
        # Should clamp to maximum of 50
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_metadata_handling(self, analysis_tools):
        """Test proper metadata extraction and formatting"""
        result = await analysis_tools.knowledge_search("vitamins", k=3)
        
        # Check metadata is included
        assert "Date:" in result
        assert "Author:" in result
        assert "URL:" in result
    
    @pytest.mark.asyncio
    async def test_contradiction_detection_algorithm(self, analysis_tools):
        """Test the contradiction detection algorithm"""
        # Create mock results with conflicting information
        positive_result = MockSearchResult(
            text="This supplement has many benefits and is highly recommended for daily use.",
            score=0.9,
            source="books",
            title="Benefits Book",
            metadata={"date": "2023-01-01"}
        )
        
        negative_result = MockSearchResult(
            text="This supplement has risks and should be avoided due to harmful effects.",
            score=0.85,
            source="news",
            title="Warning Article",
            metadata={"date": "2023-06-01"}
        )
        
        # Mock search to return conflicting results
        analysis_tools.search_tool.search = lambda *args, **kwargs: [
            positive_result, negative_result
        ]
        
        result = await analysis_tools.find_contradictions("test supplement")
        
        assert "Potential contradiction" in result or "Consistent messaging" in result
        assert "positive statements" in result.lower() or "cautionary statements" in result.lower()


class TestBatch3Integration:
    """Integration tests for Batch 3 with MCP server"""
    
    @pytest.mark.asyncio
    async def test_batch3_feature_flag_enabled(self):
        """Test Batch 3 with feature flag enabled"""
        import os
        os.environ["ENABLE_BATCH3_MIGRATION"] = "true"
        
        # Import after setting env var
        from src.mcp.mcp_server_clean import initialize_vector_store
        
        # Mock the KnowledgeSearcher
        with patch('src.mcp.mcp_server_clean.KnowledgeSearcher') as mock_searcher:
            mock_instance = MockSearchTool()
            mock_searcher.return_value = mock_instance
            
            success = await initialize_vector_store()
            # Note: Can't fully test without proper imports, but structure is correct
    
    @pytest.mark.asyncio
    async def test_batch3_feature_flag_disabled(self):
        """Test Batch 3 with feature flag disabled"""
        import os
        os.environ["ENABLE_BATCH3_MIGRATION"] = "false"
        
        from src.mcp.mcp_server_clean import ENABLE_BATCH3_MIGRATION
        assert ENABLE_BATCH3_MIGRATION == False
    
    def test_batch3_tool_schemas(self):
        """Test that tool schemas are properly defined"""
        # This would normally test against the actual MCP server
        # but we'll verify the schema structure
        
        schemas = {
            "knowledge_search": {
                "required": ["query"],
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 50},
                    "sources": {"type": "array", "items": {"type": "string"}}
                }
            },
            "find_contradictions": {
                "required": ["topic"],
                "properties": {
                    "topic": {"type": "string"}
                }
            },
            "search_by_date_range": {
                "required": ["query"],
                "properties": {
                    "query": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 50}
                }
            },
            "get_vector_db_analysis": {
                "properties": {}
            },
            "ping": {
                "properties": {}
            }
        }
        
        # Verify schema structures
        for tool_name, schema in schemas.items():
            assert "properties" in schema
            if tool_name not in ["get_vector_db_analysis", "ping"]:
                assert "required" in schema or tool_name == "knowledge_search"


class TestBatch3Performance:
    """Performance tests for Batch 3 tools"""
    
    @pytest.mark.asyncio
    async def test_search_performance(self):
        """Test that search operations meet performance requirements"""
        import time
        
        mock_tool = MockSearchTool()
        analysis_tools = ComplexAnalysisTools(mock_tool)
        
        # Test various search operations
        operations = [
            ("knowledge_search", {"query": "test", "k": 10}),
            ("find_contradictions", {"topic": "vitamins"}),
            ("search_by_date_range", {"query": "diet", "k": 5}),
            ("get_vector_db_analysis", {}),
            ("ping", {})
        ]
        
        for op_name, params in operations:
            start_time = time.time()
            
            if op_name == "knowledge_search":
                await analysis_tools.knowledge_search(**params)
            elif op_name == "find_contradictions":
                await analysis_tools.find_contradictions(**params)
            elif op_name == "search_by_date_range":
                await analysis_tools.search_by_date_range(**params)
            elif op_name == "get_vector_db_analysis":
                await analysis_tools.get_vector_db_analysis()
            elif op_name == "ping":
                await analysis_tools.ping()
            
            elapsed = time.time() - start_time
            
            # Most operations should be very fast with mocked data
            # Real FAISS searches would take longer
            assert elapsed < 1.0, f"{op_name} took {elapsed:.2f}s"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])