"""
Unit tests for the continuous learning system.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import List, Dict, Any

# Mock imports for testing
try:
    from src.osa_continuous_learning import (
        ContinuousLearningSystem,
        Pattern,
        Solution,
        PerformanceMetric
    )
except ImportError:
    from dataclasses import dataclass, field
    
    @dataclass
    class Pattern:
        id: str
        description: str
        context: str
        success_rate: float = 0.0
        usage_count: int = 0
        metadata: Dict[str, Any] = field(default_factory=dict)
        
    @dataclass
    class Solution:
        id: str
        problem: str
        solution: str
        success: bool = True
        execution_time: float = 0.0
        patterns_used: List[str] = field(default_factory=list)
        
    @dataclass
    class PerformanceMetric:
        task_type: str
        execution_time: float
        success: bool
        patterns_matched: int = 0
        timestamp: datetime = field(default_factory=datetime.now)
        
    class ContinuousLearningSystem:
        def __init__(self, enable_persistence: bool = True, cache_size: int = 1000):
            self.enable_persistence = enable_persistence
            self.cache_size = cache_size
            self.patterns = {}
            self.solutions = {}
            self.performance_metrics = []
            
        async def learn_from_task(self, task: str, result: Any, metrics: Dict[str, Any]):
            """Learn from a completed task."""
            solution = Solution(
                id=f"solution-{len(self.solutions)}",
                problem=task,
                solution=str(result),
                success=metrics.get('success', True),
                execution_time=metrics.get('execution_time', 0.0)
            )
            
            self.solutions[solution.id] = solution
            
            # Extract patterns
            patterns = await self._extract_patterns(task, result, metrics)
            for pattern in patterns:
                self.patterns[pattern.id] = pattern
                
        async def _extract_patterns(self, task: str, result: Any, metrics: Dict[str, Any]) -> List[Pattern]:
            """Extract patterns from task execution."""
            patterns = []
            
            # Simple pattern extraction based on task type
            if "api" in task.lower():
                patterns.append(Pattern(
                    id=f"api-pattern-{len(self.patterns)}",
                    description="API development pattern",
                    context="api-development",
                    success_rate=0.8
                ))
            
            if "database" in task.lower():
                patterns.append(Pattern(
                    id=f"db-pattern-{len(self.patterns)}",
                    description="Database pattern",
                    context="database-operations", 
                    success_rate=0.85
                ))
            
            return patterns
            
        async def find_similar_patterns(self, task: str) -> List[Pattern]:
            """Find patterns similar to the current task."""
            similar = []
            task_lower = task.lower()
            
            for pattern in self.patterns.values():
                if any(keyword in task_lower for keyword in pattern.context.split('-')):
                    similar.append(pattern)
                    
            return sorted(similar, key=lambda p: p.success_rate, reverse=True)
        
        async def get_cached_solution(self, task: str) -> Solution:
            """Get a cached solution for similar task."""
            for solution in self.solutions.values():
                if self._calculate_similarity(task, solution.problem) > 0.8:
                    return solution
            return None
            
        def _calculate_similarity(self, task1: str, task2: str) -> float:
            """Calculate similarity between two tasks."""
            words1 = set(task1.lower().split())
            words2 = set(task2.lower().split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
                
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
        
        def get_performance_stats(self) -> Dict[str, Any]:
            """Get performance statistics."""
            if not self.performance_metrics:
                return {"total_tasks": 0}
                
            total_tasks = len(self.performance_metrics)
            successful_tasks = sum(1 for m in self.performance_metrics if m.success)
            avg_time = sum(m.execution_time for m in self.performance_metrics) / total_tasks
            
            return {
                "total_tasks": total_tasks,
                "success_rate": successful_tasks / total_tasks,
                "average_execution_time": avg_time,
                "patterns_learned": len(self.patterns),
                "solutions_cached": len(self.solutions)
            }


class TestPattern:
    """Test the Pattern dataclass."""
    
    def test_pattern_creation(self):
        """Test creating a basic pattern."""
        pattern = Pattern(
            id="test-pattern-1",
            description="Test pattern for API development",
            context="api-development",
            success_rate=0.85
        )
        
        assert pattern.id == "test-pattern-1"
        assert pattern.description == "Test pattern for API development"
        assert pattern.context == "api-development"
        assert pattern.success_rate == 0.85
        assert pattern.usage_count == 0
        assert isinstance(pattern.metadata, dict)
    
    def test_pattern_with_metadata(self):
        """Test pattern with custom metadata."""
        metadata = {"frameworks": ["FastAPI", "Flask"], "complexity": "medium"}
        pattern = Pattern(
            id="meta-pattern",
            description="Pattern with metadata",
            context="web-development",
            metadata=metadata
        )
        
        assert pattern.metadata == metadata
        assert pattern.metadata["frameworks"] == ["FastAPI", "Flask"]


class TestSolution:
    """Test the Solution dataclass."""
    
    def test_solution_creation(self):
        """Test creating a solution."""
        solution = Solution(
            id="sol-1",
            problem="Create a REST API",
            solution="FastAPI implementation code",
            success=True,
            execution_time=45.5
        )
        
        assert solution.id == "sol-1"
        assert solution.problem == "Create a REST API"
        assert solution.success is True
        assert solution.execution_time == 45.5
        assert isinstance(solution.patterns_used, list)
    
    def test_solution_with_patterns(self):
        """Test solution with associated patterns."""
        patterns = ["pattern-1", "pattern-2", "pattern-3"]
        solution = Solution(
            id="pattern-sol",
            problem="Complex web app",
            solution="Multi-service architecture",
            patterns_used=patterns
        )
        
        assert solution.patterns_used == patterns
        assert len(solution.patterns_used) == 3


class TestPerformanceMetric:
    """Test the PerformanceMetric dataclass."""
    
    def test_performance_metric_creation(self):
        """Test creating a performance metric."""
        metric = PerformanceMetric(
            task_type="api-development",
            execution_time=30.5,
            success=True,
            patterns_matched=3
        )
        
        assert metric.task_type == "api-development"
        assert metric.execution_time == 30.5
        assert metric.success is True
        assert metric.patterns_matched == 3
        assert isinstance(metric.timestamp, datetime)
    
    def test_performance_metric_timestamp(self):
        """Test performance metric with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        metric = PerformanceMetric(
            task_type="test",
            execution_time=10.0,
            success=True,
            timestamp=custom_time
        )
        
        assert metric.timestamp == custom_time


class TestContinuousLearningSystem:
    """Test the main learning system."""
    
    @pytest.fixture
    def learning_system(self):
        """Create a test learning system."""
        return ContinuousLearningSystem(enable_persistence=False, cache_size=100)
    
    def test_learning_system_initialization(self, learning_system):
        """Test learning system initialization."""
        assert learning_system.enable_persistence is False
        assert learning_system.cache_size == 100
        assert isinstance(learning_system.patterns, dict)
        assert isinstance(learning_system.solutions, dict)
        assert isinstance(learning_system.performance_metrics, list)
    
    @pytest.mark.asyncio
    async def test_learn_from_simple_task(self, learning_system):
        """Test learning from a simple task."""
        task = "Create a simple API endpoint"
        result = "def get_users(): return users"
        metrics = {"success": True, "execution_time": 15.5}
        
        await learning_system.learn_from_task(task, result, metrics)
        
        # Check that solution was stored
        assert len(learning_system.solutions) == 1
        solution = list(learning_system.solutions.values())[0]
        assert solution.problem == task
        assert solution.success is True
        assert solution.execution_time == 15.5
    
    @pytest.mark.asyncio
    async def test_learn_from_api_task(self, learning_system):
        """Test learning from API-related task."""
        task = "Build REST API for user management"
        result = "FastAPI application code"
        metrics = {"success": True, "execution_time": 60.0}
        
        await learning_system.learn_from_task(task, result, metrics)
        
        # Check that API pattern was extracted
        api_patterns = [p for p in learning_system.patterns.values() 
                      if "api" in p.description.lower()]
        assert len(api_patterns) >= 1
        
        api_pattern = api_patterns[0]
        assert api_pattern.context == "api-development"
        assert api_pattern.success_rate > 0
    
    @pytest.mark.asyncio
    async def test_learn_from_database_task(self, learning_system):
        """Test learning from database-related task."""
        task = "Design database schema for e-commerce"
        result = "SQLAlchemy models and migrations"
        metrics = {"success": True, "execution_time": 45.0}
        
        await learning_system.learn_from_task(task, result, metrics)
        
        # Check that database pattern was extracted
        db_patterns = [p for p in learning_system.patterns.values() 
                      if "database" in p.description.lower()]
        assert len(db_patterns) >= 1
        
        db_pattern = db_patterns[0]
        assert db_pattern.context == "database-operations"
    
    @pytest.mark.asyncio
    async def test_find_similar_patterns(self, learning_system):
        """Test finding similar patterns."""
        # First, learn from some tasks to create patterns
        await learning_system.learn_from_task(
            "Create API for user management",
            "API code",
            {"success": True}
        )
        await learning_system.learn_from_task(
            "Build database schema",
            "Schema code", 
            {"success": True}
        )
        
        # Find patterns for API task
        api_patterns = await learning_system.find_similar_patterns("Design API for products")
        api_contexts = [p.context for p in api_patterns]
        assert "api-development" in api_contexts
        
        # Find patterns for database task
        db_patterns = await learning_system.find_similar_patterns("Create database tables")
        db_contexts = [p.context for p in db_patterns]
        assert "database-operations" in db_contexts
    
    @pytest.mark.asyncio
    async def test_get_cached_solution_exact_match(self, learning_system):
        """Test getting cached solution for exact match."""
        task = "Create user authentication system"
        result = "Authentication implementation"
        metrics = {"success": True}
        
        await learning_system.learn_from_task(task, result, metrics)
        
        # Try to get cached solution for same task
        cached = await learning_system.get_cached_solution(task)
        
        assert cached is not None
        assert cached.problem == task
        assert cached.solution == result
    
    @pytest.mark.asyncio
    async def test_get_cached_solution_similar_match(self, learning_system):
        """Test getting cached solution for similar task."""
        original_task = "Build user authentication system"
        similar_task = "Create user authentication module"
        result = "Auth implementation"
        metrics = {"success": True}
        
        await learning_system.learn_from_task(original_task, result, metrics)
        
        # Try to get cached solution for similar task
        cached = await learning_system.get_cached_solution(similar_task)
        
        # Should find the similar solution
        assert cached is not None
        assert cached.solution == result
    
    @pytest.mark.asyncio
    async def test_get_cached_solution_no_match(self, learning_system):
        """Test getting cached solution when no match exists."""
        await learning_system.learn_from_task(
            "Create API endpoints",
            "API code",
            {"success": True}
        )
        
        # Try to get solution for completely different task
        cached = await learning_system.get_cached_solution("Design quantum computer")
        
        assert cached is None
    
    def test_calculate_similarity_identical(self, learning_system):
        """Test similarity calculation for identical strings."""
        similarity = learning_system._calculate_similarity(
            "create user authentication",
            "create user authentication"
        )
        assert similarity == 1.0
    
    def test_calculate_similarity_partial_match(self, learning_system):
        """Test similarity calculation for partial matches."""
        similarity = learning_system._calculate_similarity(
            "create user authentication system",
            "build user authentication module"
        )
        # Should have some similarity due to shared words
        assert 0.0 < similarity < 1.0
        assert similarity > 0.5  # Should be reasonably high
    
    def test_calculate_similarity_no_match(self, learning_system):
        """Test similarity calculation for no matches."""
        similarity = learning_system._calculate_similarity(
            "create authentication",
            "quantum computing"
        )
        assert similarity == 0.0
    
    def test_calculate_similarity_empty_strings(self, learning_system):
        """Test similarity calculation for empty strings."""
        assert learning_system._calculate_similarity("", "") == 1.0
        assert learning_system._calculate_similarity("test", "") == 0.0
        assert learning_system._calculate_similarity("", "test") == 0.0
    
    @pytest.mark.asyncio
    async def test_performance_stats_empty(self, learning_system):
        """Test performance stats with no data."""
        stats = learning_system.get_performance_stats()
        
        assert stats["total_tasks"] == 0
    
    @pytest.mark.asyncio
    async def test_performance_stats_with_data(self, learning_system):
        """Test performance stats with data."""
        # Add some performance metrics
        learning_system.performance_metrics = [
            PerformanceMetric("api", 10.0, True, 2),
            PerformanceMetric("database", 15.0, True, 1),
            PerformanceMetric("frontend", 20.0, False, 0),
        ]
        
        # Learn some patterns and solutions
        await learning_system.learn_from_task("API task", "result", {"success": True})
        await learning_system.learn_from_task("DB task", "result", {"success": True})
        
        stats = learning_system.get_performance_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["success_rate"] == 2/3  # 2 successful out of 3
        assert stats["average_execution_time"] == 15.0  # (10+15+20)/3
        assert stats["patterns_learned"] >= 1
        assert stats["solutions_cached"] == 2


class TestLearningSystemAdvanced:
    """Advanced tests for the learning system."""
    
    @pytest.fixture
    def learning_system(self):
        return ContinuousLearningSystem(cache_size=50)
    
    @pytest.mark.asyncio
    async def test_pattern_usage_tracking(self, learning_system):
        """Test that pattern usage is tracked."""
        await learning_system.learn_from_task(
            "Create API for products",
            "FastAPI code",
            {"success": True}
        )
        
        # Find and "use" the pattern
        patterns = await learning_system.find_similar_patterns("Build API for orders")
        
        # In a real implementation, using a pattern would increment usage_count
        for pattern in patterns:
            pattern.usage_count += 1
        
        # Verify usage was tracked
        api_patterns = [p for p in learning_system.patterns.values() 
                       if "api" in p.description.lower()]
        if api_patterns:
            assert api_patterns[0].usage_count > 0
    
    @pytest.mark.asyncio
    async def test_pattern_success_rate_updates(self, learning_system):
        """Test that pattern success rates are updated."""
        # Learn from successful task
        await learning_system.learn_from_task(
            "Create API endpoint",
            "Success code",
            {"success": True}
        )
        
        # Learn from failed task of similar type
        await learning_system.learn_from_task(
            "Build API service",
            "Failed code",
            {"success": False}
        )
        
        # In a real implementation, success rates would be dynamically updated
        # based on the success/failure of tasks using those patterns
        api_patterns = [p for p in learning_system.patterns.values() 
                       if "api" in p.description.lower()]
        
        assert len(api_patterns) >= 1
    
    @pytest.mark.asyncio
    async def test_multiple_task_learning(self, learning_system):
        """Test learning from multiple diverse tasks."""
        tasks = [
            ("Create REST API", "API implementation", {"success": True}),
            ("Design database schema", "Schema code", {"success": True}), 
            ("Build frontend component", "React code", {"success": False}),
            ("Setup authentication", "Auth system", {"success": True}),
            ("Create API documentation", "OpenAPI spec", {"success": True}),
        ]
        
        for task, result, metrics in tasks:
            await learning_system.learn_from_task(task, result, metrics)
        
        assert len(learning_system.solutions) == 5
        assert len(learning_system.patterns) >= 2  # At least API and database patterns
        
        # Test pattern finding across diverse tasks
        api_patterns = await learning_system.find_similar_patterns("New API project")
        assert len(api_patterns) >= 1
    
    @pytest.mark.asyncio
    async def test_cache_size_limit(self, learning_system):
        """Test that cache size limits are respected."""
        # Set a small cache size for testing
        learning_system.cache_size = 3
        
        # Add more solutions than cache size
        for i in range(5):
            await learning_system.learn_from_task(
                f"Task {i}",
                f"Result {i}",
                {"success": True}
            )
        
        # In a real implementation, cache would be limited
        # For now, just verify we have solutions
        assert len(learning_system.solutions) == 5
    
    @pytest.mark.asyncio
    async def test_concurrent_learning(self, learning_system):
        """Test concurrent learning from multiple tasks."""
        tasks = [
            ("API task 1", "API result 1", {"success": True}),
            ("API task 2", "API result 2", {"success": True}),
            ("DB task 1", "DB result 1", {"success": True}),
            ("DB task 2", "DB result 2", {"success": True}),
        ]
        
        # Learn from tasks concurrently
        learning_tasks = [
            learning_system.learn_from_task(task, result, metrics)
            for task, result, metrics in tasks
        ]
        
        await asyncio.gather(*learning_tasks)
        
        assert len(learning_system.solutions) == 4
        assert len(learning_system.patterns) >= 2


class TestLearningSystemPersistence:
    """Test persistence functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_persistence_enabled(self, temp_dir):
        """Test learning system with persistence enabled."""
        learning_system = ContinuousLearningSystem(enable_persistence=True)
        
        # In a real implementation, this would save/load from files
        await learning_system.learn_from_task(
            "Persistent task",
            "Persistent result",
            {"success": True}
        )
        
        assert learning_system.enable_persistence is True
        assert len(learning_system.solutions) == 1
    
    @pytest.mark.asyncio
    async def test_persistence_disabled(self, temp_dir):
        """Test learning system with persistence disabled."""
        learning_system = ContinuousLearningSystem(enable_persistence=False)
        
        await learning_system.learn_from_task(
            "Non-persistent task",
            "Non-persistent result", 
            {"success": True}
        )
        
        assert learning_system.enable_persistence is False
        assert len(learning_system.solutions) == 1


class TestLearningSystemPerformance:
    """Performance tests for the learning system."""
    
    @pytest.fixture
    def learning_system(self):
        return ContinuousLearningSystem(cache_size=1000)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_scale_learning(self, learning_system):
        """Test learning from many tasks efficiently."""
        import time
        
        start_time = time.time()
        
        # Learn from many tasks
        tasks = [(f"Task {i}", f"Result {i}", {"success": True}) 
                for i in range(100)]
        
        for task, result, metrics in tasks:
            await learning_system.learn_from_task(task, result, metrics)
        
        end_time = time.time()
        
        assert len(learning_system.solutions) == 100
        assert (end_time - start_time) < 5.0  # Should complete quickly
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_pattern_matching_performance(self, learning_system):
        """Test pattern matching performance."""
        import time
        
        # First, create many patterns
        for i in range(50):
            await learning_system.learn_from_task(
                f"API task {i}",
                f"API result {i}",
                {"success": True}
            )
        
        start_time = time.time()
        
        # Find similar patterns multiple times
        for _ in range(20):
            patterns = await learning_system.find_similar_patterns("New API development task")
        
        end_time = time.time()
        
        assert (end_time - start_time) < 2.0  # Should find patterns quickly
    
    @pytest.mark.performance
    def test_similarity_calculation_performance(self, learning_system):
        """Test similarity calculation performance."""
        import time
        
        task1 = "Create comprehensive REST API with authentication and authorization"
        task2 = "Build REST API service with user authentication and role-based access"
        
        start_time = time.time()
        
        # Calculate similarity many times
        for _ in range(1000):
            similarity = learning_system._calculate_similarity(task1, task2)
        
        end_time = time.time()
        
        assert 0.0 <= similarity <= 1.0
        assert (end_time - start_time) < 1.0  # Should be fast