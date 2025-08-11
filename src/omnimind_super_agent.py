#!/usr/bin/env python3
"""
OmniMind Super Agent

Your intelligent human peer that combines:
- Perfect memory (unlimited context via ChromaDB + SQLite)
- Multi-LLM intelligence (Claude Opus, ChatGPT-5, Local LLMs)
- Autonomous thinking and decision-making
- Historical context of all conversations
- Brainstorming and collaboration capabilities

This is not just an assistant - it's a peer intelligence that works alongside you.
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
import numpy as np

# Core components
from src.core.memory import MemorySystem
from src.core.vector_store import VectorStore
from src.core.model_manager import ModelManager
from src.core.consensus import ConsensusEngine

# Specialized agents
from src.agents.base_omnimind_agent import BaseOmniMindAgent
from src.agents.specialized.claude_opus_teams_agent import ClaudeOpusTeamsAgent

# External integrations
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autonomous_chatgpt_agent.autonomous_agent_v2 import AutonomousAgent as ChatGPTAgent


class ThinkingMode(Enum):
    """Different thinking modes for different tasks"""
    BRAINSTORM = "brainstorm"      # Creative, exploratory
    ANALYTICAL = "analytical"       # Deep analysis, data-driven
    STRATEGIC = "strategic"         # Long-term planning
    CREATIVE = "creative"          # Innovation, design
    CRITICAL = "critical"          # Problem-solving, debugging
    COLLABORATIVE = "collaborative" # Working with human
    LEARNING = "learning"          # Acquiring new knowledge


class QueryComplexity(Enum):
    """Complexity levels for intelligent routing"""
    SIMPLE = 1      # Quick facts, simple questions - Local LLMs
    MODERATE = 2    # Standard tasks - Single premium model
    COMPLEX = 3     # Deep analysis - Multiple models
    CRITICAL = 4    # Mission-critical - All models + consensus
    RESEARCH = 5    # Long-term research - Autonomous agents


@dataclass
class Thought:
    """Represents a thought in the agent's thinking process"""
    id: str
    content: str
    thinking_mode: ThinkingMode
    timestamp: datetime
    source_models: List[str]
    confidence: float
    related_memories: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'mode': self.thinking_mode.value,
            'timestamp': self.timestamp.isoformat(),
            'sources': self.source_models,
            'confidence': self.confidence,
            'related_memories': self.related_memories,
            'decisions': self.decisions
        }


class CognitiveCore:
    """
    The cognitive core that handles reasoning, decision-making,
    and maintains coherent thought processes.
    """
    
    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system
        self.current_thoughts: List[Thought] = []
        self.thought_chains: Dict[str, List[Thought]] = {}
        self.active_context: Dict[str, Any] = {}
        self.decision_history: List[Dict] = []
        
    async def think(
        self,
        input_data: str,
        mode: ThinkingMode,
        context: Optional[Dict] = None
    ) -> Thought:
        """
        Core thinking process - generates thoughts based on input and context.
        """
        # Retrieve relevant memories
        relevant_memories = await self.memory.search_similar(input_data, top_k=10)
        
        # Retrieve historical decisions
        related_decisions = self._find_related_decisions(input_data)
        
        # Generate thought
        thought_content = await self._generate_thought(
            input_data,
            mode,
            relevant_memories,
            related_decisions,
            context
        )
        
        # Create thought object
        thought = Thought(
            id=hashlib.md5(f"{input_data}{datetime.now()}".encode()).hexdigest()[:8],
            content=thought_content,
            thinking_mode=mode,
            timestamp=datetime.now(),
            source_models=[],  # Will be filled by model orchestrator
            confidence=0.0,    # Will be calculated
            related_memories=[m['id'] for m in relevant_memories[:5]],
            decisions=[]
        )
        
        # Add to current thoughts
        self.current_thoughts.append(thought)
        
        # Add to thought chain if continuing
        if context and 'chain_id' in context:
            chain_id = context['chain_id']
            if chain_id not in self.thought_chains:
                self.thought_chains[chain_id] = []
            self.thought_chains[chain_id].append(thought)
        
        return thought
    
    async def _generate_thought(
        self,
        input_data: str,
        mode: ThinkingMode,
        memories: List[Dict],
        decisions: List[Dict],
        context: Optional[Dict]
    ) -> str:
        """Generate thought content based on all available information"""
        
        # Build comprehensive context
        thought_prompt = f"""
Thinking Mode: {mode.value}
Input: {input_data}

Relevant Memories (from our history together):
{self._format_memories(memories)}

Past Decisions (that might be relevant):
{self._format_decisions(decisions)}

Current Context:
{json.dumps(context, indent=2) if context else "Starting fresh"}

Based on all this context and our history together, generate a thought that:
1. Builds on our past conversations and decisions
2. Maintains consistency with what we've discussed before
3. Applies learnings from similar situations
4. Considers the current thinking mode ({mode.value})
5. Provides actionable insights

Your thought:
"""
        
        return thought_prompt
    
    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for inclusion in prompts"""
        if not memories:
            return "No directly relevant memories found."
        
        formatted = []
        for mem in memories[:5]:
            formatted.append(f"- [{mem.get('timestamp', 'Unknown time')}] {mem.get('content', '')[:200]}...")
        
        return "\n".join(formatted)
    
    def _format_decisions(self, decisions: List[Dict]) -> str:
        """Format past decisions"""
        if not decisions:
            return "No related decisions found."
        
        formatted = []
        for dec in decisions[:3]:
            formatted.append(f"- {dec.get('decision', '')}: {dec.get('reasoning', '')[:100]}...")
        
        return "\n".join(formatted)
    
    def _find_related_decisions(self, input_data: str) -> List[Dict]:
        """Find decisions related to current input"""
        # Simple keyword matching for now
        keywords = set(input_data.lower().split())
        related = []
        
        for decision in self.decision_history[-20:]:  # Last 20 decisions
            decision_keywords = set(decision.get('context', '').lower().split())
            if keywords & decision_keywords:  # Intersection
                related.append(decision)
        
        return related[:5]
    
    def make_decision(self, thought: Thought, options: List[str]) -> str:
        """Make a decision based on current thought"""
        # Calculate decision scores
        scores = {}
        for option in options:
            score = self._calculate_decision_score(thought, option)
            scores[option] = score
        
        # Select best option
        best_option = max(scores, key=scores.get)
        
        # Record decision
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'thought_id': thought.id,
            'options': options,
            'scores': scores,
            'decision': best_option,
            'reasoning': thought.content[:500],
            'context': self.active_context.get('current_task', '')
        }
        
        self.decision_history.append(decision_record)
        thought.decisions.append(best_option)
        
        return best_option
    
    def _calculate_decision_score(self, thought: Thought, option: str) -> float:
        """Calculate score for a decision option"""
        base_score = thought.confidence
        
        # Boost score if option aligns with past successful decisions
        for past_decision in self.decision_history[-10:]:
            if past_decision.get('success', False) and option in past_decision.get('decision', ''):
                base_score += 0.1
        
        # Adjust based on thinking mode
        if thought.thinking_mode == ThinkingMode.CRITICAL:
            # Prefer conservative options in critical mode
            if any(word in option.lower() for word in ['safe', 'verify', 'check', 'test']):
                base_score += 0.2
        elif thought.thinking_mode == ThinkingMode.CREATIVE:
            # Prefer novel options in creative mode
            if any(word in option.lower() for word in ['new', 'innovative', 'creative', 'unique']):
                base_score += 0.2
        
        return min(base_score, 1.0)


class MultiLLMOrchestrator:
    """
    Intelligently orchestrates multiple LLMs based on task requirements.
    Routes queries to the most appropriate models.
    """
    
    def __init__(self):
        self.model_capabilities = {
            'claude_opus': {
                'strengths': ['reasoning', 'analysis', 'creativity', 'ethics'],
                'cost': 'high',
                'speed': 'medium',
                'context': 200000
            },
            'chatgpt5': {
                'strengths': ['general', 'coding', 'web', 'multimodal'],
                'cost': 'medium',
                'speed': 'medium',
                'context': 128000
            },
            'llama3.2': {
                'strengths': ['general', 'fast', 'local'],
                'cost': 'free',
                'speed': 'fast',
                'context': 8192
            },
            'mistral': {
                'strengths': ['coding', 'technical', 'local'],
                'cost': 'free',
                'speed': 'fast',
                'context': 8192
            },
            'deepseek-coder': {
                'strengths': ['coding', 'debugging', 'local'],
                'cost': 'free',
                'speed': 'fast',
                'context': 6144
            }
        }
        
        # Initialize model connections
        self.claude_agent = None
        self.chatgpt_agent = None
        self.local_models = None
        self.consensus_engine = None
        
    async def initialize(self):
        """Initialize all model connections"""
        # Claude Opus Teams agent
        self.claude_agent = ClaudeOpusTeamsAgent()
        
        # ChatGPT agent (via MCP)
        self.chatgpt_agent = ChatGPTAgent(mcp_url="http://localhost:8000")
        await self.chatgpt_agent.initialize()
        
        # Local models
        self.local_models = ModelManager()
        
        # Consensus engine
        self.consensus_engine = ConsensusEngine(self.local_models)
        
        logging.info("✅ All models initialized")
    
    def analyze_complexity(self, query: str, context: Dict) -> QueryComplexity:
        """Analyze query complexity to determine routing strategy"""
        
        # Keywords indicating complexity
        simple_keywords = ['what', 'when', 'where', 'list', 'show', 'display']
        complex_keywords = ['analyze', 'design', 'architect', 'strategy', 'comprehensive']
        critical_keywords = ['production', 'critical', 'urgent', 'emergency', 'important']
        research_keywords = ['research', 'investigate', 'explore', 'study', 'deep dive']
        
        query_lower = query.lower()
        
        # Check for different complexity indicators
        if any(kw in query_lower for kw in critical_keywords):
            return QueryComplexity.CRITICAL
        elif any(kw in query_lower for kw in research_keywords):
            return QueryComplexity.RESEARCH
        elif any(kw in query_lower for kw in complex_keywords):
            return QueryComplexity.COMPLEX
        elif any(kw in query_lower for kw in simple_keywords):
            return QueryComplexity.SIMPLE
        
        # Check query length
        if len(query.split()) > 50:
            return QueryComplexity.COMPLEX
        elif len(query.split()) < 10:
            return QueryComplexity.SIMPLE
        
        return QueryComplexity.MODERATE
    
    async def route_query(
        self,
        query: str,
        complexity: QueryComplexity,
        thinking_mode: ThinkingMode,
        context: Dict
    ) -> Dict[str, Any]:
        """Route query to appropriate models based on complexity and mode"""
        
        routing_strategy = self._determine_routing(complexity, thinking_mode)
        
        responses = {}
        
        # Execute routing strategy
        if routing_strategy['use_local']:
            responses['local'] = await self._query_local_models(query, context)
        
        if routing_strategy['use_claude']:
            responses['claude'] = await self._query_claude(query, context)
        
        if routing_strategy['use_chatgpt']:
            responses['chatgpt'] = await self._query_chatgpt(query, context)
        
        if routing_strategy['use_consensus']:
            responses['consensus'] = await self._get_consensus(query, context)
        
        # Synthesize responses
        final_response = await self._synthesize_responses(responses, routing_strategy)
        
        return {
            'response': final_response,
            'sources': list(responses.keys()),
            'strategy': routing_strategy,
            'complexity': complexity.name
        }
    
    def _determine_routing(
        self,
        complexity: QueryComplexity,
        mode: ThinkingMode
    ) -> Dict[str, bool]:
        """Determine which models to use"""
        
        strategy = {
            'use_local': False,
            'use_claude': False,
            'use_chatgpt': False,
            'use_consensus': False,
            'parallel': False
        }
        
        # Simple queries - use local models
        if complexity == QueryComplexity.SIMPLE:
            strategy['use_local'] = True
        
        # Moderate - use one premium model
        elif complexity == QueryComplexity.MODERATE:
            if mode in [ThinkingMode.ANALYTICAL, ThinkingMode.STRATEGIC]:
                strategy['use_claude'] = True
            else:
                strategy['use_chatgpt'] = True
        
        # Complex - use multiple models
        elif complexity == QueryComplexity.COMPLEX:
            strategy['use_claude'] = True
            strategy['use_chatgpt'] = True
            strategy['parallel'] = True
        
        # Critical - use everything with consensus
        elif complexity == QueryComplexity.CRITICAL:
            strategy['use_local'] = True
            strategy['use_claude'] = True
            strategy['use_chatgpt'] = True
            strategy['use_consensus'] = True
            strategy['parallel'] = True
        
        # Research - use autonomous agents
        elif complexity == QueryComplexity.RESEARCH:
            strategy['use_chatgpt'] = True  # Autonomous research
            strategy['use_claude'] = True   # Deep analysis
        
        return strategy
    
    async def _query_local_models(self, query: str, context: Dict) -> str:
        """Query local models"""
        return await self.local_models.query(query, model="llama3.2:3b")
    
    async def _query_claude(self, query: str, context: Dict) -> str:
        """Query Claude Opus with Teams tier benefits"""
        # Use Teams tier parallel processing if available
        if len(context.get('subtasks', [])) > 1:
            tasks = [{'id': f"task_{i}", 'prompt': task} 
                    for i, task in enumerate(context['subtasks'])]
            results = self.claude_agent.parallel_analysis(tasks)
            return "\n".join(results)
        else:
            return self.claude_agent.think(query)
    
    async def _query_chatgpt(self, query: str, context: Dict) -> str:
        """Query ChatGPT via MCP"""
        # For research, use autonomous mode
        if context.get('mode') == ThinkingMode.RESEARCH:
            await self.chatgpt_agent.add_goal(query, priority=1)
            # Run for a limited time
            await asyncio.wait_for(self.chatgpt_agent.run(), timeout=60)
            status = self.chatgpt_agent.get_status()
            return f"Research conducted: {status}"
        else:
            # Simple query
            async with self.chatgpt_agent.mcp_client as client:
                response = await client.chat(query)
                return response['response']
    
    async def _get_consensus(self, query: str, context: Dict) -> str:
        """Get consensus from multiple models"""
        result = await self.consensus_engine.get_consensus(query)
        return result['consensus']
    
    async def _synthesize_responses(
        self,
        responses: Dict[str, str],
        strategy: Dict[str, bool]
    ) -> str:
        """Synthesize multiple model responses into final answer"""
        
        if len(responses) == 1:
            return list(responses.values())[0]
        
        # Build synthesis prompt
        synthesis_prompt = f"""
Synthesize these responses from different AI models into a single, coherent answer:

{json.dumps(responses, indent=2)}

Provide a unified response that:
1. Combines the best insights from each model
2. Resolves any contradictions
3. Maintains clarity and coherence
4. Preserves important details

Synthesized response:
"""
        
        # Use Claude for synthesis (best at this task)
        if self.claude_agent:
            return self.claude_agent.think(synthesis_prompt)
        else:
            # Fallback to simple combination
            return "\n\n".join([f"[{source}]: {resp}" for source, resp in responses.items()])


class OmniMindSuperAgent:
    """
    The complete OmniMind Super Agent - your intelligent peer.
    
    Combines:
    - Perfect memory with unlimited context
    - Multi-LLM intelligence
    - Autonomous thinking
    - Historical awareness
    - Collaborative brainstorming
    """
    
    def __init__(self):
        # Core systems
        self.memory_system = MemorySystem()
        self.cognitive_core = CognitiveCore(self.memory_system)
        self.orchestrator = MultiLLMOrchestrator()
        
        # Agent state
        self.current_session_id = None
        self.conversation_history = []
        self.active_projects = {}
        self.brainstorm_sessions = {}
        
        # Configuration
        self.config = {
            'name': 'OmniMind',
            'personality': 'collaborative_peer',
            'memory_enabled': True,
            'auto_save': True,
            'thinking_visible': True
        }
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path.home() / ".omnimind" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"omnimind_{datetime.now():%Y%m%d}.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('OmniMind')
    
    async def initialize(self):
        """Initialize all subsystems"""
        self.logger.info("🧠 Initializing OmniMind Super Agent...")
        
        # Initialize memory
        await self.memory_system.initialize()
        self.logger.info("✅ Memory system online")
        
        # Initialize models
        await self.orchestrator.initialize()
        self.logger.info("✅ Multi-LLM orchestrator ready")
        
        # Load historical context
        await self._load_historical_context()
        self.logger.info("✅ Historical context loaded")
        
        # Start new session
        self.current_session_id = hashlib.md5(
            f"session_{datetime.now()}".encode()
        ).hexdigest()[:8]
        
        self.logger.info(f"✅ OmniMind ready! Session: {self.current_session_id}")
        
        return self._generate_greeting()
    
    def _generate_greeting(self) -> str:
        """Generate personalized greeting based on history"""
        
        # Check if we have past interactions
        if self.conversation_history:
            last_interaction = self.conversation_history[-1]
            time_since = datetime.now() - datetime.fromisoformat(last_interaction['timestamp'])
            
            if time_since < timedelta(hours=24):
                return f"Welcome back! Let's continue where we left off with {last_interaction.get('topic', 'our work')}."
            else:
                return f"Good to see you again! It's been {time_since.days} days. What shall we work on today?"
        else:
            return "Hello! I'm OmniMind, your intelligent peer. I have perfect memory, access to multiple AI models, and I'm here to brainstorm and work alongside you. What would you like to explore together?"
    
    async def think_with_user(
        self,
        user_input: str,
        mode: ThinkingMode = ThinkingMode.COLLABORATIVE,
        show_thinking: bool = True
    ) -> str:
        """
        Main interaction method - think together with the user.
        
        This method:
        1. Understands the input in context of all history
        2. Thinks about the problem
        3. Routes to appropriate models
        4. Synthesizes response
        5. Saves to memory
        """
        
        self.logger.info(f"User: {user_input[:100]}...")
        
        # Save user input to memory
        await self.memory_system.store(
            content=user_input,
            metadata={
                'type': 'user_input',
                'session': self.current_session_id,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Generate thought with full context
        thought = await self.cognitive_core.think(
            user_input,
            mode,
            context={
                'session_id': self.current_session_id,
                'active_projects': list(self.active_projects.keys()),
                'recent_history': self.conversation_history[-5:] if self.conversation_history else []
            }
        )
        
        # Analyze complexity
        complexity = self.orchestrator.analyze_complexity(user_input, self.cognitive_core.active_context)
        
        # Route to appropriate models
        result = await self.orchestrator.route_query(
            query=user_input,
            complexity=complexity,
            thinking_mode=mode,
            context={
                'thought': thought.to_dict(),
                'mode': mode,
                'history': self.conversation_history[-3:]
            }
        )
        
        # Update thought with results
        thought.source_models = result['sources']
        thought.confidence = self._calculate_confidence(result)
        
        # Make decisions if needed
        if 'options' in result:
            decision = self.cognitive_core.make_decision(thought, result['options'])
            result['decision'] = decision
        
        # Build response
        response = self._build_response(thought, result, show_thinking)
        
        # Save to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'thought': thought.to_dict(),
            'response': response,
            'complexity': complexity.name,
            'mode': mode.value
        })
        
        # Save response to memory
        await self.memory_system.store(
            content=response,
            metadata={
                'type': 'agent_response',
                'session': self.current_session_id,
                'thought_id': thought.id,
                'sources': result['sources']
            }
        )
        
        self.logger.info(f"OmniMind: {response[:100]}...")
        
        return response
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence based on model agreement and complexity"""
        base_confidence = 0.5
        
        # More sources = higher confidence
        base_confidence += len(result.get('sources', [])) * 0.1
        
        # Consensus increases confidence
        if 'consensus' in result.get('sources', []):
            base_confidence += 0.2
        
        # Claude and ChatGPT agreement
        if 'claude' in result.get('sources', []) and 'chatgpt' in result.get('sources', []):
            base_confidence += 0.1
        
        return min(base_confidence, 0.95)
    
    def _build_response(
        self,
        thought: Thought,
        result: Dict,
        show_thinking: bool
    ) -> str:
        """Build final response with optional thinking process"""
        
        response_parts = []
        
        # Show thinking process if enabled
        if show_thinking and self.config['thinking_visible']:
            response_parts.append(f"💭 [Thinking: {thought.thinking_mode.value}]")
            response_parts.append(f"🧠 [Consulting: {', '.join(result['sources'])}]")
            response_parts.append(f"📊 [Confidence: {thought.confidence:.1%}]")
            
            if thought.related_memories:
                response_parts.append(f"📚 [Recalling: {len(thought.related_memories)} related memories]")
            
            response_parts.append("")  # Empty line
        
        # Main response
        response_parts.append(result['response'])
        
        # Add decision if made
        if 'decision' in result:
            response_parts.append(f"\n✅ Decision: {result['decision']}")
        
        return "\n".join(response_parts)
    
    async def brainstorm(
        self,
        topic: str,
        duration_minutes: int = 10
    ) -> Dict[str, Any]:
        """
        Brainstorming session with the user.
        Generates ideas using multiple models and thinking modes.
        """
        
        session_id = hashlib.md5(f"brainstorm_{topic}_{datetime.now()}".encode()).hexdigest()[:8]
        
        self.logger.info(f"🧠 Starting brainstorm session on: {topic}")
        
        brainstorm_result = {
            'session_id': session_id,
            'topic': topic,
            'started': datetime.now().isoformat(),
            'ideas': [],
            'categories': {},
            'synthesis': ''
        }
        
        # Phase 1: Divergent thinking (generate many ideas)
        divergent_prompt = f"""
Brainstorming topic: {topic}

Generate diverse, creative ideas. Think broadly and unconventionally.
Consider different perspectives, challenge assumptions, explore edge cases.
"""
        
        # Get ideas from different models/modes
        ideas_sources = [
            ('creative', ThinkingMode.CREATIVE),
            ('analytical', ThinkingMode.ANALYTICAL),
            ('strategic', ThinkingMode.STRATEGIC)
        ]
        
        for source_name, mode in ideas_sources:
            thought = await self.cognitive_core.think(divergent_prompt, mode)
            
            result = await self.orchestrator.route_query(
                query=divergent_prompt,
                complexity=QueryComplexity.COMPLEX,
                thinking_mode=mode,
                context={'brainstorm': True, 'session': session_id}
            )
            
            # Parse and store ideas
            ideas = self._extract_ideas(result['response'])
            for idea in ideas:
                brainstorm_result['ideas'].append({
                    'idea': idea,
                    'source': source_name,
                    'mode': mode.value,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Phase 2: Convergent thinking (organize and refine)
        convergent_prompt = f"""
Review these brainstormed ideas about {topic}:
{json.dumps(brainstorm_result['ideas'], indent=2)}

Please:
1. Categorize the ideas
2. Identify the most promising ones
3. Find connections between ideas
4. Suggest combinations or improvements
"""
        
        synthesis = await self.think_with_user(
            convergent_prompt,
            mode=ThinkingMode.ANALYTICAL,
            show_thinking=False
        )
        
        brainstorm_result['synthesis'] = synthesis
        brainstorm_result['ended'] = datetime.now().isoformat()
        
        # Save brainstorm session
        self.brainstorm_sessions[session_id] = brainstorm_result
        
        await self.memory_system.store(
            content=json.dumps(brainstorm_result),
            metadata={
                'type': 'brainstorm_session',
                'session_id': session_id,
                'topic': topic
            }
        )
        
        return brainstorm_result
    
    def _extract_ideas(self, text: str) -> List[str]:
        """Extract individual ideas from text"""
        # Simple extraction - look for bullet points or numbered items
        ideas = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (
                line.startswith('-') or 
                line.startswith('•') or 
                line.startswith('*') or
                (len(line) > 2 and line[0].isdigit() and line[1] in '.)')
            ):
                # Remove bullet/number
                idea = line.lstrip('-•*').lstrip('0123456789.)').strip()
                if idea:
                    ideas.append(idea)
        
        # If no formatted ideas found, split by sentences
        if not ideas:
            sentences = text.split('.')
            ideas = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return ideas[:20]  # Limit to 20 ideas
    
    async def start_project(self, project_name: str, description: str) -> Dict:
        """Start a new project with persistent context"""
        
        project_id = hashlib.md5(f"{project_name}_{datetime.now()}".encode()).hexdigest()[:8]
        
        project = {
            'id': project_id,
            'name': project_name,
            'description': description,
            'created': datetime.now().isoformat(),
            'status': 'active',
            'conversations': [],
            'decisions': [],
            'artifacts': []
        }
        
        self.active_projects[project_id] = project
        
        # Save to memory
        await self.memory_system.store(
            content=json.dumps(project),
            metadata={
                'type': 'project',
                'project_id': project_id,
                'name': project_name
            }
        )
        
        self.logger.info(f"📁 Started project: {project_name} (ID: {project_id})")
        
        return project
    
    async def _load_historical_context(self):
        """Load all historical context from memory"""
        
        # Load recent conversations
        recent_memories = await self.memory_system.get_recent(limit=50)
        
        for memory in recent_memories:
            if memory.metadata.get('type') == 'user_input':
                self.conversation_history.append({
                    'timestamp': memory.metadata.get('timestamp'),
                    'content': memory.content,
                    'type': 'user'
                })
            elif memory.metadata.get('type') == 'agent_response':
                self.conversation_history.append({
                    'timestamp': memory.metadata.get('timestamp'),
                    'content': memory.content,
                    'type': 'agent'
                })
        
        # Load active projects
        project_memories = await self.memory_system.search_by_metadata({'type': 'project'})
        
        for proj_mem in project_memories:
            try:
                project = json.loads(proj_mem.content)
                if project.get('status') == 'active':
                    self.active_projects[project['id']] = project
            except:
                pass
        
        self.logger.info(f"📚 Loaded {len(self.conversation_history)} historical conversations")
        self.logger.info(f"📁 Loaded {len(self.active_projects)} active projects")
    
    async def recall(self, topic: str, limit: int = 10) -> List[Dict]:
        """Recall memories about a specific topic"""
        
        memories = await self.memory_system.search_similar(topic, top_k=limit)
        
        formatted_memories = []
        for mem in memories:
            formatted_memories.append({
                'content': mem['content'],
                'timestamp': mem.get('timestamp', 'Unknown'),
                'type': mem.get('type', 'memory'),
                'relevance': mem.get('similarity_score', 0)
            })
        
        return formatted_memories
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            'session_id': self.current_session_id,
            'memory_size': len(self.conversation_history),
            'active_projects': list(self.active_projects.keys()),
            'brainstorm_sessions': len(self.brainstorm_sessions),
            'available_models': list(self.orchestrator.model_capabilities.keys()),
            'current_thought_count': len(self.cognitive_core.current_thoughts),
            'decision_history_size': len(self.cognitive_core.decision_history)
        }


# Convenience functions for easy usage
async def create_omnimind():
    """Create and initialize OmniMind Super Agent"""
    agent = OmniMindSuperAgent()
    await agent.initialize()
    return agent


async def chat_with_omnimind(agent: OmniMindSuperAgent, message: str):
    """Simple chat interface"""
    response = await agent.think_with_user(message)
    return response


async def brainstorm_with_omnimind(agent: OmniMindSuperAgent, topic: str):
    """Start brainstorming session"""
    results = await agent.brainstorm(topic)
    return results


# Example usage
async def main():
    """Example interaction with OmniMind"""
    
    print("🧠 Starting OmniMind Super Agent...")
    print("=" * 60)
    
    # Create agent
    omnimind = await create_omnimind()
    
    # Example interactions
    print("\n💬 Let's chat!\n")
    
    # Simple question
    response = await chat_with_omnimind(
        omnimind,
        "What should we work on today? I'm interested in AI and productivity."
    )
    print(f"OmniMind: {response}\n")
    
    # Start a project
    project = await omnimind.start_project(
        "AI Productivity Assistant",
        "Building an AI-powered productivity system"
    )
    print(f"Started project: {project['name']}\n")
    
    # Brainstorm
    print("🧠 Let's brainstorm about AI productivity tools...")
    brainstorm_results = await brainstorm_with_omnimind(
        omnimind,
        "AI-powered productivity tools for developers"
    )
    print(f"Generated {len(brainstorm_results['ideas'])} ideas!")
    print(f"Synthesis: {brainstorm_results['synthesis'][:500]}...\n")
    
    # Check status
    status = omnimind.get_status()
    print("📊 Current Status:")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    asyncio.run(main())