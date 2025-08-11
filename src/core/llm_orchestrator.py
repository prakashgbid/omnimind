#!/usr/bin/env python3
"""
OSA Multi-LLM Orchestrator
Intelligently routes queries to the best AI model for the task
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
import openai
import anthropic
from datetime import datetime

# Try importing optional dependencies
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from github import Github
    from github.Copilot import Copilot
except ImportError:
    Github = None
    Copilot = None


class ModelCapability(Enum):
    """Capabilities of different models"""
    REASONING = "reasoning"
    CODING = "coding"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    FAST = "fast"
    LOCAL = "local"
    VISION = "vision"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: str
    capabilities: List[ModelCapability]
    max_tokens: int
    cost_per_1k: float  # in USD
    latency: str  # fast/medium/slow
    requires_api_key: bool


class LLMOrchestrator:
    """Orchestrates multiple LLMs for optimal task completion"""
    
    # Model configurations
    MODELS = {
        "gpt-4": ModelConfig(
            name="gpt-4",
            provider="openai",
            capabilities=[ModelCapability.REASONING, ModelCapability.CODING, ModelCapability.LONG_CONTEXT],
            max_tokens=8192,
            cost_per_1k=0.03,
            latency="slow",
            requires_api_key=True
        ),
        "gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            provider="openai",
            capabilities=[ModelCapability.FAST, ModelCapability.CODING],
            max_tokens=4096,
            cost_per_1k=0.002,
            latency="fast",
            requires_api_key=True
        ),
        "claude-3-opus": ModelConfig(
            name="claude-3-opus",
            provider="anthropic",
            capabilities=[ModelCapability.REASONING, ModelCapability.CODING, ModelCapability.CREATIVE],
            max_tokens=200000,
            cost_per_1k=0.015,
            latency="medium",
            requires_api_key=True
        ),
        "claude-3-sonnet": ModelConfig(
            name="claude-3-sonnet",
            provider="anthropic",
            capabilities=[ModelCapability.FAST, ModelCapability.CODING],
            max_tokens=200000,
            cost_per_1k=0.003,
            latency="fast",
            requires_api_key=True
        ),
        "gemini-pro": ModelConfig(
            name="gemini-pro",
            provider="google",
            capabilities=[ModelCapability.REASONING, ModelCapability.CREATIVE, ModelCapability.VISION],
            max_tokens=32000,
            cost_per_1k=0.001,
            latency="fast",
            requires_api_key=True
        ),
        "llama3.2:3b": ModelConfig(
            name="llama3.2:3b",
            provider="ollama",
            capabilities=[ModelCapability.LOCAL, ModelCapability.FAST],
            max_tokens=8192,
            cost_per_1k=0.0,
            latency="fast",
            requires_api_key=False
        ),
        "codellama": ModelConfig(
            name="codellama",
            provider="ollama",
            capabilities=[ModelCapability.LOCAL, ModelCapability.CODING],
            max_tokens=8192,
            cost_per_1k=0.0,
            latency="medium",
            requires_api_key=False
        )
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the orchestrator"""
        self.config = config or {}
        self.api_keys = self._load_api_keys()
        self.clients = self._initialize_clients()
        self.usage_stats = {}
        self.model_performance = {}
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "github": os.getenv("GITHUB_TOKEN", "")
        }
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize API clients"""
        clients = {}
        
        # OpenAI
        if self.api_keys.get("openai"):
            openai.api_key = self.api_keys["openai"]
            clients["openai"] = openai
        
        # Anthropic
        if self.api_keys.get("anthropic"):
            clients["anthropic"] = anthropic.Anthropic(api_key=self.api_keys["anthropic"])
        
        # Google
        if genai and self.api_keys.get("google"):
            genai.configure(api_key=self.api_keys["google"])
            clients["google"] = genai
        
        return clients
    
    def select_model(self, task: str, requirements: Dict[str, Any]) -> str:
        """Select the best model for a given task"""
        # Extract requirements
        needs_speed = requirements.get("speed", False)
        needs_long_context = requirements.get("long_context", False)
        needs_coding = requirements.get("coding", False)
        needs_reasoning = requirements.get("reasoning", False)
        needs_local = requirements.get("local_only", False)
        max_cost = requirements.get("max_cost", float('inf'))
        
        # Filter models based on requirements
        suitable_models = []
        
        for model_name, model_config in self.MODELS.items():
            # Check if we have necessary API access
            if model_config.requires_api_key:
                if model_config.provider not in self.clients:
                    continue
            
            # Check capabilities
            if needs_local and ModelCapability.LOCAL not in model_config.capabilities:
                continue
            if needs_coding and ModelCapability.CODING not in model_config.capabilities:
                continue
            if needs_reasoning and ModelCapability.REASONING not in model_config.capabilities:
                continue
            if needs_long_context and ModelCapability.LONG_CONTEXT not in model_config.capabilities:
                continue
            
            # Check cost
            if model_config.cost_per_1k > max_cost:
                continue
            
            # Check speed
            if needs_speed and model_config.latency == "slow":
                continue
            
            suitable_models.append(model_name)
        
        # Rank models based on task type
        if not suitable_models:
            # Fallback to local model
            return "llama3.2:3b"
        
        # Simple ranking for now
        if needs_coding and "claude-3-opus" in suitable_models:
            return "claude-3-opus"
        elif needs_reasoning and "gpt-4" in suitable_models:
            return "gpt-4"
        elif needs_speed and "gpt-3.5-turbo" in suitable_models:
            return "gpt-3.5-turbo"
        else:
            return suitable_models[0]
    
    async def query_model(self, model_name: str, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Query a specific model"""
        model_config = self.MODELS.get(model_name)
        if not model_config:
            return "Model not found", {"error": "Model not found"}
        
        metadata = {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "tokens_used": 0,
            "cost": 0.0,
            "latency": 0.0
        }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            if model_config.provider == "openai":
                response = await self._query_openai(model_name, prompt, **kwargs)
            elif model_config.provider == "anthropic":
                response = await self._query_anthropic(model_name, prompt, **kwargs)
            elif model_config.provider == "google":
                response = await self._query_google(model_name, prompt, **kwargs)
            elif model_config.provider == "ollama":
                response = await self._query_ollama(model_name, prompt, **kwargs)
            else:
                response = "Provider not implemented"
            
            metadata["latency"] = asyncio.get_event_loop().time() - start_time
            metadata["success"] = True
            
            # Update usage stats
            self._update_usage_stats(model_name, metadata)
            
            return response, metadata
            
        except Exception as e:
            metadata["error"] = str(e)
            metadata["success"] = False
            return f"Error querying {model_name}: {str(e)}", metadata
    
    async def _query_openai(self, model: str, prompt: str, **kwargs) -> str:
        """Query OpenAI models"""
        client = self.clients.get("openai")
        if not client:
            return "OpenAI client not initialized"
        
        response = await asyncio.to_thread(
            client.ChatCompletion.create,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def _query_anthropic(self, model: str, prompt: str, **kwargs) -> str:
        """Query Anthropic Claude models"""
        client = self.clients.get("anthropic")
        if not client:
            return "Anthropic client not initialized"
        
        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        
        return response.content[0].text
    
    async def _query_google(self, model: str, prompt: str, **kwargs) -> str:
        """Query Google Gemini models"""
        if not genai:
            return "Google Generative AI not installed"
        
        client = self.clients.get("google")
        if not client:
            return "Google client not initialized"
        
        model = genai.GenerativeModel(model)
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        return response.text
    
    async def _query_ollama(self, model: str, prompt: str, **kwargs) -> str:
        """Query local Ollama models"""
        try:
            import ollama
            response = ollama.generate(model=model, prompt=prompt)
            return response.get('response', '')
        except Exception as e:
            return f"Ollama error: {str(e)}"
    
    def _update_usage_stats(self, model: str, metadata: Dict[str, Any]) -> None:
        """Update usage statistics for a model"""
        if model not in self.usage_stats:
            self.usage_stats[model] = {
                "total_queries": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "success_rate": 0.0
            }
        
        stats = self.usage_stats[model]
        stats["total_queries"] += 1
        stats["total_tokens"] += metadata.get("tokens_used", 0)
        stats["total_cost"] += metadata.get("cost", 0.0)
        
        # Update average latency
        prev_avg = stats["avg_latency"]
        new_latency = metadata.get("latency", 0.0)
        stats["avg_latency"] = (prev_avg * (stats["total_queries"] - 1) + new_latency) / stats["total_queries"]
        
        # Update success rate
        if metadata.get("success", False):
            stats["success_rate"] = ((stats["success_rate"] * (stats["total_queries"] - 1)) + 1) / stats["total_queries"]
        else:
            stats["success_rate"] = (stats["success_rate"] * (stats["total_queries"] - 1)) / stats["total_queries"]
    
    async def multi_model_consensus(self, prompt: str, models: List[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Query multiple models and synthesize responses"""
        if not models:
            # Default to a balanced set
            models = ["gpt-3.5-turbo", "claude-3-sonnet", "llama3.2:3b"]
        
        # Filter to available models
        available_models = [m for m in models if m in self.MODELS]
        
        # Query all models in parallel
        tasks = [self.query_model(model, prompt) for model in available_models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        responses = []
        metadata_list = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(f"Error from {available_models[i]}: {str(result)}")
                metadata_list.append({"model": available_models[i], "error": str(result)})
            else:
                response, metadata = result
                responses.append(response)
                metadata_list.append(metadata)
        
        # Synthesize responses (simple voting for now)
        consensus = self._synthesize_responses(responses, metadata_list)
        
        return consensus, metadata_list
    
    def _synthesize_responses(self, responses: List[str], metadata: List[Dict[str, Any]]) -> str:
        """Synthesize multiple model responses into a consensus"""
        # For now, return the response from the most reliable model
        # In the future, implement more sophisticated consensus mechanisms
        
        valid_responses = []
        for i, response in enumerate(responses):
            if not response.startswith("Error") and metadata[i].get("success", False):
                valid_responses.append((response, metadata[i]))
        
        if not valid_responses:
            return "All models failed to provide a response"
        
        # Sort by success rate and latency
        valid_responses.sort(key=lambda x: (
            -self.usage_stats.get(x[1]["model"], {}).get("success_rate", 0),
            x[1].get("latency", float('inf'))
        ))
        
        return valid_responses[0][0]
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        status = {}
        
        for model_name, model_config in self.MODELS.items():
            available = False
            
            if not model_config.requires_api_key:
                available = True
            elif model_config.provider in self.clients:
                available = True
            
            status[model_name] = {
                "available": available,
                "provider": model_config.provider,
                "capabilities": [c.value for c in model_config.capabilities],
                "usage": self.usage_stats.get(model_name, {}),
                "cost_per_1k": model_config.cost_per_1k,
                "max_tokens": model_config.max_tokens
            }
        
        return status
    
    async def optimize_for_task(self, task_type: str, content: str) -> Tuple[str, Dict[str, Any]]:
        """Automatically select and query the best model for a task type"""
        # Define task requirements
        task_requirements = {
            "code_generation": {
                "coding": True,
                "reasoning": True,
                "speed": False
            },
            "debug": {
                "coding": True,
                "reasoning": True,
                "speed": True
            },
            "creative_writing": {
                "creative": True,
                "long_context": True,
                "speed": False
            },
            "quick_answer": {
                "speed": True,
                "reasoning": False
            },
            "complex_reasoning": {
                "reasoning": True,
                "long_context": True,
                "speed": False
            },
            "local_only": {
                "local_only": True,
                "speed": True
            }
        }
        
        requirements = task_requirements.get(task_type, {"speed": True})
        
        # Select best model
        selected_model = self.select_model(task_type, requirements)
        
        # Query the model
        response, metadata = await self.query_model(selected_model, content)
        
        # Add task type to metadata
        metadata["task_type"] = task_type
        metadata["selected_model"] = selected_model
        
        return response, metadata


# Create singleton instance
_orchestrator = None

def get_orchestrator() -> LLMOrchestrator:
    """Get or create the global LLM orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator