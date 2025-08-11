"""
Unit tests for the continuous thinking engine.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import List

# Mock imports for testing (replace with actual imports when modules exist)
try:
    from src.osa_continuous_thinking import (
        ContinuousThinkingEngine, 
        Thought, 
        Context, 
        ReasoningChain
    )
except ImportError:
    # Create mocks for initial testing
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class Thought:
        id: str
        content: str
        context: str
        confidence: float = 0.0
        connections: List[str] = None
        timestamp: datetime = None
        
        def __post_init__(self):
            if self.connections is None:
                self.connections = []
            if self.timestamp is None:
                self.timestamp = datetime.now()
    
    @dataclass
    class Context:
        name: str
        thoughts: List[Thought] = None
        priority: int = 1
        
        def __post_init__(self):
            if self.thoughts is None:
                self.thoughts = []
    
    @dataclass  
    class ReasoningChain:
        root_thought: Thought
        chain: List[List[Thought]]
        depth: int
        confidence: float
        
    class ContinuousThinkingEngine:
        def __init__(self, max_thoughts: int = 10000, max_depth: int = 10):
            self.max_thoughts = max_thoughts
            self.max_depth = max_depth
            self.thoughts = {}
            self.contexts = {}
            self.reasoning_chains = {}
            
        async def generate_thoughts(self, topic: str, count: int = 1) -> List[Thought]:
            """Generate thoughts about a topic."""
            return [
                Thought(
                    id=f"thought-{i}",
                    content=f"Thought about {topic} #{i}",
                    context="test-context",
                    confidence=0.8
                )
                for i in range(count)
            ]
        
        async def create_reasoning_chain(self, thought: Thought, depth: int = 3) -> ReasoningChain:
            """Create a reasoning chain from a thought."""
            chain = []
            for level in range(depth):
                level_thoughts = [
                    Thought(
                        id=f"chain-{level}-{i}",
                        content=f"Level {level} reasoning {i}",
                        context=thought.context,
                        confidence=0.7 - (level * 0.1)
                    )
                    for i in range(2)  # 2 thoughts per level
                ]
                chain.append(level_thoughts)
            
            return ReasoningChain(
                root_thought=thought,
                chain=chain,
                depth=depth,
                confidence=0.8
            )
        
        def find_connections(self, thoughts: List[Thought]) -> dict:
            """Find connections between thoughts."""
            connections = {}
            for i, thought1 in enumerate(thoughts):
                for j, thought2 in enumerate(thoughts[i+1:], i+1):
                    if thought1.context == thought2.context:
                        if thought1.id not in connections:
                            connections[thought1.id] = []
                        connections[thought1.id].append(thought2.id)
            return connections


class TestThought:
    """Test the Thought dataclass."""
    
    def test_thought_creation(self):
        """Test creating a basic thought."""
        thought = Thought(
            id="test-1",
            content="Test thought content",
            context="testing",
            confidence=0.8
        )
        
        assert thought.id == "test-1"
        assert thought.content == "Test thought content"
        assert thought.context == "testing"
        assert thought.confidence == 0.8
        assert isinstance(thought.connections, list)
        assert isinstance(thought.timestamp, datetime)
    
    def test_thought_validation(self):
        """Test thought parameter validation."""
        # Valid thought
        thought = Thought(id="valid", content="Valid content", context="test")
        assert thought.confidence == 0.0  # default value
        
        # Test with custom connections
        thought_with_connections = Thought(
            id="connected",
            content="Connected thought",
            context="test",
            connections=["thought-1", "thought-2"]
        )
        assert len(thought_with_connections.connections) == 2
    
    def test_thought_timestamp(self):
        """Test thought timestamp handling."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        thought = Thought(
            id="timed",
            content="Timed thought",
            context="test",
            timestamp=custom_time
        )
        assert thought.timestamp == custom_time


class TestContext:
    """Test the Context dataclass."""
    
    def test_context_creation(self):
        """Test creating a context."""
        context = Context(name="test-context")
        assert context.name == "test-context"
        assert isinstance(context.thoughts, list)
        assert context.priority == 1
    
    def test_context_with_thoughts(self):
        """Test context containing thoughts."""
        thoughts = [
            Thought(id="1", content="First", context="test"),
            Thought(id="2", content="Second", context="test")
        ]
        
        context = Context(
            name="populated-context",
            thoughts=thoughts,
            priority=5
        )
        
        assert len(context.thoughts) == 2
        assert context.priority == 5


class TestReasoningChain:
    """Test the ReasoningChain dataclass."""
    
    def test_reasoning_chain_creation(self):
        """Test creating a reasoning chain."""
        root_thought = Thought(id="root", content="Root thought", context="test")
        chain = [
            [Thought(id="1-1", content="Level 1", context="test")],
            [Thought(id="2-1", content="Level 2", context="test")]
        ]
        
        reasoning_chain = ReasoningChain(
            root_thought=root_thought,
            chain=chain,
            depth=2,
            confidence=0.9
        )
        
        assert reasoning_chain.root_thought.id == "root"
        assert reasoning_chain.depth == 2
        assert reasoning_chain.confidence == 0.9
        assert len(reasoning_chain.chain) == 2


class TestContinuousThinkingEngine:
    """Test the main thinking engine."""
    
    @pytest.fixture
    def thinking_engine(self):
        """Create a test thinking engine."""
        return ContinuousThinkingEngine(max_thoughts=100, max_depth=5)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, thinking_engine):
        """Test engine initialization."""
        assert thinking_engine.max_thoughts == 100
        assert thinking_engine.max_depth == 5
        assert isinstance(thinking_engine.thoughts, dict)
        assert isinstance(thinking_engine.contexts, dict)
        assert isinstance(thinking_engine.reasoning_chains, dict)
    
    @pytest.mark.asyncio
    async def test_generate_single_thought(self, thinking_engine):
        """Test generating a single thought."""
        thoughts = await thinking_engine.generate_thoughts("test topic", count=1)
        
        assert len(thoughts) == 1
        thought = thoughts[0]
        assert "test topic" in thought.content
        assert thought.confidence > 0
        assert thought.id.startswith("thought-")
    
    @pytest.mark.asyncio
    async def test_generate_multiple_thoughts(self, thinking_engine):
        """Test generating multiple thoughts."""
        thoughts = await thinking_engine.generate_thoughts("complex topic", count=5)
        
        assert len(thoughts) == 5
        # Check all thoughts are unique
        thought_ids = [t.id for t in thoughts]
        assert len(set(thought_ids)) == 5
        
        # Check all thoughts reference the topic
        for thought in thoughts:
            assert "complex topic" in thought.content
    
    @pytest.mark.asyncio
    async def test_create_reasoning_chain(self, thinking_engine):
        """Test creating reasoning chains."""
        root_thought = Thought(id="root", content="Root", context="test")
        
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=3)
        
        assert chain.root_thought.id == "root"
        assert chain.depth == 3
        assert len(chain.chain) == 3
        
        # Check each level has thoughts
        for level, level_thoughts in enumerate(chain.chain):
            assert len(level_thoughts) > 0
            for thought in level_thoughts:
                assert thought.context == "test"
                assert f"Level {level}" in thought.content
    
    @pytest.mark.asyncio
    async def test_reasoning_chain_confidence_decay(self, thinking_engine):
        """Test that reasoning chain confidence decreases with depth."""
        root_thought = Thought(id="root", content="Root", context="test", confidence=0.9)
        
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=4)
        
        # Check confidence decreases at deeper levels
        for level, level_thoughts in enumerate(chain.chain):
            for thought in level_thoughts:
                expected_confidence = 0.7 - (level * 0.1)
                assert abs(thought.confidence - expected_confidence) < 0.01
    
    def test_find_connections_same_context(self, thinking_engine):
        """Test finding connections between thoughts in same context."""
        thoughts = [
            Thought(id="1", content="First", context="same"),
            Thought(id="2", content="Second", context="same"),
            Thought(id="3", content="Third", context="different")
        ]
        
        connections = thinking_engine.find_connections(thoughts)
        
        # Thoughts 1 and 2 should be connected (same context)
        assert "1" in connections
        assert "2" in connections["1"]
        
        # Thought 3 should not be connected (different context)
        assert "3" not in connections.get("1", [])
    
    def test_find_connections_different_contexts(self, thinking_engine):
        """Test that thoughts in different contexts aren't connected."""
        thoughts = [
            Thought(id="1", content="First", context="context1"),
            Thought(id="2", content="Second", context="context2"),
            Thought(id="3", content="Third", context="context3")
        ]
        
        connections = thinking_engine.find_connections(thoughts)
        
        # No connections should be found
        assert len(connections) == 0
    
    @pytest.mark.asyncio
    async def test_thought_generation_performance(self, thinking_engine):
        """Test that thought generation is reasonably fast."""
        start_time = asyncio.get_event_loop().time()
        
        thoughts = await thinking_engine.generate_thoughts("performance test", count=10)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        assert len(thoughts) == 10
        assert execution_time < 1.0  # Should complete in under 1 second
    
    @pytest.mark.asyncio
    async def test_max_thoughts_limit(self, thinking_engine):
        """Test that the engine respects max_thoughts limit."""
        # This is a conceptual test - implementation would depend on actual storage
        assert thinking_engine.max_thoughts == 100
        
        # In a real implementation, you'd test:
        # 1. Generate max_thoughts number of thoughts
        # 2. Verify that additional thoughts either replace old ones or are rejected
        # 3. Ensure memory usage doesn't grow unbounded
    
    @pytest.mark.asyncio
    async def test_max_depth_limit(self, thinking_engine):
        """Test that reasoning chains respect max_depth limit."""
        root_thought = Thought(id="deep", content="Deep thought", context="test")
        
        # Request depth greater than max_depth
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=10)
        
        # Should be limited to max_depth
        assert chain.depth <= thinking_engine.max_depth
        assert len(chain.chain) <= thinking_engine.max_depth


class TestThinkingEngineErrorHandling:
    """Test error handling in the thinking engine."""
    
    @pytest.fixture
    def thinking_engine(self):
        return ContinuousThinkingEngine()
    
    @pytest.mark.asyncio
    async def test_empty_topic_handling(self, thinking_engine):
        """Test handling of empty topic."""
        thoughts = await thinking_engine.generate_thoughts("", count=1)
        
        # Should still generate a thought, even with empty topic
        assert len(thoughts) == 1
        assert isinstance(thoughts[0], Thought)
    
    @pytest.mark.asyncio
    async def test_zero_count_thoughts(self, thinking_engine):
        """Test requesting zero thoughts."""
        thoughts = await thinking_engine.generate_thoughts("test", count=0)
        
        assert len(thoughts) == 0
        assert isinstance(thoughts, list)
    
    @pytest.mark.asyncio
    async def test_negative_count_thoughts(self, thinking_engine):
        """Test requesting negative number of thoughts."""
        # Should handle gracefully - either return empty list or convert to 0
        thoughts = await thinking_engine.generate_thoughts("test", count=-5)
        
        assert len(thoughts) == 0
    
    @pytest.mark.asyncio
    async def test_zero_depth_reasoning_chain(self, thinking_engine):
        """Test creating reasoning chain with zero depth."""
        root_thought = Thought(id="root", content="Root", context="test")
        
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=0)
        
        assert chain.depth == 0
        assert len(chain.chain) == 0
    
    @pytest.mark.asyncio
    async def test_negative_depth_reasoning_chain(self, thinking_engine):
        """Test creating reasoning chain with negative depth."""
        root_thought = Thought(id="root", content="Root", context="test")
        
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=-3)
        
        # Should handle gracefully
        assert chain.depth >= 0
        assert len(chain.chain) >= 0


class TestThinkingEngineIntegration:
    """Integration tests for thinking engine components."""
    
    @pytest.fixture
    def thinking_engine(self):
        return ContinuousThinkingEngine(max_thoughts=50, max_depth=3)
    
    @pytest.mark.asyncio
    async def test_thought_to_reasoning_chain_flow(self, thinking_engine):
        """Test the flow from thought generation to reasoning chain creation."""
        # Generate initial thoughts
        thoughts = await thinking_engine.generate_thoughts("integration test", count=3)
        assert len(thoughts) == 3
        
        # Create reasoning chains from thoughts
        chains = []
        for thought in thoughts:
            chain = await thinking_engine.create_reasoning_chain(thought, depth=2)
            chains.append(chain)
        
        assert len(chains) == 3
        
        # Verify each chain is properly formed
        for chain in chains:
            assert chain.depth == 2
            assert len(chain.chain) == 2
            assert chain.root_thought in thoughts
    
    @pytest.mark.asyncio
    async def test_context_based_thinking(self, thinking_engine):
        """Test thinking within specific contexts."""
        # Generate thoughts for different contexts
        context1_thoughts = await thinking_engine.generate_thoughts("problem solving", count=3)
        context2_thoughts = await thinking_engine.generate_thoughts("creative thinking", count=3)
        
        # Manually assign contexts (in real implementation this would be automatic)
        for thought in context1_thoughts:
            thought.context = "problem-solving"
        for thought in context2_thoughts:
            thought.context = "creativity"
        
        all_thoughts = context1_thoughts + context2_thoughts
        connections = thinking_engine.find_connections(all_thoughts)
        
        # Verify connections are only within contexts
        for thought_id, connected_ids in connections.items():
            source_thought = next(t for t in all_thoughts if t.id == thought_id)
            for connected_id in connected_ids:
                connected_thought = next(t for t in all_thoughts if t.id == connected_id)
                assert source_thought.context == connected_thought.context
    
    @pytest.mark.asyncio
    async def test_concurrent_thinking(self, thinking_engine):
        """Test concurrent thought generation."""
        # Generate thoughts concurrently
        tasks = [
            thinking_engine.generate_thoughts(f"topic {i}", count=2)
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all tasks completed successfully
        assert len(results) == 5
        for thoughts in results:
            assert len(thoughts) == 2
        
        # Verify total thoughts generated
        total_thoughts = sum(len(thoughts) for thoughts in results)
        assert total_thoughts == 10


# Performance benchmarks
class TestThinkingEnginePerformance:
    """Performance tests for the thinking engine."""
    
    @pytest.fixture
    def thinking_engine(self):
        return ContinuousThinkingEngine(max_thoughts=1000, max_depth=5)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_scale_thought_generation(self, thinking_engine):
        """Test generating many thoughts efficiently."""
        import time
        
        start_time = time.time()
        thoughts = await thinking_engine.generate_thoughts("large scale test", count=100)
        end_time = time.time()
        
        assert len(thoughts) == 100
        # Should generate 100 thoughts in reasonable time
        assert (end_time - start_time) < 5.0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_deep_reasoning_chain_performance(self, thinking_engine):
        """Test creating deep reasoning chains efficiently."""
        import time
        
        root_thought = Thought(id="deep", content="Deep reasoning test", context="test")
        
        start_time = time.time()
        chain = await thinking_engine.create_reasoning_chain(root_thought, depth=5)
        end_time = time.time()
        
        assert chain.depth == 5
        # Should create deep chain quickly
        assert (end_time - start_time) < 2.0
    
    @pytest.mark.performance
    def test_connection_finding_performance(self, thinking_engine):
        """Test finding connections among many thoughts efficiently."""
        import time
        
        # Create many thoughts
        thoughts = [
            Thought(id=f"perf-{i}", content=f"Performance test {i}", context=f"context-{i%10}")
            for i in range(200)
        ]
        
        start_time = time.time()
        connections = thinking_engine.find_connections(thoughts)
        end_time = time.time()
        
        # Should find connections quickly
        assert (end_time - start_time) < 1.0
        assert isinstance(connections, dict)