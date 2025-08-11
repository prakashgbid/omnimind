#!/usr/bin/env python3
"""
OSA Continuous Learning System

This component enables OSA to:
1. Learn from user interactions and feedback
2. Conduct internal research and debates
3. Avoid repetition through pattern recognition
4. Work smarter, not harder

Core Philosophy:
- Minimum custom coding - find existing tools first
- Learn from every interaction
- Debate internally for best solutions
- Recognize and avoid repeated work
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from collections import Counter, defaultdict

# For web research
import aiohttp
from bs4 import BeautifulSoup


class LearningType(Enum):
    """Types of learning"""
    USER_FEEDBACK = "user_feedback"
    TASK_COMPLETION = "task_completion"
    ERROR_RECOVERY = "error_recovery"
    PATTERN_RECOGNITION = "pattern_recognition"
    TOOL_DISCOVERY = "tool_discovery"
    OPTIMIZATION = "optimization"
    INTERNAL_DEBATE = "internal_debate"


@dataclass
class Learning:
    """Represents a single learning"""
    id: str
    type: LearningType
    content: str
    source: str
    confidence: float
    timestamp: datetime
    applications: List[str] = field(default_factory=list)
    validations: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type.value,
            'content': self.content,
            'source': self.source,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'applications': self.applications,
            'validations': self.validations
        }


@dataclass
class Pattern:
    """Represents a recognized pattern to avoid repetition"""
    id: str
    pattern_type: str  # task, error, solution
    signature: str  # Pattern signature for matching
    occurrences: List[Dict]
    solution: Optional[str]
    efficiency_gain: float  # Time saved by recognizing pattern
    
    def matches(self, input_text: str) -> bool:
        """Check if input matches this pattern"""
        # Simple matching - can be enhanced with ML
        return self.signature.lower() in input_text.lower()


@dataclass
class InternalDebate:
    """Represents an internal debate between different approaches"""
    id: str
    topic: str
    options: List[Dict[str, Any]]
    arguments_for: Dict[str, List[str]]
    arguments_against: Dict[str, List[str]]
    conclusion: Optional[str]
    winner: Optional[str]
    timestamp: datetime


class ContinuousLearningSystem:
    """
    OSA's continuous learning component that enables:
    - Learning from user feedback
    - Internal research and debates
    - Pattern recognition to avoid repetition
    - Smart work over hard work
    """
    
    def __init__(self):
        # Learning storage
        self.learnings: Dict[str, Learning] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.debates: Dict[str, InternalDebate] = {}
        
        # Pattern detection
        self.task_history: List[Dict] = []
        self.solution_cache: Dict[str, Any] = {}
        self.error_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Learning configuration
        self.config = {
            'pattern_threshold': 3,  # Occurrences before pattern recognition
            'confidence_threshold': 0.7,  # Minimum confidence for applying learning
            'debate_participants': 3,  # Number of perspectives in debates
            'cache_size': 1000,  # Max cached solutions
            'learning_rate': 0.1  # How quickly to adapt
        }
        
        # Research tools cache
        self.tool_registry: Dict[str, Dict] = {}
        self.tool_evaluations: Dict[str, float] = {}
        
        # Setup logging
        self.logger = logging.getLogger('OSA-Learning')
        
        # Initialize knowledge base
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize with base knowledge"""
        
        # Common patterns to recognize
        self.base_patterns = {
            'crud_api': 'Create REST API with CRUD operations',
            'auth_system': 'Implement authentication and authorization',
            'data_pipeline': 'Build data processing pipeline',
            'frontend_app': 'Create frontend application',
            'testing_suite': 'Write comprehensive tests',
            'deployment': 'Deploy application to cloud',
            'documentation': 'Generate documentation',
            'optimization': 'Optimize performance'
        }
        
        # Common tool preferences (minimum custom coding)
        self.preferred_tools = {
            'web_framework': ['FastAPI', 'Next.js', 'Django'],
            'database': ['PostgreSQL', 'MongoDB', 'Redis'],
            'authentication': ['Auth0', 'Supabase', 'Firebase Auth'],
            'deployment': ['Vercel', 'Railway', 'Fly.io'],
            'testing': ['Pytest', 'Jest', 'Playwright'],
            'monitoring': ['Sentry', 'DataDog', 'Grafana'],
            'ai_tools': ['LangChain', 'Ollama', 'Transformers'],
            'ui_components': ['Shadcn/ui', 'MUI', 'Chakra UI']
        }
    
    async def learn_from_user(self, interaction: Dict[str, Any]) -> Learning:
        """
        Learn from user interaction.
        
        This captures:
        - User preferences
        - Corrections
        - Feedback
        - Success patterns
        """
        
        learning_content = self._extract_learning(interaction)
        
        if not learning_content:
            return None
        
        learning = Learning(
            id=hashlib.md5(f"{learning_content}{datetime.now()}".encode()).hexdigest()[:8],
            type=LearningType.USER_FEEDBACK,
            content=learning_content,
            source=interaction.get('source', 'user_interaction'),
            confidence=self._calculate_confidence(interaction),
            timestamp=datetime.now()
        )
        
        # Store learning
        self.learnings[learning.id] = learning
        
        # Check for patterns
        await self._detect_patterns(interaction)
        
        self.logger.info(f"📚 Learned from user: {learning_content[:100]}")
        
        return learning
    
    def _extract_learning(self, interaction: Dict[str, Any]) -> Optional[str]:
        """Extract actionable learning from interaction"""
        
        user_input = interaction.get('user_input', '')
        response = interaction.get('response', '')
        feedback = interaction.get('feedback', '')
        
        # Look for correction patterns
        correction_patterns = [
            r"(?:no|not|don't|dont).*(?:instead|rather|actually)",
            r"(?:wrong|incorrect|mistake)",
            r"(?:better|prefer|should)",
            r"(?:always|never|must)"
        ]
        
        for pattern in correction_patterns:
            if re.search(pattern, user_input.lower()):
                return f"User correction: {user_input}"
        
        # Look for preferences
        if 'prefer' in user_input.lower() or 'like' in user_input.lower():
            return f"User preference: {user_input}"
        
        # Look for success indicators
        if any(word in feedback.lower() for word in ['good', 'great', 'perfect', 'exactly']):
            return f"Successful approach: {response[:200]}"
        
        return None
    
    def _calculate_confidence(self, interaction: Dict[str, Any]) -> float:
        """Calculate confidence in the learning"""
        
        base_confidence = 0.5
        
        # Explicit feedback increases confidence
        if interaction.get('feedback'):
            if 'correct' in interaction['feedback'].lower():
                base_confidence += 0.3
            elif 'wrong' in interaction['feedback'].lower():
                base_confidence += 0.4  # High confidence in corrections
        
        # Repeated patterns increase confidence
        similar_count = self._count_similar_interactions(interaction)
        base_confidence += min(similar_count * 0.1, 0.3)
        
        return min(base_confidence, 1.0)
    
    def _count_similar_interactions(self, interaction: Dict[str, Any]) -> int:
        """Count similar past interactions"""
        
        count = 0
        current_text = interaction.get('user_input', '').lower()
        
        for task in self.task_history[-20:]:  # Check last 20 tasks
            if self._calculate_similarity(current_text, task.get('input', '').lower()) > 0.7:
                count += 1
        
        return count
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple version)"""
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    async def _detect_patterns(self, interaction: Dict[str, Any]):
        """Detect patterns to avoid repetition"""
        
        # Add to history
        self.task_history.append(interaction)
        
        # Look for repeated tasks
        task_text = interaction.get('task', '').lower()
        
        # Count similar tasks
        similar_tasks = []
        for past_task in self.task_history[-50:]:  # Check last 50 tasks
            if self._calculate_similarity(task_text, past_task.get('task', '').lower()) > 0.8:
                similar_tasks.append(past_task)
        
        # If pattern detected
        if len(similar_tasks) >= self.config['pattern_threshold']:
            pattern = Pattern(
                id=hashlib.md5(task_text.encode()).hexdigest()[:8],
                pattern_type='task',
                signature=self._extract_pattern_signature(similar_tasks),
                occurrences=similar_tasks,
                solution=self._extract_common_solution(similar_tasks),
                efficiency_gain=self._calculate_efficiency_gain(similar_tasks)
            )
            
            self.patterns[pattern.id] = pattern
            
            self.logger.info(f"🔍 Pattern detected: {pattern.signature}")
            self.logger.info(f"   Efficiency gain: {pattern.efficiency_gain:.1f} minutes saved")
    
    def _extract_pattern_signature(self, tasks: List[Dict]) -> str:
        """Extract common pattern from similar tasks"""
        
        # Find common words
        all_words = []
        for task in tasks:
            all_words.extend(task.get('task', '').lower().split())
        
        word_counts = Counter(all_words)
        common_words = [word for word, count in word_counts.most_common(5) if count >= len(tasks) * 0.5]
        
        return ' '.join(common_words)
    
    def _extract_common_solution(self, tasks: List[Dict]) -> Optional[str]:
        """Extract common solution from similar tasks"""
        
        solutions = [task.get('solution', '') for task in tasks if task.get('solution')]
        
        if not solutions:
            return None
        
        # Find most common solution approach
        # (In production, this would use more sophisticated analysis)
        return solutions[0] if solutions else None
    
    def _calculate_efficiency_gain(self, tasks: List[Dict]) -> float:
        """Calculate time saved by recognizing pattern"""
        
        # Average time spent on similar tasks
        times = [task.get('execution_time', 10) for task in tasks]
        avg_time = sum(times) / len(times) if times else 10
        
        # Pattern recognition saves ~70% of time
        return avg_time * 0.7
    
    async def conduct_internal_debate(self, topic: str, options: List[str]) -> InternalDebate:
        """
        Conduct internal debate between different approaches.
        
        This simulates multiple perspectives debating to find best solution.
        """
        
        self.logger.info(f"🤔 Starting internal debate on: {topic}")
        
        debate = InternalDebate(
            id=hashlib.md5(f"{topic}{datetime.now()}".encode()).hexdigest()[:8],
            topic=topic,
            options=[{'name': opt, 'score': 0} for opt in options],
            arguments_for=defaultdict(list),
            arguments_against=defaultdict(list),
            conclusion=None,
            winner=None,
            timestamp=datetime.now()
        )
        
        # Generate arguments for each option
        for option in options:
            # Arguments for
            debate.arguments_for[option] = self._generate_arguments_for(option, topic)
            
            # Arguments against
            debate.arguments_against[option] = self._generate_arguments_against(option, topic)
        
        # Score each option
        scores = {}
        for option in options:
            score = 0
            score += len(debate.arguments_for[option]) * 2
            score -= len(debate.arguments_against[option])
            
            # Check against preferred tools (minimum custom coding)
            if self._uses_preferred_tools(option):
                score += 5
            
            # Check for pattern match (avoid repetition)
            if self._matches_successful_pattern(option):
                score += 3
            
            scores[option] = score
        
        # Determine winner
        winner = max(scores, key=scores.get)
        debate.winner = winner
        
        # Generate conclusion
        debate.conclusion = f"""
After internal debate on '{topic}':

Winner: {winner}
Reasoning: 
- Strongest arguments: {', '.join(debate.arguments_for[winner][:2])}
- Minimal concerns: {', '.join(debate.arguments_against[winner][:1]) if debate.arguments_against[winner] else 'None'}
- Aligns with principles: Minimum custom coding, uses existing tools

Decision: Proceed with {winner} approach.
"""
        
        # Store debate
        self.debates[debate.id] = debate
        
        self.logger.info(f"✅ Debate concluded. Winner: {winner}")
        
        return debate
    
    def _generate_arguments_for(self, option: str, topic: str) -> List[str]:
        """Generate arguments in favor of an option"""
        
        arguments = []
        
        # Check if uses existing tools
        if 'existing' in option.lower() or 'library' in option.lower():
            arguments.append("Uses existing tools (minimum custom coding)")
        
        # Check for simplicity
        if 'simple' in option.lower() or 'straightforward' in option.lower():
            arguments.append("Simple and maintainable approach")
        
        # Check for performance
        if 'fast' in option.lower() or 'efficient' in option.lower():
            arguments.append("Performance optimized")
        
        # Check for scalability
        if 'scale' in option.lower() or 'distributed' in option.lower():
            arguments.append("Scalable architecture")
        
        # Default arguments based on keywords
        option_lower = option.lower()
        if 'api' in option_lower:
            arguments.append("Industry standard approach")
        if 'cloud' in option_lower:
            arguments.append("Cloud-native solution")
        if 'test' in option_lower:
            arguments.append("Ensures quality")
        
        return arguments[:5]  # Limit arguments
    
    def _generate_arguments_against(self, option: str, topic: str) -> List[str]:
        """Generate arguments against an option"""
        
        arguments = []
        
        # Check for complexity
        if 'custom' in option.lower() or 'build' in option.lower():
            arguments.append("Requires custom development")
        
        # Check for dependencies
        if 'depends' in option.lower() or 'requires' in option.lower():
            arguments.append("Has external dependencies")
        
        # Check for maintenance
        if 'complex' in option.lower():
            arguments.append("Higher maintenance burden")
        
        # Default concerns based on keywords
        option_lower = option.lower()
        if 'legacy' in option_lower:
            arguments.append("Uses outdated technology")
        if 'experimental' in option_lower:
            arguments.append("Not production-ready")
        
        return arguments[:3]  # Limit arguments
    
    def _uses_preferred_tools(self, option: str) -> bool:
        """Check if option uses preferred tools"""
        
        option_lower = option.lower()
        
        for category, tools in self.preferred_tools.items():
            for tool in tools:
                if tool.lower() in option_lower:
                    return True
        
        return False
    
    def _matches_successful_pattern(self, option: str) -> bool:
        """Check if option matches a successful pattern"""
        
        for pattern in self.patterns.values():
            if pattern.matches(option) and pattern.efficiency_gain > 5:
                return True
        
        return False
    
    async def research_better_tools(self, current_tool: str, purpose: str) -> Dict[str, Any]:
        """
        Research if better tools are available for the purpose.
        
        This implements the principle of always finding the best existing tool.
        """
        
        self.logger.info(f"🔍 Researching better tools than {current_tool} for {purpose}")
        
        research_result = {
            'current_tool': current_tool,
            'purpose': purpose,
            'alternatives': [],
            'recommendation': None,
            'reasoning': []
        }
        
        # Search for alternatives (would use real web search in production)
        alternatives = await self._find_tool_alternatives(current_tool, purpose)
        
        # Evaluate each alternative
        for alt in alternatives:
            evaluation = await self._evaluate_tool(alt, purpose)
            alt['score'] = evaluation['score']
            alt['pros'] = evaluation['pros']
            alt['cons'] = evaluation['cons']
            research_result['alternatives'].append(alt)
        
        # Sort by score
        research_result['alternatives'].sort(key=lambda x: x['score'], reverse=True)
        
        # Make recommendation
        if research_result['alternatives']:
            best = research_result['alternatives'][0]
            
            # Only recommend if significantly better
            current_score = await self._get_current_tool_score(current_tool)
            
            if best['score'] > current_score + 0.2:  # 20% better threshold
                research_result['recommendation'] = best['name']
                research_result['reasoning'] = [
                    f"Better suited for {purpose}",
                    f"Score: {best['score']:.2f} vs current {current_score:.2f}",
                    f"Key advantages: {', '.join(best['pros'][:2])}"
                ]
            else:
                research_result['recommendation'] = current_tool
                research_result['reasoning'] = [
                    "Current tool is sufficient",
                    "No significant improvement found",
                    f"Current score: {current_score:.2f}"
                ]
        
        # Cache research
        self.tool_registry[f"{current_tool}_{purpose}"] = research_result
        
        return research_result
    
    async def _find_tool_alternatives(self, current_tool: str, purpose: str) -> List[Dict]:
        """Find alternative tools for the purpose"""
        
        # In production, this would search GitHub, npm, PyPI, etc.
        # For now, use knowledge base
        
        alternatives = []
        
        # Map purposes to tool categories
        purpose_mapping = {
            'web_framework': self.preferred_tools.get('web_framework', []),
            'database': self.preferred_tools.get('database', []),
            'auth': self.preferred_tools.get('authentication', []),
            'deploy': self.preferred_tools.get('deployment', []),
            'test': self.preferred_tools.get('testing', []),
            'monitor': self.preferred_tools.get('monitoring', []),
            'ai': self.preferred_tools.get('ai_tools', []),
            'ui': self.preferred_tools.get('ui_components', [])
        }
        
        # Find relevant category
        for key, tools in purpose_mapping.items():
            if key in purpose.lower():
                for tool in tools:
                    if tool != current_tool:
                        alternatives.append({
                            'name': tool,
                            'category': key,
                            'popularity': 'high',  # Would fetch real data
                            'last_updated': 'recent'  # Would fetch real data
                        })
        
        return alternatives[:5]  # Limit to top 5
    
    async def _evaluate_tool(self, tool: Dict, purpose: str) -> Dict[str, Any]:
        """Evaluate a tool for the purpose"""
        
        evaluation = {
            'score': 0.5,  # Base score
            'pros': [],
            'cons': []
        }
        
        # Evaluate based on criteria
        tool_name = tool['name'].lower()
        
        # Popularity
        if tool.get('popularity') == 'high':
            evaluation['score'] += 0.2
            evaluation['pros'].append('Popular and well-supported')
        
        # Maintenance
        if tool.get('last_updated') == 'recent':
            evaluation['score'] += 0.1
            evaluation['pros'].append('Actively maintained')
        
        # Specific tool knowledge
        if tool_name in ['fastapi', 'next.js', 'postgresql']:
            evaluation['score'] += 0.2
            evaluation['pros'].append('Industry standard')
        
        # Check against our principles
        if 'custom' not in tool_name and 'build' not in tool_name:
            evaluation['score'] += 0.1
            evaluation['pros'].append('Existing solution (no custom coding)')
        
        # Purpose fit
        if purpose.lower() in tool.get('category', ''):
            evaluation['score'] += 0.15
            evaluation['pros'].append(f'Designed for {purpose}')
        
        return evaluation
    
    async def _get_current_tool_score(self, tool: str) -> float:
        """Get score for current tool"""
        
        # Check cache
        if tool in self.tool_evaluations:
            return self.tool_evaluations[tool]
        
        # Default score based on tool
        scores = {
            'express': 0.6,
            'django': 0.7,
            'fastapi': 0.85,
            'next.js': 0.9,
            'react': 0.8,
            'vue': 0.75,
            'postgresql': 0.9,
            'mongodb': 0.7,
            'mysql': 0.65
        }
        
        score = scores.get(tool.lower(), 0.5)
        self.tool_evaluations[tool] = score
        
        return score
    
    def check_for_repetition(self, task: str) -> Optional[Dict[str, Any]]:
        """
        Check if we're about to repeat work.
        Returns cached solution if available.
        """
        
        # Check patterns
        for pattern in self.patterns.values():
            if pattern.matches(task):
                self.logger.info(f"♻️ Recognized pattern: {pattern.signature}")
                
                if pattern.solution:
                    return {
                        'pattern_matched': True,
                        'pattern_id': pattern.id,
                        'cached_solution': pattern.solution,
                        'time_saved': pattern.efficiency_gain,
                        'message': f"I've done this {len(pattern.occurrences)} times before. Using optimized approach."
                    }
        
        # Check solution cache
        task_hash = hashlib.md5(task.lower().encode()).hexdigest()
        if task_hash in self.solution_cache:
            cached = self.solution_cache[task_hash]
            self.logger.info(f"♻️ Found cached solution for: {task[:50]}")
            
            return {
                'pattern_matched': False,
                'cached': True,
                'cached_solution': cached,
                'message': "I've solved this exact task before. Reusing solution."
            }
        
        return None
    
    def store_solution(self, task: str, solution: Any):
        """Store solution for future reuse"""
        
        task_hash = hashlib.md5(task.lower().encode()).hexdigest()
        
        # Store in cache (with size limit)
        if len(self.solution_cache) >= self.config['cache_size']:
            # Remove oldest entries
            oldest_keys = list(self.solution_cache.keys())[:100]
            for key in oldest_keys:
                del self.solution_cache[key]
        
        self.solution_cache[task_hash] = solution
        
        self.logger.info(f"💾 Cached solution for: {task[:50]}")
    
    def get_smart_approach(self, task: str) -> Dict[str, Any]:
        """
        Get smart approach for a task (work smarter, not harder).
        
        Returns optimized approach based on learnings.
        """
        
        approach = {
            'strategy': 'standard',
            'optimizations': [],
            'tools_to_use': [],
            'patterns_to_apply': [],
            'estimated_time_saved': 0
        }
        
        # Check for repetition first
        repetition_check = self.check_for_repetition(task)
        if repetition_check:
            approach['strategy'] = 'reuse'
            approach['optimizations'].append('Reusing previous solution')
            approach['estimated_time_saved'] = repetition_check.get('time_saved', 10)
            return approach
        
        # Analyze task for optimization opportunities
        task_lower = task.lower()
        
        # Look for tool opportunities (minimum custom coding)
        for category, tools in self.preferred_tools.items():
            if category.replace('_', ' ') in task_lower:
                approach['tools_to_use'].extend(tools[:2])
                approach['optimizations'].append(f"Use existing {category} tools")
                approach['estimated_time_saved'] += 15
        
        # Apply learned patterns
        relevant_learnings = []
        for learning in self.learnings.values():
            if learning.confidence > self.config['confidence_threshold']:
                if any(word in task_lower for word in learning.content.lower().split()[:5]):
                    relevant_learnings.append(learning)
        
        if relevant_learnings:
            approach['strategy'] = 'optimized'
            for learning in relevant_learnings[:3]:
                approach['patterns_to_apply'].append(learning.content[:100])
                approach['estimated_time_saved'] += 5
        
        # Check for batch optimization
        if any(word in task_lower for word in ['multiple', 'several', 'many', 'bulk']):
            approach['optimizations'].append('Use parallel processing')
            approach['strategy'] = 'parallel'
            approach['estimated_time_saved'] += 20
        
        # Check for automation opportunities
        if any(word in task_lower for word in ['automate', 'schedule', 'monitor', 'continuous']):
            approach['optimizations'].append('Set up automation')
            approach['tools_to_use'].append('GitHub Actions or similar')
            approach['estimated_time_saved'] += 30
        
        return approach
    
    def summarize_learnings(self) -> Dict[str, Any]:
        """Summarize all learnings for review"""
        
        summary = {
            'total_learnings': len(self.learnings),
            'total_patterns': len(self.patterns),
            'total_debates': len(self.debates),
            'cached_solutions': len(self.solution_cache),
            'top_patterns': [],
            'recent_learnings': [],
            'efficiency_gains': 0
        }
        
        # Top patterns by efficiency gain
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.efficiency_gain,
            reverse=True
        )
        
        for pattern in sorted_patterns[:5]:
            summary['top_patterns'].append({
                'signature': pattern.signature,
                'occurrences': len(pattern.occurrences),
                'time_saved': pattern.efficiency_gain
            })
            summary['efficiency_gains'] += pattern.efficiency_gain * len(pattern.occurrences)
        
        # Recent learnings
        sorted_learnings = sorted(
            self.learnings.values(),
            key=lambda l: l.timestamp,
            reverse=True
        )
        
        for learning in sorted_learnings[:5]:
            summary['recent_learnings'].append({
                'content': learning.content[:100],
                'type': learning.type.value,
                'confidence': learning.confidence
            })
        
        return summary


# Integration functions for OSA
async def enhance_osa_with_learning(osa_instance):
    """Enhance OSA instance with continuous learning"""
    
    learning_system = ContinuousLearningSystem()
    
    # Add learning system to OSA
    osa_instance.learning_system = learning_system
    
    # Override OSA methods to include learning
    original_accomplish = osa_instance.accomplish
    
    async def enhanced_accomplish(goal: str) -> Dict[str, Any]:
        # Check for smart approach
        smart_approach = learning_system.get_smart_approach(goal)
        
        if smart_approach['strategy'] == 'reuse':
            logging.info(f"♻️ Reusing previous solution, saving {smart_approach['estimated_time_saved']} minutes")
            return smart_approach.get('cached_solution', await original_accomplish(goal))
        
        # Apply optimizations
        if smart_approach['optimizations']:
            logging.info(f"🚀 Applying optimizations: {smart_approach['optimizations']}")
        
        # Execute with learnings
        result = await original_accomplish(goal)
        
        # Store solution for future
        learning_system.store_solution(goal, result)
        
        # Learn from execution
        await learning_system.learn_from_user({
            'task': goal,
            'solution': result,
            'execution_time': result.get('execution_time', 10)
        })
        
        return result
    
    osa_instance.accomplish = enhanced_accomplish
    
    return osa_instance