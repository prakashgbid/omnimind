#!/usr/bin/env python3
"""
OSA Claude Code Orchestrator

OSA can spawn, manage, and orchestrate hundreds of Claude Code instances,
acting as a human would - providing inputs, reading outputs, making decisions,
and completing complex tasks autonomously.

This is the ultimate automation - OSA becomes YOU, managing all Claude instances.
"""

import asyncio
import subprocess
import json
import hashlib
import os
import pty
import select
import termios
import tty
import fcntl
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import re
import time

# For terminal interaction
import pexpect
import psutil


class ClaudeTaskType(Enum):
    """Types of tasks for Claude instances"""
    CODING = "coding"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"


@dataclass
class ClaudeInstance:
    """Represents a single Claude Code instance"""
    id: str
    terminal_process: Optional[Any]  # pexpect spawn object
    task: str
    task_type: ClaudeTaskType
    status: str  # idle, working, waiting_input, completed, error
    created_at: datetime
    last_interaction: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    current_prompt: Optional[str] = None
    completion_percentage: float = 0.0
    
    def is_alive(self) -> bool:
        """Check if the Claude instance is still running"""
        if self.terminal_process:
            return self.terminal_process.isalive()
        return False
    
    def needs_input(self) -> bool:
        """Check if Claude is waiting for input"""
        return self.status == "waiting_input"


@dataclass
class TaskPlan:
    """Execution plan for a complex task"""
    id: str
    description: str
    subtasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]  # task_id -> [dependency_ids]
    parallel_groups: List[List[str]]  # Groups of tasks that can run in parallel
    required_instances: int
    estimated_time: timedelta
    priority: int = 1
    
    def get_ready_tasks(self, completed_tasks: List[str]) -> List[Dict[str, Any]]:
        """Get tasks that are ready to execute"""
        ready = []
        for task in self.subtasks:
            task_id = task['id']
            if task_id not in completed_tasks:
                deps = self.dependencies.get(task_id, [])
                if all(dep in completed_tasks for dep in deps):
                    ready.append(task)
        return ready


class ClaudeCodeOrchestrator:
    """
    Orchestrates multiple Claude Code instances.
    Acts as a human would - provides inputs, reads outputs, makes decisions.
    """
    
    def __init__(self, max_instances: int = 10):
        self.max_instances = max_instances
        self.instances: Dict[str, ClaudeInstance] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[str] = []
        self.active_plan: Optional[TaskPlan] = None
        
        # Execution control
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=max_instances)
        
        # Patterns to detect Claude states
        self.patterns = {
            'ready': r'(Ready|How can I help|What would you like)',
            'thinking': r'(Thinking|Analyzing|Let me|I\'ll)',
            'waiting': r'(\?|:)\s*$',  # Ends with ? or :
            'error': r'(Error|Failed|Cannot|Unable)',
            'completed': r'(Complete|Finished|Done|Successfully)',
            'needs_approval': r'(Proceed\?|Continue\?|Is this correct|Shall I)'
        }
        
        # Response strategies
        self.response_strategies = {
            'approval': self._handle_approval_request,
            'clarification': self._handle_clarification_request,
            'error': self._handle_error,
            'next_step': self._provide_next_step
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path.home() / ".omnimind" / "osa_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"osa_orchestrator_{datetime.now():%Y%m%d_%H%M%S}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('OSA-Orchestrator')
    
    async def spawn_claude_instance(
        self,
        task: str,
        task_type: ClaudeTaskType,
        context: Optional[Dict] = None
    ) -> ClaudeInstance:
        """
        Spawn a new Claude Code instance in a terminal.
        This simulates opening a new terminal and running Claude.
        """
        
        instance_id = hashlib.md5(f"{task}{datetime.now()}".encode()).hexdigest()[:8]
        
        self.logger.info(f"🚀 Spawning Claude instance {instance_id} for: {task[:50]}...")
        
        try:
            # Spawn Claude Code in a new process
            # Using pexpect for better terminal interaction
            process = pexpect.spawn(
                'claude-code',
                timeout=30,
                maxread=10000,
                encoding='utf-8',
                codec_errors='ignore'
            )
            
            # Create instance object
            instance = ClaudeInstance(
                id=instance_id,
                terminal_process=process,
                task=task,
                task_type=task_type,
                status="initializing",
                created_at=datetime.now(),
                last_interaction=datetime.now(),
                context=context or {}
            )
            
            # Wait for Claude to be ready
            await self._wait_for_ready(instance)
            
            # Store instance
            self.instances[instance_id] = instance
            
            self.logger.info(f"✅ Claude instance {instance_id} ready")
            
            return instance
            
        except Exception as e:
            self.logger.error(f"❌ Failed to spawn Claude instance: {e}")
            raise
    
    async def _wait_for_ready(self, instance: ClaudeInstance):
        """Wait for Claude to be ready for input"""
        try:
            # Look for ready patterns
            instance.terminal_process.expect(
                [self.patterns['ready'], pexpect.TIMEOUT],
                timeout=10
            )
            instance.status = "idle"
        except pexpect.TIMEOUT:
            # Assume ready if no specific pattern
            instance.status = "idle"
    
    async def send_to_claude(
        self,
        instance: ClaudeInstance,
        prompt: str,
        wait_for_response: bool = True
    ) -> Optional[str]:
        """
        Send a prompt to a Claude instance and optionally wait for response.
        This acts exactly as a human would - typing and reading.
        """
        
        if not instance.is_alive():
            self.logger.error(f"Instance {instance.id} is not alive")
            return None
        
        self.logger.info(f"📝 Sending to {instance.id}: {prompt[:100]}...")
        
        instance.current_prompt = prompt
        instance.last_interaction = datetime.now()
        instance.status = "working"
        
        # Send the prompt (like typing in terminal)
        instance.terminal_process.sendline(prompt)
        
        # Record in history
        instance.conversation_history.append({
            'type': 'user',
            'content': prompt,
            'timestamp': datetime.now().isoformat()
        })
        
        if wait_for_response:
            response = await self._read_claude_response(instance)
            
            # Record response
            instance.conversation_history.append({
                'type': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            instance.outputs.append(response)
            
            # Analyze response to determine next action
            await self._analyze_and_respond(instance, response)
            
            return response
        
        return None
    
    async def _read_claude_response(
        self,
        instance: ClaudeInstance,
        timeout: int = 60
    ) -> str:
        """Read Claude's response from the terminal"""
        
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Read available output
                instance.terminal_process.expect(['\n', pexpect.TIMEOUT], timeout=1)
                line = instance.terminal_process.before
                
                if line:
                    response_lines.append(line)
                    
                    # Check if Claude is done responding
                    if self._is_response_complete(line):
                        break
                        
            except pexpect.TIMEOUT:
                # Check if we have enough response
                if response_lines and self._looks_complete('\n'.join(response_lines)):
                    break
        
        response = '\n'.join(response_lines)
        return response
    
    def _is_response_complete(self, text: str) -> bool:
        """Determine if Claude has finished responding"""
        # Check for completion patterns
        complete_patterns = [
            r'Is there anything else',
            r'Let me know if',
            r'Feel free to',
            r'Would you like',
            r'\?$',  # Ends with question
            r'```\s*$',  # Code block ended
        ]
        
        for pattern in complete_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _looks_complete(self, text: str) -> bool:
        """Check if the response looks complete"""
        # Simple heuristics
        sentences = text.count('.')
        questions = text.count('?')
        code_blocks = text.count('```')
        
        return (
            sentences > 2 or
            questions > 0 or
            (code_blocks > 0 and code_blocks % 2 == 0)  # Closed code blocks
        )
    
    async def _analyze_and_respond(self, instance: ClaudeInstance, response: str):
        """
        Analyze Claude's response and determine if/how to respond.
        This is where OSA acts as a human would.
        """
        
        response_lower = response.lower()
        
        # Check if Claude needs input
        if re.search(self.patterns['needs_approval'], response):
            await self._handle_approval_request(instance, response)
        
        elif re.search(self.patterns['error'], response):
            await self._handle_error(instance, response)
        
        elif re.search(self.patterns['completed'], response):
            await self._handle_completion(instance, response)
        
        elif response.endswith('?'):
            await self._handle_question(instance, response)
        
        else:
            # Claude is working, let it continue
            instance.status = "idle"
    
    async def _handle_approval_request(self, instance: ClaudeInstance, response: str):
        """Handle when Claude asks for approval"""
        self.logger.info(f"🤔 {instance.id} requests approval")
        
        # OSA makes the decision based on context and task
        if self._should_approve(instance, response):
            await self.send_to_claude(instance, "Yes, proceed", wait_for_response=True)
        else:
            # Provide guidance
            guidance = self._generate_guidance(instance, response)
            await self.send_to_claude(instance, guidance, wait_for_response=True)
    
    def _should_approve(self, instance: ClaudeInstance, response: str) -> bool:
        """Determine if OSA should approve Claude's request"""
        # Check for risky operations
        risky_patterns = ['delete', 'remove', 'drop', 'force', 'sudo', 'admin']
        
        for pattern in risky_patterns:
            if pattern in response.lower():
                return False  # Need to provide guidance instead
        
        # Check if it aligns with task
        task_keywords = instance.task.lower().split()
        response_keywords = response.lower().split()
        
        overlap = set(task_keywords) & set(response_keywords)
        
        # Approve if good alignment
        return len(overlap) > 2
    
    def _generate_guidance(self, instance: ClaudeInstance, response: str) -> str:
        """Generate guidance for Claude when not auto-approving"""
        
        if 'delete' in response.lower() or 'remove' in response.lower():
            return "Instead of deleting, first create a backup or move to an archive folder"
        
        elif 'error' in response.lower():
            return "Let's debug this step by step. First, show me the full error message and stack trace"
        
        else:
            # Provide task-specific guidance
            return f"Let's approach this differently. Focus on: {instance.task}. What are the key requirements?"
    
    async def _handle_error(self, instance: ClaudeInstance, response: str):
        """Handle when Claude encounters an error"""
        self.logger.warning(f"⚠️ {instance.id} encountered error")
        
        # Provide debugging assistance
        debug_prompt = """
I see there's an error. Let's debug this systematically:
1. First, check the error message carefully
2. Verify all prerequisites are met
3. Try a simpler version first
4. Check the logs for more details

Can you show me the exact error and what you tried?
"""
        
        await self.send_to_claude(instance, debug_prompt, wait_for_response=True)
    
    async def _handle_completion(self, instance: ClaudeInstance, response: str):
        """Handle when Claude completes a task"""
        self.logger.info(f"✅ {instance.id} completed task")
        
        instance.status = "completed"
        instance.completion_percentage = 100.0
        
        # Check if there are follow-up tasks
        if self.active_plan:
            next_tasks = self._get_next_tasks_for_instance(instance)
            if next_tasks:
                next_task = next_tasks[0]
                await self.assign_task_to_instance(instance, next_task)
    
    async def _handle_question(self, instance: ClaudeInstance, response: str):
        """Handle when Claude asks a question"""
        self.logger.info(f"❓ {instance.id} asks: {response[:100]}")
        
        # Generate intelligent response based on context
        answer = self._generate_answer(instance, response)
        await self.send_to_claude(instance, answer, wait_for_response=True)
    
    def _generate_answer(self, instance: ClaudeInstance, question: str) -> str:
        """Generate an intelligent answer to Claude's question"""
        
        question_lower = question.lower()
        
        # Common question patterns and responses
        if 'which' in question_lower and 'prefer' in question_lower:
            # Choice question
            return "Choose the option that best aligns with best practices and maintainability"
        
        elif 'should i' in question_lower:
            # Decision question
            return f"Yes, that aligns with our goal: {instance.task}"
        
        elif 'what' in question_lower and 'name' in question_lower:
            # Naming question
            return "Use descriptive names following the project's naming conventions"
        
        elif 'how many' in question_lower:
            # Quantity question
            return "Start with a reasonable default (3-5) and we can adjust later"
        
        else:
            # Generic guidance
            return f"Proceed with what makes most sense for: {instance.task}. Use your best judgment."
    
    async def execute_complex_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a complex task by breaking it down and orchestrating multiple Claude instances.
        This is the main entry point where OSA takes over completely.
        """
        
        self.logger.info(f"🎯 OSA taking over task: {task_description}")
        
        # 1. Create execution plan
        plan = self._create_execution_plan(task_description)
        self.active_plan = plan
        
        self.logger.info(f"📋 Created plan with {len(plan.subtasks)} subtasks, needs {plan.required_instances} instances")
        
        # 2. Spawn required Claude instances
        instances = await self._spawn_instances_for_plan(plan)
        
        # 3. Execute plan
        results = await self._execute_plan(plan, instances)
        
        # 4. Synthesize results
        final_output = self._synthesize_results(results)
        
        return {
            'task': task_description,
            'plan': plan,
            'instances_used': len(instances),
            'results': results,
            'final_output': final_output,
            'success': True
        }
    
    def _create_execution_plan(self, task_description: str) -> TaskPlan:
        """Create an execution plan for the task"""
        
        # Analyze task to break it down
        task_keywords = task_description.lower().split()
        
        subtasks = []
        
        # Identify task components
        if 'app' in task_keywords or 'application' in task_keywords:
            subtasks.extend([
                {'id': 'design', 'type': ClaudeTaskType.ANALYSIS, 'description': 'Design application architecture'},
                {'id': 'backend', 'type': ClaudeTaskType.CODING, 'description': 'Implement backend API'},
                {'id': 'frontend', 'type': ClaudeTaskType.CODING, 'description': 'Build frontend interface'},
                {'id': 'database', 'type': ClaudeTaskType.CODING, 'description': 'Set up database'},
                {'id': 'tests', 'type': ClaudeTaskType.TESTING, 'description': 'Write tests'},
                {'id': 'deploy', 'type': ClaudeTaskType.DEPLOYMENT, 'description': 'Deploy application'}
            ])
            
            dependencies = {
                'backend': ['design'],
                'frontend': ['design'],
                'database': ['design'],
                'tests': ['backend', 'frontend'],
                'deploy': ['tests']
            }
            
            parallel_groups = [
                ['design'],
                ['backend', 'frontend', 'database'],
                ['tests'],
                ['deploy']
            ]
            
        elif 'analyze' in task_keywords or 'research' in task_keywords:
            subtasks.extend([
                {'id': 'gather', 'type': ClaudeTaskType.RESEARCH, 'description': 'Gather information'},
                {'id': 'analyze', 'type': ClaudeTaskType.ANALYSIS, 'description': 'Analyze data'},
                {'id': 'report', 'type': ClaudeTaskType.DOCUMENTATION, 'description': 'Generate report'}
            ])
            
            dependencies = {
                'analyze': ['gather'],
                'report': ['analyze']
            }
            
            parallel_groups = [
                ['gather'],
                ['analyze'],
                ['report']
            ]
            
        else:
            # Generic task breakdown
            subtasks = [
                {'id': 'plan', 'type': ClaudeTaskType.ANALYSIS, 'description': 'Plan approach'},
                {'id': 'implement', 'type': ClaudeTaskType.CODING, 'description': 'Implement solution'},
                {'id': 'verify', 'type': ClaudeTaskType.TESTING, 'description': 'Verify results'}
            ]
            
            dependencies = {
                'implement': ['plan'],
                'verify': ['implement']
            }
            
            parallel_groups = [
                ['plan'],
                ['implement'],
                ['verify']
            ]
        
        # Calculate required instances (max parallel tasks)
        required_instances = max(len(group) for group in parallel_groups)
        
        return TaskPlan(
            id=hashlib.md5(task_description.encode()).hexdigest()[:8],
            description=task_description,
            subtasks=subtasks,
            dependencies=dependencies,
            parallel_groups=parallel_groups,
            required_instances=min(required_instances, self.max_instances),
            estimated_time=timedelta(minutes=len(subtasks) * 10)
        )
    
    async def _spawn_instances_for_plan(self, plan: TaskPlan) -> List[ClaudeInstance]:
        """Spawn Claude instances needed for the plan"""
        instances = []
        
        for i in range(plan.required_instances):
            instance = await self.spawn_claude_instance(
                task=f"Worker {i+1} for: {plan.description}",
                task_type=ClaudeTaskType.CODING,
                context={'plan_id': plan.id}
            )
            instances.append(instance)
        
        return instances
    
    async def _execute_plan(
        self,
        plan: TaskPlan,
        instances: List[ClaudeInstance]
    ) -> Dict[str, Any]:
        """Execute the plan using available instances"""
        
        results = {}
        completed = []
        
        for group in plan.parallel_groups:
            # Get tasks in this parallel group
            group_tasks = [t for t in plan.subtasks if t['id'] in group]
            
            # Assign tasks to instances
            assignments = []
            for i, task in enumerate(group_tasks):
                if i < len(instances):
                    instance = instances[i]
                    assignments.append((instance, task))
            
            # Execute in parallel
            group_results = await asyncio.gather(*[
                self.assign_task_to_instance(instance, task)
                for instance, task in assignments
            ])
            
            # Store results
            for task, result in zip(group_tasks, group_results):
                results[task['id']] = result
                completed.append(task['id'])
            
            self.logger.info(f"✅ Completed parallel group: {group}")
        
        return results
    
    async def assign_task_to_instance(
        self,
        instance: ClaudeInstance,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assign a specific task to a Claude instance"""
        
        self.logger.info(f"📌 Assigning {task['id']} to {instance.id}")
        
        # Create detailed prompt for the task
        prompt = f"""
Task: {task['description']}
Type: {task['type'].value}

Please complete this task following best practices.
Provide clear output and let me know when you're done.
If you need any clarification, just ask.

Begin now.
"""
        
        # Send task to Claude
        response = await self.send_to_claude(instance, prompt, wait_for_response=True)
        
        # Continue interaction until task is complete
        max_interactions = 10
        interactions = 0
        
        while instance.status != "completed" and interactions < max_interactions:
            # Check if Claude needs input
            if instance.status == "waiting_input":
                # Provide input based on context
                next_input = self._generate_next_input(instance, task)
                response = await self.send_to_claude(instance, next_input, wait_for_response=True)
            
            interactions += 1
            await asyncio.sleep(2)
        
        return {
            'task_id': task['id'],
            'instance_id': instance.id,
            'outputs': instance.outputs[-5:],  # Last 5 outputs
            'status': instance.status,
            'interactions': interactions
        }
    
    def _generate_next_input(self, instance: ClaudeInstance, task: Dict[str, Any]) -> str:
        """Generate the next input for Claude based on context"""
        
        # Look at recent output to determine what's needed
        if instance.outputs:
            last_output = instance.outputs[-1].lower()
            
            if 'error' in last_output:
                return "Let's debug this. Can you show me the full error and what line it occurs on?"
            elif 'which' in last_output:
                return f"Choose the option that best fits: {task['description']}"
            elif 'done' in last_output or 'complete' in last_output:
                return "Great! Can you summarize what was accomplished?"
            else:
                return "Continue with the next step"
        
        return "Please proceed with the task"
    
    def _synthesize_results(self, results: Dict[str, Any]) -> str:
        """Synthesize results from all tasks"""
        
        synthesis = "Task Execution Complete\n"
        synthesis += "=" * 50 + "\n\n"
        
        for task_id, result in results.items():
            synthesis += f"Task: {task_id}\n"
            synthesis += f"Status: {result['status']}\n"
            synthesis += f"Interactions: {result['interactions']}\n"
            
            if result['outputs']:
                synthesis += "Key outputs:\n"
                for output in result['outputs'][-2:]:  # Last 2 outputs
                    synthesis += f"  - {output[:200]}...\n"
            
            synthesis += "\n"
        
        return synthesis
    
    def _get_next_tasks_for_instance(self, instance: ClaudeInstance) -> List[Dict[str, Any]]:
        """Get next tasks that can be assigned to an instance"""
        if not self.active_plan:
            return []
        
        completed = [t['id'] for t in self.completed_tasks]
        ready_tasks = self.active_plan.get_ready_tasks(completed)
        
        # Filter tasks that haven't been assigned
        unassigned = []
        assigned_tasks = set()
        
        for inst in self.instances.values():
            if inst.task:
                assigned_tasks.add(inst.task)
        
        for task in ready_tasks:
            if task['description'] not in assigned_tasks:
                unassigned.append(task)
        
        return unassigned
    
    async def monitor_all_instances(self):
        """Monitor all active Claude instances"""
        while self.running:
            for instance_id, instance in list(self.instances.items()):
                if not instance.is_alive():
                    self.logger.warning(f"Instance {instance_id} died")
                    del self.instances[instance_id]
                    continue
                
                # Check if instance needs attention
                if instance.status == "waiting_input":
                    idle_time = datetime.now() - instance.last_interaction
                    if idle_time > timedelta(seconds=30):
                        # Instance has been waiting too long
                        await self._provide_next_step(instance)
            
            await asyncio.sleep(5)
    
    async def _provide_next_step(self, instance: ClaudeInstance):
        """Provide next step to an idle instance"""
        next_prompt = "Continue with the next logical step for the task"
        await self.send_to_claude(instance, next_prompt, wait_for_response=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'active_instances': len(self.instances),
            'max_instances': self.max_instances,
            'instances': {
                id: {
                    'task': inst.task[:50],
                    'status': inst.status,
                    'completion': inst.completion_percentage,
                    'alive': inst.is_alive()
                }
                for id, inst in self.instances.items()
            },
            'active_plan': self.active_plan.description if self.active_plan else None,
            'completed_tasks': len(self.completed_tasks)
        }


class OSAClaudeInterface:
    """
    High-level interface for OSA to control Claude Code instances.
    This is what OSA uses to complete tasks autonomously.
    """
    
    def __init__(self, max_parallel: int = 10):
        self.orchestrator = ClaudeCodeOrchestrator(max_instances=max_parallel)
        self.logger = logging.getLogger('OSA-Interface')
    
    async def complete_task(self, task: str) -> Dict[str, Any]:
        """
        Complete any task autonomously.
        OSA handles everything - no human intervention needed.
        """
        
        self.logger.info(f"🚀 OSA taking control to complete: {task}")
        
        # Execute the task
        result = await self.orchestrator.execute_complex_task(task)
        
        self.logger.info(f"✅ Task completed using {result['instances_used']} Claude instances")
        
        return result
    
    async def parallel_execute(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel"""
        
        self.logger.info(f"🚀 OSA executing {len(tasks)} tasks in parallel")
        
        results = await asyncio.gather(*[
            self.orchestrator.execute_complex_task(task)
            for task in tasks
        ])
        
        return results
    
    async def interactive_development(
        self,
        project_description: str,
        requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Develop a complete project interactively.
        OSA manages all Claude instances to build the project.
        """
        
        self.logger.info(f"🏗️ OSA starting project: {project_description}")
        
        # Create project plan
        project_task = f"""
Build a complete project: {project_description}

Requirements:
{chr(10).join([f'- {req}' for req in requirements])}

Deliverables:
- Complete source code
- Tests
- Documentation
- Deployment configuration
"""
        
        # Execute project
        result = await self.complete_task(project_task)
        
        return result
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current status of all Claude instances"""
        return self.orchestrator.get_status()


# Example usage
async def demo_osa_orchestration():
    """Demonstrate OSA orchestrating Claude Code instances"""
    
    print("🧠 OSA Claude Orchestrator Demo")
    print("=" * 60)
    
    # Create OSA interface
    osa = OSAClaudeInterface(max_parallel=5)
    
    # Complete a complex task autonomously
    task = "Build a REST API with authentication, database, and testing"
    
    print(f"\n📋 Task: {task}")
    print("OSA is taking over...\n")
    
    result = await osa.complete_task(task)
    
    print("\n✅ Task Complete!")
    print(f"Used {result['instances_used']} Claude instances")
    print(f"Final output:\n{result['final_output']}")
    
    # Check status
    status = osa.get_orchestrator_status()
    print(f"\n📊 Status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    asyncio.run(demo_osa_orchestration())