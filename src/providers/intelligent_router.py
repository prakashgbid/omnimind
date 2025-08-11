"""
Intelligent Model Router for OmniMind

Automatically routes queries to the best model (local or premium) based on:
- Task complexity and requirements
- Cost optimization
- Response time needs
- Model availability
- User preferences
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

from .base import BaseProvider, ProviderResponse
from .ollama_provider import OllamaProvider
from .chatgpt5_provider import ChatGPT5Provider
from .claude_opus_provider import ClaudeOpusProvider


class IntelligentRouter:
    """
    Smart router that decides between local and premium models.
    
    Strategy:
    1. Use local models for 80% of tasks (free)
    2. Use premium models for critical/complex tasks
    3. Track costs and optimize usage
    4. Learn from user feedback
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the intelligent router."""
        self.config = config or {}
        
        # Initialize providers
        self.providers = {
            'local': None,
            'chatgpt5': None,
            'claude_opus': None
        }
        
        # Cost tracking
        self.monthly_budget = self.config.get('monthly_budget', 10.0)  # $10/month default
        self.current_month_cost = 0.0
        self.cost_history = []
        
        # Routing preferences
        self.prefer_local = self.config.get('prefer_local', True)
        self.local_first_threshold = self.config.get('local_first_threshold', 0.8)  # Use local 80% of time
        
        # Task routing rules
        self.routing_rules = {
            # Tasks that REQUIRE premium models
            'require_premium': [
                'critical decision', 'production code', 'customer facing',
                'legal', 'financial analysis', 'medical', 'safety critical'
            ],
            # Tasks better with premium models
            'prefer_premium': [
                'complex analysis', 'creative writing', 'deep reasoning',
                'philosophical', 'nuanced understanding', 'research paper'
            ],
            # Tasks fine with local models
            'local_capable': [
                'code review', 'bug fix', 'documentation', 'testing',
                'refactoring', 'formatting', 'simple questions', 'explanations'
            ]
        }
        
        # Model capability matrix
        self.model_capabilities = {
            # Local models
            'llama3.2:3b': {
                'cost': 0, 'speed': 'fast', 'quality': 7,
                'good_for': ['general', 'conversation', 'explanations']
            },
            'mistral:7b': {
                'cost': 0, 'speed': 'medium', 'quality': 8,
                'good_for': ['reasoning', 'analysis', 'complex_tasks']
            },
            'deepseek-coder:6.7b': {
                'cost': 0, 'speed': 'medium', 'quality': 9,
                'good_for': ['code', 'programming', 'debugging']
            },
            # Premium models
            'gpt-4-turbo': {
                'cost': 0.03, 'speed': 'medium', 'quality': 9.5,
                'good_for': ['complex_reasoning', 'creative', 'analysis']
            },
            'gpt-5': {
                'cost': 0.10, 'speed': 'slow', 'quality': 10,
                'good_for': ['critical_tasks', 'research', 'innovation']
            },
            'claude-3-opus': {
                'cost': 0.075, 'speed': 'medium', 'quality': 9.8,
                'good_for': ['nuanced_reasoning', 'creative', 'analysis']
            }
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers."""
        # Local provider (always available)
        try:
            self.providers['local'] = OllamaProvider({})
            print("✅ Local models available (FREE)")
        except:
            print("⚠️ Local models not available")
        
        # ChatGPT 5 / GPT-4
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.providers['chatgpt5'] = ChatGPT5Provider({
                    'api_key': os.getenv('OPENAI_API_KEY'),
                    'smart_routing': True
                })
                print("✅ ChatGPT/GPT-4 available")
            except:
                print("⚠️ ChatGPT not configured")
        
        # Claude Opus
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                self.providers['claude_opus'] = ClaudeOpusProvider({
                    'api_key': os.getenv('ANTHROPIC_API_KEY'),
                    'smart_routing': True
                })
                print("✅ Claude Opus available")
            except:
                print("⚠️ Claude not configured")
    
    def analyze_task(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze a task to determine routing.
        
        Returns:
            Dict with routing decision and reasoning
        """
        prompt_lower = prompt.lower()
        analysis = {
            'complexity': 'medium',
            'requires_premium': False,
            'suggested_provider': 'local',
            'suggested_model': 'llama3.2:3b',
            'estimated_cost': 0.0,
            'reasoning': []
        }
        
        # Check if premium is required
        for pattern in self.routing_rules['require_premium']:
            if pattern in prompt_lower:
                analysis['requires_premium'] = True
                analysis['reasoning'].append(f"Contains '{pattern}' - requires premium model")
                break
        
        # Check if premium is preferred
        if not analysis['requires_premium']:
            premium_score = sum(1 for pattern in self.routing_rules['prefer_premium'] 
                              if pattern in prompt_lower)
            if premium_score > 0:
                analysis['complexity'] = 'complex'
                analysis['reasoning'].append(f"Complex task detected (score: {premium_score})")
        
        # Check if local is sufficient
        local_score = sum(1 for pattern in self.routing_rules['local_capable'] 
                         if pattern in prompt_lower)
        if local_score > 0 and not analysis['requires_premium']:
            analysis['complexity'] = 'simple'
            analysis['reasoning'].append(f"Local models capable (score: {local_score})")
        
        # Determine routing based on analysis
        if analysis['requires_premium']:
            # Choose between ChatGPT and Claude
            if 'creative' in prompt_lower or 'nuanced' in prompt_lower:
                analysis['suggested_provider'] = 'claude_opus'
                analysis['suggested_model'] = 'claude-3-opus'
                analysis['estimated_cost'] = 0.075
            else:
                analysis['suggested_provider'] = 'chatgpt5'
                analysis['suggested_model'] = 'gpt-4-turbo'
                analysis['estimated_cost'] = 0.03
        elif analysis['complexity'] == 'complex' and not self.prefer_local:
            # Use premium for complex tasks if not preferring local
            analysis['suggested_provider'] = 'chatgpt5'
            analysis['suggested_model'] = 'gpt-4-turbo'
            analysis['estimated_cost'] = 0.03
        else:
            # Use local models
            if 'code' in prompt_lower or 'function' in prompt_lower:
                analysis['suggested_model'] = 'deepseek-coder:6.7b'
            elif 'reason' in prompt_lower or 'analyze' in prompt_lower:
                analysis['suggested_model'] = 'mistral:7b'
            else:
                analysis['suggested_model'] = 'llama3.2:3b'
        
        # Check budget
        if self.current_month_cost + analysis['estimated_cost'] > self.monthly_budget:
            if not analysis['requires_premium']:
                analysis['suggested_provider'] = 'local'
                analysis['suggested_model'] = 'mistral:7b'
                analysis['estimated_cost'] = 0.0
                analysis['reasoning'].append("Budget limit reached - using local model")
        
        return analysis
    
    async def route_query(self, prompt: str, 
                         force_provider: Optional[str] = None,
                         force_model: Optional[str] = None,
                         require_quality: bool = False) -> ProviderResponse:
        """
        Route a query to the best model.
        
        Args:
            prompt: The query
            force_provider: Force specific provider
            force_model: Force specific model
            require_quality: Require high quality response
        
        Returns:
            Response from selected model
        """
        # Analyze the task
        analysis = self.analyze_task(prompt)
        
        # Override with forced options
        if force_provider:
            provider_name = force_provider
            model_name = force_model or analysis['suggested_model']
        elif require_quality:
            provider_name = 'claude_opus' if self.providers['claude_opus'] else 'chatgpt5'
            model_name = 'claude-3-opus' if provider_name == 'claude_opus' else 'gpt-4-turbo'
        else:
            provider_name = analysis['suggested_provider']
            model_name = analysis['suggested_model']
        
        # Get the provider
        provider = self.providers.get(provider_name)
        
        # Fallback logic
        if not provider or not provider.available:
            # Try fallbacks
            fallback_order = ['local', 'chatgpt5', 'claude_opus']
            for fallback in fallback_order:
                if self.providers[fallback] and self.providers[fallback].available:
                    provider = self.providers[fallback]
                    provider_name = fallback
                    # Select appropriate model for fallback provider
                    if fallback == 'local':
                        model_name = 'mistral:7b'
                    break
        
        if not provider:
            raise Exception("No providers available")
        
        # Execute query
        try:
            response = await provider.complete(prompt, model=model_name)
            
            # Track cost
            if response.cost > 0:
                self.current_month_cost += response.cost
                self.cost_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'cost': response.cost,
                    'model': model_name,
                    'provider': provider_name
                })
            
            # Add routing metadata
            response.metadata['routing'] = {
                'analysis': analysis,
                'selected_provider': provider_name,
                'selected_model': model_name,
                'month_cost': self.current_month_cost,
                'budget_remaining': self.monthly_budget - self.current_month_cost
            }
            
            return response
            
        except Exception as e:
            # Fallback to local if premium fails
            if provider_name != 'local' and self.providers['local']:
                print(f"Premium model failed: {e}, falling back to local")
                return await self.providers['local'].complete(
                    prompt, 
                    model='mistral:7b'
                )
            raise e
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            'current_month_cost': self.current_month_cost,
            'budget_remaining': self.monthly_budget - self.current_month_cost,
            'monthly_budget': self.monthly_budget,
            'prefer_local': self.prefer_local,
            'available_providers': [
                name for name, provider in self.providers.items() 
                if provider and provider.available
            ],
            'cost_history': self.cost_history[-10:],  # Last 10 queries
            'recommendations': self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get cost optimization recommendations."""
        recommendations = []
        
        if self.current_month_cost > self.monthly_budget * 0.8:
            recommendations.append("📊 Approaching budget limit - consider using more local models")
        
        if self.current_month_cost < self.monthly_budget * 0.2:
            recommendations.append("💡 Budget underutilized - can use premium models for better quality")
        
        if not self.providers['local'] or not self.providers['local'].available:
            recommendations.append("⚠️ Local models not available - set up Ollama to reduce costs")
        
        return recommendations
    
    def set_budget(self, monthly_budget: float):
        """Update monthly budget."""
        self.monthly_budget = monthly_budget
    
    def reset_monthly_cost(self):
        """Reset monthly cost tracking."""
        self.current_month_cost = 0.0
        self.cost_history = []


# Global router instance
intelligent_router = IntelligentRouter()


async def smart_complete(prompt: str, 
                         require_quality: bool = False,
                         force_local: bool = False) -> ProviderResponse:
    """
    Smart completion that automatically selects the best model.
    
    Args:
        prompt: The query
        require_quality: Force use of premium model
        force_local: Force use of local model
    
    Returns:
        Response from best available model
    """
    if force_local:
        return await intelligent_router.route_query(prompt, force_provider='local')
    
    return await intelligent_router.route_query(prompt, require_quality=require_quality)


def get_router_stats() -> Dict[str, Any]:
    """Get router statistics and recommendations."""
    return intelligent_router.get_routing_stats()