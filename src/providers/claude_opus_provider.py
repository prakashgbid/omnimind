"""
Claude Opus Provider for OmniMind

Integrates Claude 3 Opus and other Anthropic models with intelligent routing.
Optimizes between Opus, Sonnet, and Haiku based on task requirements.
"""

import os
import time
from typing import Dict, List, Optional, Any
import anthropic
from anthropic import AsyncAnthropic
import asyncio

from .base import BaseProvider, ProviderResponse


class ClaudeOpusProvider(BaseProvider):
    """
    Provider for Claude 3 models with intelligent routing.
    
    Model hierarchy:
    - Claude 3 Opus: Most capable, best for complex reasoning
    - Claude 3 Sonnet: Balanced performance and cost
    - Claude 3 Haiku: Fast and efficient for simple tasks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Claude Opus provider."""
        super().__init__(config)
        
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
            self.sync_client = anthropic.Anthropic(api_key=self.api_key)
            self.available = True
        else:
            self.available = False
        
        # Claude 3 model family
        self.model_hierarchy = {
            'claude-3-opus': {
                'name': 'claude-3-opus-20240229',
                'cost_per_1k_input': 0.015,
                'cost_per_1k_output': 0.075,
                'capability': 'supreme',
                'context_window': 200000,
                'use_for': ['complex_reasoning', 'nuanced_understanding', 'creative_tasks', 'analysis']
            },
            'claude-3-sonnet': {
                'name': 'claude-3-sonnet-20240229',
                'cost_per_1k_input': 0.003,
                'cost_per_1k_output': 0.015,
                'capability': 'balanced',
                'context_window': 200000,
                'use_for': ['general_tasks', 'code_generation', 'content_creation']
            },
            'claude-3-haiku': {
                'name': 'claude-3-haiku-20240307',
                'cost_per_1k_input': 0.00025,
                'cost_per_1k_output': 0.00125,
                'capability': 'efficient',
                'context_window': 200000,
                'use_for': ['simple_tasks', 'quick_responses', 'basic_queries']
            }
        }
        
        # Task analysis patterns
        self.task_patterns = {
            'opus_required': [
                'analyze deeply', 'explain complex', 'philosophical', 
                'nuanced', 'creative writing', 'research', 'strategy'
            ],
            'sonnet_suitable': [
                'code', 'implement', 'create', 'build', 'design', 
                'write', 'summarize', 'translate'
            ],
            'haiku_sufficient': [
                'list', 'format', 'simple', 'quick', 'basic', 
                'yes/no', 'classify', 'extract'
            ]
        }
        
        self.default_model = config.get('default_model', 'claude-3-sonnet')
        self.use_smart_routing = config.get('smart_routing', True)
        self.max_cost_per_query = config.get('max_cost_per_query', 1.0)
        self.prefer_opus = config.get('prefer_opus', False)
    
    def _analyze_task_requirements(self, prompt: str) -> str:
        """Analyze task to select appropriate Claude model."""
        prompt_lower = prompt.lower()
        prompt_length = len(prompt)
        
        # Check for Opus-level requirements
        opus_score = sum(1 for pattern in self.task_patterns['opus_required'] 
                        if pattern in prompt_lower)
        
        # Check for Sonnet-level tasks
        sonnet_score = sum(1 for pattern in self.task_patterns['sonnet_suitable'] 
                          if pattern in prompt_lower)
        
        # Check for Haiku-level tasks
        haiku_score = sum(1 for pattern in self.task_patterns['haiku_sufficient'] 
                         if pattern in prompt_lower)
        
        # Decision logic
        if self.prefer_opus or opus_score > 0 or prompt_length > 5000:
            return 'claude-3-opus'
        elif sonnet_score > haiku_score or prompt_length > 1000:
            return 'claude-3-sonnet'
        else:
            return 'claude-3-haiku'
    
    def _build_claude_prompt(self, prompt: str, use_expertise: bool = True) -> str:
        """Build an optimized prompt for Claude."""
        if use_expertise:
            return f"""You are Claude, an AI assistant created by Anthropic with expertise across all domains.
You excel at nuanced reasoning, creative problem-solving, and providing thoughtful, detailed responses.

{prompt}

Please provide a comprehensive and well-structured response."""
        return prompt
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion with intelligent Claude model selection."""
        if not self.available:
            raise Exception("Anthropic API key not configured")
        
        # Select appropriate model
        if model and model in self.model_hierarchy:
            selected_model = model
        elif self.use_smart_routing:
            selected_model = self._analyze_task_requirements(prompt)
        else:
            selected_model = self.default_model
        
        model_config = self.model_hierarchy[selected_model]
        
        # Estimate cost
        prompt_tokens = len(prompt) / 3  # Claude's tokenization estimate
        estimated_cost = (prompt_tokens / 1000) * model_config['cost_per_1k_input']
        
        # Check cost limit and downgrade if needed
        if estimated_cost > self.max_cost_per_query:
            if selected_model == 'claude-3-opus':
                selected_model = 'claude-3-sonnet'
            elif selected_model == 'claude-3-sonnet':
                selected_model = 'claude-3-haiku'
            model_config = self.model_hierarchy[selected_model]
        
        # Build optimized prompt
        optimized_prompt = self._build_claude_prompt(
            prompt, 
            use_expertise=(selected_model == 'claude-3-opus')
        )
        
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=model_config['name'],
                max_tokens=max_tokens or 4000,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": optimized_prompt}
                ],
                **kwargs
            )
            
            # Extract content
            content = response.content[0].text if response.content else ""
            
            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_cost = (
                (input_tokens / 1000) * model_config['cost_per_1k_input'] +
                (output_tokens / 1000) * model_config['cost_per_1k_output']
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=content,
                model=model_config['name'],
                provider="Anthropic",
                tokens_used=input_tokens + output_tokens,
                latency_ms=latency_ms,
                cost=total_cost,
                metadata={
                    'model_capability': model_config['capability'],
                    'selected_for': self._analyze_task_requirements(prompt),
                    'stop_reason': response.stop_reason
                }
            )
            
        except anthropic.RateLimitError:
            # Try with a cheaper model
            if selected_model != 'claude-3-haiku':
                print(f"Rate limited on {selected_model}, trying cheaper model")
                return await self.complete(
                    prompt, 
                    model='claude-3-haiku',
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            raise Exception("Rate limited - use local model")
        except Exception as e:
            raise e
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Complete with message history."""
        if not self.available:
            raise Exception("Anthropic API key not configured")
        
        # Analyze conversation complexity
        full_context = " ".join([m['content'] for m in messages])
        selected_model = self._analyze_task_requirements(full_context) if not model else model
        model_config = self.model_hierarchy[selected_model]
        
        start_time = time.time()
        
        response = await self.client.messages.create(
            model=model_config['name'],
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 4000),
            **kwargs
        )
        
        content = response.content[0].text if response.content else ""
        
        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_cost = (
            (input_tokens / 1000) * model_config['cost_per_1k_input'] +
            (output_tokens / 1000) * model_config['cost_per_1k_output']
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return ProviderResponse(
            content=content,
            model=model_config['name'],
            provider="Anthropic",
            tokens_used=input_tokens + output_tokens,
            latency_ms=latency_ms,
            cost=total_cost,
            metadata={
                'model_capability': model_config['capability']
            }
        )
    
    def list_models(self) -> List[str]:
        """List available Claude models."""
        return [config['name'] for config in self.model_hierarchy.values()]
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost for a query."""
        for model_key, config in self.model_hierarchy.items():
            if config['name'] == model or model_key == model:
                return (
                    (prompt_tokens / 1000) * config['cost_per_1k_input'] +
                    (completion_tokens / 1000) * config['cost_per_1k_output']
                )
        # Default to Sonnet pricing
        config = self.model_hierarchy['claude-3-sonnet']
        return (
            (prompt_tokens / 1000) * config['cost_per_1k_input'] +
            (completion_tokens / 1000) * config['cost_per_1k_output']
        )
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return self.available and self.api_key is not None
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        for model_key, config in self.model_hierarchy.items():
            if model_key == model or config['name'] == model:
                return config
        return {}


# Provider registration
PROVIDER_NAME = "claude_opus"
PROVIDER_CLASS = ClaudeOpusProvider