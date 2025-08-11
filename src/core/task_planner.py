#!/usr/bin/env python3
"""
OSA Autonomous Task Decomposition and Planning System
Breaks down complex tasks into manageable steps and executes them autonomously
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

# LangChain for advanced planning
try:
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class TaskStatus(Enum):
    """Status of a task in the execution pipeline"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for task execution"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskType(Enum):
    """Types of tasks for specialized handling"""
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    SYSTEM = "system"
    LEARNING = "learning"
    COMMUNICATION = "communication"
    DECISION = "decision"


@dataclass
class TaskStep:
    """Represents a single step in a task plan"""
    step_id: str
    description: str
    action: str
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration: int = 60  # seconds
    required_tools: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def is_ready(self, completed_steps: List[str]) -> bool:
        """Check if this step is ready to execute"""
        return all(prereq in completed_steps for prereq in self.prerequisites)
    
    def mark_started(self):
        """Mark step as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Any = None):
        """Mark step as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error: str):
        """Mark step as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error


@dataclass
class Task:
    """Represents a complex task to be decomposed and executed"""
    task_id: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    steps: List[TaskStep] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: TaskStep):
        """Add a step to the task plan"""
        self.steps.append(step)
    
    def get_ready_steps(self, completed_step_ids: List[str]) -> List[TaskStep]:
        """Get steps that are ready to execute"""
        return [
            step for step in self.steps
            if step.status == TaskStatus.PENDING and step.is_ready(completed_step_ids)
        ]
    
    def is_complete(self) -> bool:
        """Check if all steps are complete"""
        return all(
            step.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            for step in self.steps
        )
    
    def get_progress(self) -> float:
        """Get task completion progress (0-1)"""
        if not self.steps:
            return 0.0
        completed = sum(
            1 for step in self.steps
            if step.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        )
        return completed / len(self.steps)


class TaskPlanner:
    """Autonomous task planning and execution system"""
    
    def __init__(self, llm_engine=None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.llm_engine = llm_engine
        self.tasks = {}  # task_id -> Task
        self.execution_queue = asyncio.Queue()
        self.running_tasks = {}
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 3)
        
        # Task templates for common scenarios
        self.task_templates = self._load_task_templates()
        
        # Execution strategies
        self.execution_strategies = {
            TaskType.RESEARCH: self._execute_research_step,
            TaskType.CODING: self._execute_coding_step,
            TaskType.ANALYSIS: self._execute_analysis_step,
            TaskType.CREATIVE: self._execute_creative_step,
            TaskType.SYSTEM: self._execute_system_step,
            TaskType.LEARNING: self._execute_learning_step,
            TaskType.COMMUNICATION: self._execute_communication_step,
            TaskType.DECISION: self._execute_decision_step
        }
        
        # Planning prompts
        self.planning_prompt = PromptTemplate(
            input_variables=["task_description", "task_type", "context"],
            template="""You are an expert task planner. Break down the following task into actionable steps.

Task: {task_description}
Type: {task_type}
Context: {context}

Provide a detailed plan with the following structure for each step:
1. Clear description of what needs to be done
2. Specific action to take
3. Prerequisites (step IDs that must complete first)
4. Estimated duration in seconds
5. Required tools or resources
6. Validation criteria to confirm completion

Output the plan as a JSON array with this structure:
[
  {{
    "step_id": "step_1",
    "description": "...",
    "action": "...",
    "prerequisites": [],
    "estimated_duration": 60,
    "required_tools": ["tool1", "tool2"],
    "validation_criteria": ["criterion1", "criterion2"]
  }},
  ...
]

Plan:"""
        )
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined task templates"""
        return {
            "code_generation": {
                "steps": [
                    {"action": "understand_requirements", "duration": 30},
                    {"action": "design_solution", "duration": 60},
                    {"action": "implement_code", "duration": 180},
                    {"action": "test_implementation", "duration": 120},
                    {"action": "refactor_optimize", "duration": 90}
                ]
            },
            "problem_solving": {
                "steps": [
                    {"action": "analyze_problem", "duration": 60},
                    {"action": "identify_constraints", "duration": 30},
                    {"action": "generate_solutions", "duration": 90},
                    {"action": "evaluate_options", "duration": 60},
                    {"action": "implement_solution", "duration": 120}
                ]
            },
            "research": {
                "steps": [
                    {"action": "define_scope", "duration": 30},
                    {"action": "gather_information", "duration": 180},
                    {"action": "analyze_findings", "duration": 120},
                    {"action": "synthesize_insights", "duration": 90},
                    {"action": "create_summary", "duration": 60}
                ]
            }
        }
    
    async def create_task(self, 
                          description: str,
                          task_type: TaskType = TaskType.ANALYSIS,
                          priority: TaskPriority = TaskPriority.MEDIUM,
                          context: Dict[str, Any] = None) -> Task:
        """Create a new task and plan its execution"""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            description=description,
            task_type=task_type,
            priority=priority,
            metadata=context or {}
        )
        
        # Generate execution plan
        task.status = TaskStatus.PLANNING
        plan = await self._generate_plan(task)
        
        # Add steps to task
        for step_data in plan:
            step = TaskStep(
                step_id=step_data.get("step_id", str(uuid.uuid4())),
                description=step_data.get("description", ""),
                action=step_data.get("action", ""),
                prerequisites=step_data.get("prerequisites", []),
                estimated_duration=step_data.get("estimated_duration", 60),
                required_tools=step_data.get("required_tools", []),
                validation_criteria=step_data.get("validation_criteria", [])
            )
            task.add_step(step)
        
        # Store task
        self.tasks[task_id] = task
        task.status = TaskStatus.PENDING
        
        # Add to execution queue
        await self.execution_queue.put(task)
        
        return task
    
    async def _generate_plan(self, task: Task) -> List[Dict[str, Any]]:
        """Generate execution plan for a task"""
        # Try using LLM for planning
        if self.llm_engine and LANGCHAIN_AVAILABLE:
            try:
                # Use LangChain to generate plan
                llm = self.llm_engine.select_best_llm("reasoning")
                if llm:
                    chain = LLMChain(llm=llm, prompt=self.planning_prompt)
                    response = await chain.arun(
                        task_description=task.description,
                        task_type=task.task_type.value,
                        context=json.dumps(task.metadata)
                    )
                    
                    # Parse JSON response
                    try:
                        plan = json.loads(response)
                        if isinstance(plan, list) and plan:
                            return plan
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"Error generating plan with LLM: {e}")
        
        # Fallback to template-based planning
        return self._generate_template_plan(task)
    
    def _generate_template_plan(self, task: Task) -> List[Dict[str, Any]]:
        """Generate plan using templates"""
        # Map task type to template
        template_map = {
            TaskType.CODING: "code_generation",
            TaskType.RESEARCH: "research",
            TaskType.ANALYSIS: "problem_solving"
        }
        
        template_name = template_map.get(task.task_type, "problem_solving")
        template = self.task_templates.get(template_name, {})
        
        plan = []
        for i, step_template in enumerate(template.get("steps", [])):
            step = {
                "step_id": f"step_{i+1}",
                "description": f"{step_template['action'].replace('_', ' ').title()} for {task.description[:50]}",
                "action": step_template["action"],
                "prerequisites": [f"step_{i}"] if i > 0 else [],
                "estimated_duration": step_template.get("duration", 60),
                "required_tools": [],
                "validation_criteria": [f"Completed {step_template['action']}"]
            }
            plan.append(step)
        
        return plan if plan else self._generate_default_plan(task)
    
    def _generate_default_plan(self, task: Task) -> List[Dict[str, Any]]:
        """Generate a default plan for any task"""
        return [
            {
                "step_id": "step_1",
                "description": "Analyze the task requirements",
                "action": "analyze",
                "prerequisites": [],
                "estimated_duration": 30,
                "required_tools": [],
                "validation_criteria": ["Requirements understood"]
            },
            {
                "step_id": "step_2", 
                "description": "Execute main task",
                "action": "execute",
                "prerequisites": ["step_1"],
                "estimated_duration": 120,
                "required_tools": [],
                "validation_criteria": ["Task executed"]
            },
            {
                "step_id": "step_3",
                "description": "Validate results",
                "action": "validate",
                "prerequisites": ["step_2"],
                "estimated_duration": 30,
                "required_tools": [],
                "validation_criteria": ["Results validated"]
            }
        ]
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task by running its steps"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        completed_steps = []
        results = {}
        
        while not task.is_complete():
            # Get ready steps
            ready_steps = task.get_ready_steps(completed_steps)
            
            if not ready_steps:
                # Check for blocked state
                pending_steps = [s for s in task.steps if s.status == TaskStatus.PENDING]
                if pending_steps:
                    # Task is blocked
                    task.status = TaskStatus.BLOCKED
                    break
            
            # Execute ready steps in parallel
            step_tasks = []
            for step in ready_steps[:self.max_concurrent_tasks]:
                step_task = asyncio.create_task(
                    self._execute_step(task, step)
                )
                step_tasks.append((step, step_task))
            
            # Wait for steps to complete
            for step, step_task in step_tasks:
                try:
                    result = await step_task
                    results[step.step_id] = result
                    completed_steps.append(step.step_id)
                except Exception as e:
                    step.mark_failed(str(e))
                    # Continue with other steps
        
        # Update task status
        if task.is_complete():
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "progress": task.get_progress(),
            "results": results,
            "duration": (task.completed_at - task.started_at).total_seconds() if task.completed_at else None
        }
    
    async def _execute_step(self, task: Task, step: TaskStep) -> Any:
        """Execute a single step of a task"""
        step.mark_started()
        
        try:
            # Get execution strategy for task type
            strategy = self.execution_strategies.get(
                task.task_type,
                self._execute_generic_step
            )
            
            # Execute the step
            result = await strategy(task, step)
            
            # Validate results
            if await self._validate_step(step, result):
                step.mark_completed(result)
            else:
                step.mark_failed("Validation failed")
                
            return result
            
        except Exception as e:
            step.mark_failed(str(e))
            raise
    
    async def _validate_step(self, step: TaskStep, result: Any) -> bool:
        """Validate step execution results"""
        if not step.validation_criteria:
            return True  # No criteria means auto-pass
        
        # Simple validation for now
        return result is not None
    
    # Execution strategies for different task types
    async def _execute_generic_step(self, task: Task, step: TaskStep) -> Any:
        """Generic step execution"""
        # Simulate execution
        await asyncio.sleep(min(step.estimated_duration / 10, 5))
        return f"Executed {step.action} for {task.description[:50]}"
    
    async def _execute_research_step(self, task: Task, step: TaskStep) -> Any:
        """Execute research-related step"""
        if self.llm_engine:
            try:
                response, _ = await self.llm_engine.query_with_memory(
                    f"Research task: {step.description}\nContext: {json.dumps(task.metadata)}",
                    "reasoning"
                )
                return response
            except Exception as e:
                print(f"Research step failed: {e}")
        
        return await self._execute_generic_step(task, step)
    
    async def _execute_coding_step(self, task: Task, step: TaskStep) -> Any:
        """Execute coding-related step"""
        if self.llm_engine:
            try:
                response, _ = await self.llm_engine.query_with_memory(
                    f"Coding task: {step.description}\nAction: {step.action}",
                    "coding"
                )
                return response
            except Exception as e:
                print(f"Coding step failed: {e}")
        
        return await self._execute_generic_step(task, step)
    
    async def _execute_analysis_step(self, task: Task, step: TaskStep) -> Any:
        """Execute analysis-related step"""
        if self.llm_engine:
            try:
                response, _ = await self.llm_engine.query_with_memory(
                    f"Analysis task: {step.description}",
                    "reasoning"
                )
                return response
            except Exception as e:
                print(f"Analysis step failed: {e}")
        
        return await self._execute_generic_step(task, step)
    
    async def _execute_creative_step(self, task: Task, step: TaskStep) -> Any:
        """Execute creative task step"""
        if self.llm_engine:
            try:
                response, _ = await self.llm_engine.query_with_memory(
                    f"Creative task: {step.description}",
                    "creative"
                )
                return response
            except Exception as e:
                print(f"Creative step failed: {e}")
        
        return await self._execute_generic_step(task, step)
    
    async def _execute_system_step(self, task: Task, step: TaskStep) -> Any:
        """Execute system-related step"""
        # Could integrate with system commands here
        return await self._execute_generic_step(task, step)
    
    async def _execute_learning_step(self, task: Task, step: TaskStep) -> Any:
        """Execute learning-related step"""
        # Could integrate with self-learning system
        return await self._execute_generic_step(task, step)
    
    async def _execute_communication_step(self, task: Task, step: TaskStep) -> Any:
        """Execute communication step"""
        return await self._execute_generic_step(task, step)
    
    async def _execute_decision_step(self, task: Task, step: TaskStep) -> Any:
        """Execute decision-making step"""
        if self.llm_engine:
            try:
                response, _ = await self.llm_engine.query_with_memory(
                    f"Decision needed: {step.description}\nOptions: {step.metadata.get('options', [])}",
                    "reasoning"
                )
                return response
            except Exception as e:
                print(f"Decision step failed: {e}")
        
        return await self._execute_generic_step(task, step)
    
    async def run_execution_loop(self):
        """Main execution loop for processing tasks"""
        while True:
            try:
                # Get next task from queue
                task = await self.execution_queue.get()
                
                # Check if we can run it
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    # Re-queue the task
                    await self.execution_queue.put(task)
                    await asyncio.sleep(1)
                    continue
                
                # Execute task
                self.running_tasks[task.task_id] = task
                asyncio.create_task(self._run_task(task))
                
            except Exception as e:
                print(f"Error in execution loop: {e}")
                await asyncio.sleep(5)
    
    async def _run_task(self, task: Task):
        """Run a single task"""
        try:
            result = await self.execute_task(task)
            print(f"Task {task.task_id} completed: {result}")
        except Exception as e:
            print(f"Task {task.task_id} failed: {e}")
            task.status = TaskStatus.FAILED
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task.task_id, None)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status.value,
            "progress": task.get_progress(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "status": step.status.value,
                    "error": step.error
                }
                for step in task.steps
            ],
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get status of all tasks"""
        return [
            self.get_task_status(task_id)
            for task_id in self.tasks.keys()
        ]


# Create singleton instance
_task_planner = None

def get_task_planner(llm_engine=None, config: Dict[str, Any] = None) -> TaskPlanner:
    """Get or create the global task planner"""
    global _task_planner
    if _task_planner is None:
        _task_planner = TaskPlanner(llm_engine, config)
    return _task_planner