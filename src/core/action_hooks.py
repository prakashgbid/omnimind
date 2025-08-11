#!/usr/bin/env python3
"""
OSA Action Hooks System
Shows real-time learning and capability improvements
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of actions OSA can perform"""
    SKILL_LEARNED = "🎓"
    KNOWLEDGE_ACQUIRED = "📚"
    PATTERN_RECOGNIZED = "🔄"
    OPTIMIZATION_APPLIED = "⚡"
    CONTEXT_EXPANDED = "🧠"
    SELF_IMPROVEMENT = "🔧"
    CAPABILITY_DISCOVERED = "✨"
    ERROR_RECOVERY = "🔨"
    CACHE_OPTIMIZATION = "💾"
    PERFORMANCE_TUNED = "🚀"


@dataclass
class ActionEvent:
    """Represents a single action event"""
    action_type: ActionType
    description: str
    timestamp: float
    confidence: float = 0.0
    details: Optional[Dict[str, Any]] = None
    impact: Optional[str] = None


class ActionHooks:
    """Manages action hooks and notifications"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.hooks: Dict[ActionType, List[Callable]] = {}
        self.recent_actions: List[ActionEvent] = []
        self.max_history = 100
        self.display_queue = asyncio.Queue() if asyncio.get_event_loop().is_running() else None
        
        # Register default display hook
        self.register_hook(None, self._display_action)
    
    def register_hook(self, action_type: Optional[ActionType], callback: Callable) -> None:
        """Register a callback for a specific action type (or all if None)"""
        if action_type is None:
            # Register for all action types
            for at in ActionType:
                if at not in self.hooks:
                    self.hooks[at] = []
                self.hooks[at].append(callback)
        else:
            if action_type not in self.hooks:
                self.hooks[action_type] = []
            self.hooks[action_type].append(callback)
    
    async def trigger_action(self, action_type: ActionType, description: str,
                            confidence: float = 0.0, details: Optional[Dict] = None,
                            impact: Optional[str] = None) -> None:
        """Trigger an action event"""
        event = ActionEvent(
            action_type=action_type,
            description=description,
            timestamp=time.time(),
            confidence=confidence,
            details=details,
            impact=impact
        )
        
        # Store in history
        self.recent_actions.append(event)
        if len(self.recent_actions) > self.max_history:
            self.recent_actions.pop(0)
        
        # Call registered hooks
        if action_type in self.hooks:
            for callback in self.hooks[action_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
    
    def _display_action(self, event: ActionEvent) -> None:
        """Default display hook for actions"""
        if not self.verbose:
            return
        
        # Format the action notification
        icon = event.action_type.value
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
        
        # Build the message
        message = f"\n{icon} {event.description}"
        
        if event.confidence > 0:
            conf_bar = self._confidence_bar(event.confidence)
            message += f" {conf_bar}"
        
        if event.impact:
            message += f"\n   Impact: {event.impact}"
        
        if event.details and self.verbose:
            for key, value in event.details.items():
                message += f"\n   {key}: {value}"
        
        print(message)
    
    def _confidence_bar(self, confidence: float) -> str:
        """Create a visual confidence bar"""
        filled = int(confidence * 10)
        empty = 10 - filled
        return f"[{'█' * filled}{'░' * empty}] {confidence:.0%}"
    
    # Convenience methods for common actions
    
    async def skill_learned(self, skill: str, source: str = "interaction") -> None:
        """Notify that a new skill was learned"""
        await self.trigger_action(
            ActionType.SKILL_LEARNED,
            f"New skill learned: {skill}",
            confidence=0.9,
            details={"source": source},
            impact="Can now handle similar requests more effectively"
        )
    
    async def knowledge_acquired(self, topic: str, facts: int = 1) -> None:
        """Notify that new knowledge was acquired"""
        await self.trigger_action(
            ActionType.KNOWLEDGE_ACQUIRED,
            f"Knowledge acquired about: {topic}",
            confidence=0.85,
            details={"facts_learned": facts},
            impact=f"Enhanced understanding of {topic}"
        )
    
    async def pattern_recognized(self, pattern: str, occurrences: int = 1) -> None:
        """Notify that a pattern was recognized"""
        await self.trigger_action(
            ActionType.PATTERN_RECOGNIZED,
            f"Pattern recognized: {pattern}",
            confidence=0.8,
            details={"occurrences": occurrences},
            impact="Improved response prediction"
        )
    
    async def optimization_applied(self, optimization: str, speedup: float = 0.0) -> None:
        """Notify that an optimization was applied"""
        impact = f"{speedup:.1f}x faster" if speedup > 0 else "Improved efficiency"
        await self.trigger_action(
            ActionType.OPTIMIZATION_APPLIED,
            f"Optimization applied: {optimization}",
            confidence=0.95,
            impact=impact
        )
    
    async def context_expanded(self, context_type: str, tokens_added: int = 0) -> None:
        """Notify that context was expanded"""
        await self.trigger_action(
            ActionType.CONTEXT_EXPANDED,
            f"Context expanded: {context_type}",
            confidence=0.9,
            details={"tokens_added": tokens_added},
            impact="Better understanding of conversation"
        )
    
    async def capability_discovered(self, capability: str) -> None:
        """Notify that a new capability was discovered"""
        await self.trigger_action(
            ActionType.CAPABILITY_DISCOVERED,
            f"New capability discovered: {capability}",
            confidence=0.85,
            impact="Expanded range of possible actions"
        )
    
    async def error_recovered(self, error_type: str, solution: str) -> None:
        """Notify that an error was recovered from"""
        await self.trigger_action(
            ActionType.ERROR_RECOVERY,
            f"Recovered from {error_type}",
            confidence=0.8,
            details={"solution": solution},
            impact="Improved resilience"
        )
    
    async def performance_tuned(self, component: str, improvement: str) -> None:
        """Notify that performance was tuned"""
        await self.trigger_action(
            ActionType.PERFORMANCE_TUNED,
            f"Performance tuned: {component}",
            confidence=0.9,
            details={"improvement": improvement},
            impact="Faster response times"
        )
    
    def get_recent_actions(self, limit: int = 10) -> List[ActionEvent]:
        """Get recent action events"""
        return self.recent_actions[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about actions"""
        stats = {
            "total_actions": len(self.recent_actions),
            "actions_by_type": {},
            "avg_confidence": 0.0,
            "last_action": None
        }
        
        if self.recent_actions:
            # Count by type
            for event in self.recent_actions:
                type_name = event.action_type.name
                stats["actions_by_type"][type_name] = stats["actions_by_type"].get(type_name, 0) + 1
            
            # Average confidence
            confidences = [e.confidence for e in self.recent_actions if e.confidence > 0]
            if confidences:
                stats["avg_confidence"] = sum(confidences) / len(confidences)
            
            # Last action
            last = self.recent_actions[-1]
            stats["last_action"] = {
                "type": last.action_type.name,
                "description": last.description,
                "time_ago": time.time() - last.timestamp
            }
        
        return stats


class ThinkingStatus:
    """Shows OSA's current thinking/planning status"""
    
    def __init__(self):
        self.current_thoughts: List[str] = []
        self.planning_stack: List[str] = []
        self.decision_tree: List[Dict[str, Any]] = []
        self.is_thinking = False
        self.thinking_start = None
        
    def start_thinking(self, topic: str) -> None:
        """Start a thinking session"""
        self.is_thinking = True
        self.thinking_start = time.time()
        self.current_thoughts = [topic]
        self._display_thinking()
    
    def add_thought(self, thought: str) -> None:
        """Add a thought to current thinking"""
        if self.is_thinking:
            self.current_thoughts.append(thought)
            self._display_thinking()
    
    def add_plan(self, plan: str) -> None:
        """Add to planning stack"""
        self.planning_stack.append(plan)
        self._display_thinking()
    
    def add_decision(self, decision: str, alternatives: List[str], confidence: float) -> None:
        """Add a decision point"""
        self.decision_tree.append({
            "decision": decision,
            "alternatives": alternatives,
            "confidence": confidence,
            "timestamp": time.time()
        })
    
    def end_thinking(self) -> float:
        """End thinking session and return duration"""
        if self.is_thinking:
            duration = time.time() - self.thinking_start
            self.is_thinking = False
            self.thinking_start = None
            return duration
        return 0.0
    
    def _display_thinking(self) -> None:
        """Display current thinking status"""
        if not self.is_thinking:
            return
        
        print("\n💭 OSA's Current Thoughts:")
        
        # Show primary thought
        if self.current_thoughts:
            print(f"├─ Primary: \"{self.current_thoughts[-1]}\"")
        
        # Show secondary thoughts
        if len(self.current_thoughts) > 1:
            for thought in self.current_thoughts[-3:-1]:
                print(f"├─ Secondary: \"{thought}\"")
        
        # Show planning
        if self.planning_stack:
            print(f"├─ Planning: \"{self.planning_stack[-1]}\"")
        
        # Show background
        if len(self.current_thoughts) > 3:
            print(f"└─ Background: Processing {len(self.current_thoughts) - 3} more thoughts")
        else:
            print("└─ Status: Analyzing...")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current thinking status"""
        return {
            "is_thinking": self.is_thinking,
            "duration": time.time() - self.thinking_start if self.thinking_start else 0,
            "thoughts_count": len(self.current_thoughts),
            "plans_count": len(self.planning_stack),
            "decisions_made": len(self.decision_tree),
            "current_focus": self.current_thoughts[-1] if self.current_thoughts else None
        }


# Global instances
_action_hooks = None
_thinking_status = None


def get_action_hooks() -> ActionHooks:
    """Get or create the global action hooks instance"""
    global _action_hooks
    if _action_hooks is None:
        _action_hooks = ActionHooks()
    return _action_hooks


def get_thinking_status() -> ThinkingStatus:
    """Get or create the global thinking status instance"""
    global _thinking_status
    if _thinking_status is None:
        _thinking_status = ThinkingStatus()
    return _thinking_status