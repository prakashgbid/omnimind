#!/usr/bin/env python3
"""
OSA Metrics and Performance Tracking System
Provides transparency into OSA's operations
"""

import time
import psutil
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ResponseMetrics:
    """Metrics for a single response"""
    start_time: float = 0
    end_time: float = 0
    model_used: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_total: int = 0
    confidence: float = 0.0
    context_usage: float = 0.0
    cache_hit: bool = False
    intent_type: str = ""
    error: Optional[str] = None
    
    @property
    def response_time(self) -> float:
        """Calculate response time in seconds"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0
    
    def to_status_bar(self) -> str:
        """Format metrics for status bar display"""
        time_str = f"{self.response_time:.1f}s" if self.response_time else "--"
        token_str = f"{self.tokens_total}" if self.tokens_total else "--"
        conf_str = f"{self.confidence:.0%}" if self.confidence else "--"
        context_str = f"{self.context_usage:.0%}" if self.context_usage else "--"
        cache_str = "Hit" if self.cache_hit else "Miss"
        
        return (f"⚡ {time_str} | "
                f"🪙 {token_str} | "
                f"🤖 {self.model_used[:10]} | "
                f"💭 {conf_str} | "
                f"🧠 {context_str} | "
                f"💾 {cache_str}")


@dataclass
class SystemMetrics:
    """System-wide metrics and resource tracking"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    disk_usage_percent: float = 0.0
    active_threads: int = 0
    parallel_operations: List[str] = field(default_factory=list)
    
    @classmethod
    def capture(cls) -> 'SystemMetrics':
        """Capture current system metrics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return cls(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            disk_usage_percent=disk.percent,
            active_threads=len(asyncio.all_tasks()) if asyncio.get_event_loop().is_running() else 0
        )
    
    def get_warnings(self) -> List[str]:
        """Check for system warnings"""
        warnings = []
        
        if self.cpu_percent > 80:
            warnings.append(f"⚠️ High CPU usage: {self.cpu_percent:.0f}%")
        
        if self.memory_percent > 85:
            warnings.append(f"⚠️ High memory usage: {self.memory_percent:.0f}% ({self.memory_used_gb:.1f}GB)")
        
        if self.disk_usage_percent > 90:
            warnings.append(f"⚠️ Low disk space: {self.disk_usage_percent:.0f}% used")
        
        return warnings


class MetricsTracker:
    """Central metrics tracking system for OSA"""
    
    def __init__(self, history_size: int = 100):
        self.current_response = ResponseMetrics()
        self.response_history = deque(maxlen=history_size)
        self.system_metrics = SystemMetrics()
        self.session_start = time.time()
        self.total_tokens = 0
        self.total_responses = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        
        # Learning and knowledge tracking
        self.skills_learned = []
        self.knowledge_acquired = []
        self.patterns_recognized = []
        
        # Background operations
        self.background_tasks = {}
        self.parallel_operations = []
    
    def start_response(self, model: str = "unknown", intent: str = "") -> None:
        """Start tracking a new response"""
        self.current_response = ResponseMetrics(
            start_time=time.time(),
            model_used=model,
            intent_type=intent
        )
    
    def end_response(self, tokens_in: int = 0, tokens_out: int = 0, 
                     confidence: float = 0.0, cache_hit: bool = False) -> ResponseMetrics:
        """Complete response tracking"""
        self.current_response.end_time = time.time()
        self.current_response.tokens_input = tokens_in
        self.current_response.tokens_output = tokens_out
        self.current_response.tokens_total = tokens_in + tokens_out
        self.current_response.confidence = confidence
        self.current_response.cache_hit = cache_hit
        
        # Update totals
        self.total_responses += 1
        self.total_tokens += self.current_response.tokens_total
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        # Store in history
        self.response_history.append(self.current_response)
        
        return self.current_response
    
    def add_skill_learned(self, skill: str) -> None:
        """Track a new skill learned"""
        entry = {
            "skill": skill,
            "timestamp": datetime.now().isoformat(),
            "responses_since": self.total_responses
        }
        self.skills_learned.append(entry)
    
    def add_knowledge(self, knowledge: str) -> None:
        """Track new knowledge acquired"""
        entry = {
            "knowledge": knowledge,
            "timestamp": datetime.now().isoformat()
        }
        self.knowledge_acquired.append(entry)
    
    def add_pattern(self, pattern: str) -> None:
        """Track a recognized pattern"""
        entry = {
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
            "occurrences": 1
        }
        
        # Check if pattern already exists
        for p in self.patterns_recognized:
            if p["pattern"] == pattern:
                p["occurrences"] += 1
                return
        
        self.patterns_recognized.append(entry)
    
    def add_background_task(self, task_id: str, description: str) -> None:
        """Track a background task"""
        self.background_tasks[task_id] = {
            "description": description,
            "start_time": time.time(),
            "status": "running"
        }
    
    def complete_background_task(self, task_id: str) -> None:
        """Mark a background task as complete"""
        if task_id in self.background_tasks:
            self.background_tasks[task_id]["status"] = "complete"
            self.background_tasks[task_id]["end_time"] = time.time()
    
    def update_system_metrics(self) -> SystemMetrics:
        """Update system metrics"""
        self.system_metrics = SystemMetrics.capture()
        self.system_metrics.parallel_operations = list(self.background_tasks.keys())
        return self.system_metrics
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get overall session statistics"""
        session_time = time.time() - self.session_start
        avg_response_time = sum(r.response_time for r in self.response_history) / max(len(self.response_history), 1)
        cache_hit_rate = self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
        
        return {
            "session_duration": session_time,
            "total_responses": self.total_responses,
            "total_tokens": self.total_tokens,
            "avg_response_time": avg_response_time,
            "cache_hit_rate": cache_hit_rate,
            "error_rate": self.errors / max(self.total_responses, 1),
            "skills_learned": len(self.skills_learned),
            "knowledge_entries": len(self.knowledge_acquired),
            "patterns_found": len(self.patterns_recognized),
            "active_tasks": len([t for t in self.background_tasks.values() if t["status"] == "running"])
        }
    
    def format_status_bar(self) -> str:
        """Format a complete status bar"""
        metrics = self.current_response
        system = self.system_metrics
        
        # Main metrics line
        main_line = metrics.to_status_bar()
        
        # System resources line (if concerning)
        warnings = system.get_warnings()
        
        if warnings:
            return f"{main_line}\n{warnings[0]}"
        
        return main_line
    
    def format_detailed_status(self) -> str:
        """Format detailed status information"""
        stats = self.get_session_stats()
        system = self.system_metrics
        
        status = []
        status.append("═" * 60)
        status.append("📊 OSA Performance Metrics")
        status.append("═" * 60)
        
        # Session stats
        status.append(f"Session Duration    : {stats['session_duration']:.0f}s")
        status.append(f"Total Responses     : {stats['total_responses']}")
        status.append(f"Total Tokens        : {stats['total_tokens']}")
        status.append(f"Avg Response Time   : {stats['avg_response_time']:.2f}s")
        status.append(f"Cache Hit Rate      : {stats['cache_hit_rate']:.0%}")
        
        # Learning stats
        if stats['skills_learned'] or stats['knowledge_entries']:
            status.append("")
            status.append("🧠 Learning Progress")
            status.append(f"Skills Learned      : {stats['skills_learned']}")
            status.append(f"Knowledge Acquired  : {stats['knowledge_entries']}")
            status.append(f"Patterns Recognized : {stats['patterns_found']}")
        
        # System resources
        status.append("")
        status.append("💻 System Resources")
        status.append(f"CPU Usage           : {system.cpu_percent:.0f}%")
        status.append(f"Memory Usage        : {system.memory_percent:.0f}% ({system.memory_used_gb:.1f}GB)")
        status.append(f"Active Operations   : {system.active_threads}")
        
        # Background tasks
        if self.background_tasks:
            running_tasks = [t for t in self.background_tasks.values() if t["status"] == "running"]
            if running_tasks:
                status.append("")
                status.append("🔄 Background Operations")
                for task in running_tasks[:3]:  # Show max 3
                    status.append(f"  • {task['description']}")
        
        status.append("═" * 60)
        
        return "\n".join(status)


# Global metrics instance
_metrics_tracker = None

def get_metrics_tracker() -> MetricsTracker:
    """Get or create the global metrics tracker"""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = MetricsTracker()
    return _metrics_tracker