#!/usr/bin/env python3
"""
Minimal OAuth Implementation for Claude.ai
This provides just enough OAuth to satisfy Claude.ai without actual authentication
"""

import os
from typing import Optional
from fastapi import Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
import uuid
import logging

logger = logging.getLogger(__name__)

def setup_minimal_oauth_routes(app):
    """Add minimal OAuth routes to satisfy Claude.ai"""
    
    @app.get("/.well-known/oauth-authorization-server")
    async def oauth_metadata_minimal():
        """Minimal OAuth metadata for Claude.ai"""
        base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
        return {
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}/oauth/authorize",
            "token_endpoint": f"{base_url}/oauth/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"]
        }
    
    @app.get("/authorize")
    @app.get("/oauth/authorize")
    async def authorize_minimal(
        client_id: str = Query(...),
        redirect_uri: str = Query(...),
        response_type: str = Query(default="code"),
        state: Optional[str] = Query(default=None),
        scope: Optional[str] = Query(default="read"),
        code_challenge: Optional[str] = Query(default=None),
        code_challenge_method: Optional[str] = Query(default=None)
    ):
        """Minimal OAuth authorize - auto-approves for Claude.ai"""
        logger.info(f"OAuth authorize request from: {client_id}")
        
        # Check if this is Claude.ai
        if "claude" in client_id.lower() or "claude.ai" in redirect_uri:
            # Auto-approve for Claude.ai
            auth_code = f"auth_{uuid.uuid4().hex[:16]}"
            
            # Build redirect URL
            redirect_url = f"{redirect_uri}?code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
            
            logger.info(f"Auto-approving OAuth for Claude.ai, redirecting to: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=302)
        
        # For other clients, return error
        return JSONResponse({"error": "unauthorized_client"}, status_code=400)
    
    @app.post("/oauth/token")
    async def token_minimal(request: Request):
        """Minimal token endpoint - returns dummy token for Claude.ai"""
        try:
            form_data = await request.form()
            grant_type = form_data.get("grant_type")
            code = form_data.get("code")
            
            logger.info(f"Token request: grant_type={grant_type}, code={code}")
            
            if grant_type == "authorization_code" and code and code.startswith("auth_"):
                # Return minimal access token
                return JSONResponse({
                    "access_token": f"access_{uuid.uuid4().hex}",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": "read"
                })
            else:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
                
        except Exception as e:
            logger.error(f"Token endpoint error: {e}")
            return JSONResponse({"error": "server_error"}, status_code=500)
    
    # Remove the 404 returns for OAuth endpoints
    # Find and remove the OAuth endpoints that return 404
    routes_to_modify = []
    for route in app.routes:
        if route.path in ["/.well-known/oauth-authorization-server", "/oauth/authorize", "/oauth/token", "/authorize"]:
            routes_to_modify.append(route)
    
    # Remove old routes
    for route in routes_to_modify:
        app.routes.remove(route)
    
    logger.info("Minimal OAuth routes configured for Claude.ai compatibility")