#!/usr/bin/env python3
"""
OSA Autonomous Intelligence System
Automatically determines intent and chooses appropriate actions
"""

import asyncio
import json
import logging
import re
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
        
        # Initialize Ollama client
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
        
        # Check available models
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
        
        # Process based on intent
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
        return {
            'model': self.model,
            'conversations': len(self.conversation_context),
            'learning_entries': len(self.learning_memory),
            'last_intent': self.conversation_context[-1]['intent'] if self.conversation_context else None,
            'ollama_connected': self.client is not None
        }
    
    async def shutdown(self):
        """Shutdown OSA gracefully."""
        self.logger.info("Shutting down OSA Autonomous...")
        # Could save state here if needed
        pass