"""
Performance tests for OSA thinking engine and related components.
"""

import pytest
import asyncio
import time
import psutil
import gc
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock

# Performance testing utilities
def measure_time():
    """Decorator to measure execution time."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            return result, end - start
        return wrapper
    return decorator

def measure_memory():
    """Context manager to measure memory usage."""
    class MemoryMeasurer:
        def __enter__(self):
            gc.collect()
            self.process = psutil.Process()
            self.initial_memory = self.process.memory_info().rss
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            gc.collect()
            self.final_memory = self.process.memory_info().rss
            self.memory_used = self.final_memory - self.initial_memory
    
    return MemoryMeasurer()

# Mock thinking engine for performance testing
class MockThinkingEngine:
    """Mock thinking engine optimized for performance testing."""
    
    def __init__(self, max_thoughts: int = 10000):
        self.max_thoughts = max_thoughts
        self.thoughts = {}
        self.reasoning_chains = {}
        
    async def generate_thoughts(self, topic: str, count: int) -> List[Dict]:
        """Generate thoughts with controlled performance characteristics."""
        thoughts = []
        
        # Simulate realistic processing time
        base_time = 0.001  # 1ms per thought
        await asyncio.sleep(base_time * count)
        
        for i in range(count):
            thought = {
                "id": f"perf-thought-{i}",
                "content": f"Performance thought {i} about {topic}",
                "confidence": 0.8 - (i * 0.01),  # Decreasing confidence
                "timestamp": time.time()
            }
            thoughts.append(thought)
            
        return thoughts
    
    async def create_reasoning_chain(self, thought: Dict, depth: int) -> Dict:
        """Create reasoning chain with performance characteristics."""
        # Processing time increases with depth
        processing_time = 0.01 * depth  # 10ms per level
        await asyncio.sleep(processing_time)
        
        chain = []
        for level in range(depth):
            level_thoughts = []
            for i in range(2):  # 2 thoughts per level
                level_thought = {
                    "id": f"chain-{level}-{i}",
                    "content": f"Level {level} reasoning {i}",
                    "confidence": 0.9 - (level * 0.1)
                }
                level_thoughts.append(level_thought)
            chain.append(level_thoughts)
        
        return {
            "root_thought": thought,
            "chain": chain,
            "depth": depth,
            "confidence": 0.8
        }
    
    def find_connections(self, thoughts: List[Dict]) -> Dict[str, List[str]]:
        """Find connections with O(n²) complexity for testing."""
        connections = {}
        
        # Simulate realistic connection finding
        for i, thought1 in enumerate(thoughts):
            for j, thought2 in enumerate(thoughts[i+1:], i+1):
                # Simple similarity based on content length
                if abs(len(thought1["content"]) - len(thought2["content"])) < 10:
                    if thought1["id"] not in connections:
                        connections[thought1["id"]] = []
                    connections[thought1["id"]].append(thought2["id"])
        
        return connections


class TestThinkingEnginePerformance:
    """Performance tests for the thinking engine."""
    
    @pytest.fixture
    def thinking_engine(self):
        return MockThinkingEngine(max_thoughts=5000)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_thought_generation_speed(self, thinking_engine):
        """Test speed of generating a single thought."""
        topic = "performance testing"
        
        start_time = time.perf_counter()
        thoughts = await thinking_engine.generate_thoughts(topic, 1)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        assert len(thoughts) == 1
        assert execution_time < 0.01  # Should complete in under 10ms
        
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bulk_thought_generation_speed(self, thinking_engine):
        """Test speed of generating many thoughts."""
        topic = "bulk performance test"
        thought_count = 100
        
        start_time = time.perf_counter()
        thoughts = await thinking_engine.generate_thoughts(topic, thought_count)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        thoughts_per_second = thought_count / execution_time
        
        assert len(thoughts) == thought_count
        assert thoughts_per_second > 50  # Should generate at least 50 thoughts/second
        assert execution_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.performance 
    @pytest.mark.asyncio
    async def test_thought_generation_scaling(self, thinking_engine):
        """Test how thought generation scales with count."""
        topic = "scaling test"
        counts = [10, 50, 100, 500]
        times = []
        
        for count in counts:
            start_time = time.perf_counter()
            thoughts = await thinking_engine.generate_thoughts(topic, count)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            
            assert len(thoughts) == count
        
        # Execution time should scale roughly linearly
        # (allowing for some variation due to overhead)
        time_ratios = [times[i+1] / times[i] for i in range(len(times)-1)]
        count_ratios = [counts[i+1] / counts[i] for i in range(len(counts)-1)]
        
        for time_ratio, count_ratio in zip(time_ratios, count_ratios):
            # Time ratio should be close to count ratio (within 2x tolerance)
            assert time_ratio < count_ratio * 2
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_reasoning_chain_performance(self, thinking_engine):
        """Test performance of reasoning chain creation."""
        thought = {
            "id": "root-thought",
            "content": "Root thought for performance testing"
        }
        
        depths = [1, 3, 5, 7, 10]
        times = []
        
        for depth in depths:
            start_time = time.perf_counter()
            chain = await thinking_engine.create_reasoning_chain(thought, depth)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            
            assert chain["depth"] == depth
            assert len(chain["chain"]) == depth
        
        # Deeper chains should take proportionally longer
        for i in range(1, len(times)):
            assert times[i] >= times[i-1]  # Should be monotonically increasing
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_thought_generation(self, thinking_engine):
        """Test performance of concurrent thought generation."""
        topic = "concurrent test"
        concurrent_tasks = 10
        thoughts_per_task = 20
        
        async def generate_task():
            return await thinking_engine.generate_thoughts(topic, thoughts_per_task)
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*[generate_task() for _ in range(concurrent_tasks)])
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        total_thoughts = sum(len(thoughts) for thoughts in results)
        thoughts_per_second = total_thoughts / execution_time
        
        assert total_thoughts == concurrent_tasks * thoughts_per_task
        assert thoughts_per_second > 100  # Should handle concurrent load efficiently
        
        # Concurrent execution should be faster than sequential
        sequential_estimate = concurrent_tasks * thoughts_per_task * 0.001  # 1ms per thought
        assert execution_time < sequential_estimate * 2  # At most 2x sequential time
    
    @pytest.mark.performance
    def test_connection_finding_performance(self, thinking_engine):
        """Test performance of finding connections between thoughts."""
        # Create test thoughts
        thought_counts = [10, 50, 100, 200]
        times = []
        
        for count in thought_counts:
            thoughts = [
                {
                    "id": f"thought-{i}",
                    "content": f"Test thought {i} with varying length {'x' * (i % 20)}"
                }
                for i in range(count)
            ]
            
            start_time = time.perf_counter()
            connections = thinking_engine.find_connections(thoughts)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            
            assert isinstance(connections, dict)
        
        # Connection finding has O(n²) complexity, so time should scale quadratically
        for i in range(1, len(times)):
            count_ratio = thought_counts[i] / thought_counts[i-1]
            time_ratio = times[i] / times[i-1]
            
            # Allow some tolerance for measurement variation
            assert time_ratio < count_ratio ** 2 * 2


class TestMemoryPerformance:
    """Test memory usage and performance."""
    
    @pytest.fixture
    def thinking_engine(self):
        return MockThinkingEngine()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_during_thought_generation(self, thinking_engine):
        """Test memory usage during thought generation."""
        with measure_memory() as mem:
            thoughts = await thinking_engine.generate_thoughts("memory test", 1000)
        
        # Memory usage should be reasonable (less than 50MB for 1000 thoughts)
        memory_used_mb = mem.memory_used / (1024 * 1024)
        assert memory_used_mb < 50
        
        # Verify thoughts were created
        assert len(thoughts) == 1000
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_operations(self, thinking_engine):
        """Test that memory is cleaned up after operations."""
        initial_memory = psutil.Process().memory_info().rss
        
        # Perform many operations
        for i in range(20):
            thoughts = await thinking_engine.generate_thoughts(f"cleanup test {i}", 50)
            del thoughts  # Explicitly delete
            
            if i % 5 == 0:
                gc.collect()  # Force garbage collection
        
        gc.collect()
        final_memory = psutil.Process().memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal (less than 20MB)
        memory_growth_mb = memory_growth / (1024 * 1024)
        assert memory_growth_mb < 20
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_scaling(self, thinking_engine):
        """Test how memory usage scales with problem size."""
        thought_counts = [100, 500, 1000]
        memory_usage = []
        
        for count in thought_counts:
            gc.collect()
            initial_memory = psutil.Process().memory_info().rss
            
            thoughts = await thinking_engine.generate_thoughts("scaling test", count)
            
            current_memory = psutil.Process().memory_info().rss
            memory_used = current_memory - initial_memory
            memory_usage.append(memory_used)
            
            # Clean up
            del thoughts
            gc.collect()
        
        # Memory usage should scale roughly linearly
        for i in range(1, len(memory_usage)):
            count_ratio = thought_counts[i] / thought_counts[i-1] 
            memory_ratio = memory_usage[i] / memory_usage[i-1]
            
            # Memory should scale roughly linearly (within 3x tolerance)
            assert memory_ratio < count_ratio * 3
    
    @pytest.mark.performance
    @pytest.mark.asyncio 
    async def test_large_dataset_memory_efficiency(self, thinking_engine):
        """Test memory efficiency with large datasets."""
        large_count = 5000
        
        with measure_memory() as mem:
            thoughts = await thinking_engine.generate_thoughts("large dataset", large_count)
            
            # Perform operations on the large dataset
            connections = thinking_engine.find_connections(thoughts[:100])  # Sample for performance
            
            # Create reasoning chains
            chains = []
            for i in range(0, min(10, len(thoughts))):
                chain = await thinking_engine.create_reasoning_chain(thoughts[i], 3)
                chains.append(chain)
        
        memory_used_mb = mem.memory_used / (1024 * 1024)
        
        # Should handle large dataset efficiently (less than 200MB)
        assert memory_used_mb < 200
        assert len(thoughts) == large_count
        assert len(chains) > 0


class TestConcurrencyPerformance:
    """Test performance under concurrent load."""
    
    @pytest.fixture
    def thinking_engine(self):
        return MockThinkingEngine()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_concurrency_thought_generation(self, thinking_engine):
        """Test performance under high concurrency."""
        concurrent_count = 50
        thoughts_per_task = 10
        
        async def concurrent_task(task_id):
            return await thinking_engine.generate_thoughts(f"concurrent-{task_id}", thoughts_per_task)
        
        start_time = time.perf_counter()
        
        # Run many concurrent tasks
        tasks = [concurrent_task(i) for i in range(concurrent_count)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        total_thoughts = sum(len(thoughts) for thoughts in results)
        throughput = total_thoughts / execution_time
        
        assert total_thoughts == concurrent_count * thoughts_per_task
        assert throughput > 200  # Should handle high throughput
        assert execution_time < 10.0  # Should complete within reasonable time
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_reasoning_chains(self, thinking_engine):
        """Test concurrent reasoning chain creation."""
        concurrent_count = 20
        
        # Create base thoughts
        base_thoughts = await thinking_engine.generate_thoughts("base", concurrent_count)
        
        async def create_chain_task(thought):
            return await thinking_engine.create_reasoning_chain(thought, 4)
        
        start_time = time.perf_counter()
        
        # Create reasoning chains concurrently
        chain_tasks = [create_chain_task(thought) for thought in base_thoughts]
        chains = await asyncio.gather(*chain_tasks)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        assert len(chains) == concurrent_count
        assert execution_time < 5.0  # Should handle concurrent chain creation efficiently
        
        # All chains should be properly formed
        for chain in chains:
            assert chain["depth"] == 4
            assert len(chain["chain"]) == 4
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(self, thinking_engine):
        """Test performance of mixed concurrent operations."""
        async def thought_generation_task():
            return await thinking_engine.generate_thoughts("mixed-1", 30)
        
        async def reasoning_chain_task():
            thought = {"id": "mixed", "content": "Mixed operation thought"}
            return await thinking_engine.create_reasoning_chain(thought, 3)
        
        async def connection_finding_task():
            thoughts = await thinking_engine.generate_thoughts("mixed-2", 20)
            return thinking_engine.find_connections(thoughts)
        
        start_time = time.perf_counter()
        
        # Run mixed operations concurrently
        tasks = []
        for _ in range(5):
            tasks.extend([
                thought_generation_task(),
                reasoning_chain_task(), 
                connection_finding_task()
            ])
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        assert len(results) == 15  # 5 sets of 3 operations
        assert execution_time < 8.0  # Should handle mixed load efficiently


class TestRegressionPerformance:
    """Performance regression tests."""
    
    @pytest.fixture
    def thinking_engine(self):
        return MockThinkingEngine()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline_thought_generation(self, thinking_engine):
        """Establish performance baseline for thought generation."""
        # This test establishes baseline performance metrics
        # In a real CI/CD system, these would be compared against historical data
        
        test_cases = [
            {"count": 10, "max_time": 0.5},
            {"count": 100, "max_time": 2.0}, 
            {"count": 500, "max_time": 8.0},
        ]
        
        for case in test_cases:
            start_time = time.perf_counter()
            thoughts = await thinking_engine.generate_thoughts("baseline", case["count"])
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            assert len(thoughts) == case["count"]
            assert execution_time < case["max_time"], f"Performance regression detected: {execution_time:.2f}s > {case['max_time']}s for {case['count']} thoughts"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline_reasoning_chains(self, thinking_engine):
        """Establish performance baseline for reasoning chains."""
        thought = {"id": "baseline", "content": "Baseline thought"}
        
        test_cases = [
            {"depth": 3, "max_time": 0.1},
            {"depth": 5, "max_time": 0.2},
            {"depth": 10, "max_time": 0.5},
        ]
        
        for case in test_cases:
            start_time = time.perf_counter()
            chain = await thinking_engine.create_reasoning_chain(thought, case["depth"])
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            assert chain["depth"] == case["depth"]
            assert execution_time < case["max_time"], f"Performance regression detected: {execution_time:.2f}s > {case['max_time']}s for depth {case['depth']}"
    
    @pytest.mark.performance
    def test_performance_baseline_connection_finding(self, thinking_engine):
        """Establish performance baseline for connection finding."""
        test_cases = [
            {"count": 50, "max_time": 0.1},
            {"count": 100, "max_time": 0.5},
            {"count": 200, "max_time": 2.0},
        ]
        
        for case in test_cases:
            thoughts = [
                {"id": f"conn-{i}", "content": f"Connection test {i}"}
                for i in range(case["count"])
            ]
            
            start_time = time.perf_counter()
            connections = thinking_engine.find_connections(thoughts)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            assert isinstance(connections, dict)
            assert execution_time < case["max_time"], f"Performance regression detected: {execution_time:.2f}s > {case['max_time']}s for {case['count']} thoughts"


class TestStressPerformance:
    """Stress tests for performance limits."""
    
    @pytest.fixture
    def thinking_engine(self):
        return MockThinkingEngine(max_thoughts=20000)
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_large_thought_generation(self, thinking_engine):
        """Stress test with large number of thoughts."""
        large_count = 10000
        
        start_time = time.perf_counter()
        
        with measure_memory() as mem:
            thoughts = await thinking_engine.generate_thoughts("stress test", large_count)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        memory_used_mb = mem.memory_used / (1024 * 1024)
        
        assert len(thoughts) == large_count
        assert execution_time < 30.0  # Should complete within 30 seconds
        assert memory_used_mb < 500    # Should use less than 500MB
        
        throughput = large_count / execution_time
        assert throughput > 100  # Should maintain reasonable throughput
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_extreme_concurrency(self, thinking_engine):
        """Stress test with extreme concurrency."""
        concurrent_count = 100
        thoughts_per_task = 50
        
        async def stress_task(task_id):
            return await thinking_engine.generate_thoughts(f"stress-{task_id}", thoughts_per_task)
        
        start_time = time.perf_counter()
        
        # Run extreme concurrent load
        tasks = [stress_task(i) for i in range(concurrent_count)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        total_thoughts = sum(len(thoughts) for thoughts in results)
        throughput = total_thoughts / execution_time
        
        assert total_thoughts == concurrent_count * thoughts_per_task
        assert execution_time < 20.0  # Should handle extreme load
        assert throughput > 500       # Should maintain high throughput
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_deep_reasoning_chains(self, thinking_engine):
        """Stress test with very deep reasoning chains."""
        thought = {"id": "deep-stress", "content": "Deep reasoning stress test"}
        max_depth = 20
        
        start_time = time.perf_counter()
        chain = await thinking_engine.create_reasoning_chain(thought, max_depth)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        assert chain["depth"] == max_depth
        assert len(chain["chain"]) == max_depth
        assert execution_time < 5.0  # Should handle deep chains efficiently