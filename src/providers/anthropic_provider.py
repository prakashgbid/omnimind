"""
Anthropic Provider

Supports Claude 3 family (Opus, Sonnet, Haiku) and future models.
"""

import os
import time
from typing import Dict, List, Optional, Any
import aiohttp
import json

from .base import BaseProvider, ProviderResponse


class AnthropicProvider(BaseProvider):
    """
    Provider for Anthropic's Claude models.
    
    Supports:
    - Claude 3 Opus (most capable)
    - Claude 3 Sonnet (balanced)
    - Claude 3 Haiku (fastest)
    - Future Claude models
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Anthropic provider."""
        super().__init__(config)
        
        # Get API key
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = config.get('base_url', 'https://api.anthropic.com/v1')
        
        # Model defaults
        self.default_model = config.get('default_model', 'claude-3-opus-20240229')
        
        # Features
        self.supports_streaming = True
        self.max_tokens = 200000  # Claude's context window
        
        # Pricing (cents per 1K tokens)
        self.pricing = {
            'claude-3-opus-20240229': {'input': 1.5, 'output': 7.5},
            'claude-3-sonnet-20240229': {'input': 0.3, 'output': 1.5},
            'claude-3-haiku-20240307': {'input': 0.025, 'output': 0.125},
            'claude-opus-4-1-20250805': {'input': 2.0, 'output': 10.0},  # Future Opus
        }
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion from Anthropic."""
        messages = [{"role": "user", "content": prompt}]
        return await self.complete_with_messages(messages, model, temperature=temperature, max_tokens=max_tokens, **kwargs)
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Get completion using messages format."""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        model = model or self.default_model
        
        # Prepare headers
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        # Convert messages to Anthropic format
        # Anthropic expects a system message separately
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                anthropic_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Prepare request data
        data = {
            'model': model,
            'messages': anthropic_messages,
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 1.0),
            'top_k': kwargs.get('top_k', None),
            'stop_sequences': kwargs.get('stop_sequences', None)
        }
        
        if system_message:
            data['system'] = system_message
        
        # Track timing
        start_time = time.time()
        
        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                
                if 'error' in result:
                    raise Exception(f"Anthropic API error: {result['error']['message']}")
                
                # Extract response
                content = result['content'][0]['text']
                
                # Get token usage
                input_tokens = result.get('usage', {}).get('input_tokens')
                output_tokens = result.get('usage', {}).get('output_tokens')
                total_tokens = (input_tokens or 0) + (output_tokens or 0)
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Calculate cost
                cost = None
                if input_tokens and output_tokens and model in self.pricing:
                    cost = self.estimate_cost(input_tokens, output_tokens, model)
                
                return ProviderResponse(
                    content=content,
                    model=model,
                    provider="Anthropic",
                    tokens_used=total_tokens,
                    latency_ms=latency_ms,
                    cost=cost,
                    metadata={
                        'stop_reason': result.get('stop_reason'),
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens
                    }
                )
    
    def list_models(self) -> List[str]:
        """List available Anthropic models."""
        return [
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307',
            'claude-2.1',
            'claude-2.0',
            'claude-instant-1.2',
            # Future models
            'claude-opus-4-1-20250805',  # Placeholder for Opus 4.1
            'claude-4-opus',  # Placeholder
            'claude-4-sonnet'  # Placeholder
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
        """Check if Anthropic is properly configured."""
        return bool(self.api_key)