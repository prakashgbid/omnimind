"""
Provider Manager

Manages multiple LLM providers and coordinates between them.
"""

from typing import Dict, List, Optional, Any
from .base import BaseProvider


class ProviderManager:
    """
    Manages multiple LLM providers.
    
    This class:
    - Registers and manages providers
    - Routes requests to appropriate providers
    - Handles failover between providers
    - Tracks usage and costs
    """
    
    def __init__(self):
        """Initialize the provider manager."""
        self.providers: Dict[str, BaseProvider] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self.default_provider: Optional[str] = None
    
    def add_provider(self, name: str, provider: BaseProvider) -> None:
        """
        Add a provider to the manager.
        
        Args:
            name: Unique name for the provider
            provider: Provider instance
        """
        if provider.validate_config():
            self.providers[name] = provider
            self.usage_stats[name] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0,
                'errors': 0
            }
            
            # Set first provider as default
            if not self.default_provider:
                self.default_provider = name
    
    def remove_provider(self, name: str) -> None:
        """Remove a provider."""
        if name in self.providers:
            del self.providers[name]
            
            # Update default if needed
            if self.default_provider == name:
                self.default_provider = list(self.providers.keys())[0] if self.providers else None
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get a specific provider by name."""
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all available provider names."""
        return list(self.providers.keys())
    
    def get_local_providers(self) -> List[str]:
        """Get list of local providers."""
        return [
            name for name, provider in self.providers.items()
            if provider.is_local
        ]
    
    def get_cloud_providers(self) -> List[str]:
        """Get list of cloud providers."""
        return [
            name for name, provider in self.providers.items()
            if not provider.is_local
        ]
    
    def set_default_provider(self, name: str) -> None:
        """Set the default provider."""
        if name in self.providers:
            self.default_provider = name
        else:
            raise ValueError(f"Provider {name} not found")
    
    def get_default_provider(self) -> Optional[BaseProvider]:
        """Get the default provider."""
        if self.default_provider:
            return self.providers.get(self.default_provider)
        return None
    
    def update_stats(self, provider_name: str, tokens: int = 0, 
                    cost: float = 0.0, error: bool = False) -> None:
        """
        Update usage statistics for a provider.
        
        Args:
            provider_name: Name of the provider
            tokens: Tokens used in request
            cost: Cost of request
            error: Whether request had an error
        """
        if provider_name in self.usage_stats:
            stats = self.usage_stats[provider_name]
            stats['requests'] += 1
            stats['tokens'] += tokens
            stats['cost'] += cost
            if error:
                stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all providers."""
        return self.usage_stats
    
    def get_provider_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a provider."""
        provider = self.providers.get(name)
        if provider:
            info = provider.get_info()
            info['stats'] = self.usage_stats.get(name, {})
            return info
        return None
    
    def select_providers_for_consensus(self, count: int = 3, 
                                      prefer_cloud: bool = False) -> List[str]:
        """
        Select providers for consensus building.
        
        Args:
            count: Number of providers to select
            prefer_cloud: Whether to prefer cloud providers
        
        Returns:
            List of provider names
        """
        available = self.list_providers()
        
        if prefer_cloud:
            # Prioritize cloud providers
            cloud = self.get_cloud_providers()
            local = self.get_local_providers()
            providers = cloud + local
        else:
            # Mix cloud and local
            providers = available
        
        return providers[:count]
    
    def estimate_consensus_cost(self, providers: List[str], 
                               prompt_tokens: int, 
                               completion_tokens: int) -> float:
        """
        Estimate the cost of a consensus query.
        
        Args:
            providers: List of provider names
            prompt_tokens: Estimated input tokens
            completion_tokens: Estimated output tokens
        
        Returns:
            Total estimated cost in USD
        """
        total_cost = 0.0
        
        for provider_name in providers:
            provider = self.providers.get(provider_name)
            if provider:
                # Use first available model for estimation
                models = provider.list_models()
                if models:
                    cost = provider.estimate_cost(
                        prompt_tokens, 
                        completion_tokens, 
                        models[0]
                    )
                    total_cost += cost
        
        return total_cost