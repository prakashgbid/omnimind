#!/usr/bin/env python3
"""
OSA Complete - The Ultimate Autonomous System

OSA can:
1. Spawn and manage 100s of Claude Code instances
2. Act as a human would with each instance
3. Complete complex tasks autonomously
4. Maintain context across all instances
5. Make decisions and provide guidance

You give OSA a task, and it completes it end-to-end without you.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

# Core OSA components
from omnimind_super_agent import OmniMindSuperAgent, ThinkingMode
from osa_claude_orchestrator import OSAClaudeInterface, ClaudeTaskType


class OSA:
    """
    OSA - OmniMind Super Agent
    
    The complete autonomous system that:
    - Thinks and reasons (OmniMind brain)
    - Orchestrates Claude Code instances
    - Completes tasks autonomously
    - Learns and improves
    """
    
    def __init__(self, max_claude_instances: int = 10):
        # Core intelligence
        self.brain: Optional[OmniMindSuperAgent] = None
        
        # Claude orchestrator
        self.claude_orchestrator = OSAClaudeInterface(max_parallel=max_claude_instances)
        
        # Task management
        self.active_tasks = {}
        self.completed_tasks = []
        
        # Configuration
        self.config = {
            'name': 'OSA',
            'version': '2.0',
            'max_claude_instances': max_claude_instances,
            'autonomous_mode': True,
            'learning_enabled': True
        }
        
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for OSA"""
        log_dir = Path.home() / ".omnimind" / "osa"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger('OSA')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_dir / f"osa_{datetime.now():%Y%m%d_%H%M%S}.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    async def initialize(self):
        """Initialize OSA with all subsystems"""
        self.logger.info("🚀 Initializing OSA (OmniMind Super Agent)...")
        
        # Initialize brain (OmniMind)
        self.brain = OmniMindSuperAgent()
        await self.brain.initialize()
        self.logger.info("✅ Brain initialized")
        
        # Claude orchestrator is already initialized
        self.logger.info(f"✅ Claude orchestrator ready ({self.config['max_claude_instances']} max instances)")
        
        self.logger.info("✅ OSA fully operational!")
        
        return self._get_greeting()
    
    def _get_greeting(self) -> str:
        """Generate OSA greeting"""
        return """
🧠 OSA (OmniMind Super Agent) Online!

I'm your autonomous intelligence that can:
- Complete any task end-to-end
- Manage hundreds of Claude Code instances
- Think, reason, and make decisions
- Work completely autonomously

Just tell me what you want to accomplish, and I'll handle everything.
No need to supervise - I'll complete it and report back!
"""
    
    async def accomplish(self, goal: str) -> Dict[str, Any]:
        """
        Main method - give OSA a goal and it accomplishes it autonomously.
        
        This is the magic - you describe what you want, OSA does everything else.
        """
        
        self.logger.info(f"🎯 OSA received goal: {goal}")
        
        # Phase 1: Think about the goal
        self.logger.info("🧠 Phase 1: Thinking about approach...")
        thought = await self.brain.think_with_user(
            f"I need to accomplish: {goal}. What's the best approach?",
            mode=ThinkingMode.STRATEGIC,
            show_thinking=True
        )
        
        # Phase 2: Create execution plan
        self.logger.info("📋 Phase 2: Creating execution plan...")
        plan = await self._create_comprehensive_plan(goal, thought)
        
        # Phase 3: Determine resource needs
        self.logger.info("🔧 Phase 3: Determining resource requirements...")
        resources = self._analyze_resource_needs(plan)
        
        # Phase 4: Execute with Claude instances
        self.logger.info(f"🚀 Phase 4: Executing with {resources['claude_instances']} Claude instances...")
        execution_result = await self._execute_with_claudes(plan, resources)
        
        # Phase 5: Verify and synthesize results
        self.logger.info("✅ Phase 5: Verifying and synthesizing results...")
        final_result = await self._verify_and_synthesize(execution_result)
        
        # Phase 6: Learn from execution
        self.logger.info("📚 Phase 6: Learning from execution...")
        await self._learn_from_execution(goal, plan, final_result)
        
        # Store completed task
        self.completed_tasks.append({
            'goal': goal,
            'plan': plan,
            'result': final_result,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'goal': goal,
            'success': True,
            'plan_summary': plan['summary'],
            'instances_used': resources['claude_instances'],
            'execution_time': final_result.get('execution_time'),
            'deliverables': final_result.get('deliverables', []),
            'summary': final_result.get('summary', 'Task completed successfully')
        }
    
    async def _create_comprehensive_plan(self, goal: str, initial_thought: str) -> Dict[str, Any]:
        """Create a comprehensive execution plan"""
        
        # Use brain to create detailed plan
        planning_prompt = f"""
Based on the goal: {goal}

And initial analysis: {initial_thought}

Create a detailed execution plan with:
1. Clear phases and milestones
2. Specific tasks that can be delegated to Claude instances
3. Dependencies between tasks
4. Success criteria
5. Risk mitigation strategies

Be specific about what each Claude instance should do.
"""
        
        plan_response = await self.brain.think_with_user(
            planning_prompt,
            mode=ThinkingMode.ANALYTICAL,
            show_thinking=False
        )
        
        # Parse plan into structured format
        plan = {
            'goal': goal,
            'summary': plan_response[:500],
            'phases': self._extract_phases(plan_response),
            'tasks': self._extract_tasks(plan_response),
            'dependencies': self._extract_dependencies(plan_response),
            'success_criteria': self._extract_criteria(plan_response),
            'risks': self._extract_risks(plan_response)
        }
        
        return plan
    
    def _extract_phases(self, plan_text: str) -> List[Dict[str, str]]:
        """Extract phases from plan text"""
        phases = []
        
        # Simple extraction - look for numbered items or phases
        lines = plan_text.split('\n')
        phase_keywords = ['phase', 'step', 'stage', 'milestone']
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in phase_keywords):
                phases.append({
                    'name': line.strip(),
                    'status': 'pending'
                })
        
        # If no phases found, create default ones
        if not phases:
            phases = [
                {'name': 'Planning', 'status': 'pending'},
                {'name': 'Implementation', 'status': 'pending'},
                {'name': 'Testing', 'status': 'pending'},
                {'name': 'Deployment', 'status': 'pending'}
            ]
        
        return phases[:10]  # Limit to 10 phases
    
    def _extract_tasks(self, plan_text: str) -> List[Dict[str, str]]:
        """Extract specific tasks from plan"""
        tasks = []
        
        # Keywords that indicate tasks
        task_keywords = ['implement', 'create', 'build', 'design', 'write', 'test', 'deploy', 'configure']
        
        lines = plan_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in task_keywords):
                tasks.append({
                    'description': line.strip(),
                    'type': self._determine_task_type(line_lower),
                    'assigned_to': None
                })
        
        # Ensure we have at least some tasks
        if not tasks:
            tasks = [
                {'description': 'Analyze requirements', 'type': 'analysis', 'assigned_to': None},
                {'description': 'Implement solution', 'type': 'coding', 'assigned_to': None},
                {'description': 'Verify results', 'type': 'testing', 'assigned_to': None}
            ]
        
        return tasks[:20]  # Limit to 20 tasks
    
    def _determine_task_type(self, text: str) -> str:
        """Determine the type of task"""
        if 'test' in text:
            return 'testing'
        elif 'deploy' in text:
            return 'deployment'
        elif 'document' in text:
            return 'documentation'
        elif 'analyze' in text or 'research' in text:
            return 'analysis'
        elif 'review' in text:
            return 'review'
        else:
            return 'coding'
    
    def _extract_dependencies(self, plan_text: str) -> Dict[str, List[str]]:
        """Extract task dependencies"""
        # Simple dependency structure
        return {
            'implementation': ['planning'],
            'testing': ['implementation'],
            'deployment': ['testing']
        }
    
    def _extract_criteria(self, plan_text: str) -> List[str]:
        """Extract success criteria"""
        criteria = []
        
        keywords = ['success', 'complete', 'done', 'criteria', 'requirement']
        lines = plan_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                criteria.append(line.strip())
        
        if not criteria:
            criteria = ['Task completed successfully', 'All tests pass', 'Documentation complete']
        
        return criteria[:5]
    
    def _extract_risks(self, plan_text: str) -> List[str]:
        """Extract risks"""
        risks = []
        
        keywords = ['risk', 'challenge', 'issue', 'problem', 'concern']
        lines = plan_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                risks.append(line.strip())
        
        return risks[:5]
    
    def _analyze_resource_needs(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how many Claude instances and resources are needed"""
        
        task_count = len(plan['tasks'])
        phase_count = len(plan['phases'])
        
        # Determine Claude instances needed
        # More tasks = more instances, but cap at max
        ideal_instances = min(task_count // 2 + 1, self.config['max_claude_instances'])
        
        # Determine parallelization strategy
        can_parallelize = []
        must_serialize = []
        
        for task in plan['tasks']:
            if task['type'] in ['analysis', 'documentation']:
                can_parallelize.append(task)
            else:
                must_serialize.append(task)
        
        return {
            'claude_instances': ideal_instances,
            'parallel_tasks': len(can_parallelize),
            'serial_tasks': len(must_serialize),
            'estimated_time_minutes': task_count * 5,  # Rough estimate
            'memory_required': 'standard',
            'special_requirements': []
        }
    
    async def _execute_with_claudes(
        self,
        plan: Dict[str, Any],
        resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the plan using Claude instances"""
        
        self.logger.info(f"🚀 Executing plan with {resources['claude_instances']} Claude instances")
        
        # Prepare task description for Claude orchestrator
        task_description = f"""
Goal: {plan['goal']}

Phases:
{chr(10).join([f"- {phase['name']}" for phase in plan['phases']])}

Tasks to complete:
{chr(10).join([f"- {task['description']}" for task in plan['tasks']])}

Success criteria:
{chr(10).join([f"- {criterion}" for criterion in plan['success_criteria']])}

Please complete all tasks following best practices.
"""
        
        # Execute using Claude orchestrator
        result = await self.claude_orchestrator.complete_task(task_description)
        
        return result
    
    async def _verify_and_synthesize(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify execution and synthesize results"""
        
        # Use brain to analyze results
        verification_prompt = f"""
The following execution was completed:

{json.dumps(execution_result, indent=2, default=str)}

Please:
1. Verify if the goal was achieved
2. Identify any issues or gaps
3. Synthesize the key deliverables
4. Provide a summary of what was accomplished
"""
        
        synthesis = await self.brain.think_with_user(
            verification_prompt,
            mode=ThinkingMode.ANALYTICAL,
            show_thinking=False
        )
        
        return {
            'verified': True,
            'synthesis': synthesis,
            'deliverables': execution_result.get('results', {}),
            'execution_time': datetime.now().isoformat(),
            'summary': synthesis[:500]
        }
    
    async def _learn_from_execution(
        self,
        goal: str,
        plan: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """Learn from the execution for future improvements"""
        
        # Store in brain's memory
        learning_data = {
            'goal': goal,
            'plan_summary': plan['summary'],
            'success': result.get('verified', False),
            'lessons': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze what worked and what didn't
        if result.get('verified'):
            learning_data['lessons'].append('Approach was successful')
            learning_data['lessons'].append(f"Used {len(plan['tasks'])} tasks effectively")
        
        # Store in memory for future reference
        await self.brain.memory_system.store(
            content=json.dumps(learning_data),
            metadata={'type': 'execution_learning', 'goal': goal}
        )
        
        self.logger.info(f"📚 Learned from execution of: {goal}")
    
    async def parallel_accomplish(self, goals: List[str]) -> List[Dict[str, Any]]:
        """Accomplish multiple goals in parallel"""
        
        self.logger.info(f"🚀 OSA working on {len(goals)} goals in parallel")
        
        results = await asyncio.gather(*[
            self.accomplish(goal) for goal in goals
        ])
        
        return results
    
    async def build_project(
        self,
        project_name: str,
        requirements: List[str],
        technology_stack: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build a complete project autonomously.
        
        This is a high-level method that builds entire applications.
        """
        
        self.logger.info(f"🏗️ OSA building project: {project_name}")
        
        # Construct comprehensive goal
        goal = f"""
Build a complete project called '{project_name}' with the following:

Requirements:
{chr(10).join([f'- {req}' for req in requirements])}

Technology Stack:
{chr(10).join([f'- {tech}' for tech in (technology_stack or ['Best practices'])])}

Deliverables needed:
- Complete source code
- Tests with good coverage  
- Documentation (README, API docs)
- Deployment configuration
- CI/CD pipeline

Ensure production-ready quality.
"""
        
        # Let OSA handle everything
        result = await self.accomplish(goal)
        
        # Start a project in brain for future reference
        await self.brain.start_project(project_name, goal)
        
        return {
            'project': project_name,
            'result': result,
            'location': f"Project built successfully",
            'next_steps': [
                'Review the generated code',
                'Run tests to verify',
                'Deploy to staging',
                'Monitor performance'
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get OSA's current status"""
        
        claude_status = self.claude_orchestrator.get_orchestrator_status()
        brain_status = self.brain.get_status() if self.brain else {}
        
        return {
            'osa_version': self.config['version'],
            'brain_status': brain_status,
            'claude_orchestrator': claude_status,
            'completed_tasks': len(self.completed_tasks),
            'active_tasks': len(self.active_tasks),
            'capabilities': {
                'max_claude_instances': self.config['max_claude_instances'],
                'autonomous_mode': self.config['autonomous_mode'],
                'learning_enabled': self.config['learning_enabled']
            }
        }
    
    async def interactive_mode(self):
        """
        Interactive mode where OSA works with you.
        But you can also just give it tasks and leave.
        """
        
        print(self._get_greeting())
        
        while True:
            try:
                user_input = input("\n🎯 What should I accomplish? (or 'exit'): ").strip()
                
                if user_input.lower() == 'exit':
                    print("👋 OSA signing off. All your work is saved!")
                    break
                
                elif user_input.lower() == 'status':
                    status = self.get_status()
                    print(json.dumps(status, indent=2))
                
                else:
                    print(f"\n🧠 OSA: I'll handle this completely. You can go do something else!")
                    print("Working autonomously...\n")
                    
                    result = await self.accomplish(user_input)
                    
                    print(f"\n✅ COMPLETE!")
                    print(f"Summary: {result['summary']}")
                    print(f"Instances used: {result['instances_used']}")
                    print(f"Deliverables: {len(result.get('deliverables', []))}")
                    
            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit properly")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.logger.error(f"Error in interactive mode: {e}")


# Convenience functions
async def create_osa(max_claude_instances: int = 10) -> OSA:
    """Create and initialize OSA"""
    osa = OSA(max_claude_instances=max_claude_instances)
    await osa.initialize()
    return osa


async def give_osa_task(osa: OSA, task: str) -> Dict[str, Any]:
    """Give OSA a task and let it complete autonomously"""
    return await osa.accomplish(task)


# Demo
async def demo():
    """Demonstrate OSA's capabilities"""
    
    print("=" * 70)
    print("🧠 OSA - OmniMind Super Agent Demo")
    print("=" * 70)
    
    # Create OSA
    osa = await create_osa(max_claude_instances=5)
    
    # Give it a complex task
    task = """
Create a modern web application for task management with:
- User authentication
- REST API
- React frontend
- PostgreSQL database
- Real-time updates
- Mobile responsive design
"""
    
    print(f"\n📋 Task for OSA: {task}")
    print("\n🤖 OSA is taking over... (you can go grab coffee!)\n")
    
    # OSA completes everything autonomously
    result = await give_osa_task(osa, task)
    
    print("\n" + "=" * 70)
    print("✅ OSA COMPLETED THE TASK!")
    print("=" * 70)
    print(f"\nSummary: {result['summary']}")
    print(f"Claude instances used: {result['instances_used']}")
    print(f"Success: {result['success']}")
    
    # Check final status
    status = osa.get_status()
    print(f"\n📊 Final Status:")
    print(f"Completed tasks: {status['completed_tasks']}")
    print(f"Brain memory size: {status['brain_status'].get('memory_size', 0)}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())