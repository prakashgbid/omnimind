"""
OmniMind Providers - Support for Local and Cloud LLMs

This module provides a unified interface for different LLM providers:
- Local: Ollama (Llama, Mixtral, etc.)
- OpenAI: GPT-4, GPT-5 (when available)
- Anthropic: Claude 3, Claude Opus
- Google: Gemini Pro, Ultra
"""

from .base import BaseProvider, ProviderResponse
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .manager import ProviderManager

__all__ = [
    "BaseProvider",
    "ProviderResponse",
    "OllamaProvider",
    "OpenAIProvider", 
    "AnthropicProvider",
    "GoogleProvider",
    "ProviderManager"
]