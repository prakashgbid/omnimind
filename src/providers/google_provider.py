"""
Google Provider for Gemini Models

Supports Gemini Pro, Ultra, and future models.
"""

import os
import time
from typing import Dict, List, Optional, Any
import aiohttp
import json

from .base import BaseProvider, ProviderResponse


class GoogleProvider(BaseProvider):
    """
    Provider for Google's Gemini models.
    
    Supports:
    - Gemini Pro
    - Gemini Ultra
    - Future Gemini models
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Google provider."""
        super().__init__(config)
        
        self.api_key = config.get('api_key') or os.getenv('GOOGLE_API_KEY')
        self.base_url = config.get('base_url', 'https://generativelanguage.googleapis.com/v1beta')
        
        self.default_model = config.get('default_model', 'gemini-pro')
        
        # Features
        self.supports_streaming = True
        self.max_tokens = 32000  # Gemini context window
        
        # Pricing (cents per 1K tokens)
        self.pricing = {
            'gemini-pro': {'input': 0.05, 'output': 0.15},
            'gemini-ultra': {'input': 0.2, 'output': 0.6},
            'gemini-1.5-pro': {'input': 0.1, 'output': 0.3}
        }
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion from Google Gemini."""
        messages = [{"role": "user", "parts": [{"text": prompt}]}]
        return await self.complete_with_messages(messages, model, temperature=temperature, max_tokens=max_tokens, **kwargs)
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Get completion using messages format."""
        if not self.api_key:
            raise ValueError("Google API key not configured")
        
        model = model or self.default_model
        
        # Convert to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg['role'] == 'user':
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": msg['content']}]
                })
            elif msg['role'] == 'assistant':
                gemini_messages.append({
                    "role": "model",
                    "parts": [{"text": msg['content']}]
                })
        
        # Prepare request
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        
        data = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": kwargs.get('temperature', 0.7),
                "topK": kwargs.get('top_k', 1),
                "topP": kwargs.get('top_p', 1),
                "maxOutputTokens": kwargs.get('max_tokens', 2048),
                "stopSequences": kwargs.get('stop_sequences', [])
            }
        }
        
        # Track timing
        start_time = time.time()
        
        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if 'error' in result:
                    raise Exception(f"Google API error: {result['error']['message']}")
                
                # Extract response
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Get token counts (if available)
                tokens_used = result.get('usageMetadata', {}).get('totalTokenCount')
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Calculate cost
                cost = None
                if tokens_used and model in self.pricing:
                    prompt_tokens = result.get('usageMetadata', {}).get('promptTokenCount', 0)
                    candidates_tokens = result.get('usageMetadata', {}).get('candidatesTokenCount', 0)
                    cost = self.estimate_cost(prompt_tokens, candidates_tokens, model)
                
                return ProviderResponse(
                    content=content,
                    model=model,
                    provider="Google",
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    cost=cost,
                    metadata={
                        'finish_reason': result['candidates'][0].get('finishReason'),
                        'safety_ratings': result['candidates'][0].get('safetyRatings')
                    }
                )
    
    def list_models(self) -> List[str]:
        """List available Google models."""
        return [
            'gemini-pro',
            'gemini-pro-vision',
            'gemini-ultra',
            'gemini-1.5-pro',
            'gemini-1.5-flash'
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
        """Check if Google is properly configured."""
        return bool(self.api_key)