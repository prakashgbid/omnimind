#!/usr/bin/env python3
"""
Minimal working OSA implementation with Ollama integration.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Warning: ollama package not installed. Install with: pip install ollama")
    ollama = None

from .logger import setup_logger, OSALogger


class OSACompleteFinal:
    """
    Minimal working OSA with core capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize OSA with configuration."""
        self.config = config or {}
        self.model = self.config.get("model", "llama3.2:3b")
        self.verbose = self.config.get("verbose", False)
        
        # Setup logger
        self.logger = setup_logger("OSA", level="DEBUG" if self.verbose else "INFO")
        
        # Initialize Ollama client
        self.client = None
        if ollama:
            try:
                self.client = ollama.Client()
                self.logger.info(f"Ollama client initialized with model: {self.model}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama: {e}")
        
        # Context for continuous conversation
        self.context = []
        self.thought_history = []
        self.task_history = []
        
        # Thinking and learning flags
        self.enable_thinking = self.config.get("enable_thinking", True)
        self.enable_learning = self.config.get("enable_learning", True)
        
        self.logger.info("OSA initialized successfully")
    
    async def initialize(self):
        """Initialize OSA systems."""
        self.logger.info("Starting OSA systems...")
        
        # Check if Ollama is available
        if self.client:
            try:
                # Simple and direct approach - just use subprocess
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0:
                    # Parse the output
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    model_names = [line.split()[0] for line in lines if line.strip()]
                    
                    if model_names:
                        self.logger.info(f"Available models: {model_names}")
                        
                        # Check if requested model exists
                        if self.model not in model_names:
                            self.logger.warning(f"Model {self.model} not found")
                            self.model = model_names[0]  # Use first available
                            self.logger.info(f"Using model: {self.model}")
                        else:
                            self.logger.info(f"Using requested model: {self.model}")
                    else:
                        # No models found, use default
                        self.logger.warning("No models found, using default: llama3.2:3b")
                        self.model = "llama3.2:3b"
                else:
                    # Ollama command failed, use default
                    self.logger.warning("Could not list models, using default: llama3.2:3b")
                    self.model = "llama3.2:3b"
            except Exception as e:
                self.logger.error(f"Error checking models: {e}")
        
        # Start background thinking if enabled
        if self.enable_thinking:
            self.logger.info("Continuous thinking enabled")
            asyncio.create_task(self._continuous_thinking())
        
        # Start learning system if enabled
        if self.enable_learning:
            self.logger.info("Continuous learning enabled")
        
        self.logger.info("OSA systems initialized")
    
    async def _continuous_thinking(self):
        """Background thinking process."""
        while self.enable_thinking:
            try:
                # Generate background thoughts every 30 seconds
                await asyncio.sleep(30)
                
                if self.thought_history:
                    # Think about recent thoughts
                    recent_thought = self.thought_history[-1]
                    new_thought = await self._generate_thought(recent_thought)
                    if new_thought:
                        self.thought_history.append(new_thought)
                        if self.verbose:
                            self.logger.debug(f"New thought: {new_thought[:100]}...")
                
            except Exception as e:
                self.logger.error(f"Error in continuous thinking: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _generate_thought(self, context: str) -> Optional[str]:
        """Generate a new thought based on context."""
        if not self.client:
            return None
        
        try:
            prompt = f"Reflect on this and generate a deeper insight: {context}"
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                context=self.context if self.context else None
            )
            
            thought = response.get('response', '')
            
            # Update context for continuity
            if 'context' in response:
                self.context = response['context']
            
            return thought
            
        except Exception as e:
            self.logger.error(f"Error generating thought: {e}")
            return None
    
    async def accomplish_task(self, task: str) -> str:
        """
        Main method to accomplish any given task.
        
        Args:
            task: The task description
            
        Returns:
            The result/response
        """
        self.logger.info(f"Processing task: {task[:100]}...")
        
        # Add to task history
        self.task_history.append({
            'task': task,
            'timestamp': datetime.now().isoformat()
        })
        
        # If no Ollama client, return mock response
        if not self.client:
            return self._mock_response(task)
        
        try:
            # Break down the task
            steps = await self._analyze_task(task)
            
            # Process with Ollama
            response = self.client.generate(
                model=self.model,
                prompt=task,
                context=self.context if self.context else None
            )
            
            result = response.get('response', 'No response generated')
            
            # Update context for continuity
            if 'context' in response:
                self.context = response['context']
            
            # Add to thought history for learning
            if self.enable_learning:
                self.thought_history.append(f"Task: {task}\nResponse: {result[:200]}")
            
            self.logger.info("Task completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            return f"Error: {e}"
    
    async def _analyze_task(self, task: str) -> List[str]:
        """Analyze and break down a task into steps."""
        # Simple task breakdown (can be enhanced)
        steps = [
            "Understanding the request",
            "Identifying key components",
            "Generating solution",
            "Validating response"
        ]
        
        if self.verbose:
            for step in steps:
                self.logger.debug(f"  Step: {step}")
        
        return steps
    
    def _mock_response(self, task: str) -> str:
        """Generate a mock response when Ollama is not available."""
        return f"""
I understand you want me to: {task}

While I cannot process this with a language model right now (Ollama not available),
here's what I would typically do:

1. Analyze the requirements
2. Break down the task into manageable steps
3. Generate a comprehensive solution
4. Validate and refine the response

Please ensure Ollama is running with: ollama serve
And that you have models installed: ollama pull llama3.2:3b
"""
    
    async def think_about(self, topic: str) -> str:
        """
        Think deeply about a specific topic.
        
        Args:
            topic: The topic to think about
            
        Returns:
            Thoughts and insights
        """
        self.logger.info(f"Thinking about: {topic}")
        
        if not self.client:
            return "Cannot think without Ollama connection"
        
        try:
            prompt = f"""Think deeply about this topic and provide insights:
Topic: {topic}

Consider:
- Key concepts and principles
- Connections to other ideas
- Practical implications
- Potential challenges
- Creative perspectives
"""
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                context=self.context if self.context else None
            )
            
            thoughts = response.get('response', '')
            
            # Update context
            if 'context' in response:
                self.context = response['context']
            
            # Store in thought history
            self.thought_history.append(f"Topic: {topic}\nThoughts: {thoughts[:200]}")
            
            return thoughts
            
        except Exception as e:
            self.logger.error(f"Error thinking about topic: {e}")
            return f"Error: {e}"
    
    async def solve_problem(self, problem: str) -> str:
        """
        Solve a specific problem.
        
        Args:
            problem: Problem description
            
        Returns:
            Solution
        """
        self.logger.info(f"Solving problem: {problem[:100]}...")
        
        if not self.client:
            return "Cannot solve without Ollama connection"
        
        try:
            prompt = f"""Solve this problem step by step:
Problem: {problem}

Provide:
1. Problem analysis
2. Solution approach
3. Step-by-step solution
4. Verification
5. Alternative approaches (if applicable)
"""
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                context=self.context if self.context else None
            )
            
            solution = response.get('response', '')
            
            # Update context
            if 'context' in response:
                self.context = response['context']
            
            return solution
            
        except Exception as e:
            self.logger.error(f"Error solving problem: {e}")
            return f"Error: {e}"
    
    async def shutdown(self):
        """Shutdown OSA systems."""
        self.logger.info("Shutting down OSA systems...")
        
        # Stop continuous thinking
        self.enable_thinking = False
        self.enable_learning = False
        
        # Clear context
        self.context = []
        
        # Save history if needed (can be enhanced)
        if self.task_history:
            self.logger.info(f"Processed {len(self.task_history)} tasks in this session")
        
        if self.thought_history:
            self.logger.info(f"Generated {len(self.thought_history)} thoughts")
        
        self.logger.info("OSA shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OSA status."""
        return {
            'model': self.model,
            'thinking_enabled': self.enable_thinking,
            'learning_enabled': self.enable_learning,
            'tasks_processed': len(self.task_history),
            'thoughts_generated': len(self.thought_history),
            'context_size': len(self.context) if self.context else 0,
            'ollama_connected': self.client is not None
        }