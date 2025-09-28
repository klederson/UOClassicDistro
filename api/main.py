from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict
import docker
import os
import json
import asyncio
import psutil
from datetime import datetime
import subprocess
from pathlib import Path

# Import our modules
from auth import verify_token, create_access_token
from models import Account, ServerStatus, ServerConfig, LoginRequest
from account_manager import AccountManager
from server_controller import ServerController

app = FastAPI(title="POL Server Control API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize managers
account_manager = AccountManager("/workspace/accounts")
server_controller = ServerController()

# Authentication endpoint
@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Login to the control panel"""
    # For demo purposes, using a simple check
    if login_data.username == "admin" and login_data.password == os.getenv("POL_ADMIN_PASSWORD", "admin123"):
        access_token = create_access_token(data={"sub": login_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

# Server status endpoint
@app.get("/api/server/status")
async def get_server_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current server status"""
    verify_token(credentials.credentials)
    
    status = await server_controller.get_status()
    return status

# Start server endpoint
@app.post("/api/server/start")
async def start_server(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Start the POL server"""
    verify_token(credentials.credentials)
    
    result = await server_controller.start_server()
    if result["success"]:
        return {"message": "Server started successfully"}
    else:
        raise HTTPException(status_code=500, detail=result["error"])

# Stop server endpoint
@app.post("/api/server/stop")
async def stop_server(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Stop the POL server"""
    verify_token(credentials.credentials)
    
    result = await server_controller.stop_server()
    if result["success"]:
        return {"message": "Server stopped successfully"}
    else:
        raise HTTPException(status_code=500, detail=result["error"])

# Restart server endpoint
@app.post("/api/server/restart")
async def restart_server(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Restart the POL server"""
    verify_token(credentials.credentials)
    
    result = await server_controller.restart_server()
    if result["success"]:
        return {"message": "Server restarted successfully"}
    else:
        raise HTTPException(status_code=500, detail=result["error"])

# Get server logs
@app.get("/api/server/logs")
async def get_server_logs(
    lines: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get server logs"""
    verify_token(credentials.credentials)
    
    logs = await server_controller.get_logs(lines)
    return {"logs": logs}

# Account management endpoints
@app.get("/api/accounts")
async def list_accounts(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List all accounts"""
    verify_token(credentials.credentials)
    
    accounts = await account_manager.list_accounts()
    return {"accounts": accounts}

@app.get("/api/accounts/{username}")
async def get_account(username: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get account details"""
    verify_token(credentials.credentials)
    
    account = await account_manager.get_account(username)
    if account:
        return account
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/accounts")
async def create_account(account: Account, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new account"""
    verify_token(credentials.credentials)
    
    result = await account_manager.create_account(account)
    if result["success"]:
        return {"message": "Account created successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.put("/api/accounts/{username}")
async def update_account(
    username: str,
    account: Account,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update an account"""
    verify_token(credentials.credentials)
    
    result = await account_manager.update_account(username, account)
    if result["success"]:
        return {"message": "Account updated successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.delete("/api/accounts/{username}")
async def delete_account(username: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an account"""
    verify_token(credentials.credentials)
    
    result = await account_manager.delete_account(username)
    if result["success"]:
        return {"message": "Account deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

# Server configuration endpoints
@app.get("/api/config")
async def get_server_config(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get server configuration"""
    verify_token(credentials.credentials)
    
    config = await server_controller.get_config()
    return config

@app.put("/api/config")
async def update_server_config(
    config: ServerConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update server configuration"""
    verify_token(credentials.credentials)
    
    result = await server_controller.update_config(config)
    if result["success"]:
        return {"message": "Configuration updated successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

# System stats endpoint
@app.get("/api/system/stats")
async def get_system_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get system statistics"""
    verify_token(credentials.credentials)
    
    stats = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "percent": psutil.disk_usage('/').percent
        }
    }
    return stats

# WebSocket endpoint for real-time logs
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send latest log lines
            logs = await server_controller.get_logs(50)
            await websocket.send_json({"logs": logs})
            await asyncio.sleep(2)  # Update every 2 seconds
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)