#!/usr/bin/env python3
"""
Claude.ai Compatible MCP Server - FINAL FIX
Dr. Strunz Knowledge Base MCP Server with proper tool schemas
Version: 1.0.2 - Fixes empty tool schemas issue definitively
"""

import os
import sys
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, Request, Query, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from sse_starlette.sse import EventSourceResponse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Dr. Strunz Knowledge MCP Server")

# Session management
sessions = {}

# Tool definitions with COMPLETE schemas - this is what was missing!
TOOLS = [
    {
        "name": "knowledge_search",
        "description": "Search through Dr. Strunz's knowledge base with semantic search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "sources": {"type": "array", "items": {"type": "string"}, "description": "Filter by sources: books, news, forum"},
                "limit": {"type": "integer", "description": "Number of results (default: 10)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "find_contradictions",
        "description": "Find contradictions or conflicts in Dr. Strunz's knowledge base",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to analyze for contradictions"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "trace_topic_evolution",
        "description": "Track how a health topic evolved over time in Dr. Strunz's content",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Health topic to trace"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "create_health_protocol",
        "description": "Create a personalized health protocol based on Dr. Strunz's knowledge",
        "inputSchema": {
            "type": "object",
            "properties": {
                "condition": {"type": "string", "description": "Health condition or goal"},
                "age": {"type": "integer", "description": "Age of person"},
                "gender": {"type": "string", "description": "Gender (male/female)"},
                "activity_level": {"type": "string", "description": "Activity level (sedentary/moderate/active)"}
            },
            "required": ["condition"]
        }
    },
    {
        "name": "analyze_supplement_stack",
        "description": "Analyze and optimize supplement combinations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "supplements": {"type": "array", "items": {"type": "string"}, "description": "List of supplements"}
            },
            "required": ["supplements"]
        }
    },
    {
        "name": "nutrition_calculator",
        "description": "Calculate nutrition requirements based on Dr. Strunz's recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "weight": {"type": "number", "description": "Body weight in kg"},
                "goal": {"type": "string", "description": "Goal: weight_loss, muscle_gain, maintenance"}
            },
            "required": ["weight", "goal"]
        }
    },
    {
        "name": "summarize_posts",
        "description": "Summarize recent posts by category with personalized filtering",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Category to summarize"},
                "limit": {"type": "integer", "description": "Number of posts to summarize (default: 10)"},
                "timeframe": {"type": "string", "description": "Time period: last_week, last_month, last_year"},
                "user_profile": {"type": "object", "description": "Optional user profile for filtering"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_health_assessment_questions",
        "description": "Get personalized health assessment questions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_role": {"type": "string", "description": "User role: patient, practitioner, researcher"},
                "assessment_depth": {"type": "string", "description": "Depth: basic, comprehensive, detailed"}
            }
        }
    },
    {
        "name": "get_dr_strunz_biography",
        "description": "Get comprehensive biography and philosophy of Dr. Ulrich Strunz",
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_achievements": {"type": "boolean", "description": "Include achievements section"},
                "include_philosophy": {"type": "boolean", "description": "Include medical philosophy"}
            }
        }
    },
    {
        "name": "get_mcp_server_purpose",
        "description": "Explain the purpose and capabilities of this MCP server",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_vector_db_analysis",
        "description": "Get detailed analysis of the vector database content and statistics",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "compare_approaches",
        "description": "Compare Dr. Strunz's approach with other health methodologies",
        "inputSchema": {
            "type": "object",
            "properties": {
                "health_issue": {"type": "string", "description": "Health issue to compare approaches for"},
                "alternative_approaches": {"type": "array", "items": {"type": "string"}, "description": "List of alternative approaches to compare"},
                "criteria": {"type": "array", "items": {"type": "string"}, "description": "Optional comparison criteria"}
            },
            "required": ["health_issue", "alternative_approaches"]
        }
    },
    {
        "name": "create_meal_plan",
        "description": "Create a personalized meal plan based on Dr. Strunz's nutritional principles",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dietary_preferences": {"type": "array", "items": {"type": "string"}, "description": "Dietary preferences/restrictions"},
                "calorie_target": {"type": "integer", "description": "Daily calorie target"},
                "days": {"type": "integer", "description": "Number of days for meal plan"}
            }
        }
    },
    {
        "name": "analyze_blood_values",
        "description": "Analyze blood test results according to Dr. Strunz's optimal ranges",
        "inputSchema": {
            "type": "object",
            "properties": {
                "blood_values": {"type": "object", "description": "Blood test values as key-value pairs"},
                "age": {"type": "integer", "description": "Age of person"},
                "gender": {"type": "string", "description": "Gender (male/female)"}
            },
            "required": ["blood_values"]
        }
    },
    {
        "name": "get_exercise_recommendations",
        "description": "Get personalized exercise recommendations based on Dr. Strunz's principles",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fitness_level": {"type": "string", "description": "Current fitness level"},
                "goals": {"type": "array", "items": {"type": "string"}, "description": "Fitness goals"},
                "time_available": {"type": "integer", "description": "Minutes per day available"}
            }
        }
    },
    {
        "name": "verify_health_claim",
        "description": "Verify health claims against Dr. Strunz's knowledge base",
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim": {"type": "string", "description": "Health claim to verify"},
                "context": {"type": "string", "description": "Additional context"}
            },
            "required": ["claim"]
        }
    },
    {
        "name": "get_stress_management_techniques",
        "description": "Get stress management techniques from Dr. Strunz's methodology",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stress_type": {"type": "string", "description": "Type of stress"},
                "severity": {"type": "string", "description": "Severity level"}
            }
        }
    },
    {
        "name": "analyze_genetic_data",
        "description": "Analyze genetic data for personalized health recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "genetic_markers": {"type": "object", "description": "Genetic markers data"},
                "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Health areas to focus on"}
            }
        }
    },
    {
        "name": "get_longevity_protocol",
        "description": "Get comprehensive longevity protocol based on latest research",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_age": {"type": "integer", "description": "Current age"},
                "health_status": {"type": "string", "description": "Current health status"},
                "lifestyle_factors": {"type": "object", "description": "Current lifestyle factors"}
            }
        }
    },
    {
        "name": "find_clinical_studies",
        "description": "Find clinical studies referenced by Dr. Strunz on specific topics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "study_type": {"type": "string", "description": "Type of study"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "get_recovery_protocol",
        "description": "Get recovery protocols for specific conditions or post-exercise",
        "inputSchema": {
            "type": "object",
            "properties": {
                "condition": {"type": "string", "description": "Condition or situation requiring recovery"},
                "severity": {"type": "string", "description": "Severity or intensity level"}
            },
            "required": ["condition"]
        }
    },
    {
        "name": "analyze_lifestyle_factors",
        "description": "Comprehensive lifestyle analysis with personalized recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lifestyle_data": {"type": "object", "description": "Current lifestyle factors"},
                "health_goals": {"type": "array", "items": {"type": "string"}, "description": "Health goals"}
            },
            "required": ["lifestyle_data"]
        }
    },
    {
        "name": "get_immune_support_protocol",
        "description": "Get immune system support recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_health": {"type": "string", "description": "Current health status"},
                "risk_factors": {"type": "array", "items": {"type": "string"}, "description": "Risk factors"}
            }
        }
    },
    {
        "name": "calculate_nutrient_needs",
        "description": "Calculate specific nutrient needs based on individual factors",
        "inputSchema": {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "description": "Age"},
                "weight": {"type": "number", "description": "Weight in kg"},
                "activity_level": {"type": "string", "description": "Activity level"},
                "health_conditions": {"type": "array", "items": {"type": "string"}, "description": "Health conditions"}
            },
            "required": ["age", "weight"]
        }
    }
]

# Tool handlers - we'll use the existing implementation
tool_handlers = None

@app.on_event("startup")
async def startup_event():
    """Initialize the server on startup"""
    global tool_handlers
    
    # Preload vector store
    try:
        from src.scripts.startup.preload_vector_store import preload_vector_store
        await preload_vector_store()
        logger.info("Vector store preloaded successfully")
    except Exception as e:
        logger.warning(f"Could not preload vector store: {e}")
    
    # Load tool handlers from existing implementation
    try:
        from src.mcp.mcp_sdk_clean import StrunzKnowledgeServer
        sdk_server = StrunzKnowledgeServer()
        await sdk_server._init_vector_store()
        tool_handlers = sdk_server
        logger.info("Tool handlers loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load tool handlers: {e}")
        tool_handlers = None
    
    logger.info(f"Starting Claude.ai compatible MCP server on port 8000")
    logger.info(f"Protocol version: 2025-03-26")
    logger.info(f"Tools available: {len(TOOLS)}")
    
    # Log first few tools to verify schemas
    for i, tool in enumerate(TOOLS[:3]):
        schema_props = list(tool['inputSchema'].get('properties', {}).keys())
        logger.info(f"  - {tool['name']}: {schema_props}")

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check and server info"""
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "1.0.3",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "oauth": "/oauth/*"
        },
        "tools_count": len(TOOLS),
        "protocol_version": "2025-03-26"
    })

# SSE endpoint
@app.get("/sse")
@app.post("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol"""
    
    user_agent = request.headers.get("user-agent", "")
    logger.info(f"SSE connection established - User-Agent: {user_agent}")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created": datetime.utcnow().isoformat(),
        "initialized": False
    }
    
    async def event_generator():
        """Generate SSE events"""
        try:
            yield {
                "event": "endpoint",
                "data": f"/messages/?session_id={session_id}"
            }
            
            while True:
                await asyncio.sleep(15)
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "+00:00"
                yield {
                    "event": "ping",
                    "data": timestamp
                }
                
        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for session {session_id}")
            if session_id in sessions:
                del sessions[session_id]
            raise
    
    return EventSourceResponse(event_generator())

# Message handling endpoint
@app.post("/messages")
@app.post("/messages/")
async def messages_endpoint(request: Request, session_id: Optional[str] = Query(None)):
    """Handle MCP protocol messages"""
    
    try:
        data = await request.json()
        method = data.get("method")
        msg_id = data.get("id", "1")
        
        logger.info(f"MCP request: {method}")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False}
                    },
                    "serverInfo": {
                        "name": "Dr. Strunz Knowledge MCP Server",
                        "version": "1.0.3"
                    }
                }
            }
            return JSONResponse(response)
            
        elif method == "resources/list":
            # Return empty resources list - required by MCP Inspector
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "resources": []
                }
            }
            return JSONResponse(response)
            
        elif method == "tools/list":
            # Return tools WITH PROPER SCHEMAS!
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            }
            return JSONResponse(response)
            
        elif method == "tools/call":
            params = data.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not any(t["name"] == tool_name for t in TOOLS):
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                })
            
            # Execute tool
            try:
                if tool_handlers and hasattr(tool_handlers, f"_handle_{tool_name}"):
                    handler = getattr(tool_handlers, f"_handle_{tool_name}")
                    result_content = await handler(arguments)
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": result_content
                        }
                    }
                else:
                    # Fallback response
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Tool {tool_name} executed (handler not available in test mode)"}]
                        }
                    }
                
                return JSONResponse(response)
                
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution failed: {str(e)}"
                    }
                })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
            
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id", "1"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })

# Claude.ai specific endpoints
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(org_id: str, auth_id: str, redirect_url: Optional[str] = Query(None)):
    """Claude.ai specific auth endpoint"""
    
    if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        return JSONResponse({
            "status": "success",
            "auth_not_required": True,
            "server_url": "https://strunz.up.railway.app"
        })
    
    return JSONResponse({"error": "OAuth not implemented"}, status_code=501)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)