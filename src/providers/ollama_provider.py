"""
Ollama Provider for Local LLMs

Supports all models that can run through Ollama.
"""

import time
import subprocess
from typing import Dict, List, Optional, Any
import ollama
import asyncio

from .base import BaseProvider, ProviderResponse


class OllamaProvider(BaseProvider):
    """
    Provider for local LLMs via Ollama.
    
    Supports:
    - Llama 3.2
    - Mixtral
    - DeepSeek Coder
    - Any model Ollama supports
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Ollama provider."""
        super().__init__(config)
        
        self.is_local = True
        self.default_model = config.get('default_model', 'llama3.2:3b')
        
        # Our downloaded models
        self.downloaded_models = [
            'llama3.2:3b',
            'mistral:7b',
            'phi3:mini',
            'deepseek-coder:6.7b',
            'gemma2:2b'
        ]
        
        # Try to connect to Ollama
        try:
            self.client = ollama.Client()
            self.available = True
            self._ensure_ollama_running()
        except:
            self.available = False
    
    def _ensure_ollama_running(self):
        """Ensure Ollama service is running."""
        import subprocess
        try:
            # Check if Ollama is running
            result = subprocess.run(['pgrep', '-x', 'ollama'], capture_output=True)
            if result.returncode != 0:
                # Start Ollama
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)  # Give it time to start
        except:
            pass
    
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """Get completion from local Ollama model."""
        if not self.available:
            raise Exception("Ollama is not running. Start with: ollama serve")
        
        model = model or self.default_model
        
        # Track timing
        start_time = time.time()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens or 2000
                }
            )
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        return ProviderResponse(
            content=response['response'],
            model=model,
            provider="Ollama",
            tokens_used=response.get('eval_count'),
            latency_ms=latency_ms,
            cost=0.0,  # Local models are free!
            metadata={
                'eval_duration': response.get('eval_duration'),
                'load_duration': response.get('load_duration')
            }
        )
    
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """Get completion using messages format."""
        # Convert messages to single prompt for Ollama
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        
        return await self.complete(prompt, model, **kwargs)
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        if not self.available:
            return []
        
        try:
            models = self.client.list()
            available = [m['name'] for m in models.get('models', [])]
            # Prioritize our downloaded models
            result = []
            for model in self.downloaded_models:
                if model in available:
                    result.append(model)
            # Add any other models
            for model in available:
                if model not in result:
                    result.append(model)
            return result
        except:
            # Return our downloaded models as fallback
            return self.downloaded_models
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        model_info = {
            'llama3.2:3b': {'speed': 'fast', 'quality': 'good', 'best_for': 'general'},
            'mistral:7b': {'speed': 'medium', 'quality': 'excellent', 'best_for': 'reasoning'},
            'phi3:mini': {'speed': 'fast', 'quality': 'good', 'best_for': 'efficiency'},
            'deepseek-coder:6.7b': {'speed': 'medium', 'quality': 'excellent', 'best_for': 'code'},
            'gemma2:2b': {'speed': 'very_fast', 'quality': 'good', 'best_for': 'speed'}
        }
        return model_info.get(model, {'speed': 'unknown', 'quality': 'unknown', 'best_for': 'general'})
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Local models are free!"""
        return 0.0
    
    def validate_config(self) -> bool:
        """Check if Ollama is available."""
        return self.available