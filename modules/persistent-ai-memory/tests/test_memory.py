"""Tests for persistent AI memory."""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from persistent_ai_memory import (
    PersistentMemory,
    MemoryType,
    MemoryPriority
)


class TestPersistentMemory:
    """Test persistent memory functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory(self, temp_dir):
        """Create memory instance for testing."""
        config = {"memory_dir": temp_dir}
        return PersistentMemory(config)
    
    def test_store_and_recall(self, memory):
        """Test storing and recalling memories."""
        # Store a memory
        memory_id = memory.store_memory(
            content="Test memory content",
            memory_type=MemoryType.CONTEXT,
            priority=MemoryPriority.HIGH
        )
        
        assert memory_id is not None
        
        # Recall the memory
        memories = memory.recall_memories("test memory", n_results=1)
        
        assert len(memories) > 0
        assert "Test memory content" in memories[0].content
    
    def test_memory_priorities(self, memory):
        """Test memory priority system."""
        # Store memories with different priorities
        memory.store_memory(
            "Critical information",
            MemoryType.VISION,
            MemoryPriority.CRITICAL
        )
        
        memory.store_memory(
            "Low priority info",
            MemoryType.CONTEXT,
            MemoryPriority.LOW
        )
        
        # Get context should prioritize critical
        context = memory.get_context_for_session()
        
        assert len(context["core_vision"]) > 0
        assert "Critical information" in str(context["core_vision"])
    
    def test_skill_tracking(self, memory):
        """Test skill addition and tracking."""
        memory.add_skill(
            name="Python Programming",
            description="Expert Python development",
            code_template="def main(): pass"
        )
        
        context = memory.get_context_for_session()
        skills = context["skills"]
        
        assert len(skills) > 0
        assert any(s["name"] == "Python Programming" for s in skills)
    
    def test_memory_reinforcement(self, memory):
        """Test memory reinforcement."""
        # Store a memory
        memory_id = memory.store_memory(
            "Important pattern",
            MemoryType.LEARNING,
            MemoryPriority.MEDIUM
        )
        
        # Reinforce it
        memory.reinforce_memory(memory_id, score=0.5)
        
        # Should have higher score when recalled
        memories = memory.recall_memories("Important pattern", n_results=1)
        assert memories[0].reinforcement_score > 1.0
    
    def test_memory_compression(self, memory):
        """Test memory compression."""
        # Store similar memories
        memory.store_memory(
            "User prefers Python",
            MemoryType.LEARNING,
            MemoryPriority.MEDIUM
        )
        
        memory.store_memory(
            "User likes Python programming",
            MemoryType.LEARNING,
            MemoryPriority.MEDIUM
        )
        
        # Compress should merge similar ones
        memory.compress_memories()
        
        # Should still find the pattern
        memories = memory.recall_memories("Python preference", n_results=2)
        assert len(memories) > 0
    
    def test_session_checkpoint(self, memory):
        """Test session checkpointing."""
        checkpoint_id = memory.create_session_checkpoint(
            summary="Test session",
            key_decisions=["Decision 1", "Decision 2"]
        )
        
        assert checkpoint_id is not None
        assert len(checkpoint_id) > 0
    
    def test_context_export(self, memory):
        """Test context export."""
        # Store some memories
        memory.store_memory(
            "Core vision test",
            MemoryType.VISION,
            MemoryPriority.CRITICAL
        )
        
        # Export context
        context_str = memory.export_critical_context()
        
        assert "OSA CRITICAL CONTEXT" in context_str
        assert "CORE VISION" in context_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])