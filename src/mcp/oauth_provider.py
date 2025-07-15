#!/usr/bin/env python3
"""
OAuth 2.1 Provider for Claude MCP Server
Implements Dynamic Client Registration (RFC 7591) and OAuth 2.1 with PKCE
"""

import os
import json
import secrets
import hashlib
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, AsyncGenerator
from dataclasses import dataclass, asdict
import jwt
from fastapi import FastAPI, HTTPException, Request, Query, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration
ISSUER_URL = os.environ.get('OAUTH_ISSUER_URL', 'https://strunz.up.railway.app')
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_EXPIRY = 604800  # 1 week

# Storage (in production, use a database)
registered_clients: Dict[str, 'OAuthClient'] = {}
authorization_codes: Dict[str, 'AuthorizationCode'] = {}
access_tokens: Dict[str, 'AccessToken'] = {}
refresh_tokens: Dict[str, str] = {}


@dataclass
class OAuthClient:
    """OAuth Client registration"""
    client_id: str
    client_name: str
    client_secret: Optional[str]
    redirect_uris: List[str]
    grant_types: List[str]
    response_types: List[str]
    scope: str
    token_endpoint_auth_method: str
    created_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class AuthorizationCode:
    """Authorization code for OAuth flow"""
    code: str
    client_id: str
    redirect_uri: str
    scope: str
    user_id: str
    code_challenge: Optional[str]
    code_challenge_method: Optional[str]
    expires_at: datetime
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


@dataclass
class AccessToken:
    """Access token"""
    token: str
    client_id: str
    user_id: str
    scope: str
    expires_at: datetime
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class ClientRegistrationRequest(BaseModel):
    """Dynamic Client Registration request (RFC 7591)"""
    client_name: str
    redirect_uris: List[str]
    grant_types: List[str] = ["authorization_code", "refresh_token"]
    response_types: List[str] = ["code"]
    scope: Optional[str] = "read write"
    token_endpoint_auth_method: str = "client_secret_basic"


class TokenRequest(BaseModel):
    """Token request"""
    grant_type: str
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    code_verifier: Optional[str] = None
    refresh_token: Optional[str] = None


class OAuthProvider:
    """OAuth 2.1 Provider with Dynamic Client Registration"""
    
    def __init__(self):
        self.app = FastAPI()
        # Setup templates
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        self.templates = Jinja2Templates(directory=str(template_dir))
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup OAuth endpoints"""
        
        @self.app.get("/.well-known/oauth-authorization-server")
        async def oauth_metadata():
            """OAuth 2.1 Authorization Server Metadata (RFC 8414)"""
            return {
                "issuer": ISSUER_URL,
                "authorization_endpoint": f"{ISSUER_URL}/oauth/authorize",
                "token_endpoint": f"{ISSUER_URL}/oauth/token",
                "registration_endpoint": f"{ISSUER_URL}/oauth/register",
                "scopes_supported": ["read", "write", "admin"],
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code", "refresh_token"],
                "code_challenge_methods_supported": ["S256", "plain"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
                "service_documentation": f"{ISSUER_URL}/docs",
                "ui_locales_supported": ["en"],
                "op_policy_uri": f"{ISSUER_URL}/policy",
                "op_tos_uri": f"{ISSUER_URL}/tos"
            }
        
        @self.app.post("/oauth/register")
        async def register_client(request: ClientRegistrationRequest):
            """Dynamic Client Registration endpoint (RFC 7591)"""
            # Generate client credentials
            client_id = f"client_{secrets.token_urlsafe(16)}"
            client_secret = secrets.token_urlsafe(32)
            
            # Create client
            client = OAuthClient(
                client_id=client_id,
                client_name=request.client_name,
                client_secret=client_secret,
                redirect_uris=request.redirect_uris,
                grant_types=request.grant_types,
                response_types=request.response_types,
                scope=request.scope or "read write",
                token_endpoint_auth_method=request.token_endpoint_auth_method,
                created_at=datetime.utcnow()
            )
            
            # Store client
            registered_clients[client_id] = client
            logger.info(f"Registered new OAuth client: {client_id} ({client.client_name})")
            
            # Return registration response
            response = client.to_dict()
            response['client_secret'] = client_secret
            response['client_id_issued_at'] = int(time.time())
            response['client_secret_expires_at'] = 0  # Never expires
            
            return JSONResponse(content=response, status_code=201)
        
        @self.app.get("/oauth/authorize")
        async def authorize(
            response_type: str = Query(...),
            client_id: str = Query(...),
            redirect_uri: str = Query(...),
            scope: str = Query(...),
            state: str = Query(...),
            code_challenge: Optional[str] = Query(None),
            code_challenge_method: Optional[str] = Query(None)
        ):
            """Authorization endpoint"""
            # Validate client
            if client_id not in registered_clients:
                raise HTTPException(status_code=400, detail="Invalid client_id")
            
            client = registered_clients[client_id]
            
            # Validate redirect_uri
            if redirect_uri not in client.redirect_uris:
                raise HTTPException(status_code=400, detail="Invalid redirect_uri")
            
            # Validate response_type
            if response_type != "code":
                raise HTTPException(status_code=400, detail="Unsupported response_type")
            
            # For demo purposes, auto-approve (in production, show consent screen)
            # Generate authorization code
            auth_code = secrets.token_urlsafe(32)
            
            # Store authorization code
            authorization_codes[auth_code] = AuthorizationCode(
                code=auth_code,
                client_id=client_id,
                redirect_uri=redirect_uri,
                scope=scope,
                user_id="strunz_user",  # In production, get from login
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            
            # Redirect back with code
            redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
            return RedirectResponse(url=redirect_url)
        
        @self.app.post("/oauth/token")
        async def token(request: Request):
            """Token endpoint"""
            # Parse form data
            form_data = await request.form()
            grant_type = form_data.get("grant_type")
            
            # Get client credentials from Authorization header or form
            client_id, client_secret = self._get_client_credentials(request, form_data)
            
            if not client_id or client_id not in registered_clients:
                raise HTTPException(status_code=401, detail="Invalid client")
            
            client = registered_clients[client_id]
            
            # Verify client secret
            if client.client_secret and client.client_secret != client_secret:
                raise HTTPException(status_code=401, detail="Invalid client credentials")
            
            if grant_type == "authorization_code":
                return await self._handle_authorization_code_grant(form_data, client)
            elif grant_type == "refresh_token":
                return await self._handle_refresh_token_grant(form_data, client)
            else:
                raise HTTPException(status_code=400, detail="Unsupported grant_type")
        
        @self.app.get("/oauth/userinfo")
        async def userinfo(request: Request):
            """UserInfo endpoint (optional but useful)"""
            # Get access token from Authorization header
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = auth_header[7:]
            
            # Validate token
            if token not in access_tokens:
                raise HTTPException(status_code=401, detail="Invalid access token")
            
            access_token = access_tokens[token]
            if access_token.is_expired():
                raise HTTPException(status_code=401, detail="Token expired")
            
            # Return user info
            return {
                "sub": access_token.user_id,
                "name": "Dr. Strunz Knowledge User",
                "email": "user@strunz-knowledge.com",
                "scope": access_token.scope
            }
    
    def _get_client_credentials(self, request: Request, form_data) -> tuple:
        """Extract client credentials from request"""
        # Try Authorization header first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Basic "):
            import base64
            try:
                decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                client_id, client_secret = decoded.split(':', 1)
                return client_id, client_secret
            except:
                pass
        
        # Try form data
        client_id = form_data.get("client_id")
        client_secret = form_data.get("client_secret")
        return client_id, client_secret
    
    async def _handle_authorization_code_grant(self, form_data, client: OAuthClient) -> Dict:
        """Handle authorization code grant"""
        code = form_data.get("code")
        redirect_uri = form_data.get("redirect_uri")
        code_verifier = form_data.get("code_verifier")
        
        if not code or code not in authorization_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        auth_code = authorization_codes[code]
        
        # Validate code
        if auth_code.is_expired():
            raise HTTPException(status_code=400, detail="Authorization code expired")
        
        if auth_code.client_id != client.client_id:
            raise HTTPException(status_code=400, detail="Code not issued to this client")
        
        if auth_code.redirect_uri != redirect_uri:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")
        
        # Validate PKCE if present
        if auth_code.code_challenge:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="Code verifier required")
            
            if auth_code.code_challenge_method == "S256":
                verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
                verifier_challenge = base64.urlsafe_b64encode(verifier_hash).decode().rstrip('=')
                if verifier_challenge != auth_code.code_challenge:
                    raise HTTPException(status_code=400, detail="Invalid code verifier")
            elif auth_code.code_challenge != code_verifier:
                raise HTTPException(status_code=400, detail="Invalid code verifier")
        
        # Generate tokens
        access_token = self._generate_access_token(client.client_id, auth_code.user_id, auth_code.scope)
        refresh_token = secrets.token_urlsafe(32)
        
        # Store tokens
        access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope,
            expires_at=datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY)
        )
        refresh_tokens[refresh_token] = access_token
        
        # Remove used authorization code
        del authorization_codes[code]
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": TOKEN_EXPIRY,
            "refresh_token": refresh_token,
            "scope": auth_code.scope
        }
    
    async def _handle_refresh_token_grant(self, form_data, client: OAuthClient) -> Dict:
        """Handle refresh token grant"""
        refresh_token = form_data.get("refresh_token")
        
        if not refresh_token or refresh_token not in refresh_tokens:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        # Get associated access token
        old_access_token = refresh_tokens[refresh_token]
        if old_access_token not in access_tokens:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        old_token_data = access_tokens[old_access_token]
        
        # Generate new access token
        new_access_token = self._generate_access_token(
            client.client_id,
            old_token_data.user_id,
            old_token_data.scope
        )
        
        # Store new token
        access_tokens[new_access_token] = AccessToken(
            token=new_access_token,
            client_id=client.client_id,
            user_id=old_token_data.user_id,
            scope=old_token_data.scope,
            expires_at=datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY)
        )
        
        # Clean up old token
        del access_tokens[old_access_token]
        refresh_tokens[refresh_token] = new_access_token
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": TOKEN_EXPIRY,
            "refresh_token": refresh_token,
            "scope": old_token_data.scope
        }
    
    def _generate_access_token(self, client_id: str, user_id: str, scope: str) -> str:
        """Generate JWT access token"""
        payload = {
            "iss": ISSUER_URL,
            "sub": user_id,
            "aud": client_id,
            "exp": int(time.time()) + TOKEN_EXPIRY,
            "iat": int(time.time()),
            "scope": scope
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


# Create OAuth provider instance
oauth_provider = OAuthProvider()
oauth_app = oauth_provider.app