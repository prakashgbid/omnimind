#!/usr/bin/env python3
"""
OSA Real-time Logger and WebSocket Server

Provides real-time logging of all OSA activities through WebSocket
for the web monitoring interface.
"""

import asyncio
import json
import logging

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with the specified name and level.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler if not exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum


class LogType(Enum):
    """Types of log entries"""
    THINKING = "thinking"
    LEARNING = "learning"
    EXECUTING = "executing"
    DELEGATION = "delegation"
    ERROR = "error"
    SYSTEM = "system"
    ARCHITECTURE = "architecture"
    PATTERN = "pattern"
    BLOCKER = "blocker"
    ALTERNATIVE = "alternative"


@dataclass
class LogEntry:
    """Represents a single log entry"""
    type: LogType
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return {
            'type': self.type.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }


class OSALogger:
    """
    Real-time logger for OSA activities.
    Sends logs to web interface via WebSocket.
    """
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.clients = set()
        self.logs = deque(maxlen=10000)  # Keep last 10k logs
        self.sessions = []
        self.current_session_id = None
        self.metrics = {
            'thoughts': 0,
            'chains': 0,
            'contexts': 0,
            'blockers': 0,
            'patterns': 0,
            'efficiency': 0
        }
        
        # Setup file logging
        self.setup_file_logging()
        
        # Start WebSocket server in background
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        
        # Log startup
        self.log(LogType.SYSTEM, "OSA Logger initialized")
    
    def setup_file_logging(self):
        """Setup file-based logging"""
        log_dir = Path.home() / ".omnimind" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session directory
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = log_dir / self.current_session_id
        session_dir.mkdir(exist_ok=True)
        
        # Setup Python logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(session_dir / "osa.log"),
                logging.StreamHandler()
            ]
        )
        
        self.session_dir = session_dir
        self.logger = logging.getLogger('OSA')
    
    def log(self, log_type: LogType, message: str, metadata: Dict[str, Any] = None):
        """Log an event"""
        entry = LogEntry(
            type=log_type,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        # Add to memory
        self.logs.append(entry)
        
        # Log to file
        self.logger.info(f"[{log_type.value}] {message}")
        
        # Send to WebSocket clients
        asyncio.run_coroutine_threadsafe(
            self.broadcast(entry),
            self.loop
        )
        
        # Update metrics based on log type
        self.update_metrics(log_type, metadata)
    
    def update_metrics(self, log_type: LogType, metadata: Optional[Dict]):
        """Update metrics based on log entry"""
        if log_type == LogType.THINKING:
            self.metrics['thoughts'] += 1
            if metadata and 'chain_depth' in metadata:
                self.metrics['chains'] += 1
        elif log_type == LogType.BLOCKER:
            self.metrics['blockers'] += 1
        elif log_type == LogType.PATTERN:
            self.metrics['patterns'] += 1
        elif log_type == LogType.LEARNING:
            if metadata and 'efficiency_gain' in metadata:
                self.metrics['efficiency'] = min(100, 
                    self.metrics['efficiency'] + metadata['efficiency_gain'])
        
        # Broadcast metrics update
        asyncio.run_coroutine_threadsafe(
            self.broadcast_metrics(),
            self.loop
        )
    
    async def broadcast(self, entry: LogEntry):
        """Broadcast log entry to all connected clients"""
        if self.clients:
            message = json.dumps({
                'type': 'log',
                'category': entry.type.value,
                'message': entry.message,
                'timestamp': entry.timestamp.isoformat(),
                'metadata': entry.metadata or {}
            })
            
            # Send to all clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected
    
    async def broadcast_metrics(self):
        """Broadcast metrics update to all clients"""
        if self.clients:
            message = json.dumps({
                'type': 'metrics',
                'metrics': self.metrics
            })
            
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            self.clients -= disconnected
    
    async def handle_client(self, websocket, path):
        """Handle a WebSocket client connection"""
        # Register client
        self.clients.add(websocket)
        
        try:
            # Send initial state
            await websocket.send(json.dumps({
                'type': 'status',
                'status': {
                    'connected': True,
                    'session_id': self.current_session_id,
                    'total_logs': len(self.logs)
                }
            }))
            
            # Send current metrics
            await websocket.send(json.dumps({
                'type': 'metrics',
                'metrics': self.metrics
            }))
            
            # Send recent logs
            for log in list(self.logs)[-50:]:  # Last 50 logs
                await websocket.send(json.dumps({
                    'type': 'log',
                    'category': log.type.value,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat(),
                    'metadata': log.metadata or {}
                }))
            
            # Keep connection alive
            async for message in websocket:
                # Handle client messages if needed
                pass
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Unregister client
            self.clients.discard(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.server = await websockets.serve(
            self.handle_client,
            'localhost',
            self.port
        )
        
        self.log(LogType.SYSTEM, f"WebSocket server started on port {self.port}")
        
        # Keep server running
        await asyncio.Future()
    
    def run_server(self):
        """Run the WebSocket server in a thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())
    
    def log_thinking(self, message: str, depth: int = 0, confidence: float = 0.5):
        """Log a thinking event"""
        self.log(LogType.THINKING, message, {
            'depth': depth,
            'confidence': confidence
        })
    
    def log_learning(self, message: str, pattern: str = None, efficiency_gain: float = 0):
        """Log a learning event"""
        self.log(LogType.LEARNING, message, {
            'pattern': pattern,
            'efficiency_gain': efficiency_gain
        })
    
    def log_execution(self, message: str, task: str = None, instance_id: str = None):
        """Log an execution event"""
        self.log(LogType.EXECUTING, message, {
            'task': task,
            'instance_id': instance_id
        })
    
    def log_delegation(self, message: str, work_item: str = None, assigned_to: str = None):
        """Log a delegation event"""
        self.log(LogType.DELEGATION, message, {
            'work_item': work_item,
            'assigned_to': assigned_to
        })
    
    def log_blocker(self, message: str, alternatives: int = 0):
        """Log a blocker detection"""
        self.log(LogType.BLOCKER, message, {
            'alternatives_generated': alternatives
        })
    
    def log_error(self, message: str, error_type: str = None):
        """Log an error"""
        self.log(LogType.ERROR, message, {
            'error_type': error_type
        })
    
    def save_session(self):
        """Save current session to file"""
        session_file = self.session_dir / "session.json"
        
        session_data = {
            'id': self.current_session_id,
            'timestamp': datetime.now().isoformat(),
            'logs': [log.to_dict() for log in self.logs],
            'metrics': self.metrics
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.log(LogType.SYSTEM, f"Session saved: {self.current_session_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get logger status"""
        return {
            'session_id': self.current_session_id,
            'total_logs': len(self.logs),
            'connected_clients': len(self.clients),
            'metrics': self.metrics,
            'session_dir': str(self.session_dir)
        }


# Global logger instance
_logger_instance = None

def get_osa_logger() -> OSALogger:
    """Get or create the global OSA logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = OSALogger()
    return _logger_instance


# Integration with OSA
def integrate_logger_with_osa(osa_instance):
    """Integrate the logger with an OSA instance"""
    logger = get_osa_logger()
    
    # Store logger in OSA
    osa_instance.logger_instance = logger
    
    # Override logging methods
    original_log = osa_instance.logger.info if hasattr(osa_instance, 'logger') else print
    
    def enhanced_log(message):
        # Original logging
        original_log(message)
        
        # Determine log type from message
        message_lower = message.lower()
        
        if 'thinking' in message_lower or '💭' in message:
            logger.log_thinking(message)
        elif 'learning' in message_lower or '📚' in message:
            logger.log_learning(message)
        elif 'executing' in message_lower or '🚀' in message:
            logger.log_execution(message)
        elif 'delegat' in message_lower or '📋' in message:
            logger.log_delegation(message)
        elif 'block' in message_lower or '🚧' in message:
            logger.log_blocker(message)
        elif 'error' in message_lower or '❌' in message:
            logger.log_error(message)
        else:
            logger.log(LogType.SYSTEM, message)
    
    # Replace logger
    if hasattr(osa_instance, 'logger'):
        osa_instance.logger.info = enhanced_log
    
    return osa_instance


# Demo/Test
if __name__ == "__main__":
    import time
    
    logger = get_osa_logger()
    
    print("OSA Logger running on ws://localhost:8765")
    print("Open web/index.html in a browser to view logs")
    
    # Simulate OSA activity
    logger.log_thinking("Analyzing user goal: Build a viral app")
    time.sleep(1)
    
    logger.log_thinking("Breaking down into subtasks", depth=1, confidence=0.8)
    time.sleep(1)
    
    logger.log_learning("Pattern recognized: Similar to previous social app", 
                        pattern="social_app", efficiency_gain=15)
    time.sleep(1)
    
    logger.log_execution("Spawning Claude instance for backend")
    time.sleep(1)
    
    logger.log_delegation("Delegating frontend to Claude_2", 
                         work_item="frontend", assigned_to="Claude_2")
    time.sleep(1)
    
    logger.log_blocker("Database connection timeout", alternatives=3)
    time.sleep(1)
    
    logger.log_thinking("Finding alternative: Use connection pool", 
                       depth=2, confidence=0.9)
    
    print("\nLogger running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.save_session()
        print("\nSession saved. Goodbye!")