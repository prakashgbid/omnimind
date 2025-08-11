# 🧠 Persistent AI Memory

[![PyPI version](https://badge.fury.io/py/persistent-ai-memory.svg)](https://badge.fury.io/py/persistent-ai-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Never lose context again** - A persistent memory system for AI agents that maintains context across sessions, learns from interactions, and improves over time.

## 🚀 Features

- **Persistent Context**: Maintains memory across sessions using SQLite + ChromaDB
- **Semantic Search**: Vector-based memory retrieval for relevant context
- **Memory Prioritization**: Critical, High, Medium, Low priority levels
- **Auto-Compression**: Automatically merges similar memories to save space
- **Memory Decay**: Old, unused memories fade while important ones persist
- **Skill Tracking**: Remember and improve learned capabilities
- **Cross-Project Learning**: Learn patterns across different projects

## 📦 Installation

```bash
pip install persistent-ai-memory
```

## 🔧 Quick Start

```python
from persistent_ai_memory import PersistentMemory, MemoryType, MemoryPriority

# Initialize memory system
memory = PersistentMemory()

# Store a memory
memory.store_memory(
    content="User prefers TypeScript over JavaScript",
    memory_type=MemoryType.LEARNING,
    priority=MemoryPriority.HIGH,
    metadata={"project": "web-app", "confidence": 0.9}
)

# Recall relevant memories
memories = memory.recall_memories(
    query="What language should I use for the frontend?",
    n_results=5
)

for mem in memories:
    print(f"[{mem.priority.value}] {mem.content}")
    print(f"  Relevance: {mem.reinforcement_score:.2f}")

# Get context for new session
context = memory.get_context_for_session()
print(f"Loaded {len(context['learned_patterns'])} learned patterns")
```

## 🎯 Use Cases

### AI Agents
```python
# Remember user preferences across sessions
memory.store_memory(
    "User wants clean, minimalist UI designs",
    MemoryType.CONTEXT,
    MemoryPriority.HIGH
)

# Learn from mistakes
memory.store_memory(
    "TypeError when using async without await - always check",
    MemoryType.ERROR,
    MemoryPriority.CRITICAL
)
```

### Project Management
```python
# Track project decisions
memory.store_memory(
    "Decided to use PostgreSQL for scalability",
    MemoryType.DECISION,
    MemoryPriority.HIGH,
    metadata={"project": "saas-platform", "date": "2024-01-15"}
)

# Remember skills
memory.add_skill(
    name="Docker Deployment",
    description="Can containerize and deploy applications",
    code_template="docker build -t {app_name} . && docker run -p {port}:80 {app_name}"
)
```

### Learning & Improvement
```python
# Track successful patterns
memory.store_memory(
    "Using factory pattern improved code maintainability",
    MemoryType.LEARNING,
    MemoryPriority.MEDIUM,
    metadata={"pattern": "factory", "impact": "positive"}
)

# Reinforce useful memories
useful_memory = memory.recall_memories("factory pattern")[0]
memory.reinforce_memory(useful_memory.id, score=0.2)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Memory Interface            │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐     ┌──────────┐    │
│  │ SQLite   │     │ ChromaDB │    │
│  │ Metadata │     │ Vectors  │    │
│  └──────────┘     └──────────┘    │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Sentence Transformers      │  │
│  │   (Embeddings)               │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 🔍 Memory Types

- **VISION**: Core purpose and goals
- **DECISION**: Architectural and design decisions
- **LEARNING**: Learned patterns and insights
- **PROJECT**: Project-specific knowledge
- **SKILL**: Acquired capabilities
- **CONTEXT**: Conversation and interaction context
- **CODE**: Code patterns and solutions
- **ERROR**: Mistakes to avoid

## ⚙️ Configuration

```python
from persistent_ai_memory import PersistentMemory

memory = PersistentMemory({
    "memory_dir": "~/.ai/memory",           # Storage location
    "max_memories": 10000,                  # Maximum memories to store
    "compression_threshold": 0.8,           # Similarity threshold for merging
    "embedding_model": "all-MiniLM-L6-v2"   # Sentence transformer model
})
```

## 🧪 Advanced Features

### Memory Compression
```python
# Automatically merge similar memories
memory.compress_memories()  # Merges memories with >80% similarity
```

### Memory Decay
```python
# Apply decay to old memories
memory.decay_memories()  # Reduces importance of unused memories
```

### Session Checkpoints
```python
# Create checkpoint for important sessions
checkpoint_id = memory.create_session_checkpoint(
    summary="Implemented authentication system",
    key_decisions=["Used JWT", "Added 2FA", "PostgreSQL for users"]
)
```

### Export/Import
```python
# Export critical context
context_str = memory.export_critical_context()

# Import into another instance
new_memory = PersistentMemory()
new_memory.import_context(context_str)
```

## 📊 Performance

- **Storage**: ~1KB per memory entry
- **Retrieval**: <100ms for semantic search
- **Compression**: 30-50% reduction in similar memories
- **Scalability**: Tested with 100K+ memories

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Documentation](https://persistent-ai-memory.readthedocs.io)
- [PyPI Package](https://pypi.org/project/persistent-ai-memory)
- [GitHub Repository](https://github.com/prakashgbid/persistent-ai-memory)
- [Issue Tracker](https://github.com/prakashgbid/persistent-ai-memory/issues)

## 💡 Examples

Check out the [examples/](examples/) directory for:
- Chat bot with persistent memory
- Project management assistant
- Learning agent that improves over time
- Multi-agent shared memory system

## 🙏 Acknowledgments

Built as part of the OSA (OmniMind Super Agent) project. Special thanks to all contributors!

---

**Made with ❤️ for AI developers who want their agents to remember**