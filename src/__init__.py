"""
OmniMind - Your Persistent Intelligence System

A local, persistent AI system with perfect memory and multi-model consensus.
"""

from .core.omnimind import OmniMind
from .cli import OmniMindCLI
from .web_ui import OmniMindWebUI

__version__ = "1.0.0"
__author__ = "OmniMind Contributors"
__all__ = ["OmniMind", "OmniMindCLI", "OmniMindWebUI"]