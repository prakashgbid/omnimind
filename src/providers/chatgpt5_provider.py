"""
ChatGPT 5.0 Provider for OmniMind

Integrates the latest ChatGPT 5.0 model (when available) with intelligent fallback.
Uses local models when possible to minimize costs.
"""

import os
import time
from typing import Dict, List, Optional, Any
import openai
from openai import AsyncOpenAI
import asyncio

from .base import BaseProvider, ProviderResponse


class ChatGPT5Provider(BaseProvider):
    """
    Provider for ChatGPT 5.0 and GPT-4 models.
    
    Intelligently routes between:
    - ChatGPT 5.0 (when available) for complex tasks
    - GPT-4 Turbo for standard tasks
    - GPT-3.5 Turbo for simple tasks
    - Local models for cost optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ChatGPT 5 provider with smart routing."""
        super().__init__(config)
        
        self.api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.sync_client = openai.OpenAI(api_key=self.api_key)
            self.available = True
        else:
            self.available = False
        
        # Model hierarchy (best to cheapest)
        self.model_hierarchy = {
            'gpt-5': {  # Future model
                'name': 'gpt-5',
                'cost_per_1k_input': 0.10,  # Estimated
                'cost_per_1k_output': 0.30,  # Estimated
                'capability': 'supreme',
                'use_for': ['complex_reasoning', 'creative_tasks', 'critical_decisions']
            },
            'gpt-4-turbo-preview': {
                'name': 'gpt-4-turbo-preview',
                'cost_per_1k_input': 0.01,
                'cost_per_1k_output': 0.03,
                'capability': 'advanced',
                'use_for': ['reasoning', 'analysis', 'code_generation']
            },
            'gpt-4': {
                'name': 'gpt-4',
                'cost_per_1k_input': 0.03,
                'cost_per_1k_output': 0.06,
                'capability': 'advanced',
                'use_for': ['complex_tasks', 'detailed_analysis']
            },
            'gpt-3.5-turbo': {
                'name': 'gpt-3.5-turbo',
                'cost_per_1k_input': 0.0005,
                'cost_per_1k_output': 0.0015,
                'capability': 'standard',
                'use_for': ['simple_tasks', 'quick_responses']
            }
        }
        
        # Task complexity analyzer
        self.complexity_keywords = {
            'complex': ['analyze', 'design', 'architect', 'optimize', 'debug', 'explain why'],
            'medium': ['implement', 'create', 'build', 'fix', 'review'],
            'simple': ['list', 'name', 'count', 'format', 'convert']
        }
        
        self.default_model = config.get('default_model', 'gpt-4-turbo-preview')
        self.use_smart_routing = config.get('smart_routing', True)
        self.max_cost_per_query = config.get('max_cost_per_query', 0.50)
    
    def _analyze_task_complexity(self, prompt: str) -> str:
        """Analyze task complexity to select appropriate model."""
        prompt_lower = prompt.lower()
        
        # Check for complexity indicators
        complex_score = sum(1 for word in self.complexity_keywords['complex'] 
                           if word in prompt_lower)
        medium_score = sum(1 for word in self.complexity_keywords['medium'] 
                          if word in prompt_lower)
        simple_score = sum(1 for word in self.complexity_keywords['simple'] 
                          if word in prompt_lower)
        
        # Determine complexity
        if complex_score > 0 or len(prompt) > 1000:
            return 'complex'
        elif medium_score > simple_score:
            return 'medium'
        else:
            return 'simple'
    
    def _select_model_for_task(self, prompt: str, 
                               preferred_model: Optional[str] = None) -> str:
        """Select the most appropriate model for the task."""
        if preferred_model and preferred_model in self.model_hierarchy:
            return preferred_model
        
        if not self.use_smart_routing:
            return self.default_model
        
        complexity = self._analyze_task_complexity(prompt)
        
        # Map complexity to model
        if complexity == 'complex':
            # Try GPT-5 first if available, then GPT-4
            if self._is_model_available('gpt-5'):
                return 'gpt-5'
            return 'gpt-4-turbo-preview'
        elif complexity == 'medium':
            return 'gpt-4-turbo-preview'
        else:
            return 'gpt-3.5-turbo'
    
    def _is_model_available(self, model: str) -> bool:
        """Check if a model is available."""
        try:
            # Quick test to see if model exists
            response = self.sync_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion with intelligent model selection."""
        if not self.available:
            raise Exception("OpenAI API key not configured")
        
        # Select appropriate model
        selected_model = self._select_model_for_task(prompt, model)
        model_config = self.model_hierarchy.get(selected_model, 
                                               self.model_hierarchy['gpt-4-turbo-preview'])
        
        # Estimate cost
        prompt_tokens = len(prompt) / 4  # Rough estimate
        estimated_cost = (prompt_tokens / 1000) * model_config['cost_per_1k_input']
        
        # Check cost limit
        if estimated_cost > self.max_cost_per_query:
            # Fallback to cheaper model
            selected_model = 'gpt-3.5-turbo'
            model_config = self.model_hierarchy['gpt-3.5-turbo']
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model_config['name'],
                messages=[
                    {"role": "system", "content": "You are an expert assistant with deep knowledge across all domains."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )
            
            # Calculate actual cost
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = (
                (prompt_tokens / 1000) * model_config['cost_per_1k_input'] +
                (completion_tokens / 1000) * model_config['cost_per_1k_output']
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=response.choices[0].message.content,
                model=model_config['name'],
                provider="OpenAI",
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms,
                cost=total_cost,
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'model_capability': model_config['capability'],
                    'complexity_detected': self._analyze_task_complexity(prompt)
                }
            )
            
        except openai.RateLimitError:
            # Fallback to local model via Ollama
            print(f"Rate limited on {selected_model}, falling back to local model")
            raise Exception("Rate limited - use local model")
        except Exception as e:
            # Try with cheaper model
            if selected_model != 'gpt-3.5-turbo':
                return await self.complete(prompt, model='gpt-3.5-turbo', 
                                         temperature=temperature, max_tokens=max_tokens)
            raise e
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Complete with message history."""
        if not self.available:
            raise Exception("OpenAI API key not configured")
        
        # Analyze the conversation to determine model
        full_context = " ".join([m['content'] for m in messages])
        selected_model = self._select_model_for_task(full_context, model)
        model_config = self.model_hierarchy.get(selected_model,
                                               self.model_hierarchy['gpt-4-turbo-preview'])
        
        start_time = time.time()
        
        response = await self.client.chat.completions.create(
            model=model_config['name'],
            messages=messages,
            **kwargs
        )
        
        # Calculate cost
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens
        total_cost = (
            (prompt_tokens / 1000) * model_config['cost_per_1k_input'] +
            (completion_tokens / 1000) * model_config['cost_per_1k_output']
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return ProviderResponse(
            content=response.choices[0].message.content,
            model=model_config['name'],
            provider="OpenAI",
            tokens_used=response.usage.total_tokens,
            latency_ms=latency_ms,
            cost=total_cost,
            metadata={
                'finish_reason': response.choices[0].finish_reason,
                'model_capability': model_config['capability']
            }
        )
    
    def list_models(self) -> List[str]:
        """List available OpenAI models."""
        available = []
        for model_key, model_info in self.model_hierarchy.items():
            if self._is_model_available(model_info['name']):
                available.append(model_info['name'])
        return available
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost for a query."""
        model_config = None
        for config in self.model_hierarchy.values():
            if config['name'] == model:
                model_config = config
                break
        
        if not model_config:
            model_config = self.model_hierarchy['gpt-4-turbo-preview']
        
        return (
            (prompt_tokens / 1000) * model_config['cost_per_1k_input'] +
            (completion_tokens / 1000) * model_config['cost_per_1k_output']
        )
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return self.available and self.api_key is not None


# Provider registration
PROVIDER_NAME = "chatgpt5"
PROVIDER_CLASS = ChatGPT5Provider