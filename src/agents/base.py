"""
Base OmniMind Agent for Claude Code

This is the foundational agent class that all specialized Claude Code agents inherit from.
Each agent gets:
- Perfect memory recall
- Multi-model consensus capabilities  
- Semantic search through all knowledge
- Project-specific context
- Real-time learning from interactions
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.omnimind_enhanced import OmniMindEnhanced


class BaseOmniMindAgent(ABC):
    """
    Base class for all OmniMind-powered Claude Code agents.
    
    Every specialized agent inherits:
    - Persistent memory across sessions
    - Multi-model intelligence (5 local LLMs)
    - Semantic knowledge search
    - Contextual awareness
    - Learning from past decisions
    """
    
    def __init__(self, agent_name: str, specialization: str):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the specialized agent (e.g., 'frontend-developer')
            specialization: Area of expertise (e.g., 'React and UI development')
        """
        self.agent_name = agent_name
        self.specialization = specialization
        self.omnimind = None
        self.session_start = datetime.now()
        self.current_context = {}
        self.conversation_history = []
        
        # Agent-specific configuration
        self.preferred_models = self._get_preferred_models()
        self.memory_tags = [agent_name, specialization]
        
    @abstractmethod
    def _get_preferred_models(self) -> Dict[str, str]:
        """
        Define preferred models for different tasks.
        Must be implemented by each specialized agent.
        
        Returns:
            Dict mapping task types to model names
        """
        pass
    
    @abstractmethod
    def get_specialization_prompt(self) -> str:
        """
        Return a prompt that defines this agent's specialization.
        Must be implemented by each specialized agent.
        
        Returns:
            Specialization prompt string
        """
        pass
    
    def initialize(self, config: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Initialize OmniMind with agent-specific configuration.
        
        Args:
            config: Optional configuration overrides
        
        Returns:
            Tuple of (success, status_message)
        """
        try:
            # Initialize OmniMind
            self.omnimind = OmniMindEnhanced(config_path=".env")
            
            # Store agent initialization in memory
            self.omnimind.remember(
                f"Agent {self.agent_name} initialized with specialization: {self.specialization}",
                context={
                    "type": "agent_init",
                    "agent": self.agent_name,
                    "specialization": self.specialization,
                    "session_start": str(self.session_start)
                }
            )
            
            # Get available models
            info = self.omnimind.get_provider_info()
            local_models = info.get('local_providers', [])
            
            return True, f"""
✅ {self.agent_name} Agent Ready!

Specialization: {self.specialization}
Memory: Active with perfect recall
Local Models: {len(local_models)} available
- Llama 3.2 (general)
- Mistral (reasoning)  
- Phi-3 (efficiency)
- DeepSeek (code)
- Gemma 2 (speed)

I remember everything and learn from each interaction!
"""
        except Exception as e:
            return False, f"❌ Failed to initialize {self.agent_name}: {str(e)}"
    
    def think(self, question: str, use_specialization: bool = True, 
             use_consensus: bool = False, **kwargs) -> str:
        """
        Think about a question with agent specialization and memory.
        
        Args:
            question: The question to think about
            use_specialization: Apply agent's specialized knowledge
            use_consensus: Use multiple models for consensus
            **kwargs: Additional parameters
        
        Returns:
            Thoughtful response with context
        """
        if not self.omnimind:
            success, msg = self.initialize()
            if not success:
                return msg
        
        # Build enhanced prompt with specialization
        enhanced_prompt = question
        if use_specialization:
            enhanced_prompt = f"""
{self.get_specialization_prompt()}

Current Context: {json.dumps(self.current_context, indent=2) if self.current_context else 'None'}

Question: {question}

Provide a response that:
1. Leverages my specialization in {self.specialization}
2. References relevant past decisions or patterns
3. Maintains consistency with previous guidance
4. Applies best practices for {self.agent_name}

Response:
"""
        
        # Add conversation history for context
        self.conversation_history.append({"role": "user", "content": question})
        
        # Select model based on task type
        model = self._select_model_for_task(question)
        
        # Get response from OmniMind
        response = self.omnimind.think(
            enhanced_prompt,
            use_consensus=use_consensus,
            model=model if not use_consensus else None,
            **kwargs
        )
        
        # Store the interaction in memory
        self.omnimind.remember(
            f"Q: {question}\nA: {response}",
            context={
                "type": "qa_pair",
                "agent": self.agent_name,
                "specialization": self.specialization,
                "model_used": model if not use_consensus else "consensus",
                **self.current_context
            }
        )
        
        # Update conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def remember_decision(self, decision: str, rationale: str, 
                         tags: Optional[List[str]] = None) -> str:
        """
        Remember an important decision with rationale.
        
        Args:
            decision: The decision made
            rationale: Why this decision was made
            tags: Additional tags for categorization
        
        Returns:
            Confirmation message
        """
        if not self.omnimind:
            self.initialize()
        
        memory_content = f"""
Decision: {decision}
Rationale: {rationale}
Agent: {self.agent_name}
Specialization: {self.specialization}
Context: {json.dumps(self.current_context, indent=2)}
"""
        
        all_tags = self.memory_tags.copy()
        if tags:
            all_tags.extend(tags)
        
        memory_id = self.omnimind.remember(
            memory_content,
            context={
                "type": "decision",
                "agent": self.agent_name,
                "tags": ','.join(all_tags),
                **self.current_context
            }
        )
        
        return f"✅ Decision remembered (ID: {memory_id})\nI'll consider this in future recommendations."
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search through accumulated knowledge.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of relevant memories
        """
        if not self.omnimind:
            self.initialize()
        
        # Add agent context to search
        enhanced_query = f"{query} {self.agent_name} {self.specialization}"
        
        memories = self.omnimind.search_memories(enhanced_query, limit=limit)
        
        # Filter for agent-relevant memories
        relevant_memories = []
        for memory in memories:
            # Prioritize memories from this agent or related to specialization
            metadata = memory.get('metadata', {})
            if (metadata.get('agent') == self.agent_name or 
                self.specialization.lower() in memory.get('content', '').lower()):
                memory['relevance_boost'] = True
                relevant_memories.insert(0, memory)
            else:
                relevant_memories.append(memory)
        
        return relevant_memories[:limit]
    
    def get_best_practices(self, topic: str) -> str:
        """
        Get best practices for a topic based on accumulated knowledge.
        
        Args:
            topic: The topic to get best practices for
        
        Returns:
            Best practices recommendations
        """
        # Search for related decisions and patterns
        memories = self.search_knowledge(f"best practices {topic} decision", limit=10)
        
        if not memories:
            # No specific memories, use general knowledge
            return self.think(
                f"What are the best practices for {topic} in {self.specialization}?",
                use_specialization=True
            )
        
        # Build context from memories
        context = "\n".join([m['content'][:200] for m in memories[:5]])
        
        prompt = f"""
Based on past decisions and patterns:

{context}

Provide best practices for {topic} considering:
1. Previous successful approaches
2. Lessons learned from past projects
3. {self.specialization} specific considerations

Best Practices:
"""
        
        return self.think(prompt, use_specialization=True)
    
    def learn_from_feedback(self, situation: str, outcome: str, 
                           lesson: str) -> str:
        """
        Learn from feedback and outcomes.
        
        Args:
            situation: What happened
            outcome: The result (positive/negative)
            lesson: What was learned
        
        Returns:
            Confirmation of learning
        """
        if not self.omnimind:
            self.initialize()
        
        learning_content = f"""
Learning Entry:
Agent: {self.agent_name}
Situation: {situation}
Outcome: {outcome}
Lesson: {lesson}
Timestamp: {datetime.now()}

This will inform future {self.specialization} decisions.
"""
        
        self.omnimind.remember(
            learning_content,
            context={
                "type": "learning",
                "agent": self.agent_name,
                "outcome_type": "positive" if "success" in outcome.lower() else "negative",
                "tags": f"learning,feedback,{self.agent_name}"
            }
        )
        
        return f"✅ Learned: {lesson}\nI'll apply this knowledge in future {self.specialization} tasks."
    
    def set_context(self, **context) -> str:
        """
        Set the current working context.
        
        Args:
            **context: Context key-value pairs
        
        Returns:
            Confirmation message
        """
        self.current_context.update(context)
        
        context_str = "\n".join([f"  • {k}: {v}" for k, v in context.items()])
        return f"✅ Context updated:\n{context_str}"
    
    def get_consensus(self, question: str, models: Optional[List[str]] = None) -> str:
        """
        Get consensus from multiple models.
        
        Args:
            question: Question to get consensus on
            models: Specific models to use
        
        Returns:
            Consensus response
        """
        if not self.omnimind:
            self.initialize()
        
        if not models:
            # Use default consensus models
            models = ['llama3.2:3b', 'mistral:7b', 'phi3:mini']
        
        enhanced_question = f"{self.get_specialization_prompt()}\n\n{question}"
        
        response = self.omnimind.think(
            enhanced_question,
            use_consensus=True,
            providers=['ollama'] * len(models)
        )
        
        return f"🤝 Consensus from {len(models)} models:\n\n{response}"
    
    def _select_model_for_task(self, task: str) -> str:
        """
        Select the best model for a given task.
        
        Args:
            task: The task description
        
        Returns:
            Model name
        """
        task_lower = task.lower()
        
        # Check for code-related tasks
        if any(word in task_lower for word in ['code', 'function', 'class', 'debug', 'implement']):
            return self.preferred_models.get('code', 'deepseek-coder:6.7b')
        
        # Check for reasoning tasks
        elif any(word in task_lower for word in ['explain', 'why', 'analyze', 'compare', 'evaluate']):
            return self.preferred_models.get('reasoning', 'mistral:7b')
        
        # Check for quick tasks
        elif any(word in task_lower for word in ['list', 'name', 'quick', 'simple']):
            return self.preferred_models.get('quick', 'gemma2:2b')
        
        # Default to general model
        return self.preferred_models.get('general', 'llama3.2:3b')
    
    def summarize_session(self) -> str:
        """
        Summarize the current session.
        
        Returns:
            Session summary
        """
        if not self.omnimind:
            return "No session to summarize."
        
        duration = datetime.now() - self.session_start
        
        summary = f"""
📊 {self.agent_name} Session Summary
{'=' * 40}
Duration: {duration}
Specialization: {self.specialization}
Context: {json.dumps(self.current_context, indent=2) if self.current_context else 'None'}
Interactions: {len(self.conversation_history) // 2}

Key Topics Discussed:
{self._extract_topics()}

Use 'search_knowledge' to find specific information or 'get_best_practices' for recommendations.
"""
        return summary
    
    def _extract_topics(self) -> str:
        """Extract main topics from conversation history."""
        if not self.conversation_history:
            return "- No topics yet"
        
        topics = []
        for i, msg in enumerate(self.conversation_history):
            if msg['role'] == 'user' and i < 10:  # Last 5 questions
                topics.append(f"- {msg['content'][:60]}...")
        
        return "\n".join(topics) if topics else "- No topics extracted"