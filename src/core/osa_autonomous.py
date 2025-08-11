#!/usr/bin/env python3
"""
OSA Autonomous Intelligence System
Automatically determines intent and chooses appropriate actions
"""

import asyncio
import json
import logging
import re
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

try:
    import ollama
except ImportError:
    print("Warning: ollama package not installed. Install with: pip install ollama")
    ollama = None

from .logger import setup_logger
from .langchain_engine import get_langchain_engine, LANGCHAIN_AVAILABLE
from .self_learning import get_learning_system, LearningDomain, FeedbackType
from .task_planner import get_task_planner, TaskType, TaskPriority
from .mcp_client import get_mcp_client
from .code_generator import get_code_generator, CodeGenerationRequest, CodeType, ProgrammingLanguage


class IntentType(Enum):
    """Types of user intents OSA can detect"""
    CODE_GENERATION = "code_generation"
    CODE_DEBUG = "code_debug"
    CODE_REFACTOR = "code_refactor"
    DEEP_THINKING = "deep_thinking"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"
    EXPLANATION = "explanation"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    GENERAL_CHAT = "general_chat"
    SYSTEM_TASK = "system_task"


class OSAAutonomous:
    """
    Autonomous OSA that automatically determines what to do
    based on user input without manual mode switching.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize autonomous OSA."""
        self.config = config or {}
        self.model = self.config.get("model", "llama3.2:3b")
        self.verbose = self.config.get("verbose", False)
        
        # Setup logger
        self.logger = setup_logger("OSA-Auto", level="DEBUG" if self.verbose else "INFO")
        
        # Initialize LangChain engine for advanced reasoning
        self.langchain_engine = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.langchain_engine = get_langchain_engine(config)
                self.logger.info("LangChain intelligence engine initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize LangChain: {e}")
        
        # Initialize self-learning system
        self.learning_system = None
        try:
            self.learning_system = get_learning_system(config)
            self.logger.info("Self-learning system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize learning system: {e}")
        
        # Initialize task planner
        self.task_planner = None
        try:
            self.task_planner = get_task_planner(self.langchain_engine, config)
            self.logger.info("Task planning system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize task planner: {e}")
        
        # Initialize MCP client for external tool integration
        self.mcp_client = None
        try:
            self.mcp_client = get_mcp_client(config)
            self.logger.info("MCP client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP client: {e}")
        
        # Initialize code generator for autonomous code creation
        self.code_generator = None
        try:
            self.code_generator = get_code_generator(self.langchain_engine, config)
            self.logger.info("Code generation system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize code generator: {e}")
        
        # Initialize Ollama client (fallback)
        self.client = None
        if ollama:
            try:
                self.client = ollama.Client()
                self.logger.info(f"Ollama client initialized with model: {self.model}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama: {e}")
        
        # Context management
        self.conversation_context = []
        self.task_context = {}
        self.learning_memory = []
        
        # Intent patterns for automatic detection - improved patterns
        self.intent_patterns = {
            IntentType.CODE_GENERATION: [
                r"write.*(?:code|function|script|program|app)", 
                r"create.*(?:function|script|program|app|code)",
                r"implement", r"build.*(?:app|program|script|function)",
                r"generate.*(?:script|code|function)", r"code.*for",
                r"develop", r"make.*(?:function|program|script)"
            ],
            IntentType.CODE_DEBUG: [
                r"debug", r"fix.*(?:error|bug|issue|problem)", 
                r"error", r"not working", r"throwing.*error",
                r"bug", r"issue.*code", r"problem.*(?:with|in).*code",
                r"crash", r"exception", r"help.*fix"
            ],
            IntentType.CODE_REFACTOR: [
                r"refactor", r"improve.*code", r"optimize",
                r"clean.*up", r"make.*(?:better|cleaner|faster)",
                r"performance", r"faster", r"efficient"
            ],
            IntentType.DEEP_THINKING: [
                r"think.*(?:deeply|about)", r"philosophy", r"contemplate",
                r"reflect", r"ponder", r"meditate", r"consciousness",
                r"deep.*(?:dive|thought)", r"explore.*concept", r"nature of"
            ],
            IntentType.PROBLEM_SOLVING: [
                r"solve", r"how.*(?:do|can|to)", r"figure.*out",
                r"calculate", r"work.*out", r"find.*solution",
                r"resolve", r"equation", r"math"
            ],
            IntentType.LEARNING: [
                r"learn", r"teach.*(?:me|about)", r"explain.*how",
                r"understand", r"study", r"tutorial", r"guide",
                r"walk.*through", r"lesson", r"course"
            ],
            IntentType.EXPLANATION: [
                r"what.*is", r"explain(?!.*how)", r"describe",
                r"tell.*about", r"how.*does", r"why.*(?:is|does|are)",
                r"define", r"meaning", r"definition"
            ],
            IntentType.CREATIVE: [
                r"create.*(?:story|poem|tale|narrative)", 
                r"write.*(?:story|poem|creative|fiction)",
                r"imagine", r"creative", r"design.*(?:story|character)",
                r"brainstorm", r"ideas.*for", r"invent.*story"
            ],
            IntentType.ANALYSIS: [
                r"analyze", r"evaluate", r"assess", r"review",
                r"examine", r"investigate", r"compare",
                r"critique", r"pros.*cons", r"advantages.*disadvantages"
            ],
            IntentType.SYSTEM_TASK: [
                r"run.*command", r"execute", r"terminal",
                r"system.*(?:command|task)", r"list.*files",
                r"file.*operation", r"directory", r"process"
            ]
        }
        
        self.logger.info("OSA Autonomous system initialized")
    
    async def initialize(self):
        """Initialize OSA systems."""
        self.logger.info("🚀 Starting OSA Autonomous systems...")
        
        # Initialize LangChain intelligence systems
        if self.langchain_engine:
            try:
                from .action_hooks import get_action_hooks
                self.langchain_engine.set_action_hooks(get_action_hooks())
                
                success = await self.langchain_engine.initialize_intelligence_systems()
                if success:
                    self.logger.info("🧠 Advanced intelligence systems initialized")
                else:
                    self.logger.warning("⚠️ Some intelligence systems failed to initialize")
            except Exception as e:
                self.logger.error(f"Error initializing LangChain: {e}")
        
        # Check available models (fallback)
        if self.client:
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    model_names = [line.split()[0] for line in lines if line.strip()]
                    
                    if model_names:
                        self.logger.info(f"📚 Available models: {model_names}")
                        if self.model not in model_names:
                            self.model = model_names[0]
                            self.logger.info(f"🔄 Switched to available model: {self.model}")
            except Exception as e:
                self.logger.error(f"Error checking models: {e}")
        
        # Start background intelligence
        asyncio.create_task(self._background_intelligence())
        
        # Start continuous learning loop
        if self.learning_system:
            asyncio.create_task(self.learning_system.continuous_learning_loop())
            self.logger.info("📚 Continuous learning activated")
        
        # Start task execution loop
        if self.task_planner:
            asyncio.create_task(self.task_planner.run_execution_loop())
            self.logger.info("🎯 Task planner activated")
        
        # Start MCP servers
        if self.mcp_client:
            try:
                await self.mcp_client.start_all_servers()
                self.logger.info("🔌 MCP servers started")
            except Exception as e:
                self.logger.error(f"Failed to start MCP servers: {e}")
        
        self.logger.info("✅ OSA Autonomous ready!")
    
    def detect_intent(self, user_input: str) -> Tuple[IntentType, float]:
        """
        Automatically detect user intent from input.
        Returns intent type and confidence score.
        """
        user_input_lower = user_input.lower()
        intent_scores = {}
        
        # Check each intent pattern
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    score += 1
            if score > 0:
                intent_scores[intent_type] = score / len(patterns)
        
        # If no specific intent detected, use general chat
        if not intent_scores:
            return IntentType.GENERAL_CHAT, 0.5
        
        # Return highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]
    
    def get_status_emoji(self, intent: IntentType) -> str:
        """Get status emoji for intent type."""
        emoji_map = {
            IntentType.CODE_GENERATION: "💻",
            IntentType.CODE_DEBUG: "🐛",
            IntentType.CODE_REFACTOR: "🔧",
            IntentType.DEEP_THINKING: "🧠",
            IntentType.PROBLEM_SOLVING: "🎯",
            IntentType.LEARNING: "📚",
            IntentType.EXPLANATION: "💡",
            IntentType.CREATIVE: "🎨",
            IntentType.ANALYSIS: "🔍",
            IntentType.GENERAL_CHAT: "💬",
            IntentType.SYSTEM_TASK: "⚙️"
        }
        return emoji_map.get(intent, "🤖")
    
    def _map_intent_to_task_type(self, intent: IntentType) -> str:
        """Map OSA intent to LangChain task type"""
        intent_mapping = {
            IntentType.CODE_GENERATION: "coding",
            IntentType.CODE_DEBUG: "coding", 
            IntentType.CODE_REFACTOR: "coding",
            IntentType.DEEP_THINKING: "reasoning",
            IntentType.PROBLEM_SOLVING: "reasoning",
            IntentType.ANALYSIS: "reasoning",
            IntentType.LEARNING: "rag_query",
            IntentType.EXPLANATION: "reasoning",
            IntentType.CREATIVE: "creative",
            IntentType.GENERAL_CHAT: "general",
            IntentType.SYSTEM_TASK: "general"
        }
        return intent_mapping.get(intent, "general")
    
    def _map_intent_to_learning_domain(self, intent: IntentType) -> LearningDomain:
        """Map OSA intent to learning domain"""
        mapping = {
            IntentType.CODE_GENERATION: LearningDomain.CODING,
            IntentType.CODE_DEBUG: LearningDomain.CODING,
            IntentType.CODE_REFACTOR: LearningDomain.CODING,
            IntentType.DEEP_THINKING: LearningDomain.PROBLEM_SOLVING,
            IntentType.PROBLEM_SOLVING: LearningDomain.PROBLEM_SOLVING,
            IntentType.LEARNING: LearningDomain.KNOWLEDGE,
            IntentType.EXPLANATION: LearningDomain.KNOWLEDGE,
            IntentType.CREATIVE: LearningDomain.CONVERSATION,
            IntentType.ANALYSIS: LearningDomain.PROBLEM_SOLVING,
            IntentType.GENERAL_CHAT: LearningDomain.CONVERSATION,
            IntentType.SYSTEM_TASK: LearningDomain.BEHAVIOR
        }
        return mapping.get(intent, LearningDomain.CONVERSATION)
    
    def _map_intent_to_task_type_planner(self, intent: IntentType) -> TaskType:
        """Map OSA intent to task planner type"""
        mapping = {
            IntentType.CODE_GENERATION: TaskType.CODING,
            IntentType.CODE_DEBUG: TaskType.CODING,
            IntentType.CODE_REFACTOR: TaskType.CODING,
            IntentType.DEEP_THINKING: TaskType.ANALYSIS,
            IntentType.PROBLEM_SOLVING: TaskType.ANALYSIS,
            IntentType.LEARNING: TaskType.RESEARCH,
            IntentType.EXPLANATION: TaskType.COMMUNICATION,
            IntentType.CREATIVE: TaskType.CREATIVE,
            IntentType.ANALYSIS: TaskType.ANALYSIS,
            IntentType.GENERAL_CHAT: TaskType.COMMUNICATION,
            IntentType.SYSTEM_TASK: TaskType.SYSTEM
        }
        return mapping.get(intent, TaskType.ANALYSIS)
    
    async def _needs_task_decomposition(self, user_input: str, intent: IntentType) -> bool:
        """Determine if input requires task decomposition"""
        # Complex task indicators
        complex_keywords = [
            "build", "create", "develop", "implement", "design",
            "analyze", "research", "investigate", "compare",
            "multiple", "several", "various", "complete", "entire"
        ]
        
        # Check for complexity indicators
        input_lower = user_input.lower()
        has_complex_keyword = any(keyword in input_lower for keyword in complex_keywords)
        is_long_input = len(user_input) > 200
        is_complex_intent = intent in [
            IntentType.CODE_GENERATION,
            IntentType.PROBLEM_SOLVING,
            IntentType.ANALYSIS
        ]
        
        return (has_complex_keyword or is_long_input) and is_complex_intent
    
    async def process_autonomously(self, user_input: str) -> str:
        """
        Process user input completely autonomously.
        Automatically determines intent and takes appropriate action.
        """
        # Detect intent
        intent, confidence = self.detect_intent(user_input)
        
        # Show status update
        status_emoji = self.get_status_emoji(intent)
        status_msg = f"{status_emoji} Detected: {intent.value.replace('_', ' ').title()} (confidence: {confidence:.0%})"
        
        # Log the detected intent
        self.logger.info(status_msg)
        
        # Store in context
        self.conversation_context.append({
            "input": user_input,
            "intent": intent.value,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if task decomposition is needed
        if await self._needs_task_decomposition(user_input, intent):
            # Create and execute a complex task
            task = await self.task_planner.create_task(
                description=user_input,
                task_type=self._map_intent_to_task_type_planner(intent),
                priority=TaskPriority.HIGH,
                context={"intent": intent.value}
            )
            
            # Return task creation confirmation
            return f"{status_msg}\n\n🎯 Complex task created with {len(task.steps)} steps. Task ID: {task.task_id}\n\nI'll work on this autonomously and update you on progress."
        
        # Apply learning recommendations if available
        learning_applied = False
        if self.learning_system:
            learning_domain = self._map_intent_to_learning_domain(intent)
            recommendations = await self.learning_system.apply_learning(learning_domain, user_input)
            
            if recommendations["confidence"] > 0.7:
                learning_applied = True
                self.logger.info(f"Applied learning with confidence: {recommendations['confidence']}")
        
        # Use LangChain for advanced processing if available
        if self.langchain_engine:
            try:
                task_type = self._map_intent_to_task_type(intent)
                response, metadata = await self.langchain_engine.query_with_memory(
                    user_input, task_type
                )
                
                # Add metadata to context
                if "success" in metadata:
                    self.conversation_context[-1]["langchain_used"] = True
                    self.conversation_context[-1]["model_used"] = metadata.get("model_used", "unknown")
                    self.conversation_context[-1]["learning_applied"] = learning_applied
                
                # Record interaction for learning
                if self.learning_system:
                    learning_domain = self._map_intent_to_learning_domain(intent)
                    await self.learning_system.record_interaction(
                        domain=learning_domain,
                        input_context=user_input,
                        output_response=response,
                        feedback=(FeedbackType.IMPLICIT, 0.7)  # Default positive feedback
                    )
                
                return f"{status_msg}\n\n{response}"
                
            except Exception as e:
                self.logger.error(f"LangChain processing failed: {e}")
                # Fallback to original processing
        
        # Process based on intent (fallback)
        if intent == IntentType.CODE_GENERATION:
            response = await self._handle_code_generation(user_input)
        elif intent == IntentType.CODE_DEBUG:
            response = await self._handle_code_debug(user_input)
        elif intent == IntentType.CODE_REFACTOR:
            response = await self._handle_code_refactor(user_input)
        elif intent == IntentType.DEEP_THINKING:
            response = await self._handle_deep_thinking(user_input)
        elif intent == IntentType.PROBLEM_SOLVING:
            response = await self._handle_problem_solving(user_input)
        elif intent == IntentType.LEARNING:
            response = await self._handle_learning(user_input)
        elif intent == IntentType.EXPLANATION:
            response = await self._handle_explanation(user_input)
        elif intent == IntentType.CREATIVE:
            response = await self._handle_creative(user_input)
        elif intent == IntentType.ANALYSIS:
            response = await self._handle_analysis(user_input)
        elif intent == IntentType.SYSTEM_TASK:
            response = await self._handle_system_task(user_input)
        else:
            response = await self._handle_general_chat(user_input)
        
        # Learn from interaction
        await self._learn_from_interaction(user_input, intent, response)
        
        return f"{status_msg}\n\n{response}"
    
    async def _handle_code_generation(self, user_input: str) -> str:
        """Handle code generation requests."""
        self.logger.debug("📝 Generating code...")
        
        # Use advanced code generator if available
        if self.code_generator:
            try:
                # Determine language from input
                language = ProgrammingLanguage.PYTHON  # Default
                if any(lang in user_input.lower() for lang in ['javascript', 'js']):
                    language = ProgrammingLanguage.JAVASCRIPT
                elif 'typescript' in user_input.lower():
                    language = ProgrammingLanguage.TYPESCRIPT
                elif 'go' in user_input.lower() or 'golang' in user_input.lower():
                    language = ProgrammingLanguage.GO
                
                # Determine code type
                code_type = CodeType.FUNCTION  # Default
                if 'class' in user_input.lower():
                    code_type = CodeType.CLASS
                elif 'module' in user_input.lower():
                    code_type = CodeType.MODULE
                elif 'script' in user_input.lower():
                    code_type = CodeType.SCRIPT
                elif 'test' in user_input.lower():
                    code_type = CodeType.TEST
                
                # Create generation request
                request = CodeGenerationRequest(
                    description=user_input,
                    code_type=code_type,
                    language=language,
                    requirements=["Clean code", "Error handling", "Documentation"],
                    constraints=[]
                )
                
                # Generate code
                result = await self.code_generator.generate_code(request)
                
                # Format response
                response_parts = [
                    f"Generated {result.language.value} code:",
                    f"```{result.language.value}",
                    result.code,
                    "```"
                ]
                
                if result.tests:
                    response_parts.extend([
                        "\nTests:",
                        f"```{result.language.value}",
                        result.tests,
                        "```"
                    ])
                
                if result.documentation:
                    response_parts.append(f"\nDocumentation:\n{result.documentation}")
                
                if result.quality_score > 0:
                    response_parts.append(f"\nCode Quality Score: {result.quality_score:.0%}")
                
                return "\n".join(response_parts)
                
            except Exception as e:
                self.logger.error(f"Code generation failed: {e}")
                # Fallback to basic generation
        
        # Fallback to basic prompt-based generation
        prompt = f"""As an expert programmer, generate clean, efficient code for:
{user_input}

Provide:
1. Complete, working code
2. Clear comments
3. Usage example
4. Brief explanation"""
        
        return await self._generate_response(prompt)
    
    async def _handle_code_debug(self, user_input: str) -> str:
        """Handle debugging requests."""
        self.logger.debug("🔍 Debugging code...")
        
        prompt = f"""As a debugging expert, help with:
{user_input}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Fixed code (if applicable)
4. Prevention tips"""
        
        return await self._generate_response(prompt)
    
    async def _handle_code_refactor(self, user_input: str) -> str:
        """Handle code refactoring requests."""
        self.logger.debug("♻️ Refactoring code...")
        
        prompt = f"""As a code quality expert, refactor for:
{user_input}

Focus on:
1. Better structure and organization
2. Performance improvements
3. Readability and maintainability
4. Best practices"""
        
        return await self._generate_response(prompt)
    
    async def _handle_deep_thinking(self, user_input: str) -> str:
        """Handle deep thinking requests."""
        self.logger.debug("💭 Engaging deep thinking mode...")
        
        prompt = f"""Think deeply and philosophically about:
{user_input}

Consider:
- Multiple perspectives
- Underlying principles
- Broader implications
- Novel insights
- Connections to other concepts"""
        
        return await self._generate_response(prompt)
    
    async def _handle_problem_solving(self, user_input: str) -> str:
        """Handle problem-solving requests."""
        self.logger.debug("🧩 Solving problem...")
        
        prompt = f"""Solve this problem systematically:
{user_input}

Approach:
1. Understand the problem
2. Break it down into steps
3. Apply relevant methods
4. Provide clear solution
5. Verify the answer"""
        
        return await self._generate_response(prompt)
    
    async def _handle_learning(self, user_input: str) -> str:
        """Handle learning/teaching requests."""
        self.logger.debug("📖 Teaching mode activated...")
        
        prompt = f"""As an expert teacher, help learn:
{user_input}

Structure:
1. Core concepts
2. Step-by-step explanation
3. Practical examples
4. Common pitfalls
5. Practice exercises"""
        
        response = await self._generate_response(prompt)
        
        # Store in learning memory
        self.learning_memory.append({
            "topic": user_input,
            "lesson": response[:500],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def _handle_explanation(self, user_input: str) -> str:
        """Handle explanation requests."""
        self.logger.debug("💡 Explaining concept...")
        
        prompt = f"""Explain clearly and comprehensively:
{user_input}

Include:
1. Simple definition
2. How it works
3. Real-world analogy
4. Why it matters
5. Related concepts"""
        
        return await self._generate_response(prompt)
    
    async def _handle_creative(self, user_input: str) -> str:
        """Handle creative requests."""
        self.logger.debug("🎨 Engaging creative mode...")
        
        prompt = f"""Be creative and imaginative with:
{user_input}

Let creativity flow with:
- Original ideas
- Vivid descriptions
- Unexpected connections
- Emotional depth
- Unique perspectives"""
        
        return await self._generate_response(prompt)
    
    async def _handle_analysis(self, user_input: str) -> str:
        """Handle analysis requests."""
        self.logger.debug("📊 Analyzing...")
        
        prompt = f"""Provide thorough analysis of:
{user_input}

Analysis should include:
1. Key observations
2. Patterns and trends
3. Strengths and weaknesses
4. Implications
5. Recommendations"""
        
        return await self._generate_response(prompt)
    
    async def _handle_system_task(self, user_input: str) -> str:
        """Handle system/command tasks."""
        self.logger.debug("⚡ Processing system task...")
        
        prompt = f"""Help with this system/command task:
{user_input}

Provide:
1. Command or script needed
2. What it does
3. Safety considerations
4. Expected output"""
        
        return await self._generate_response(prompt)
    
    async def _handle_general_chat(self, user_input: str) -> str:
        """Handle general conversation."""
        self.logger.debug("💬 General conversation...")
        
        return await self._generate_response(user_input)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Ollama."""
        if not self.client:
            return "OSA is running in simulation mode (Ollama not connected)"
        
        try:
            # Add context from previous conversations
            if self.conversation_context:
                recent_context = self.conversation_context[-3:]
                context_str = "\n".join([f"Previous: {c['input']}" for c in recent_context])
                prompt = f"Context:\n{context_str}\n\nCurrent request:\n{prompt}"
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt
            )
            
            return response.get('response', 'No response generated')
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error processing request: {e}"
    
    async def _learn_from_interaction(self, user_input: str, intent: IntentType, response: str):
        """Learn from each interaction to improve future responses."""
        # This is where OSA would update its patterns and improve
        # For now, just log the learning
        self.logger.debug(f"📚 Learning from {intent.value} interaction")
    
    async def _background_intelligence(self):
        """Background process for continuous intelligence."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Analyze conversation patterns
                if len(self.conversation_context) > 10:
                    # Could implement pattern learning here
                    self.logger.debug("🧠 Background analysis running...")
                    
            except Exception as e:
                self.logger.error(f"Background intelligence error: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def think_autonomously(self, topic: str) -> str:
        """Autonomous thinking without user direction."""
        self.logger.info("🧠 Autonomous thinking activated...")
        
        # Generate multiple perspectives
        perspectives = [
            "technical perspective",
            "philosophical angle",
            "practical implications",
            "future possibilities"
        ]
        
        thoughts = []
        for perspective in perspectives:
            prompt = f"Think about '{topic}' from a {perspective}"
            thought = await self._generate_response(prompt)
            thoughts.append(f"[{perspective.title()}]\n{thought}")
        
        return "\n\n".join(thoughts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OSA status."""
        status = {
            'model': self.model,
            'conversations': len(self.conversation_context),
            'learning_entries': len(self.learning_memory),
            'last_intent': self.conversation_context[-1]['intent'] if self.conversation_context else None,
            'ollama_connected': self.client is not None
        }
        
        # Add LangChain status if available
        if self.langchain_engine:
            langchain_status = self.langchain_engine.get_system_status()
            status['langchain'] = langchain_status
        else:
            status['langchain'] = {'available': False}
        
        # Add learning system status
        if self.learning_system:
            status['learning'] = self.learning_system.get_learning_insights()
        else:
            status['learning'] = {'available': False}
        
        # Add task planner status
        if self.task_planner:
            active_tasks = len(self.task_planner.running_tasks)
            pending_tasks = self.task_planner.execution_queue.qsize()
            status['task_planner'] = {
                'active_tasks': active_tasks,
                'pending_tasks': pending_tasks,
                'total_tasks': len(self.task_planner.tasks)
            }
        else:
            status['task_planner'] = {'available': False}
        
        # Add MCP client status
        if self.mcp_client:
            status['mcp'] = self.mcp_client.get_all_server_status()
        else:
            status['mcp'] = {'available': False}
        
        # Add code generator status
        if self.code_generator:
            status['code_generator'] = {
                'available': True,
                'templates': len(self.code_generator.templates),
                'modifications': len(self.code_generator.modification_history)
            }
        else:
            status['code_generator'] = {'available': False}
        
        return status
    
    async def shutdown(self):
        """Shutdown OSA gracefully."""
        self.logger.info("Shutting down OSA Autonomous...")
        
        # Shutdown LangChain systems
        if self.langchain_engine:
            try:
                await self.langchain_engine.shutdown()
                self.logger.info("✓ LangChain systems shut down")
            except Exception as e:
                self.logger.error(f"Error shutting down LangChain: {e}")
        
        # Shutdown MCP servers
        if self.mcp_client:
            try:
                await self.mcp_client.stop_all_servers()
                self.logger.info("✓ MCP servers stopped")
            except Exception as e:
                self.logger.error(f"Error stopping MCP servers: {e}")
        
        # Could save state here if needed
        self.logger.info("✓ OSA Autonomous shutdown complete")