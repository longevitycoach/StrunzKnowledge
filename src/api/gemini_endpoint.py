"""
Gemini API endpoint with rate limiting and throttling
Uses server-side GOOGLE_GEMINI_API_KEY from environment
"""

import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Optional
import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GeminiRequest(BaseModel):
    """Request model for Gemini API calls"""
    prompt: str = Field(..., description="The prompt to send to Gemini")
    tool_type: str = Field("search", description="Tool type: search, ask, or analyze")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: int = Field(2048, ge=1, le=4096, description="Maximum tokens to generate")


class RateLimiter:
    """
    Rate limiter with multiple tiers of protection:
    - Per-IP rate limiting
    - Global rate limiting
    - Daily quota management
    - Cost tracking
    """
    
    def __init__(self):
        # Per-IP tracking
        self.ip_requests: Dict[str, list] = defaultdict(list)
        self.ip_daily_tokens: Dict[str, int] = defaultdict(int)
        
        # Global tracking
        self.global_requests = []
        self.daily_tokens = 0
        self.daily_cost = 0.0
        self.last_reset = datetime.now()
        
        # Configuration (conservative limits for cost control)
        self.config = {
            # Per-IP limits
            "requests_per_minute_per_ip": 5,
            "requests_per_hour_per_ip": 30,
            "daily_tokens_per_ip": 50000,  # ~25 requests
            
            # Global limits
            "requests_per_minute_global": 20,
            "requests_per_hour_global": 200,
            "daily_tokens_global": 500000,  # ~250 requests
            "daily_cost_limit": 5.0,  # $5 per day max
            
            # Gemini pricing (as of 2024)
            "cost_per_1k_input_tokens": 0.00025,
            "cost_per_1k_output_tokens": 0.0005,
        }
        
    def _cleanup_old_requests(self, requests: list, window_minutes: int):
        """Remove requests older than the specified window"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        return [req for req in requests if req > cutoff]
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters at midnight"""
        if datetime.now().date() > self.last_reset.date():
            self.ip_daily_tokens.clear()
            self.daily_tokens = 0
            self.daily_cost = 0.0
            self.last_reset = datetime.now()
            logger.info("Daily rate limit counters reset")
    
    def check_rate_limit(self, ip: str, estimated_tokens: int = 2000) -> tuple[bool, str]:
        """
        Check if request should be allowed
        Returns (allowed, reason_if_denied)
        """
        self._reset_daily_counters_if_needed()
        
        # Check global daily cost limit
        estimated_cost = (estimated_tokens / 1000) * self.config["cost_per_1k_output_tokens"]
        if self.daily_cost + estimated_cost > self.config["daily_cost_limit"]:
            return False, f"Daily cost limit exceeded (${self.config['daily_cost_limit']})"
        
        # Check global daily token limit
        if self.daily_tokens + estimated_tokens > self.config["daily_tokens_global"]:
            return False, "Daily token limit exceeded"
        
        # Check per-IP daily token limit
        if self.ip_daily_tokens[ip] + estimated_tokens > self.config["daily_tokens_per_ip"]:
            return False, "Daily token limit exceeded for your IP"
        
        # Clean up old requests
        self.ip_requests[ip] = self._cleanup_old_requests(self.ip_requests[ip], 60)
        self.global_requests = self._cleanup_old_requests(self.global_requests, 60)
        
        # Check per-minute limits
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        ip_requests_last_minute = sum(1 for req in self.ip_requests[ip] if req > minute_ago)
        if ip_requests_last_minute >= self.config["requests_per_minute_per_ip"]:
            return False, "Rate limit exceeded: too many requests per minute"
        
        global_requests_last_minute = sum(1 for req in self.global_requests if req > minute_ago)
        if global_requests_last_minute >= self.config["requests_per_minute_global"]:
            return False, "Server busy: global rate limit reached"
        
        # Check per-hour limits
        hour_ago = now - timedelta(hours=1)
        
        ip_requests_last_hour = sum(1 for req in self.ip_requests[ip] if req > hour_ago)
        if ip_requests_last_hour >= self.config["requests_per_hour_per_ip"]:
            return False, "Rate limit exceeded: too many requests per hour"
        
        global_requests_last_hour = sum(1 for req in self.global_requests if req > hour_ago)
        if global_requests_last_hour >= self.config["requests_per_hour_global"]:
            return False, "Server busy: global hourly limit reached"
        
        return True, ""
    
    def record_request(self, ip: str, tokens_used: int, cost: float):
        """Record a successful request"""
        now = datetime.now()
        
        # Record the request
        self.ip_requests[ip].append(now)
        self.global_requests.append(now)
        
        # Update token counts
        self.ip_daily_tokens[ip] += tokens_used
        self.daily_tokens += tokens_used
        self.daily_cost += cost
        
        # Log usage
        logger.info(f"Request from {ip}: {tokens_used} tokens, ${cost:.4f} cost. "
                   f"Daily total: {self.daily_tokens} tokens, ${self.daily_cost:.2f}")
    
    def get_stats(self) -> dict:
        """Get current rate limit statistics"""
        self._reset_daily_counters_if_needed()
        
        return {
            "daily_tokens_used": self.daily_tokens,
            "daily_tokens_limit": self.config["daily_tokens_global"],
            "daily_cost": round(self.daily_cost, 2),
            "daily_cost_limit": self.config["daily_cost_limit"],
            "unique_ips_today": len(self.ip_daily_tokens),
            "requests_last_hour": len(self._cleanup_old_requests(self.global_requests, 60)),
            "last_reset": self.last_reset.isoformat(),
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def create_gemini_endpoint(app):
    """
    Create Gemini API endpoint with rate limiting
    This should be called from the main server initialization
    """
    
    @app.post("/api/gemini/chat")
    async def gemini_chat(request: Request, gemini_request: GeminiRequest):
        """
        Gemini chat endpoint with rate limiting and cost control
        Uses server-side API key from environment
        """
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Check rate limits
        allowed, reason = rate_limiter.check_rate_limit(client_ip, gemini_request.max_tokens)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": reason,
                    "retry_after": 60  # seconds
                }
            )
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            logger.error("GOOGLE_GEMINI_API_KEY not configured")
            raise HTTPException(
                status_code=500,
                detail="Gemini API not configured on server"
            )
        
        try:
            # Import here to avoid circular imports
            from src.llm.gemini_client import GeminiClient
            
            # Create client and generate response
            async with GeminiClient(api_key) as client:
                response = await client.generate_content(
                    gemini_request.prompt,
                    temperature=gemini_request.temperature
                )
                
                # Estimate tokens used (rough estimate)
                input_tokens = len(gemini_request.prompt.split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                total_tokens = int(input_tokens + output_tokens)
                
                # Calculate cost
                input_cost = (input_tokens / 1000) * rate_limiter.config["cost_per_1k_input_tokens"]
                output_cost = (output_tokens / 1000) * rate_limiter.config["cost_per_1k_output_tokens"]
                total_cost = input_cost + output_cost
                
                # Record the request
                rate_limiter.record_request(client_ip, total_tokens, total_cost)
                
                return JSONResponse({
                    "status": "success",
                    "response": response,
                    "tool_type": gemini_request.tool_type,
                    "usage": {
                        "tokens": total_tokens,
                        "cost": round(total_cost, 4)
                    }
                })
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini API error: {str(e)}"
            )
    
    @app.get("/api/gemini/stats")
    async def gemini_stats():
        """Get rate limiting statistics"""
        return JSONResponse({
            "status": "ok",
            "stats": rate_limiter.get_stats()
        })
    
    @app.get("/api/gemini/limits")
    async def gemini_limits():
        """Get rate limit configuration"""
        return JSONResponse({
            "limits": {
                "per_ip": {
                    "requests_per_minute": rate_limiter.config["requests_per_minute_per_ip"],
                    "requests_per_hour": rate_limiter.config["requests_per_hour_per_ip"],
                    "daily_tokens": rate_limiter.config["daily_tokens_per_ip"],
                },
                "global": {
                    "daily_cost_limit": rate_limiter.config["daily_cost_limit"],
                    "daily_tokens": rate_limiter.config["daily_tokens_global"],
                }
            }
        })
    
    logger.info("Gemini API endpoint with rate limiting initialized")