"""
SSE Streaming Handler for progressive responses
Integrates with MCP server to handle streaming tool calls
"""

import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SSEStreamingHandler:
    """Handles streaming responses for SSE transport"""
    
    def __init__(self, search_tool=None):
        """Initialize with search tool reference"""
        self.search_tool = search_tool
        self.streaming_tools = ["analyze_health_topic"]  # Tools that support streaming
        
    async def should_stream(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Determine if a tool call should use streaming"""
        # Stream analyze_health_topic when depth is comprehensive
        if tool_name == "analyze_health_topic":
            depth = arguments.get("depth", "moderate")
            return depth == "comprehensive"
        return False
    
    async def handle_streaming_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Handle streaming tool execution.
        Yields SSE-formatted messages.
        """
        
        if tool_name == "analyze_health_topic" and self.search_tool:
            from src.mcp.streaming_analyzer import StreamingAnalyzer
            
            analyzer = StreamingAnalyzer(self.search_tool)
            topic = arguments.get("topic", "")
            depth = arguments.get("depth", "comprehensive")
            
            # Stream progress messages
            async for chunk in analyzer.analyze_health_topic_streaming(topic, depth):
                # Format as SSE message
                if chunk.get("type") == "progress":
                    # Send progress update
                    progress_msg = {
                        "jsonrpc": "2.0",
                        "method": "progress",
                        "params": {
                            "progress": chunk.get("progress", 0),
                            "message": chunk.get("message", ""),
                            "data": chunk.get("data")
                        }
                    }
                    yield f"data: {json.dumps(progress_msg)}\n\n"
                    
                elif chunk.get("type") == "complete":
                    # Send final result
                    result = chunk.get("data", {}).get("result", "")
                    complete_msg = {
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": 1  # Will be replaced with actual request ID
                    }
                    yield f"data: {json.dumps(complete_msg)}\n\n"
                    
                # Small delay to prevent overwhelming client
                await asyncio.sleep(0.1)
        
        else:
            # Fallback for non-streaming tools
            error_msg = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Tool {tool_name} does not support streaming"
                },
                "id": 1
            }
            yield f"data: {json.dumps(error_msg)}\n\n"
    
    def format_sse_message(self, data: Dict[str, Any]) -> str:
        """Format a message for SSE transport"""
        return f"data: {json.dumps(data)}\n\n"
    
    def format_progress_notification(
        self,
        progress: int,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format a progress notification for MCP protocol"""
        notification = {
            "jsonrpc": "2.0",
            "method": "$/progress",
            "params": {
                "progressToken": "analyze-progress",
                "value": {
                    "kind": "report",
                    "percentage": progress,
                    "message": message
                }
            }
        }
        
        if data:
            notification["params"]["value"]["data"] = data
            
        return self.format_sse_message(notification)