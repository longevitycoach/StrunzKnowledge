"""
Claude.ai OAuth Callback Handler
Handles the OAuth callback flow for Claude.ai integration
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/mcp/auth_callback")
async def claude_ai_oauth_callback(
    code: str = Query(...),
    state: str = Query(None),
    error: str = Query(None)
):
    """
    Handle OAuth callback from authorization server
    This is where Claude.ai lands after OAuth authorization
    """
    logger.info(f"Claude.ai OAuth callback: code={code[:10]}..., state={state}, error={error}")
    
    if error:
        return JSONResponse({
            "status": "error",
            "error": error,
            "message": "OAuth authorization failed"
        }, status_code=400)
    
    # Return success page that Claude.ai can understand
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Server Connected</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background: #f5f5f5;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .success {{
                color: #10b981;
                font-size: 48px;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #1f2937;
                margin: 0 0 0.5rem 0;
            }}
            p {{
                color: #6b7280;
                margin: 0;
            }}
            .code {{
                font-family: monospace;
                background: #f3f4f6;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.875rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✓</div>
            <h1>Successfully Connected!</h1>
            <p>Dr. Strunz Knowledge MCP Server is now connected to Claude.ai</p>
            <p style="margin-top: 1rem;">You can close this window and return to Claude.</p>
            <p style="margin-top: 2rem; font-size: 0.875rem;">
                Authorization code: <span class="code">{code[:10]}...</span>
            </p>
        </div>
        <script>
            // Notify parent window if in iframe
            if (window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'mcp-oauth-success',
                    code: '{code}',
                    state: '{state}'
                }}, 'https://claude.ai');
            }}
            
            // Auto-close after 3 seconds
            setTimeout(() => {{
                window.close();
            }}, 3000);
        </script>
    </body>
    </html>
    """)

@router.post("/api/mcp/connect")
async def claude_ai_connect(request: Request):
    """
    Handle MCP connection request from Claude.ai
    This might be called after OAuth to establish the connection
    """
    try:
        data = await request.json()
        logger.info(f"Claude.ai connect request: {data}")
        
        return JSONResponse({
            "status": "connected",
            "server": {
                "name": "Dr. Strunz Knowledge MCP Server",
                "version": "0.7.9",
                "ready": True
            },
            "capabilities": {
                "tools": True,
                "prompts": True,
                "resources": False
            },
            "endpoints": {
                "sse": "https://strunz.up.railway.app/sse",
                "messages": "https://strunz.up.railway.app/messages"
            }
        })
    except Exception as e:
        logger.error(f"Connect error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500)