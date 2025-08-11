#!/usr/bin/env python3
"""
OSA System Readiness Checker
Ensures all components are operational before starting
"""

import os
import sys
import time
import asyncio
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ComponentStatus(Enum):
    """Status of a system component"""
    CHECKING = "⏳"
    READY = "✅"
    WARNING = "⚠️"
    FAILED = "❌"
    SKIPPED = "⏭️"


@dataclass
class ComponentCheck:
    """Result of a component check"""
    name: str
    status: ComponentStatus
    message: str
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class SystemReadiness:
    """System readiness checker for OSA"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checks = []
        self.start_time = None
        self.total_time = 0
        
        # Component states
        self.ollama_ready = False
        self.database_ready = False
        self.cache_ready = False
        self.history_ready = False
        self.context_ready = False
        self.knowledge_ready = False
        
    async def run_all_checks(self) -> Tuple[bool, List[ComponentCheck]]:
        """Run all system checks"""
        self.start_time = time.time()
        self.checks = []
        
        # Display header
        self._print_header()
        
        # Run checks in order of importance
        checks_to_run = [
            self.check_python_version,
            self.check_ollama_connection,
            self.check_models_available,
            self.check_database,
            self.check_cache_system,
            self.check_history_system,
            self.check_context_manager,
            self.check_knowledge_base,
            self.check_background_services,
            self.check_disk_space,
            self.check_memory_available,
            self.check_network_connectivity,
        ]
        
        for check_func in checks_to_run:
            await self._run_check(check_func)
        
        # Calculate results
        self.total_time = time.time() - self.start_time
        all_ready = all(
            check.status in [ComponentStatus.READY, ComponentStatus.WARNING] 
            for check in self.checks
        )
        
        # Display summary
        self._print_summary(all_ready)
        
        return all_ready, self.checks
    
    def _print_header(self):
        """Print the header for readiness checks"""
        print("\n" + "═" * 60)
        print("OSA System Initialization")
        print("═" * 60)
    
    def _print_summary(self, all_ready: bool):
        """Print summary of checks"""
        ready_count = sum(1 for c in self.checks if c.status == ComponentStatus.READY)
        warning_count = sum(1 for c in self.checks if c.status == ComponentStatus.WARNING)
        failed_count = sum(1 for c in self.checks if c.status == ComponentStatus.FAILED)
        
        print("═" * 60)
        
        if all_ready:
            print(f"✅ Status: READY ({ready_count}/{len(self.checks)} systems operational)")
            if warning_count > 0:
                print(f"⚠️  Warnings: {warning_count} components need attention")
        else:
            print(f"❌ Status: NOT READY ({failed_count} critical failures)")
        
        print(f"⏱️  Initialization time: {self.total_time:.2f}s")
        print("═" * 60 + "\n")
    
    async def _run_check(self, check_func) -> ComponentCheck:
        """Run a single check and display result"""
        # Show checking status
        check_name = check_func.__name__.replace('check_', '').replace('_', ' ').title()
        print(f"[{ComponentStatus.CHECKING.value}] {check_name:<25} : ", end='', flush=True)
        
        start = time.time()
        try:
            result = await check_func()
            result.latency_ms = (time.time() - start) * 1000
        except Exception as e:
            result = ComponentCheck(
                name=check_name,
                status=ComponentStatus.FAILED,
                message=f"Exception: {str(e)[:50]}"
            )
        
        # Update display with result
        print(f"\r[{result.status.value}] {check_name:<25} : {result.message}")
        
        if self.verbose and result.details:
            for key, value in result.details.items():
                print(f"    → {key}: {value}")
        
        self.checks.append(result)
        return result
    
    async def check_python_version(self) -> ComponentCheck:
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return ComponentCheck(
                name="Python Version",
                status=ComponentStatus.READY,
                message=f"Python {version.major}.{version.minor}.{version.micro}"
            )
        else:
            return ComponentCheck(
                name="Python Version",
                status=ComponentStatus.WARNING,
                message=f"Python {version.major}.{version.minor} (3.8+ recommended)"
            )
    
    async def check_ollama_connection(self) -> ComponentCheck:
        """Check Ollama service connection"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                self.ollama_ready = True
                return ComponentCheck(
                    name="Ollama Connection",
                    status=ComponentStatus.READY,
                    message="Connected to Ollama service"
                )
            else:
                return ComponentCheck(
                    name="Ollama Connection",
                    status=ComponentStatus.FAILED,
                    message="Ollama service not responding"
                )
        except subprocess.TimeoutExpired:
            return ComponentCheck(
                name="Ollama Connection",
                status=ComponentStatus.FAILED,
                message="Connection timeout (3s)"
            )
        except FileNotFoundError:
            return ComponentCheck(
                name="Ollama Connection",
                status=ComponentStatus.FAILED,
                message="Ollama not installed"
            )
    
    async def check_models_available(self) -> ComponentCheck:
        """Check if required models are available"""
        if not self.ollama_ready:
            return ComponentCheck(
                name="Model Availability",
                status=ComponentStatus.SKIPPED,
                message="Skipped (Ollama not ready)"
            )
        
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = [line.split()[0] for line in lines if line.strip()]
                
                if 'llama3.2:3b' in models:
                    return ComponentCheck(
                        name="Model Availability",
                        status=ComponentStatus.READY,
                        message=f"llama3.2:3b ready ({len(models)} models total)",
                        details={"available_models": models[:3]}  # Show first 3
                    )
                elif models:
                    return ComponentCheck(
                        name="Model Availability",
                        status=ComponentStatus.WARNING,
                        message=f"Using {models[0]} (llama3.2:3b not found)",
                        details={"available_models": models[:3]}
                    )
                else:
                    return ComponentCheck(
                        name="Model Availability",
                        status=ComponentStatus.FAILED,
                        message="No models installed"
                    )
        except Exception as e:
            return ComponentCheck(
                name="Model Availability",
                status=ComponentStatus.FAILED,
                message=f"Error checking models: {str(e)[:30]}"
            )
    
    async def check_database(self) -> ComponentCheck:
        """Check database connection"""
        db_path = Path.home() / ".osa" / "osa.db"
        
        try:
            # Ensure directory exists
            db_path.parent.mkdir(exist_ok=True)
            
            # Test connection
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create tables if not exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    data TEXT
                )
            """)
            
            # Check table
            cursor.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            
            conn.close()
            
            self.database_ready = True
            return ComponentCheck(
                name="Database",
                status=ComponentStatus.READY,
                message=f"SQLite ready ({count} sessions)",
                details={"path": str(db_path), "sessions": count}
            )
        except Exception as e:
            return ComponentCheck(
                name="Database",
                status=ComponentStatus.WARNING,
                message=f"Database error: {str(e)[:30]}"
            )
    
    async def check_cache_system(self) -> ComponentCheck:
        """Check cache system (memory cache for now)"""
        # For now, we use in-memory cache
        # Later can check Redis/Memcached
        
        self.cache_ready = True
        return ComponentCheck(
            name="Cache System",
            status=ComponentStatus.READY,
            message="In-memory cache initialized"
        )
    
    async def check_history_system(self) -> ComponentCheck:
        """Check history file access"""
        history_file = Path.home() / ".osa" / "history.txt"
        
        try:
            history_file.parent.mkdir(exist_ok=True)
            
            if history_file.exists():
                lines = len(history_file.read_text().splitlines())
                self.history_ready = True
                return ComponentCheck(
                    name="History System",
                    status=ComponentStatus.READY,
                    message=f"{lines} entries loaded",
                    details={"path": str(history_file)}
                )
            else:
                history_file.touch()
                self.history_ready = True
                return ComponentCheck(
                    name="History System",
                    status=ComponentStatus.READY,
                    message="History file created"
                )
        except Exception as e:
            return ComponentCheck(
                name="History System",
                status=ComponentStatus.WARNING,
                message=f"History error: {str(e)[:30]}"
            )
    
    async def check_context_manager(self) -> ComponentCheck:
        """Check context manager"""
        # Check available context window
        context_size = 8192  # Default for llama3.2
        
        self.context_ready = True
        return ComponentCheck(
            name="Context Manager",
            status=ComponentStatus.READY,
            message=f"{context_size} tokens available"
        )
    
    async def check_knowledge_base(self) -> ComponentCheck:
        """Check knowledge base"""
        kb_path = Path.home() / ".osa" / "knowledge"
        
        try:
            kb_path.mkdir(exist_ok=True)
            
            # Count knowledge files
            patterns = len(list(kb_path.glob("*.json")))
            
            self.knowledge_ready = True
            return ComponentCheck(
                name="Knowledge Base",
                status=ComponentStatus.READY,
                message=f"{patterns} patterns loaded" if patterns else "Ready (empty)",
                details={"path": str(kb_path)}
            )
        except Exception as e:
            return ComponentCheck(
                name="Knowledge Base",
                status=ComponentStatus.WARNING,
                message="Knowledge base unavailable"
            )
    
    async def check_background_services(self) -> ComponentCheck:
        """Check background services"""
        # Check if we can spawn async tasks
        try:
            loop = asyncio.get_event_loop()
            tasks = len(asyncio.all_tasks(loop))
            
            return ComponentCheck(
                name="Background Services",
                status=ComponentStatus.READY,
                message=f"{tasks} tasks ready"
            )
        except Exception:
            return ComponentCheck(
                name="Background Services",
                status=ComponentStatus.WARNING,
                message="Limited async support"
            )
    
    async def check_disk_space(self) -> ComponentCheck:
        """Check available disk space"""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            percent_used = (used / total) * 100
            
            if free_gb < 1:
                return ComponentCheck(
                    name="Disk Space",
                    status=ComponentStatus.WARNING,
                    message=f"Low space: {free_gb:.1f}GB free",
                    details={"percent_used": f"{percent_used:.0f}%"}
                )
            else:
                return ComponentCheck(
                    name="Disk Space",
                    status=ComponentStatus.READY,
                    message=f"{free_gb:.0f}GB available",
                    details={"percent_used": f"{percent_used:.0f}%"}
                )
        except Exception:
            return ComponentCheck(
                name="Disk Space",
                status=ComponentStatus.SKIPPED,
                message="Unable to check"
            )
    
    async def check_memory_available(self) -> ComponentCheck:
        """Check available memory"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 1:
                return ComponentCheck(
                    name="Memory",
                    status=ComponentStatus.WARNING,
                    message=f"Low memory: {available_gb:.1f}GB available",
                    details={"percent_used": f"{memory.percent:.0f}%"}
                )
            else:
                return ComponentCheck(
                    name="Memory",
                    status=ComponentStatus.READY,
                    message=f"{available_gb:.0f}GB available",
                    details={"percent_used": f"{memory.percent:.0f}%"}
                )
        except ImportError:
            return ComponentCheck(
                name="Memory",
                status=ComponentStatus.SKIPPED,
                message="psutil not installed"
            )
    
    async def check_network_connectivity(self) -> ComponentCheck:
        """Check network connectivity for updates"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            return ComponentCheck(
                name="Network",
                status=ComponentStatus.READY,
                message="Internet connected"
            )
        except Exception:
            return ComponentCheck(
                name="Network",
                status=ComponentStatus.WARNING,
                message="Offline mode"
            )