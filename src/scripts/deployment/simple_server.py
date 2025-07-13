#!/usr/bin/env python3
"""
Minimal server for testing Railway deployment
"""
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Strunz Knowledge Test Server")

@app.get("/")
async def root():
    return JSONResponse({
        "status": "ok",
        "message": "Dr. Strunz Knowledge Base is alive!",
        "server": "simple_server.py"
    })

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting simple server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)