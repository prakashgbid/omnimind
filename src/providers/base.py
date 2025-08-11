"""
Base Provider Interface

Defines the common interface all LLM providers must implement.
This allows seamless switching between local and cloud models.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProviderResponse:
    """Standardized response from any provider."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    Every provider (Ollama, OpenAI, Anthropic, etc.) must implement this interface.
    This ensures OmniMind can work with any LLM seamlessly.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration
                   (API keys, endpoints, model names, etc.)
        """
        self.config = config
        self.name = self.__class__.__name__.replace("Provider", "")
        self.is_local = False  # Override in local providers
        self.supports_streaming = False  # Override if supported
        self.supports_functions = False  # Override if supported
        self.max_tokens = 4096  # Default, override per provider
    
    @abstractmethod
    async def complete(self, 
                      prompt: str, 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> ProviderResponse:
        """
        Get completion from the LLM.
        
        Args:
            prompt: The input prompt
            model: Specific model to use (or use default)
            temperature: Creativity parameter (0-1)
            max_tokens: Maximum response length
            **kwargs: Provider-specific parameters
        
        Returns:
            ProviderResponse with the completion
        """
        pass
    
    @abstractmethod
    async def complete_with_messages(self,
                                    messages: List[Dict[str, str]],
                                    model: Optional[str] = None,
                                    **kwargs) -> ProviderResponse:
        """
        Get completion using chat format.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Specific model to use
            **kwargs: Provider-specific parameters
        
        Returns:
            ProviderResponse with the completion
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models from this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Estimate the cost of a request.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model being used
        
        Returns:
            Estimated cost in USD (0 for local models)
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate that the provider is properly configured.
        
        Returns:
            True if configuration is valid
        """
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dictionary with provider details
        """
        return {
            "name": self.name,
            "is_local": self.is_local,
            "supports_streaming": self.supports_streaming,
            "supports_functions": self.supports_functions,
            "max_tokens": self.max_tokens,
            "models": self.list_models()
        }