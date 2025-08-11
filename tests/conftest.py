"""
Pytest configuration and shared fixtures.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from typing import AsyncGenerator, Generator

# Import OSA modules for testing
# Note: These imports might fail initially until the modules are created
try:
    from src.osa_complete_final import create_complete_osa
    from src.osa_continuous_thinking import ContinuousThinkingEngine
    from src.osa_continuous_learning import ContinuousLearningSystem
except ImportError:
    # Mock imports for initial setup
    def create_complete_osa(*args, **kwargs):
        return AsyncMock()
    
    ContinuousThinkingEngine = Mock
    ContinuousLearningSystem = Mock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def osa_instance() -> AsyncGenerator:
    """Create a test OSA instance with minimal configuration."""
    config = {
        'max_instances': 1,
        'enable_learning': False,
        'enable_monitoring': False,
        'thinking': {
            'max_depth': 3,
            'thought_limit': 100
        }
    }
    
    osa = await create_complete_osa(**config)
    yield osa
    
    # Cleanup
    if hasattr(osa, 'cleanup'):
        await osa.cleanup()


@pytest.fixture
async def thinking_engine() -> ContinuousThinkingEngine:
    """Create a test thinking engine instance."""
    return ContinuousThinkingEngine(
        max_thoughts=100,
        max_depth=3
    )


@pytest.fixture
async def learning_system() -> ContinuousLearningSystem:
    """Create a test learning system instance."""
    return ContinuousLearningSystem(
        enable_persistence=False,
        cache_size=50
    )


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_claude_response():
    """Mock Claude API response."""
    return {
        "content": [
            {
                "type": "text",
                "text": "This is a test response from Claude."
            }
        ],
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15
        }
    }


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return "Create a simple Python function that adds two numbers"


@pytest.fixture
def complex_task():
    """Complex task for testing."""
    return """
    Design and implement a distributed system that can handle:
    - 1 million concurrent users
    - Real-time data processing
    - Fault tolerance and recovery
    - Auto-scaling based on demand
    """


@pytest.fixture
def sample_thoughts():
    """Sample thoughts for testing thinking engine."""
    from src.osa_continuous_thinking import Thought
    
    return [
        Thought(
            id="thought-1",
            content="Consider using microservices architecture",
            context="system-design",
            confidence=0.8
        ),
        Thought(
            id="thought-2", 
            content="Implement load balancing for scalability",
            context="scalability",
            confidence=0.9
        ),
        Thought(
            id="thought-3",
            content="Use containerization with Docker",
            context="deployment",
            confidence=0.85
        )
    ]


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Configure logging for tests."""
    import logging
    
    # Set up test logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


@pytest.fixture
def mock_environment_variables(monkeypatch):
    """Mock environment variables for testing."""
    test_vars = {
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'OPENAI_API_KEY': 'test-openai-key',
        'OSA_MAX_INSTANCES': '2',
        'OSA_THINKING_DEPTH': '5',
        'OSA_LEARNING_ENABLED': 'true'
    }
    
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    
    return test_vars


# Performance test fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for testing."""
    return {
        'thinking_time': 5.0,  # seconds
        'memory_usage': 100,   # MB
        'api_response': 2.0,   # seconds
    }


# Security test fixtures
@pytest.fixture
def malicious_inputs():
    """Collection of malicious inputs for security testing."""
    return [
        "'; DROP TABLE users; --",
        "<script>alert('xss')</script>",
        "../../etc/passwd",
        "__import__('os').system('rm -rf /')",
        "eval('1+1')",
        "exec('print(\"hello\")')",
        "../../../windows/system32/",
    ]


# Integration test fixtures
@pytest.fixture
async def mock_external_services():
    """Mock external services for integration testing."""
    services = {
        'anthropic': AsyncMock(),
        'openai': AsyncMock(),
        'chromadb': Mock(),
        'websocket': AsyncMock()
    }
    
    # Configure mock responses
    services['anthropic'].messages.create.return_value = AsyncMock(
        content=[{"type": "text", "text": "Mock Claude response"}]
    )
    
    services['openai'].chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Mock GPT response"))]
    )
    
    return services


# Regression test data
@pytest.fixture
def regression_test_cases():
    """Known test cases for regression testing."""
    return [
        {
            "input": "Calculate 2 + 2",
            "expected_output": "4",
            "description": "Basic arithmetic"
        },
        {
            "input": "Write a hello world function in Python",
            "expected_contains": ["def", "print", "hello"],
            "description": "Simple function generation"
        },
        {
            "input": "Explain what recursion is",
            "expected_contains": ["function", "calls", "itself"],
            "description": "Concept explanation"
        }
    ]


# Parametrized test data
@pytest.fixture(params=[
    ("simple_task", "Write a function"),
    ("medium_task", "Build a web API"),
    ("complex_task", "Design a distributed system")
])
def task_complexity_levels(request):
    """Different complexity levels for parametrized testing."""
    return request.param


# Database fixtures for testing
@pytest.fixture
async def test_database():
    """Create a test database instance."""
    import sqlite3
    import tempfile
    
    # Create temporary database
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    # Initialize database
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value TEXT
        )
    ''')
    conn.commit()
    
    yield {
        'path': db_path,
        'connection': conn
    }
    
    # Cleanup
    conn.close()
    Path(db_path).unlink(missing_ok=True)


# Custom markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to unit tests
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)
        
        # Add security marker to security tests
        if "security" in item.nodeid:
            item.add_marker(pytest.mark.security)


# Timeout configuration for different test types
def pytest_timeout_set_timer(item, timeout):
    """Set different timeouts for different test types."""
    if item.get_closest_marker("slow"):
        return 300  # 5 minutes for slow tests
    elif item.get_closest_marker("integration"):
        return 120  # 2 minutes for integration tests
    else:
        return 60   # 1 minute for unit tests