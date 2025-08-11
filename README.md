# OmniMind - Human-like Thinking AI System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI/CD](https://github.com/prakashgbid/omnimind/actions/workflows/quality-gates.yml/badge.svg)](https://github.com/prakashgbid/omnimind/actions)

OmniMind is an advanced AI system that mimics human cognitive processes through continuous thinking, learning, and reasoning capabilities. It provides a framework for building intelligent applications with human-like problem-solving abilities.

## 🌟 Features

- **Continuous Thinking Engine**: Background cognitive processing that generates thoughts, connections, and insights
- **Adaptive Learning System**: Learns from interactions and improves over time
- **Multi-Model Support**: Works with Ollama (local), OpenAI, and other LLM providers
- **Modular Architecture**: Clean, extensible design for easy customization
- **Comprehensive Testing**: 200+ tests covering unit, integration, security, and performance
- **Production Ready**: Pre-commit hooks, CI/CD pipeline, and quality gates

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Ollama (for local models)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/prakashgbid/omnimind.git
cd omnimind
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run setup script:
```bash
./setup_local.sh
```

### Usage

Run OmniMind in interactive mode:
```bash
python omnimind.py
```

Process a specific task:
```bash
python omnimind.py "Create a web scraper in Python"
```

With options:
```bash
python omnimind.py --model llama3.2:3b --verbose "Explain quantum computing"
```

## 📁 Project Structure

```
omnimind/
├── src/                  # Source code
│   ├── core/            # Core OSA modules
│   │   ├── osa.py       # Main OSA implementation
│   │   ├── logger.py    # Logging utilities
│   │   └── modules/     # Core modules
│   │       ├── thinking.py   # Thinking engine
│   │       ├── learning.py   # Learning system
│   │       └── architecture_reviewer.py
│   ├── providers/       # LLM providers
│   ├── agents/          # Agent system
│   └── utils/           # Utilities
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   ├── security/       # Security tests
│   ├── performance/    # Performance tests
│   └── regression/     # Regression tests
├── tools/              # Development tools
├── docs/               # Documentation
├── web/                # Web interface
└── omnimind.py         # Main entry point
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/
```

Run specific test categories:
```bash
pytest tests/unit/          # Unit tests
pytest tests/security/      # Security tests
pytest tests/performance/   # Performance tests
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run quality checks
python tools/quality_checks.py
```

### Code Quality

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing
- **Pre-commit** hooks for quality gates

## 🤝 Contributing

Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/prakashgbid/omnimind)
- [Documentation](https://prakashgbid.github.io/omnimind/)
- [Wiki](https://github.com/prakashgbid/omnimind/wiki)

## 💡 Core Concepts

OmniMind implements several key cognitive concepts:

1. **Continuous Thinking**: Background processing that generates thoughts and connections
2. **Pattern Recognition**: Identifies and learns from patterns in data and interactions
3. **Contextual Memory**: Maintains context across conversations and tasks
4. **Adaptive Learning**: Improves performance based on feedback and experience
5. **Multi-Model Reasoning**: Combines insights from multiple AI models

## ⚡ Performance

- Supports concurrent task processing
- Memory-efficient with automatic cleanup
- Optimized for both local and cloud deployments
- Benchmarked for speed and resource usage

## 🛡️ Security

- Input validation and sanitization
- Protection against injection attacks
- Secure handling of API keys and credentials
- Regular security audits via automated testing

---

Built with passion for advancing AI capabilities 🚀