from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"

class Account(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: Optional[str] = Field(None, min_length=6)
    email: Optional[str] = None
    cmdlevel: int = Field(0, ge=0, le=5)
    expansion: str = "ML"
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    characters: Optional[List[Dict[str, str]]] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ServerStatus(BaseModel):
    running: bool
    uptime: Optional[int] = None
    player_count: int = 0
    max_players: int = 300
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_save: Optional[datetime] = None

class ServerConfig(BaseModel):
    server_name: str = "POL Server"
    listen_port: int = 5003
    max_clients: int = 300
    min_cmdlevel_to_login: int = 0
    inactivity_warning_timeout: int = 9
    inactivity_disconnect_timeout: int = 10
    character_slots: int = 5
    require_spellbooks: bool = True
    enable_secure_trading: bool = True
    web_server: bool = False
    web_server_port: int = 8080

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str

class SystemStats(BaseModel):
    cpu_percent: float
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float