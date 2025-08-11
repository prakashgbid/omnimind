"""
OmniMind Claude Code Agent

This agent allows OmniMind to be used within Claude Code as an intelligent assistant
with perfect memory and multi-model consensus capabilities.
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.omnimind_enhanced import OmniMindEnhanced


class OmniMindAgent:
    """
    Claude Code Agent wrapper for OmniMind.
    
    This agent can be invoked by Claude Code to:
    - Remember project decisions and context
    - Provide advice based on past experiences
    - Build consensus from multiple LLMs
    - Search through accumulated knowledge
    """
    
    def __init__(self):
        """Initialize the OmniMind agent."""
        self.omnimind = None
        self.current_project = None
        self.session_start = datetime.now()
        
    def initialize(self, config: Optional[Dict] = None) -> str:
        """
        Initialize OmniMind with configuration.
        
        Args:
            config: Optional configuration overrides
        
        Returns:
            Status message
        """
        try:
            # Create config file if provided
            if config:
                self._write_config(config)
            
            # Initialize OmniMind
            self.omnimind = OmniMindEnhanced()
            
            # Get provider info
            info = self.omnimind.get_provider_info()
            
            return f"""
✅ OmniMind Agent Initialized

Available Providers:
- Local: {', '.join(info['local_providers']) or 'None'}
- Cloud: {', '.join(info['cloud_providers']) or 'None'}

Total Providers: {len(info['available_providers'])}
Ready to remember and think!
"""
        except Exception as e:
            return f"❌ Failed to initialize: {str(e)}"
    
    def remember(self, content: str, tags: Optional[List[str]] = None, 
                project: Optional[str] = None) -> str:
        """
        Remember something important.
        
        Args:
            content: What to remember
            tags: Optional tags for categorization
            project: Optional project name
        
        Returns:
            Confirmation message
        """
        if not self.omnimind:
            return "❌ OmniMind not initialized. Call initialize() first."
        
        context = {}
        if tags:
            context['tags'] = ','.join(tags)
        if project:
            context['project'] = project
            self.current_project = project
        
        memory_id = self.omnimind.remember(content, context)
        
        return f"✅ Remembered (ID: {memory_id})"
    
    def think(self, question: str, use_consensus: bool = False, 
             providers: Optional[List[str]] = None) -> str:
        """
        Think about a question using accumulated knowledge.
        
        Args:
            question: The question to think about
            use_consensus: Whether to use multiple models
            providers: Specific providers to use
        
        Returns:
            The thoughtful response
        """
        if not self.omnimind:
            return "❌ OmniMind not initialized. Call initialize() first."
        
        # Add project context if set
        if self.current_project:
            question = f"[Project: {self.current_project}] {question}"
        
        response = self.omnimind.think(
            question,
            use_consensus=use_consensus,
            providers=providers
        )
        
        return response
    
    def search(self, query: str, limit: int = 5) -> str:
        """
        Search through memories.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            Formatted search results
        """
        if not self.omnimind:
            return "❌ OmniMind not initialized. Call initialize() first."
        
        memories = self.omnimind.search_memories(query, limit)
        
        if not memories:
            return "No memories found matching your query."
        
        results = ["🔍 Search Results:\n"]
        for i, memory in enumerate(memories, 1):
            score = memory['score']
            date = memory['metadata'].get('timestamp', 'Unknown')[:19]
            content = memory['content'][:150] + "..." if len(memory['content']) > 150 else memory['content']
            
            results.append(f"{i}. [{score:.2f}] {date}")
            results.append(f"   {content}\n")
        
        return "\n".join(results)
    
    def get_consensus(self, question: str, providers: Optional[List[str]] = None) -> str:
        """
        Get consensus from multiple models on a question.
        
        Args:
            question: The question to get consensus on
            providers: Specific providers to use (default: all)
        
        Returns:
            Consensus response
        """
        if not self.omnimind:
            return "❌ OmniMind not initialized. Call initialize() first."
        
        if not providers:
            # Use all available providers
            info = self.omnimind.get_provider_info()
            providers = info['available_providers']
        
        if len(providers) < 2:
            return "⚠️ Need at least 2 providers for consensus. Add more API keys to .env"
        
        response = self.omnimind.think(
            question,
            use_consensus=True,
            providers=providers
        )
        
        return f"🤝 Consensus from {len(providers)} models:\n\n{response}"
    
    def set_project(self, project_name: str) -> str:
        """
        Set the current project context.
        
        Args:
            project_name: Name of the project
        
        Returns:
            Confirmation message
        """
        self.current_project = project_name
        return f"✅ Project context set to: {project_name}"
    
    def summarize_session(self) -> str:
        """
        Summarize the current session.
        
        Returns:
            Session summary
        """
        if not self.omnimind:
            return "❌ OmniMind not initialized."
        
        duration = datetime.now() - self.session_start
        
        # Get recent memories from this session
        recent = self.omnimind.get_timeline(
            start_date=self.session_start.strftime("%Y-%m-%d")
        )
        
        summary = f"""
📊 Session Summary
================
Duration: {duration}
Project: {self.current_project or 'None set'}
Memories Created: {len(recent)}

Recent Topics:
{self._extract_topics(recent)}

Use 'search' to find specific memories or 'think' to get contextual answers.
"""
        return summary
    
    def _extract_topics(self, memories: List[Dict]) -> str:
        """Extract topics from memories."""
        if not memories:
            return "- No topics yet"
        
        topics = []
        for memory in memories[:5]:
            thought = memory.get('thought', '')[:50]
            topics.append(f"- {thought}...")
        
        return "\n".join(topics)
    
    def _write_config(self, config: Dict):
        """Write configuration to .env file."""
        env_path = os.path.join(os.path.dirname(__file__), '../../.env')
        
        lines = []
        for key, value in config.items():
            lines.append(f"{key}={value}")
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(lines))


def main(action: str, **kwargs) -> str:
    """
    Main entry point for Claude Code agent.
    
    This function is called by Claude Code when using OmniMind as an agent.
    
    Args:
        action: The action to perform (initialize, remember, think, search, etc.)
        **kwargs: Action-specific parameters
    
    Returns:
        Response from OmniMind
    """
    agent = OmniMindAgent()
    
    # Initialize if needed
    if action != 'initialize' and not agent.omnimind:
        agent.initialize()
    
    # Route to appropriate method
    if action == 'initialize':
        return agent.initialize(kwargs.get('config'))
    
    elif action == 'remember':
        return agent.remember(
            kwargs.get('content', ''),
            kwargs.get('tags'),
            kwargs.get('project')
        )
    
    elif action == 'think':
        return agent.think(
            kwargs.get('question', ''),
            kwargs.get('use_consensus', False),
            kwargs.get('providers')
        )
    
    elif action == 'search':
        return agent.search(
            kwargs.get('query', ''),
            kwargs.get('limit', 5)
        )
    
    elif action == 'consensus':
        return agent.get_consensus(
            kwargs.get('question', ''),
            kwargs.get('providers')
        )
    
    elif action == 'set_project':
        return agent.set_project(kwargs.get('project_name', ''))
    
    elif action == 'summarize':
        return agent.summarize_session()
    
    else:
        return f"""
❌ Unknown action: {action}

Available actions:
- initialize: Set up OmniMind with API keys
- remember: Store important information
- think: Get contextual answers
- search: Search through memories
- consensus: Get multi-model consensus
- set_project: Set project context
- summarize: Get session summary

Example:
    main('remember', content='We decided to use TypeScript', project='myapp')
    main('think', question='What language did we choose?')
"""


# Agent descriptor for Claude Code
AGENT_DESCRIPTOR = {
    "name": "omnimind",
    "description": "Persistent intelligence system with perfect memory and multi-LLM consensus",
    "version": "2.0.0",
    "author": "OmniMind",
    "capabilities": [
        "remember_everything",
        "semantic_search",
        "multi_model_consensus",
        "knowledge_graph",
        "project_context",
        "timeline_queries"
    ],
    "providers": [
        "ollama_local",
        "openai_gpt4",
        "anthropic_claude",
        "google_gemini"
    ],
    "usage": """
    # As a Claude Code Agent:
    
    agent = OmniMindAgent()
    agent.initialize({'OPENAI_API_KEY': 'sk-...', 'ANTHROPIC_API_KEY': 'sk-ant-...'})
    
    # Remember decisions
    agent.remember("Decided to use React for the frontend", project="webapp")
    
    # Get contextual answers
    response = agent.think("What framework should we use?")
    
    # Build consensus
    consensus = agent.get_consensus("Should we use microservices?")
    
    # Search memories
    results = agent.search("database decisions")
    """
}


if __name__ == "__main__":
    # Test the agent
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        # Parse remaining arguments as kwargs
        kwargs = {}
        for arg in sys.argv[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                kwargs[key] = value
        
        result = main(action, **kwargs)
        print(result)
    else:
        print(AGENT_DESCRIPTOR)