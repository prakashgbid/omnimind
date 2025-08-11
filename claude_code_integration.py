#!/usr/bin/env python3
"""
OmniMind Integration for Claude Code

This file enables Claude Code to use OmniMind agents with perfect memory
and multi-model intelligence. Each agent specializes in different areas
while maintaining complete recall of all interactions.

Usage in Claude Code:
    from omnimind import get_agent
    agent = get_agent('frontend-developer')
    response = agent.think("How should I structure this React app?")
"""

import sys
import os
from typing import Dict, List, Optional, Any

# Add to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agent_registry import (
    agent_registry,
    list_available_agents,
    get_agent,
    get_agent_for_task,
    coordinate_agents
)
from src.agents.base_omnimind_agent import BaseOmniMindAgent


class OmniMindClaudeCode:
    """
    Main interface for Claude Code to interact with OmniMind agents.
    
    This class provides a simplified API for Claude Code to:
    - Access specialized agents with perfect memory
    - Coordinate multiple agents for complex tasks
    - Learn from all interactions
    - Build consensus from multiple models
    """
    
    def __init__(self):
        """Initialize OmniMind for Claude Code."""
        self.registry = agent_registry
        self.current_agent = None
        self.session_context = {}
        print("🧠 OmniMind ready for Claude Code!")
        print(f"📦 {len(self.registry._agents)} specialized agents available")
    
    def list_agents(self) -> str:
        """
        List all available agents with descriptions.
        
        Returns:
            Formatted list of agents
        """
        agents = list_available_agents()
        
        output = "🤖 Available OmniMind Agents:\n\n"
        for agent in agents:
            output += f"### {agent['name']}\n"
            output += f"**Specialization**: {agent['specialization']}\n"
            output += f"{agent['description']}\n\n"
        
        return output
    
    def use_agent(self, agent_name: str) -> str:
        """
        Select and initialize a specific agent.
        
        Args:
            agent_name: Name of the agent to use
        
        Returns:
            Confirmation message
        """
        agent = get_agent(agent_name)
        if agent:
            self.current_agent = agent
            # Set any session context
            if self.session_context:
                agent.set_context(**self.session_context)
            return f"✅ Now using {agent_name} agent\n{agent.specialization}"
        else:
            return f"❌ Agent {agent_name} not found. Use list_agents() to see available agents."
    
    def ask(self, question: str, agent: Optional[str] = None, 
            consensus: bool = False) -> str:
        """
        Ask a question to an agent.
        
        Args:
            question: The question to ask
            agent: Specific agent to use (optional)
            consensus: Use multi-model consensus
        
        Returns:
            Agent's response
        """
        # Select agent if specified
        if agent:
            self.use_agent(agent)
        
        # Auto-select if no current agent
        if not self.current_agent:
            self.current_agent = get_agent_for_task(question)
            print(f"Auto-selected: {self.current_agent.agent_name}")
        
        # Get response
        return self.current_agent.think(
            question,
            use_specialization=True,
            use_consensus=consensus
        )
    
    def remember(self, content: str, tags: Optional[List[str]] = None) -> str:
        """
        Remember something important.
        
        Args:
            content: What to remember
            tags: Optional tags
        
        Returns:
            Confirmation
        """
        if not self.current_agent:
            self.current_agent = get_agent('frontend-developer')
        
        if "decision" in content.lower():
            # Parse as decision
            parts = content.split(":", 1)
            if len(parts) == 2:
                return self.current_agent.remember_decision(
                    parts[0].strip(),
                    parts[1].strip(),
                    tags
                )
        
        # General memory
        return self.current_agent.omnimind.remember(
            content,
            context={'tags': ','.join(tags) if tags else ''}
        )
    
    def search(self, query: str, limit: int = 5) -> str:
        """
        Search through accumulated knowledge.
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            Formatted search results
        """
        if not self.current_agent:
            self.current_agent = get_agent('frontend-developer')
        
        memories = self.current_agent.search_knowledge(query, limit)
        
        if not memories:
            return "No relevant memories found."
        
        output = f"🔍 Found {len(memories)} relevant memories:\n\n"
        for i, memory in enumerate(memories, 1):
            score = memory.get('score', 0)
            content = memory.get('content', '')[:200]
            output += f"{i}. [Score: {score:.2f}]\n{content}...\n\n"
        
        return output
    
    def coordinate(self, agents: List[str], task: str) -> str:
        """
        Coordinate multiple agents for a complex task.
        
        Args:
            agents: List of agent names
            task: Task description
        
        Returns:
            Coordinated response
        """
        return coordinate_agents(agents, task)
    
    def set_project(self, project_name: str, **context) -> str:
        """
        Set project context for all agents.
        
        Args:
            project_name: Project name
            **context: Additional context
        
        Returns:
            Confirmation
        """
        self.session_context['project'] = project_name
        self.session_context.update(context)
        
        if self.current_agent:
            self.current_agent.set_context(**self.session_context)
        
        return f"✅ Project context set: {project_name}"
    
    def learn(self, situation: str, outcome: str, lesson: str) -> str:
        """
        Learn from an outcome.
        
        Args:
            situation: What happened
            outcome: The result
            lesson: What was learned
        
        Returns:
            Confirmation
        """
        if not self.current_agent:
            return "Select an agent first with use_agent()"
        
        return self.current_agent.learn_from_feedback(situation, outcome, lesson)
    
    def best_practices(self, topic: str) -> str:
        """
        Get best practices for a topic.
        
        Args:
            topic: Topic to get best practices for
        
        Returns:
            Best practices recommendations
        """
        if not self.current_agent:
            self.current_agent = get_agent_for_task(topic)
        
        return self.current_agent.get_best_practices(topic)


# Create global instance for Claude Code
omnimind = OmniMindClaudeCode()

# Convenience functions for Claude Code
def ask(question: str, agent: Optional[str] = None, consensus: bool = False) -> str:
    """Quick ask function for Claude Code."""
    return omnimind.ask(question, agent, consensus)

def remember(content: str, tags: Optional[List[str]] = None) -> str:
    """Quick remember function for Claude Code."""
    return omnimind.remember(content, tags)

def search(query: str, limit: int = 5) -> str:
    """Quick search function for Claude Code."""
    return omnimind.search(query, limit)

def use_agent(agent_name: str) -> str:
    """Quick agent selection for Claude Code."""
    return omnimind.use_agent(agent_name)

def learn(situation: str, outcome: str, lesson: str) -> str:
    """Quick learning function for Claude Code."""
    return omnimind.learn(situation, outcome, lesson)


# Example usage for Claude Code
if __name__ == "__main__":
    print("""
🧠 OmniMind Claude Code Integration Ready!
=========================================

Quick Start:
-----------
from claude_code_integration import ask, remember, search, use_agent

# Auto-select agent based on task
response = ask("How should I structure my React app?")

# Use specific agent
use_agent('backend-architect')
response = ask("Design a REST API for user management")

# Remember decisions
remember("Decision: Use PostgreSQL for main database: Better JSON support")

# Search knowledge
results = search("database decisions")

# Multi-agent coordination
from claude_code_integration import omnimind
response = omnimind.coordinate(
    ['frontend-developer', 'backend-architect'],
    "Design a full-stack application"
)

# Learn from outcomes
learn(
    "Implemented microservices architecture",
    "Successful: Improved scalability by 10x",
    "Microservices work well for teams > 10 people"
)

Available Agents:
----------------
""")
    
    # List all agents
    print(omnimind.list_agents())
    
    # Demo
    print("\n📝 Demo: Frontend Development")
    print("=" * 50)
    
    use_agent('frontend-developer')
    
    # Remember a decision
    print(remember("Decision: Use Next.js 14: App router and server components"))
    
    # Ask a question
    print("\nQuestion: What's the best state management for Next.js?")
    response = ask("What's the best state management solution for Next.js 14?")
    print(f"Answer: {response[:300]}...")
    
    print("\n✨ OmniMind agents have perfect memory and learn from every interaction!")