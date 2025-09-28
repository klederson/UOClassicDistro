import docker
import os
import subprocess
import asyncio
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import aiofiles
from models import ServerStatus, ServerConfig

class ServerController:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container_name = os.getenv("POL_CONTAINER_NAME", "pol-server")
        self.pol_path = "/workspace"
        self.pol_executable = "./pol"
        self.config_file = Path(self.pol_path) / "pol.cfg"
        
    async def get_container(self):
        """Get POL server container"""
        try:
            return self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            return None
    
    async def get_status(self) -> ServerStatus:
        """Get server status"""
        container = await self.get_container()
        
        if not container:
            return ServerStatus(running=False)
        
        status = container.status == "running"
        
        # Get container stats
        stats = {}
        if status:
            try:
                stats = container.stats(stream=False)
                
                # Calculate CPU usage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
                
                # Calculate memory usage
                memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # MB
                
            except Exception:
                cpu_percent = 0.0
                memory_usage = 0.0
        else:
            cpu_percent = 0.0
            memory_usage = 0.0
        
        # Get player count (would need to parse POL data files or use POL's web interface)
        player_count = await self.get_player_count()
        
        # Get uptime
        uptime = None
        if status:
            try:
                started_at = datetime.fromisoformat(container.attrs['State']['StartedAt'].replace('Z', '+00:00'))
                uptime = int((datetime.now() - started_at.replace(tzinfo=None)).total_seconds())
            except Exception:
                pass
        
        return ServerStatus(
            running=status,
            uptime=uptime,
            player_count=player_count,
            cpu_usage=cpu_percent,
            memory_usage=memory_usage
        )
    
    async def start_server(self) -> dict:
        """Start the POL server"""
        container = await self.get_container()
        
        if container and container.status == "running":
            return {"success": False, "error": "Server is already running"}
        
        try:
            if container:
                container.start()
            else:
                # Run POL in the container
                cmd = f"cd {self.pol_path} && screen -dmS pol {self.pol_executable}"
                container = self.docker_client.containers.get(self.container_name)
                container.exec_run(cmd, user="pol")
                
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def stop_server(self) -> dict:
        """Stop the POL server"""
        container = await self.get_container()
        
        if not container or container.status != "running":
            return {"success": False, "error": "Server is not running"}
        
        try:
            # Send Ctrl+C to POL process
            container.exec_run("screen -S pol -X stuff $'\\003'", user="pol")
            
            # Wait for graceful shutdown
            await asyncio.sleep(5)
            
            # Check if still running and force stop if needed
            if container.status == "running":
                container.stop(timeout=30)
                
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def restart_server(self) -> dict:
        """Restart the POL server"""
        stop_result = await self.stop_server()
        if not stop_result["success"] and "not running" not in stop_result.get("error", ""):
            return stop_result
            
        await asyncio.sleep(2)
        
        return await self.start_server()
    
    async def get_logs(self, lines: int = 100) -> List[str]:
        """Get server logs"""
        log_file = Path(self.pol_path) / "pol.log"
        
        if not log_file.exists():
            return []
        
        try:
            # Use tail to get last N lines
            proc = await asyncio.create_subprocess_exec(
                'tail', '-n', str(lines), str(log_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            return stdout.decode().split('\n') if stdout else []
        except Exception:
            return []
    
    async def get_player_count(self) -> int:
        """Get current player count"""
        # This would need to be implemented based on POL's data structure
        # For now, return a placeholder
        return 0
    
    async def get_config(self) -> ServerConfig:
        """Get server configuration"""
        config = ServerConfig()
        
        if not self.config_file.exists():
            return config
        
        try:
            async with aiofiles.open(self.config_file, 'r') as f:
                content = await f.read()
                
            # Parse pol.cfg
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('#') or not line or '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Map config values
                if key == "ListenPort":
                    config.listen_port = int(value) if value != "0" else 5003
                elif key == "MaximumClients":
                    config.max_clients = int(value)
                elif key == "MinCmdlevelToLogin":
                    config.min_cmdlevel_to_login = int(value)
                elif key == "InactivityWarningTimeout":
                    config.inactivity_warning_timeout = int(value)
                elif key == "InactivityDisconnectTimeout":
                    config.inactivity_disconnect_timeout = int(value)
                elif key == "CharacterSlots":
                    config.character_slots = int(value)
                elif key == "RequireSpellbooks":
                    config.require_spellbooks = value == "1"
                elif key == "EnableSecureTrading":
                    config.enable_secure_trading = value == "1"
                elif key == "WebServer":
                    config.web_server = value == "1"
                elif key == "WebServerPort":
                    config.web_server_port = int(value)
                    
        except Exception as e:
            print(f"Error reading config: {e}")
            
        return config
    
    async def update_config(self, config: ServerConfig) -> dict:
        """Update server configuration"""
        if not self.config_file.exists():
            return {"success": False, "error": "Configuration file not found"}
        
        try:
            # Read current config
            async with aiofiles.open(self.config_file, 'r') as f:
                lines = await f.readlines()
            
            # Update values
            new_lines = []
            for line in lines:
                stripped = line.strip()
                
                if stripped.startswith('#') or not stripped or '=' not in stripped:
                    new_lines.append(line)
                    continue
                
                key = stripped.split('=', 1)[0].strip()
                
                # Update matching keys
                if key == "ListenPort":
                    new_lines.append(f"ListenPort={config.listen_port}\n")
                elif key == "MaximumClients":
                    new_lines.append(f"MaximumClients={config.max_clients}\n")
                elif key == "MinCmdlevelToLogin":
                    new_lines.append(f"MinCmdlevelToLogin={config.min_cmdlevel_to_login}\n")
                elif key == "InactivityWarningTimeout":
                    new_lines.append(f"InactivityWarningTimeout={config.inactivity_warning_timeout}\n")
                elif key == "InactivityDisconnectTimeout":
                    new_lines.append(f"InactivityDisconnectTimeout={config.inactivity_disconnect_timeout}\n")
                elif key == "CharacterSlots":
                    new_lines.append(f"CharacterSlots={config.character_slots}\n")
                elif key == "RequireSpellbooks":
                    new_lines.append(f"RequireSpellbooks={'1' if config.require_spellbooks else '0'}\n")
                elif key == "EnableSecureTrading":
                    new_lines.append(f"EnableSecureTrading={'1' if config.enable_secure_trading else '0'}\n")
                elif key == "WebServer":
                    new_lines.append(f"WebServer={'1' if config.web_server else '0'}\n")
                elif key == "WebServerPort":
                    new_lines.append(f"WebServerPort={config.web_server_port}\n")
                else:
                    new_lines.append(line)
            
            # Write back
            async with aiofiles.open(self.config_file, 'w') as f:
                await f.writelines(new_lines)
                
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def compile_scripts(self, path: Optional[str] = None) -> dict:
        """Compile POL scripts"""
        container = await self.get_container()
        
        if not container:
            return {"success": False, "error": "Container not found"}
        
        try:
            if path:
                cmd = f"{self.pol_path}/scripts/ecompile -A -b -f {path}"
            else:
                cmd = f"{self.pol_path}/scripts/ecompile -A -b -f"
                
            result = container.exec_run(cmd, user="pol")
            
            return {
                "success": result.exit_code == 0,
                "output": result.output.decode() if result.output else ""
            }
        except Exception as e:
            return {"success": False, "error": str(e)}