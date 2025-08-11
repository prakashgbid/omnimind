"""Adapter for using the extracted persistent-ai-memory module."""

import sys
from pathlib import Path

# Add module path (temporary until pip install)
module_path = Path(__file__).parent.parent.parent / "modules" / "persistent-ai-memory" / "src"
sys.path.insert(0, str(module_path))

# Import from the extracted module
from persistent_ai_memory import (
    PersistentMemory,
    Memory,
    MemoryType,
    MemoryPriority,
    get_persistent_memory
)

# Re-export for backward compatibility
__all__ = [
    "PersistentMemory",
    "Memory", 
    "MemoryType",
    "MemoryPriority",
    "get_persistent_memory"
]