#!/usr/bin/env python3
"""
OSA Agent Orchestrator using LangGraph
Manages multi-agent collaboration and workflow orchestration
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, TypedDict, Annotated, Sequence
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langgraph.checkpoint import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not available. Install with: pip install langgraph")

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.agents import AgentAction, AgentFinish


class AgentType(Enum):
    """Types of specialized agents"""
    SUPERVISOR = "supervisor"
    RESEARCH = "research"
    CODE = "code"
    PLANNING = "planning"
    DECISION = "decision"
    EXECUTION = "execution"
    LEARNING = "learning"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"


class CollaborationMode(Enum):
    """Agent collaboration patterns"""
    SUPERVISOR = "supervisor"  # Central coordinator
    SWARM = "swarm"  # Peer-to-peer handoffs
    HIERARCHICAL = "hierarchical"  # Layered delegation
    DEMOCRATIC = "democratic"  # Voting-based decisions
    HYBRID = "hybrid"  # Combination of patterns


@dataclass
class AgentProfile:
    """Profile for a specialized agent"""
    name: str
    agent_type: AgentType
    description: str
    capabilities: List[str]
    tools: List[str]
    llm_preference: str = "auto"  # Preferred LLM for this agent
    max_iterations: int = 10
    confidence_threshold: float = 0.7


@dataclass
class AgentHandoff:
    """Handoff between agents"""
    from_agent: str
    to_agent: str
    reason: str
    context: Dict[str, Any]
    timestamp: datetime


# Define the state schema for LangGraph
class AgentState(TypedDict):
    """State shared between agents"""
    messages: Sequence[BaseMessage]
    current_agent: str
    task: str
    context: Dict[str, Any]
    intermediate_results: List[Dict[str, Any]]
    final_result: Optional[Any]
    handoffs: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class AgentOrchestrator:
    """Multi-agent orchestrator using LangGraph"""
    
    def __init__(self, langchain_engine=None, config: Dict[str, Any] = None):
        self.config = config or {}
        self.langchain_engine = langchain_engine
        self.logger = logging.getLogger("OSA-Orchestrator")
        
        # Agent registry
        self.agents: Dict[str, AgentProfile] = {}
        self.active_agents: Dict[str, Any] = {}
        
        # Initialize default agents
        self._initialize_default_agents()
        
        # LangGraph components
        self.graph = None
        self.workflow = None
        self.checkpointer = MemorySaver()
        
        # Collaboration settings
        self.collaboration_mode = CollaborationMode.HYBRID
        self.max_handoffs = 10
        
        # Performance metrics
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_handoffs": 0,
            "agent_performance": {}
        }
        
        # Build the agent graph
        if LANGGRAPH_AVAILABLE:
            self._build_agent_graph()
    
    def _initialize_default_agents(self):
        """Initialize default specialized agents"""
        
        # Supervisor Agent
        self.register_agent(AgentProfile(
            name="supervisor",
            agent_type=AgentType.SUPERVISOR,
            description="Coordinates other agents and manages workflows",
            capabilities=["task_delegation", "workflow_management", "decision_routing"],
            tools=["agent_selector", "task_decomposer", "progress_tracker"],
            llm_preference="gpt-4"
        ))
        
        # Research Agent
        self.register_agent(AgentProfile(
            name="researcher",
            agent_type=AgentType.RESEARCH,
            description="Conducts research and gathers information",
            capabilities=["web_search", "document_analysis", "fact_checking"],
            tools=["web_search", "arxiv_search", "wikipedia", "document_reader"],
            llm_preference="claude"
        ))
        
        # Code Agent
        self.register_agent(AgentProfile(
            name="coder",
            agent_type=AgentType.CODE,
            description="Writes, debugs, and optimizes code",
            capabilities=["code_generation", "debugging", "refactoring", "testing"],
            tools=["code_executor", "linter", "test_runner", "git"],
            llm_preference="gpt-4"
        ))
        
        # Planning Agent
        self.register_agent(AgentProfile(
            name="planner",
            agent_type=AgentType.PLANNING,
            description="Creates plans and decomposes complex tasks",
            capabilities=["task_decomposition", "scheduling", "resource_allocation"],
            tools=["task_planner", "calendar", "gantt_chart", "priority_queue"],
            llm_preference="gpt-4"
        ))
        
        # Decision Agent
        self.register_agent(AgentProfile(
            name="decision_maker",
            agent_type=AgentType.DECISION,
            description="Makes informed decisions based on analysis",
            capabilities=["multi_criteria_analysis", "risk_assessment", "consensus_building"],
            tools=["decision_matrix", "voting_system", "risk_analyzer"],
            llm_preference="claude"
        ))
        
        # Execution Agent
        self.register_agent(AgentProfile(
            name="executor",
            agent_type=AgentType.EXECUTION,
            description="Executes system commands and deployments",
            capabilities=["command_execution", "deployment", "monitoring"],
            tools=["bash", "docker", "kubernetes", "monitoring"],
            llm_preference="gpt-3.5-turbo"
        ))
        
        # Learning Agent
        self.register_agent(AgentProfile(
            name="learner",
            agent_type=AgentType.LEARNING,
            description="Learns from interactions and improves system",
            capabilities=["pattern_recognition", "knowledge_extraction", "model_training"],
            tools=["memory_store", "pattern_analyzer", "feedback_collector"],
            llm_preference="claude"
        ))
        
        # Creative Agent
        self.register_agent(AgentProfile(
            name="creative",
            agent_type=AgentType.CREATIVE,
            description="Generates creative content and solutions",
            capabilities=["content_generation", "brainstorming", "design"],
            tools=["image_generator", "text_generator", "idea_combiner"],
            llm_preference="claude"
        ))
        
        # Analysis Agent
        self.register_agent(AgentProfile(
            name="analyst",
            agent_type=AgentType.ANALYSIS,
            description="Analyzes data and provides insights",
            capabilities=["data_analysis", "visualization", "reporting"],
            tools=["data_analyzer", "chart_generator", "report_builder"],
            llm_preference="gpt-4"
        ))
        
        # Communication Agent
        self.register_agent(AgentProfile(
            name="communicator",
            agent_type=AgentType.COMMUNICATION,
            description="Handles communication and messaging",
            capabilities=["email", "slack", "documentation", "translation"],
            tools=["email_sender", "slack_api", "doc_generator", "translator"],
            llm_preference="gpt-3.5-turbo"
        ))
    
    def register_agent(self, profile: AgentProfile):
        """Register a new agent"""
        self.agents[profile.name] = profile
        self.logger.info(f"Registered agent: {profile.name} ({profile.agent_type.value})")
    
    def _build_agent_graph(self):
        """Build the LangGraph workflow"""
        if not LANGGRAPH_AVAILABLE:
            self.logger.error("LangGraph not available")
            return
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Add agent nodes
        for agent_name, profile in self.agents.items():
            if agent_name != "supervisor":
                workflow.add_node(agent_name, self._create_agent_node(profile))
        
        # Add edges for supervisor pattern
        workflow.set_entry_point("supervisor")
        
        # Supervisor can route to any agent
        for agent_name in self.agents.keys():
            if agent_name != "supervisor":
                workflow.add_edge("supervisor", agent_name)
                # Agents can return to supervisor or end
                workflow.add_conditional_edges(
                    agent_name,
                    self._should_continue,
                    {
                        "supervisor": "supervisor",
                        "end": END
                    }
                )
        
        # Compile the graph
        self.workflow = workflow.compile(checkpointer=self.checkpointer)
        self.logger.info("Agent workflow graph compiled")
    
    async def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor agent node"""
        messages = state["messages"]
        task = state["task"]
        context = state["context"]
        
        # Determine which agent should handle the task
        if self.langchain_engine:
            prompt = f"""As a supervisor agent, analyze this task and decide which specialized agent should handle it:

Task: {task}
Context: {json.dumps(context, indent=2)}

Available agents:
{self._format_agent_list()}

Respond with the name of the most appropriate agent and a brief reason."""
            
            response, _ = await self.langchain_engine.query_with_memory(prompt, "reasoning")
            
            # Parse response to get agent name
            agent_name = self._extract_agent_name(response)
            
            if agent_name and agent_name in self.agents:
                state["current_agent"] = agent_name
                state["messages"].append(
                    AIMessage(content=f"Delegating to {agent_name}: {response}")
                )
                
                # Record handoff
                state["handoffs"].append({
                    "from": "supervisor",
                    "to": agent_name,
                    "reason": response,
                    "timestamp": datetime.now().isoformat()
                })
        
        return state
    
    def _create_agent_node(self, profile: AgentProfile):
        """Create an agent node function"""
        async def agent_node(state: AgentState) -> AgentState:
            messages = state["messages"]
            task = state["task"]
            context = state["context"]
            
            # Agent-specific processing
            if self.langchain_engine:
                # Select appropriate LLM for this agent
                if profile.llm_preference != "auto":
                    llm = self.langchain_engine.llms.get(profile.llm_preference)
                else:
                    llm = self.langchain_engine.select_best_llm("general")
                
                # Build agent prompt
                prompt = f"""You are a {profile.description}.
Your capabilities: {', '.join(profile.capabilities)}
Available tools: {', '.join(profile.tools)}

Task: {task}
Context: {json.dumps(context, indent=2)}

Previous messages:
{self._format_messages(messages[-5:])}

Provide your response and indicate if the task is complete or if another agent is needed."""
                
                # Get agent response
                if llm:
                    response = await llm.apredict(prompt)
                else:
                    response = f"{profile.name} processing: {task}"
                
                # Add response to messages
                state["messages"].append(
                    AIMessage(content=f"[{profile.name}] {response}")
                )
                
                # Store intermediate result
                state["intermediate_results"].append({
                    "agent": profile.name,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check if task is complete
                if self._is_task_complete(response):
                    state["final_result"] = response
            
            return state
        
        return agent_node
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if workflow should continue"""
        # Check if we have a final result
        if state.get("final_result"):
            return "end"
        
        # Check handoff limit
        if len(state.get("handoffs", [])) >= self.max_handoffs:
            self.logger.warning("Max handoffs reached")
            return "end"
        
        # Continue to supervisor for next routing
        return "supervisor"
    
    def _format_agent_list(self) -> str:
        """Format agent list for prompt"""
        lines = []
        for name, profile in self.agents.items():
            if name != "supervisor":
                lines.append(f"- {name}: {profile.description}")
        return "\n".join(lines)
    
    def _format_messages(self, messages: List[BaseMessage]) -> str:
        """Format messages for prompt"""
        formatted = []
        for msg in messages:
            role = "Human" if isinstance(msg, HumanMessage) else "AI"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)
    
    def _extract_agent_name(self, response: str) -> Optional[str]:
        """Extract agent name from supervisor response"""
        response_lower = response.lower()
        
        for agent_name in self.agents.keys():
            if agent_name in response_lower:
                return agent_name
        
        return None
    
    def _is_task_complete(self, response: str) -> bool:
        """Check if task is marked as complete"""
        completion_markers = [
            "task complete",
            "task completed",
            "finished",
            "done",
            "accomplished",
            "final answer:",
            "final result:"
        ]
        
        response_lower = response.lower()
        return any(marker in response_lower for marker in completion_markers)
    
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using multi-agent collaboration"""
        self.metrics["total_tasks"] += 1
        
        if not self.workflow:
            self.logger.error("Workflow not initialized")
            return {"error": "Workflow not initialized"}
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=task)],
            "current_agent": "supervisor",
            "task": task,
            "context": context or {},
            "intermediate_results": [],
            "final_result": None,
            "handoffs": [],
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "collaboration_mode": self.collaboration_mode.value
            }
        }
        
        try:
            # Run the workflow
            config = {"configurable": {"thread_id": f"task_{self.metrics['total_tasks']}"}}
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            # Update metrics
            self.metrics["successful_tasks"] += 1
            handoff_count = len(final_state.get("handoffs", []))
            self.metrics["average_handoffs"] = (
                (self.metrics["average_handoffs"] * (self.metrics["successful_tasks"] - 1) + handoff_count)
                / self.metrics["successful_tasks"]
            )
            
            # Track agent performance
            for handoff in final_state.get("handoffs", []):
                agent = handoff.get("to")
                if agent:
                    if agent not in self.metrics["agent_performance"]:
                        self.metrics["agent_performance"][agent] = {"tasks": 0, "success": 0}
                    self.metrics["agent_performance"][agent]["tasks"] += 1
            
            return {
                "success": True,
                "result": final_state.get("final_result"),
                "intermediate_results": final_state.get("intermediate_results", []),
                "handoffs": final_state.get("handoffs", []),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "metadata": final_state.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.metrics["failed_tasks"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_swarm(self, agents: List[str]) -> Dict[str, Any]:
        """Create a swarm of agents for peer-to-peer collaboration"""
        # TODO: Implement swarm pattern
        pass
    
    async def create_hierarchy(self, structure: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create hierarchical agent structure"""
        # TODO: Implement hierarchical pattern
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return self.metrics.copy()
    
    def get_agent_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent profiles"""
        return {
            name: {
                "type": profile.agent_type.value,
                "description": profile.description,
                "capabilities": profile.capabilities,
                "tools": profile.tools,
                "llm_preference": profile.llm_preference
            }
            for name, profile in self.agents.items()
        }


# Singleton instance
_orchestrator = None

def get_agent_orchestrator(langchain_engine=None, config: Dict[str, Any] = None) -> AgentOrchestrator:
    """Get or create the global agent orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(langchain_engine, config)
    return _orchestrator