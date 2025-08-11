# OSA Coding Standards

## 📋 Overview

This document defines the coding standards and best practices for the OSA (OmniMind Super Agent) project. These standards ensure code consistency, maintainability, and quality across all contributions.

## 🐍 Python Standards

### Code Style

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Line Endings**: LF (Unix-style)

### Formatting Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **Pre-commit**: Automatic enforcement

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .
```

### Naming Conventions

```python
# Classes: PascalCase
class ContinuousThinkingEngine:
    pass

# Functions and variables: snake_case
def generate_thoughts(topic_name: str) -> List[Thought]:
    thought_count = 0
    return thoughts

# Constants: UPPER_SNAKE_CASE
MAX_THOUGHTS = 10000
DEFAULT_REASONING_DEPTH = 10

# Private attributes: _leading_underscore
class OSA:
    def __init__(self):
        self._internal_state = {}

# Magic methods: __double_underscore__
def __str__(self) -> str:
    return "OSA Instance"
```

### Type Annotations

**Required for all public functions and methods:**

```python
# ✅ Good
def process_thoughts(
    thoughts: List[Thought], 
    context: Optional[Context] = None
) -> ProcessingResult:
    """Process a list of thoughts with optional context."""
    pass

# ❌ Bad
def process_thoughts(thoughts, context=None):
    pass
```

### Docstrings

**Use Google style docstrings:**

```python
def think_and_accomplish(goal: str, constraints: Optional[List[str]] = None) -> TaskResult:
    """Accomplish a goal through deep thinking and reasoning.
    
    This method initiates OSA's continuous thinking engine to break down
    and accomplish complex goals through human-like reasoning patterns.
    
    Args:
        goal: The objective to accomplish
        constraints: Optional list of constraints or limitations
        
    Returns:
        TaskResult containing the accomplished task details and insights
        
    Raises:
        OSABlockerException: When an unresolvable blocker is encountered
        OSATimeoutException: When the task exceeds time limits
        
    Example:
        >>> osa = await create_complete_osa()
        >>> result = await osa.think_and_accomplish("Build a web app")
        >>> print(f"Success: {result.success}")
    """
    pass
```

### Error Handling

```python
# ✅ Specific exception handling
try:
    result = await claude_instance.process(request)
except ClaudeAPIError as e:
    logger.error(f"Claude API failed: {e}")
    raise OSAProcessingError(f"Processing failed: {e}") from e
except Exception as e:
    logger.exception("Unexpected error in processing")
    raise OSAUnknownError("Unknown processing error") from e

# ✅ Custom exceptions with clear hierarchy
class OSAException(Exception):
    """Base exception for OSA-related errors."""
    pass

class OSAProcessingError(OSAException):
    """Error during thought processing."""
    pass

class OSABlockerException(OSAException):
    """Unresolvable blocker encountered."""
    
    def __init__(self, message: str, blocker: Blocker):
        super().__init__(message)
        self.blocker = blocker
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Proper logging levels
logger.debug("Detailed debugging information")
logger.info("General information about execution flow")
logger.warning("Something unexpected happened but processing continues")
logger.error("Error that affects functionality")
logger.critical("Serious error that may cause system failure")

# ✅ Structured logging
logger.info(
    "Task completed",
    extra={
        "task_id": task.id,
        "execution_time": result.execution_time,
        "thoughts_generated": result.thought_count
    }
)
```

## 🏗️ Architecture Patterns

### Async/Await Usage

```python
# ✅ Proper async patterns
async def process_multiple_thoughts(thoughts: List[Thought]) -> List[ProcessedThought]:
    """Process thoughts concurrently."""
    tasks = [process_single_thought(thought) for thought in thoughts]
    return await asyncio.gather(*tasks, return_exceptions=True)

# ✅ Context managers
async def with_thinking_context(context_name: str):
    context = await create_context(context_name)
    try:
        yield context
    finally:
        await context.cleanup()

# Usage
async with with_thinking_context("problem_solving") as ctx:
    result = await think_about_problem(problem, context=ctx)
```

### Dependency Injection

```python
# ✅ Clear dependencies
class OSAEngine:
    def __init__(
        self,
        claude_provider: ClaudeProvider,
        learning_system: LearningSystem,
        logger: logging.Logger
    ):
        self.claude_provider = claude_provider
        self.learning_system = learning_system
        self.logger = logger

# ✅ Factory pattern
async def create_complete_osa(**config) -> OSAEngine:
    claude_provider = ClaudeProvider(config.get('claude_config', {}))
    learning_system = LearningSystem(config.get('learning_config', {}))
    logger = setup_logger(config.get('log_level', 'INFO'))
    
    return OSAEngine(claude_provider, learning_system, logger)
```

### Data Classes and Models

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Thought:
    """Represents a single thought in OSA's cognitive process."""
    
    id: str
    content: str
    context: str
    confidence: float = field(default=0.0)
    connections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate thought data after initialization."""
        if not self.id:
            raise ValueError("Thought ID cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
```

## 🧪 Testing Standards

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock, Mock
from osa_complete_final import create_complete_osa

class TestOSAThinkingEngine:
    """Test suite for OSA thinking engine functionality."""
    
    @pytest.fixture
    async def osa_instance(self):
        """Create OSA instance for testing."""
        return await create_complete_osa(max_instances=1)
    
    @pytest.mark.asyncio
    async def test_basic_thinking(self, osa_instance):
        """Test basic thinking functionality."""
        # Given
        simple_task = "Calculate 2 + 2"
        
        # When
        result = await osa_instance.think_and_accomplish(simple_task)
        
        # Then
        assert result.success is True
        assert "4" in result.result
        assert result.thinking_insights.total_thoughts > 0
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complex_problem_solving(self, osa_instance):
        """Test complex problem-solving capabilities."""
        complex_task = """
        Design a scalable architecture for a social media platform
        that can handle 1M concurrent users
        """
        
        result = await osa_instance.think_and_accomplish(complex_task)
        
        assert result.success is True
        assert result.thinking_insights.blockers_handled >= 0
        assert result.thinking_insights.alternatives_generated > 0

    @pytest.mark.unit
    def test_thought_creation(self):
        """Test thought object creation and validation."""
        # Valid thought
        thought = Thought(
            id="test-thought-1",
            content="Test thinking process",
            context="testing",
            confidence=0.8
        )
        
        assert thought.id == "test-thought-1"
        assert 0 <= thought.confidence <= 1
        
        # Invalid thought should raise error
        with pytest.raises(ValueError):
            Thought(id="", content="Invalid", context="test")
```

### Test Coverage

- **Minimum coverage**: 80%
- **Critical paths**: 95%
- **Integration tests**: Required for all public APIs
- **Unit tests**: Required for all utility functions

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Coverage requirements in pyproject.toml
[tool.coverage.report]
fail_under = 80
show_missing = true
```

## 🚨 Anti-Patterns to Avoid

### Code Smells

```python
# ❌ God class - too many responsibilities
class OSAEverything:
    def think(self): pass
    def learn(self): pass
    def communicate(self): pass
    def store_data(self): pass
    def format_output(self): pass
    # ... 50 more methods

# ✅ Single responsibility
class ThinkingEngine:
    def think(self): pass

class LearningSystem:
    def learn(self): pass

# ❌ Long parameter list
def process_complex_task(
    task, context, constraints, preferences, settings, 
    timeout, retries, callbacks, metadata, options
):
    pass

# ✅ Use configuration objects
@dataclass
class TaskConfig:
    context: str
    constraints: List[str]
    timeout: int = 300
    retries: int = 3

def process_complex_task(task: str, config: TaskConfig):
    pass

# ❌ Nested conditions
def process_thought(thought):
    if thought:
        if thought.is_valid():
            if thought.context:
                if thought.context.is_active():
                    # deep nesting...
                    return process_valid_thought(thought)
    return None

# ✅ Early returns
def process_thought(thought):
    if not thought:
        return None
    
    if not thought.is_valid():
        return None
    
    if not thought.context or not thought.context.is_active():
        return None
    
    return process_valid_thought(thought)
```

### Performance Anti-Patterns

```python
# ❌ N+1 queries
async def get_thoughts_with_contexts(thought_ids):
    results = []
    for thought_id in thought_ids:  # N+1 problem
        thought = await get_thought(thought_id)
        context = await get_context(thought.context_id)
        results.append((thought, context))
    return results

# ✅ Batch operations
async def get_thoughts_with_contexts(thought_ids):
    thoughts = await get_thoughts_batch(thought_ids)
    context_ids = [t.context_id for t in thoughts]
    contexts = await get_contexts_batch(context_ids)
    context_map = {c.id: c for c in contexts}
    
    return [(t, context_map[t.context_id]) for t in thoughts]

# ❌ Blocking operations in async context
async def process_data():
    data = requests.get("https://api.example.com/data")  # Blocking!
    return process(data)

# ✅ Async HTTP client
async def process_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
    return process(data)
```

## 🔒 Security Standards

### Input Validation

```python
from pydantic import BaseModel, validator

class TaskRequest(BaseModel):
    goal: str
    max_execution_time: int = 300
    
    @validator('goal')
    def goal_must_be_safe(cls, v):
        # Prevent code injection
        forbidden = ['exec', 'eval', '__import__', 'subprocess']
        if any(word in v.lower() for word in forbidden):
            raise ValueError('Goal contains forbidden operations')
        return v
    
    @validator('max_execution_time')
    def reasonable_timeout(cls, v):
        if not 1 <= v <= 3600:  # 1 second to 1 hour
            raise ValueError('Execution time must be between 1 and 3600 seconds')
        return v
```

### Secrets Management

```python
import os
from typing import Optional

# ✅ Environment variables with defaults
def get_api_key(service: str) -> Optional[str]:
    """Get API key from environment variables."""
    return os.getenv(f"{service.upper()}_API_KEY")

# ✅ Never log secrets
def log_request(request_data: dict):
    safe_data = {k: v for k, v in request_data.items() if 'key' not in k.lower()}
    logger.info(f"Making request with data: {safe_data}")

# ❌ Never hardcode secrets
API_KEY = "sk-1234567890abcdef"  # DON'T DO THIS!
```

## 📊 Performance Guidelines

### Memory Management

```python
# ✅ Use generators for large datasets
def process_large_dataset():
    for chunk in read_data_in_chunks():
        yield process_chunk(chunk)

# ✅ Context managers for resource cleanup
class ThinkingSession:
    async def __aenter__(self):
        self.claude_instances = await initialize_claude_instances()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await cleanup_claude_instances(self.claude_instances)
```

### Caching Strategies

```python
from functools import lru_cache
import asyncio

# ✅ LRU cache for expensive computations
@lru_cache(maxsize=1000)
def expensive_pattern_matching(pattern: str, text: str) -> bool:
    # Expensive regex or ML computation
    return complex_match(pattern, text)

# ✅ Async cache with TTL
class AsyncTTLCache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    async def get_or_compute(self, key: str, compute_func):
        now = time.time()
        if key in self.cache:
            value, timestamp = self.cache[key]
            if now - timestamp < self.ttl:
                return value
        
        value = await compute_func()
        self.cache[key] = (value, now)
        return value
```

## 🔄 Pre-commit Checklist

Before committing code, ensure:

- [ ] **Code formatted** with Black and isort
- [ ] **Type checking** passes with mypy
- [ ] **Linting** passes with flake8 and pylint
- [ ] **Security scan** passes with bandit
- [ ] **Tests written** and passing
- [ ] **Documentation updated**
- [ ] **No secrets** in code
- [ ] **Performance considered**

```bash
# Run all checks locally
pre-commit run --all-files

# Or run individual tools
black --check .
isort --check-only .
mypy src/
flake8 src/
pylint src/
bandit -r src/
pytest --cov=src
```

## 📚 Resources

- [Black Code Style](https://black.readthedocs.io/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 8 – Style Guide](https://pep8.org/)
- [Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Async Best Practices](https://docs.python.org/3/library/asyncio-dev.html)

---

*These standards are enforced automatically through pre-commit hooks and CI/CD pipelines.*