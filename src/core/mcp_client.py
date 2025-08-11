#!/usr/bin/env python3
"""
OSA MCP Client Integration
Connects to Model Context Protocol servers for enhanced capabilities
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging

# Try importing MCP SDK if available
try:
    import mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP SDK not available. Install with: pip install mcp")


class MCPServerType(Enum):
    """Types of MCP servers"""
    FILESYSTEM = "filesystem"
    GIT = "git"
    GITHUB = "github"
    MEMORY = "memory"
    PLAYWRIGHT = "playwright"
    PUPPETEER = "puppeteer"
    POSTGRES = "postgres"
    SQLITE = "sqlite"
    SLACK = "slack"
    DISCORD = "discord"
    ZAPIER = "zapier"
    CUSTOM = "custom"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    server_type: MCPServerType
    command: str
    args: List[str]
    env: Dict[str, str] = None
    config: Dict[str, Any] = None
    enabled: bool = True
    auto_start: bool = True
    

class MCPClient:
    """MCP Client for OSA to connect to various MCP servers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("OSA-MCP")
        self.servers = {}
        self.processes = {}
        self.connected_servers = {}
        
        # Default MCP server configurations
        self.default_configs = self._get_default_configs()
        
        # Load user configuration
        self.user_config_path = Path.home() / ".osa" / "mcp_config.json"
        self.load_user_config()
    
    def _get_default_configs(self) -> Dict[str, MCPServerConfig]:
        """Get default MCP server configurations"""
        configs = {}
        
        # Filesystem server
        configs["filesystem"] = MCPServerConfig(
            name="filesystem",
            server_type=MCPServerType.FILESYSTEM,
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(Path.home() / "Documents"),
                str(Path.cwd())
            ],
            config={
                "allowed_directories": [
                    str(Path.home() / "Documents"),
                    str(Path.cwd())
                ]
            }
        )
        
        # Git server
        configs["git"] = MCPServerConfig(
            name="git",
            server_type=MCPServerType.GIT,
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-git"
            ]
        )
        
        # GitHub server
        configs["github"] = MCPServerConfig(
            name="github",
            server_type=MCPServerType.GITHUB,
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            env={
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
            }
        )
        
        # Memory server
        configs["memory"] = MCPServerConfig(
            name="memory",
            server_type=MCPServerType.MEMORY,
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-memory"
            ]
        )
        
        # Playwright server (Microsoft official)
        configs["playwright"] = MCPServerConfig(
            name="playwright",
            server_type=MCPServerType.PLAYWRIGHT,
            command="npx",
            args=[
                "-y",
                "@microsoft/playwright-mcp"
            ],
            config={
                "headless": False,
                "isolated": True
            }
        )
        
        # SQLite server
        configs["sqlite"] = MCPServerConfig(
            name="sqlite",
            server_type=MCPServerType.SQLITE,
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-sqlite",
                str(Path.home() / ".osa" / "osa.db")
            ],
            config={
                "database_path": str(Path.home() / ".osa" / "osa.db")
            }
        )
        
        return configs
    
    def load_user_config(self):
        """Load user-specific MCP configuration"""
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, 'r') as f:
                    user_config = json.load(f)
                    
                # Merge with default configs
                for server_name, server_config in user_config.get("servers", {}).items():
                    if server_name in self.default_configs:
                        # Update existing config
                        default = self.default_configs[server_name]
                        if "args" in server_config:
                            default.args = server_config["args"]
                        if "env" in server_config:
                            default.env = server_config["env"]
                        if "config" in server_config:
                            default.config = server_config["config"]
                        if "enabled" in server_config:
                            default.enabled = server_config["enabled"]
                    else:
                        # Add new custom server
                        self.default_configs[server_name] = MCPServerConfig(
                            name=server_name,
                            server_type=MCPServerType.CUSTOM,
                            command=server_config.get("command", "npx"),
                            args=server_config.get("args", []),
                            env=server_config.get("env", {}),
                            config=server_config.get("config", {}),
                            enabled=server_config.get("enabled", True)
                        )
                        
            except Exception as e:
                self.logger.error(f"Failed to load user MCP config: {e}")
    
    def save_user_config(self):
        """Save current configuration to user config file"""
        self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "servers": {}
        }
        
        for name, config in self.default_configs.items():
            config_data["servers"][name] = {
                "command": config.command,
                "args": config.args,
                "env": config.env,
                "config": config.config,
                "enabled": config.enabled,
                "auto_start": config.auto_start
            }
        
        with open(self.user_config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        if server_name not in self.default_configs:
            self.logger.error(f"Unknown server: {server_name}")
            return False
        
        config = self.default_configs[server_name]
        if not config.enabled:
            self.logger.info(f"Server {server_name} is disabled")
            return False
        
        if server_name in self.processes:
            self.logger.info(f"Server {server_name} is already running")
            return True
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if config.env:
                env.update(config.env)
            
            # Start the server process
            self.logger.info(f"Starting MCP server: {server_name}")
            process = await asyncio.create_subprocess_exec(
                config.command,
                *config.args,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            self.processes[server_name] = process
            
            # Wait a bit for server to initialize
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.returncode is None:
                self.logger.info(f"✓ MCP server {server_name} started successfully")
                self.connected_servers[server_name] = config
                return True
            else:
                self.logger.error(f"MCP server {server_name} failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server"""
        if server_name not in self.processes:
            self.logger.info(f"Server {server_name} is not running")
            return True
        
        try:
            process = self.processes[server_name]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                # Force kill if needed
                process.kill()
                await process.wait()
            
            del self.processes[server_name]
            if server_name in self.connected_servers:
                del self.connected_servers[server_name]
            
            self.logger.info(f"✓ MCP server {server_name} stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop MCP server {server_name}: {e}")
            return False
    
    async def restart_server(self, server_name: str) -> bool:
        """Restart an MCP server"""
        await self.stop_server(server_name)
        await asyncio.sleep(1)
        return await self.start_server(server_name)
    
    async def start_all_servers(self):
        """Start all enabled MCP servers"""
        self.logger.info("Starting all enabled MCP servers...")
        
        for server_name, config in self.default_configs.items():
            if config.enabled and config.auto_start:
                success = await self.start_server(server_name)
                if not success:
                    self.logger.warning(f"Failed to start {server_name}")
        
        self.logger.info(f"✓ Started {len(self.connected_servers)} MCP servers")
    
    async def stop_all_servers(self):
        """Stop all running MCP servers"""
        self.logger.info("Stopping all MCP servers...")
        
        server_names = list(self.processes.keys())
        for server_name in server_names:
            await self.stop_server(server_name)
        
        self.logger.info("✓ All MCP servers stopped")
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get status of a specific MCP server"""
        if server_name not in self.default_configs:
            return {"status": "unknown", "error": "Server not configured"}
        
        config = self.default_configs[server_name]
        is_running = server_name in self.processes
        
        return {
            "name": server_name,
            "type": config.server_type.value,
            "enabled": config.enabled,
            "running": is_running,
            "auto_start": config.auto_start,
            "config": config.config
        }
    
    def get_all_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        return {
            "total_configured": len(self.default_configs),
            "total_running": len(self.processes),
            "servers": {
                name: self.get_server_status(name)
                for name in self.default_configs.keys()
            }
        }
    
    async def send_command(self, server_name: str, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a command to an MCP server"""
        if server_name not in self.processes:
            self.logger.error(f"Server {server_name} is not running")
            return None
        
        try:
            process = self.processes[server_name]
            
            # Send command as JSON
            command_json = json.dumps(command) + "\n"
            process.stdin.write(command_json.encode())
            await process.stdin.drain()
            
            # Read response
            response_line = await process.stdout.readline()
            if response_line:
                return json.loads(response_line.decode())
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to send command to {server_name}: {e}")
            return None
    
    async def call_tool(self, server_name: str, tool_name: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Call a tool on an MCP server"""
        command = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
        
        return await self.send_command(server_name, command)
    
    # Convenience methods for common operations
    
    async def read_file(self, file_path: str) -> Optional[str]:
        """Read a file using filesystem MCP server"""
        if "filesystem" not in self.connected_servers:
            await self.start_server("filesystem")
        
        result = await self.call_tool("filesystem", "read_file", {"path": file_path})
        return result.get("content") if result else None
    
    async def write_file(self, file_path: str, content: str) -> bool:
        """Write a file using filesystem MCP server"""
        if "filesystem" not in self.connected_servers:
            await self.start_server("filesystem")
        
        result = await self.call_tool("filesystem", "write_file", {
            "path": file_path,
            "content": content
        })
        return result.get("success", False) if result else False
    
    async def git_status(self, repo_path: str = ".") -> Optional[str]:
        """Get git status using git MCP server"""
        if "git" not in self.connected_servers:
            await self.start_server("git")
        
        result = await self.call_tool("git", "status", {"path": repo_path})
        return result.get("output") if result else None
    
    async def browse_web(self, url: str) -> Optional[str]:
        """Browse a webpage using Playwright MCP server"""
        if "playwright" not in self.connected_servers:
            await self.start_server("playwright")
        
        result = await self.call_tool("playwright", "navigate", {"url": url})
        return result.get("content") if result else None
    
    async def query_memory(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Query the memory MCP server"""
        if "memory" not in self.connected_servers:
            await self.start_server("memory")
        
        result = await self.call_tool("memory", "query", {"query": query})
        return result.get("results") if result else None
    
    async def store_memory(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store data in memory MCP server"""
        if "memory" not in self.connected_servers:
            await self.start_server("memory")
        
        result = await self.call_tool("memory", "store", {
            "key": key,
            "value": value,
            "metadata": metadata or {}
        })
        return result.get("success", False) if result else False


# Create singleton instance
_mcp_client = None

def get_mcp_client(config: Dict[str, Any] = None) -> MCPClient:
    """Get or create the global MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(config)
    return _mcp_client