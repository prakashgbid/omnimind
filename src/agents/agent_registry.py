"""
OmniMind Agent Registry for Claude Code

Central registry for all OmniMind-powered agents.
Each agent has perfect memory and multi-model intelligence.
"""

import os
import importlib.util
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .base_omnimind_agent import BaseOmniMindAgent


class AgentRegistry:
    """
    Registry for all available OmniMind agents.
    
    This registry allows Claude Code to discover and use
    specialized agents with persistent memory.
    """
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseOmniMindAgent]] = {}
        self._agent_instances: Dict[str, BaseOmniMindAgent] = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Automatically discover all specialized agents."""
        specialized_dir = Path(__file__).parent / "specialized"
        
        if not specialized_dir.exists():
            return
        
        for agent_file in specialized_dir.glob("*_agent.py"):
            module_name = agent_file.stem
            agent_name = module_name.replace("_agent", "").replace("_", "-")
            
            try:
                # Dynamic import
                spec = importlib.util.spec_from_file_location(
                    module_name, agent_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Register if it has AGENT attribute
                if hasattr(module, 'AGENT'):
                    self._agents[agent_name] = module.AGENT
                    
            except Exception as e:
                print(f"Failed to load agent {module_name}: {e}")
    
    def list_agents(self) -> List[Dict[str, str]]:
        """
        List all available agents with descriptions.
        
        Returns:
            List of agent information dictionaries
        """
        agents = []
        for name, agent_class in self._agents.items():
            # Create temporary instance to get info
            agent = agent_class()
            agents.append({
                'name': name,
                'specialization': agent.specialization,
                'description': agent.get_specialization_prompt()[:200] + "..."
            })
        return agents
    
    def get_agent(self, agent_name: str, 
                  initialize: bool = True) -> Optional[BaseOmniMindAgent]:
        """
        Get an agent instance by name.
        
        Args:
            agent_name: Name of the agent
            initialize: Whether to initialize OmniMind
        
        Returns:
            Agent instance or None if not found
        """
        # Check if already instantiated
        if agent_name in self._agent_instances:
            return self._agent_instances[agent_name]
        
        # Create new instance
        if agent_name in self._agents:
            agent = self._agents[agent_name]()
            
            if initialize:
                success, message = agent.initialize()
                if not success:
                    print(f"Warning: {message}")
            
            self._agent_instances[agent_name] = agent
            return agent
        
        return None
    
    def create_custom_agent(self, name: str, specialization: str,
                           preferred_models: Dict[str, str]) -> BaseOmniMindAgent:
        """
        Create a custom agent with specified specialization.
        
        Args:
            name: Agent name
            specialization: Area of expertise
            preferred_models: Model preferences
        
        Returns:
            Custom agent instance
        """
        class CustomAgent(BaseOmniMindAgent):
            def _get_preferred_models(self) -> Dict[str, str]:
                return preferred_models
            
            def get_specialization_prompt(self) -> str:
                return f"I am a {name} agent specializing in {specialization}."
        
        agent = CustomAgent(name, specialization)
        self._agent_instances[name] = agent
        return agent
    
    def get_agent_for_task(self, task_description: str) -> BaseOmniMindAgent:
        """
        Automatically select the best agent for a task.
        
        Args:
            task_description: Description of the task
        
        Returns:
            Most suitable agent
        """
        task_lower = task_description.lower()
        
        # Map keywords to agents
        agent_keywords = {
            'frontend-developer': ['react', 'vue', 'ui', 'component', 'css', 'frontend'],
            'backend-architect': ['api', 'database', 'backend', 'microservice', 'auth'],
            'devops-automator': ['deploy', 'ci/cd', 'kubernetes', 'docker', 'infrastructure'],
            'mobile-app-builder': ['ios', 'android', 'react native', 'mobile', 'app'],
            'ai-engineer': ['ml', 'ai', 'model', 'training', 'neural'],
            'test-writer-fixer': ['test', 'jest', 'pytest', 'testing', 'tdd']
        }
        
        # Score each agent
        scores = {}
        for agent_name, keywords in agent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                scores[agent_name] = score
        
        # Return best match or default
        if scores:
            best_agent = max(scores, key=scores.get)
            return self.get_agent(best_agent)
        
        # Default to a general agent
        return self.get_agent('frontend-developer')  # Or create a general agent
    
    def coordinate_agents(self, agents: List[str], task: str) -> str:
        """
        Coordinate multiple agents for a complex task.
        
        Args:
            agents: List of agent names
            task: Task description
        
        Returns:
            Coordinated response
        """
        responses = {}
        
        # Get response from each agent
        for agent_name in agents:
            agent = self.get_agent(agent_name)
            if agent:
                response = agent.think(task, use_specialization=True)
                responses[agent_name] = response
        
        # Synthesize responses
        if not responses:
            return "No agents available for coordination."
        
        synthesis = "## Multi-Agent Analysis\n\n"
        for agent_name, response in responses.items():
            synthesis += f"### {agent_name.replace('-', ' ').title()}\n"
            synthesis += f"{response[:500]}...\n\n"
        
        return synthesis


# Global registry instance
agent_registry = AgentRegistry()


def list_available_agents() -> List[Dict[str, str]]:
    """List all available OmniMind agents."""
    return agent_registry.list_agents()


def get_agent(name: str) -> Optional[BaseOmniMindAgent]:
    """Get a specific agent by name."""
    return agent_registry.get_agent(name)


def get_agent_for_task(task: str) -> BaseOmniMindAgent:
    """Get the best agent for a specific task."""
    return agent_registry.get_agent_for_task(task)


def coordinate_agents(agent_names: List[str], task: str) -> str:
    """Coordinate multiple agents for complex tasks."""
    return agent_registry.coordinate_agents(agent_names, task)


# Export for Claude Code
__all__ = [
    'agent_registry',
    'list_available_agents',
    'get_agent',
    'get_agent_for_task',
    'coordinate_agents'
]


# Agent catalog for Claude Code
AGENT_CATALOG = """
# OmniMind Agent Catalog

All agents have perfect memory and use 5 local LLMs for intelligence.

## Available Specialized Agents:

### 🎨 frontend-developer
- React, Vue, Angular expertise
- Component architecture
- UI/UX best practices
- Performance optimization

### 🏗️ backend-architect  
- API design (REST, GraphQL)
- Database architecture
- Microservices design
- Scaling strategies

### 🚀 devops-automator
- CI/CD pipelines
- Kubernetes & Docker
- Infrastructure as Code
- Monitoring & alerts

### 📱 mobile-app-builder
- iOS & Android native
- React Native
- App Store optimization
- Mobile performance

### 🤖 ai-engineer
- ML model integration
- LLM implementation
- Computer vision
- NLP pipelines

### 🧪 test-writer-fixer
- Unit & integration tests
- Test coverage
- Bug fixing
- TDD practices

### 💼 product-owner
- Feature prioritization
- User stories
- Sprint planning
- Stakeholder alignment

### 📊 business-analyst
- Requirements gathering
- Process documentation
- Data analysis
- Solution design

## Usage Examples:

```python
# Get specific agent
agent = get_agent('frontend-developer')
response = agent.think("How should I structure this React app?")

# Auto-select agent for task
agent = get_agent_for_task("Design a REST API for user management")
response = agent.think("What endpoints do I need?")

# Coordinate multiple agents
response = coordinate_agents(
    ['backend-architect', 'devops-automator'],
    "Design a scalable microservices architecture"
)

# Agent with memory
agent = get_agent('backend-architect')
agent.remember_decision(
    "Use PostgreSQL for main database",
    "Better JSON support and scalability"
)
response = agent.think("What database should we use?")
# Will remember and reference the PostgreSQL decision
```

## Key Features:

✅ **Perfect Memory**: Every agent remembers all decisions and context
✅ **Multi-Model Intelligence**: Uses 5 local LLMs for consensus
✅ **Specialization**: Deep expertise in specific domains
✅ **Learning**: Improves from feedback and outcomes
✅ **Free & Private**: Runs locally with no API costs

## Agent Coordination:

Agents can work together on complex tasks:
- Frontend + Backend for full-stack solutions
- DevOps + Backend for deployment strategies
- Product + Business for requirements analysis
- AI + any agent for intelligent automation

Each agent maintains its own specialized memory while sharing knowledge when needed.
"""