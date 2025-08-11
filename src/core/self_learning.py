#!/usr/bin/env python3
"""
OSA Self-Learning System
Implements continuous learning through feedback loops and pattern recognition
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, deque

# Try importing ML libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class FeedbackType(Enum):
    """Types of feedback for learning"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"
    PREFERENCE = "preference"
    IMPLICIT = "implicit"


class LearningDomain(Enum):
    """Domains where learning can occur"""
    CONVERSATION = "conversation"
    CODING = "coding"
    PROBLEM_SOLVING = "problem_solving"
    KNOWLEDGE = "knowledge"
    BEHAVIOR = "behavior"
    PERFORMANCE = "performance"


@dataclass
class LearningEvent:
    """Represents a single learning event"""
    timestamp: datetime
    domain: LearningDomain
    input_context: str
    output_response: str
    feedback_type: FeedbackType
    feedback_value: float  # -1.0 to 1.0
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "domain": self.domain.value,
            "input_context": self.input_context,
            "output_response": self.output_response,
            "feedback_type": self.feedback_type.value,
            "feedback_value": self.feedback_value,
            "metadata": self.metadata
        }


@dataclass
class Pattern:
    """Represents a learned pattern"""
    pattern_id: str
    domain: LearningDomain
    pattern_type: str  # e.g., "response_style", "code_structure", "solution_approach"
    examples: List[Dict[str, Any]]
    confidence: float
    usage_count: int
    success_rate: float
    last_used: datetime
    
    def update_usage(self, success: bool):
        """Update pattern usage statistics"""
        self.usage_count += 1
        # Update success rate with exponential moving average
        alpha = 0.1  # Learning rate
        self.success_rate = (1 - alpha) * self.success_rate + alpha * (1.0 if success else 0.0)
        self.last_used = datetime.now()
        
        # Update confidence based on usage and success
        self.confidence = min(1.0, self.confidence + 0.01 if success else max(0.0, self.confidence - 0.02))


class ReinforcementLearner:
    """Simple reinforcement learning for action selection"""
    
    def __init__(self, actions: List[str], learning_rate: float = 0.1, exploration_rate: float = 0.1):
        self.actions = actions
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.discount_factor = 0.95
        
    def get_action(self, state: str) -> str:
        """Select action using epsilon-greedy strategy"""
        import random
        
        if random.random() < self.exploration_rate:
            return random.choice(self.actions)
        
        state_actions = self.q_table[state]
        if not state_actions:
            return random.choice(self.actions)
        
        max_q = max(state_actions.values())
        best_actions = [a for a, q in state_actions.items() if q == max_q]
        return random.choice(best_actions) if best_actions else random.choice(self.actions)
    
    def update(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-values using Q-learning"""
        current_q = self.q_table[state][action]
        
        # Get max Q-value for next state
        next_state_actions = self.q_table[next_state]
        max_next_q = max(next_state_actions.values()) if next_state_actions else 0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q


class SelfLearningSystem:
    """Main self-learning system for OSA"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.learning_dir = Path.home() / ".osa" / "learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Learning components
        self.events = deque(maxlen=10000)  # Recent learning events
        self.patterns = {}  # Learned patterns by ID
        self.domain_patterns = defaultdict(list)  # Patterns by domain
        
        # Reinforcement learning for different domains
        self.rl_agents = {
            LearningDomain.CONVERSATION: ReinforcementLearner(
                ["detailed", "concise", "technical", "simple", "creative"]
            ),
            LearningDomain.CODING: ReinforcementLearner(
                ["functional", "object_oriented", "procedural", "declarative"]
            ),
            LearningDomain.PROBLEM_SOLVING: ReinforcementLearner(
                ["analytical", "intuitive", "systematic", "creative", "pragmatic"]
            )
        }
        
        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.skill_levels = defaultdict(float)  # Skill -> proficiency (0-1)
        
        # Feature extraction for pattern recognition
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 3))
            self.pattern_vectors = None
        
        # Load existing learning data
        self.load_learning_data()
    
    def load_learning_data(self):
        """Load persisted learning data"""
        # Load events
        events_file = self.learning_dir / "events.json"
        if events_file.exists():
            try:
                with open(events_file, 'r') as f:
                    events_data = json.load(f)
                    for event_dict in events_data[-1000:]:  # Load last 1000 events
                        event = LearningEvent(
                            timestamp=datetime.fromisoformat(event_dict["timestamp"]),
                            domain=LearningDomain(event_dict["domain"]),
                            input_context=event_dict["input_context"],
                            output_response=event_dict["output_response"],
                            feedback_type=FeedbackType(event_dict["feedback_type"]),
                            feedback_value=event_dict["feedback_value"],
                            metadata=event_dict.get("metadata", {})
                        )
                        self.events.append(event)
            except Exception as e:
                print(f"Error loading events: {e}")
        
        # Load patterns
        patterns_file = self.learning_dir / "patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                    for pattern_dict in patterns_data:
                        pattern = Pattern(
                            pattern_id=pattern_dict["pattern_id"],
                            domain=LearningDomain(pattern_dict["domain"]),
                            pattern_type=pattern_dict["pattern_type"],
                            examples=pattern_dict["examples"],
                            confidence=pattern_dict["confidence"],
                            usage_count=pattern_dict["usage_count"],
                            success_rate=pattern_dict["success_rate"],
                            last_used=datetime.fromisoformat(pattern_dict["last_used"])
                        )
                        self.patterns[pattern.pattern_id] = pattern
                        self.domain_patterns[pattern.domain].append(pattern)
            except Exception as e:
                print(f"Error loading patterns: {e}")
        
        # Load Q-tables for RL agents
        rl_file = self.learning_dir / "rl_agents.json"
        if rl_file.exists():
            try:
                with open(rl_file, 'r') as f:
                    rl_data = json.load(f)
                    for domain_str, q_table in rl_data.items():
                        domain = LearningDomain(domain_str)
                        if domain in self.rl_agents:
                            self.rl_agents[domain].q_table = defaultdict(lambda: defaultdict(float), q_table)
            except Exception as e:
                print(f"Error loading RL agents: {e}")
    
    def save_learning_data(self):
        """Persist learning data to disk"""
        # Save events
        events_file = self.learning_dir / "events.json"
        events_data = [event.to_dict() for event in list(self.events)[-1000:]]
        with open(events_file, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        # Save patterns
        patterns_file = self.learning_dir / "patterns.json"
        patterns_data = []
        for pattern in self.patterns.values():
            patterns_data.append({
                "pattern_id": pattern.pattern_id,
                "domain": pattern.domain.value,
                "pattern_type": pattern.pattern_type,
                "examples": pattern.examples,
                "confidence": pattern.confidence,
                "usage_count": pattern.usage_count,
                "success_rate": pattern.success_rate,
                "last_used": pattern.last_used.isoformat()
            })
        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        # Save Q-tables
        rl_file = self.learning_dir / "rl_agents.json"
        rl_data = {}
        for domain, agent in self.rl_agents.items():
            rl_data[domain.value] = dict(agent.q_table)
        with open(rl_file, 'w') as f:
            json.dump(rl_data, f, indent=2)
    
    async def record_interaction(self, 
                                 domain: LearningDomain,
                                 input_context: str,
                                 output_response: str,
                                 feedback: Optional[Tuple[FeedbackType, float]] = None) -> LearningEvent:
        """Record an interaction for learning"""
        # Default to implicit positive feedback if none provided
        if feedback is None:
            feedback = (FeedbackType.IMPLICIT, 0.5)
        
        feedback_type, feedback_value = feedback
        
        # Create learning event
        event = LearningEvent(
            timestamp=datetime.now(),
            domain=domain,
            input_context=input_context,
            output_response=output_response,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            metadata={}
        )
        
        # Add to events
        self.events.append(event)
        
        # Update reinforcement learning
        if domain in self.rl_agents:
            state = self._extract_state(input_context)
            action = self._extract_action(output_response, domain)
            reward = feedback_value
            
            # Update Q-values
            self.rl_agents[domain].update(state, action, reward, state)
        
        # Extract patterns if we have enough events
        if len(self.events) % 100 == 0:
            await self.extract_patterns()
        
        # Persist periodically
        if len(self.events) % 50 == 0:
            self.save_learning_data()
        
        return event
    
    def _extract_state(self, input_context: str) -> str:
        """Extract state representation from input"""
        # Simple state extraction - can be made more sophisticated
        words = input_context.lower().split()[:5]
        return "_".join(words)
    
    def _extract_action(self, output_response: str, domain: LearningDomain) -> str:
        """Extract action from output response"""
        if domain == LearningDomain.CONVERSATION:
            # Classify response style
            if len(output_response) < 100:
                return "concise"
            elif len(output_response) > 500:
                return "detailed"
            elif any(term in output_response.lower() for term in ["function", "class", "variable"]):
                return "technical"
            else:
                return "simple"
        elif domain == LearningDomain.CODING:
            # Classify coding style
            if "class" in output_response:
                return "object_oriented"
            elif "def" in output_response and "return" in output_response:
                return "functional"
            else:
                return "procedural"
        else:
            # Default action
            return "analytical"
    
    async def extract_patterns(self):
        """Extract patterns from recent events"""
        if not SKLEARN_AVAILABLE or len(self.events) < 10:
            return
        
        # Group events by domain
        domain_events = defaultdict(list)
        for event in self.events:
            if event.feedback_value > 0:  # Only learn from positive feedback
                domain_events[event.domain].append(event)
        
        for domain, events in domain_events.items():
            if len(events) < 5:
                continue
            
            # Extract text features
            texts = [f"{e.input_context} {e.output_response}" for e in events]
            
            try:
                # Vectorize texts
                vectors = self.vectorizer.fit_transform(texts)
                
                # Cluster similar interactions
                n_clusters = min(3, len(events) // 3)
                if n_clusters > 1:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    clusters = kmeans.fit_predict(vectors)
                    
                    # Create patterns from clusters
                    for cluster_id in range(n_clusters):
                        cluster_events = [events[i] for i, c in enumerate(clusters) if c == cluster_id]
                        
                        if len(cluster_events) >= 2:
                            pattern_id = f"{domain.value}_{datetime.now().timestamp()}"
                            pattern = Pattern(
                                pattern_id=pattern_id,
                                domain=domain,
                                pattern_type="cluster",
                                examples=[{
                                    "input": e.input_context,
                                    "output": e.output_response,
                                    "feedback": e.feedback_value
                                } for e in cluster_events[:5]],
                                confidence=0.5,
                                usage_count=0,
                                success_rate=0.5,
                                last_used=datetime.now()
                            )
                            
                            self.patterns[pattern_id] = pattern
                            self.domain_patterns[domain].append(pattern)
            except Exception as e:
                print(f"Error extracting patterns: {e}")
    
    def get_best_approach(self, domain: LearningDomain, context: str) -> Optional[str]:
        """Get the best learned approach for a given context"""
        if domain in self.rl_agents:
            state = self._extract_state(context)
            return self.rl_agents[domain].get_action(state)
        return None
    
    def find_similar_patterns(self, domain: LearningDomain, context: str, threshold: float = 0.7) -> List[Pattern]:
        """Find patterns similar to the given context"""
        domain_patterns = self.domain_patterns.get(domain, [])
        if not domain_patterns or not SKLEARN_AVAILABLE:
            return []
        
        similar_patterns = []
        
        try:
            # Vectorize the context
            context_vector = self.vectorizer.transform([context])
            
            for pattern in domain_patterns:
                # Compare with pattern examples
                for example in pattern.examples[:3]:
                    example_text = f"{example.get('input', '')} {example.get('output', '')}"
                    example_vector = self.vectorizer.transform([example_text])
                    
                    similarity = cosine_similarity(context_vector, example_vector)[0][0]
                    if similarity > threshold:
                        similar_patterns.append(pattern)
                        break
        except Exception as e:
            print(f"Error finding similar patterns: {e}")
        
        # Sort by confidence and success rate
        similar_patterns.sort(key=lambda p: p.confidence * p.success_rate, reverse=True)
        return similar_patterns[:3]
    
    def update_skill_level(self, skill: str, performance: float):
        """Update skill proficiency based on performance"""
        current_level = self.skill_levels.get(skill, 0.5)
        
        # Update using exponential moving average
        alpha = 0.05  # Learning rate
        new_level = (1 - alpha) * current_level + alpha * performance
        
        # Ensure bounds
        self.skill_levels[skill] = max(0.0, min(1.0, new_level))
    
    def get_skill_level(self, skill: str) -> float:
        """Get current proficiency level for a skill"""
        return self.skill_levels.get(skill, 0.5)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learning progress"""
        insights = {
            "total_events": len(self.events),
            "total_patterns": len(self.patterns),
            "patterns_by_domain": {
                domain.value: len(patterns) 
                for domain, patterns in self.domain_patterns.items()
            },
            "skill_levels": dict(self.skill_levels),
            "recent_performance": self._calculate_recent_performance(),
            "top_patterns": self._get_top_patterns(),
            "learning_velocity": self._calculate_learning_velocity()
        }
        
        return insights
    
    def _calculate_recent_performance(self) -> float:
        """Calculate average performance from recent events"""
        if not self.events:
            return 0.5
        
        recent_events = list(self.events)[-50:]
        if not recent_events:
            return 0.5
        
        avg_feedback = sum(e.feedback_value for e in recent_events) / len(recent_events)
        return (avg_feedback + 1.0) / 2.0  # Normalize to 0-1
    
    def _get_top_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing patterns"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.success_rate * p.confidence,
            reverse=True
        )
        
        return [{
            "id": p.pattern_id,
            "domain": p.domain.value,
            "type": p.pattern_type,
            "confidence": p.confidence,
            "success_rate": p.success_rate,
            "usage_count": p.usage_count
        } for p in sorted_patterns[:limit]]
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate rate of learning (patterns discovered per time)"""
        if not self.patterns:
            return 0.0
        
        # Get patterns from last 7 days
        recent_patterns = [
            p for p in self.patterns.values()
            if (datetime.now() - p.last_used).days < 7
        ]
        
        if not recent_patterns:
            return 0.0
        
        # Patterns per day
        return len(recent_patterns) / 7.0
    
    async def apply_learning(self, domain: LearningDomain, context: str) -> Dict[str, Any]:
        """Apply learned knowledge to improve response"""
        recommendations = {
            "approach": None,
            "patterns": [],
            "confidence": 0.5
        }
        
        # Get best approach from RL
        best_approach = self.get_best_approach(domain, context)
        if best_approach:
            recommendations["approach"] = best_approach
        
        # Find similar successful patterns
        similar_patterns = self.find_similar_patterns(domain, context)
        if similar_patterns:
            recommendations["patterns"] = [
                {
                    "examples": p.examples[:2],
                    "confidence": p.confidence,
                    "success_rate": p.success_rate
                }
                for p in similar_patterns
            ]
            
            # Calculate overall confidence
            if similar_patterns:
                avg_confidence = sum(p.confidence for p in similar_patterns) / len(similar_patterns)
                recommendations["confidence"] = avg_confidence
        
        return recommendations
    
    async def continuous_learning_loop(self):
        """Background task for continuous learning"""
        while True:
            try:
                # Extract patterns periodically
                await self.extract_patterns()
                
                # Decay old patterns
                for pattern in self.patterns.values():
                    age_days = (datetime.now() - pattern.last_used).days
                    if age_days > 30:
                        # Reduce confidence for old unused patterns
                        pattern.confidence *= 0.95
                
                # Remove very low confidence patterns
                self.patterns = {
                    pid: p for pid, p in self.patterns.items()
                    if p.confidence > 0.1
                }
                
                # Update domain patterns
                self.domain_patterns.clear()
                for pattern in self.patterns.values():
                    self.domain_patterns[pattern.domain].append(pattern)
                
                # Save learning data
                self.save_learning_data()
                
                # Wait before next iteration
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"Error in continuous learning: {e}")
                await asyncio.sleep(60)


# Create singleton instance
_learning_system = None

def get_learning_system(config: Dict[str, Any] = None) -> SelfLearningSystem:
    """Get or create the global learning system"""
    global _learning_system
    if _learning_system is None:
        _learning_system = SelfLearningSystem(config)
    return _learning_system