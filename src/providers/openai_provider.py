"""
OpenAI Provider

Supports GPT-4, GPT-4 Turbo, and future models like GPT-5.
"""

import os
import time
from typing import Dict, List, Optional, Any
import aiohttp
import json

from .base import BaseProvider, ProviderResponse


class OpenAIProvider(BaseProvider):
    """
    Provider for OpenAI models (GPT-4, GPT-5, etc.)
    
    This provider handles:
    - GPT-4 and GPT-4 Turbo
    - GPT-3.5 Turbo
    - Future models (GPT-5 when available)
    - Function calling
    - Streaming responses
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI provider."""
        super().__init__(config)
        
        # Get API key from config or environment
        self.api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.organization = config.get('organization') or os.getenv('OPENAI_ORG_ID')
        
        # Model defaults
        self.default_model = config.get('default_model', 'gpt-4-turbo-preview')
        
        # Features
        self.supports_streaming = True
        self.supports_functions = True
        self.max_tokens = 128000  # GPT-4 Turbo context
        
        # Pricing (cents per 1K tokens) - Update as needed
        self.pricing = {
            'gpt-4': {'input': 3.0, 'output': 6.0},
            'gpt-4-turbo-preview': {'input': 1.0, 'output': 3.0},
            'gpt-3.5-turbo': {'input': 0.05, 'output': 0.15},
            'gpt-5': {'input': 5.0, 'output': 10.0},  # Placeholder for future
        }
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion from OpenAI."""
        # Convert to messages format
        messages = [{"role": "user", "content": prompt}]
        return await self.complete_with_messages(messages, model, temperature=temperature, max_tokens=max_tokens, **kwargs)
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Get completion using chat format."""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        model = model or self.default_model
        
        # Prepare request
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        if self.organization:
            headers['OpenAI-Organization'] = self.organization
        
        data = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 2000),
            'top_p': kwargs.get('top_p', 1.0),
            'frequency_penalty': kwargs.get('frequency_penalty', 0),
            'presence_penalty': kwargs.get('presence_penalty', 0)
        }
        
        # Add function calling if provided
        if 'functions' in kwargs:
            data['functions'] = kwargs['functions']
            data['function_call'] = kwargs.get('function_call', 'auto')
        
        # Track timing
        start_time = time.time()
        
        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                
                if 'error' in result:
                    raise Exception(f"OpenAI API error: {result['error']['message']}")
                
                # Extract response
                content = result['choices'][0]['message']['content']
                tokens_used = result.get('usage', {}).get('total_tokens')
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Calculate cost
                cost = None
                if tokens_used and model in self.pricing:
                    prompt_tokens = result.get('usage', {}).get('prompt_tokens', 0)
                    completion_tokens = result.get('usage', {}).get('completion_tokens', 0)
                    cost = self.estimate_cost(prompt_tokens, completion_tokens, model)
                
                return ProviderResponse(
                    content=content,
                    model=model,
                    provider="OpenAI",
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    cost=cost,
                    metadata={
                        'finish_reason': result['choices'][0].get('finish_reason'),
                        'function_call': result['choices'][0]['message'].get('function_call')
                    }
                )
    
    def list_models(self) -> List[str]:
        """List available OpenAI models."""
        return [
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-4-32k',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
            # Future models
            'gpt-5',  # Placeholder
            'gpt-4.5-turbo'  # Placeholder
        ]
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost in USD."""
        if model not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model]
        input_cost = (prompt_tokens / 1000) * (pricing['input'] / 100)
        output_cost = (completion_tokens / 1000) * (pricing['output'] / 100)
        
        return round(input_cost + output_cost, 4)
    
    def validate_config(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(self.api_key)