# Getting Started with OSA

This guide will help you get OSA up and running in minutes.

## 📋 Prerequisites

- **Python**: 3.9 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Disk Space**: 2GB free space
- **OS**: Linux, macOS, or Windows

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/prakashgbid/omnimind.git
cd omnimind
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install Ollama for Local LLMs

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.2:3b
ollama pull mistral
ollama pull deepseek-coder
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional: API Keys for cloud providers
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Optional: Custom settings
OSA_MAX_INSTANCES=10
OSA_THINKING_DEPTH=10
OSA_LEARNING_ENABLED=true
```

### Local Configuration

OSA works out of the box with local models. No API keys required!

## 🎮 Running OSA

### Interactive Mode

The easiest way to start:

```bash
python run_complete_osa.py
```

You'll see a menu with options:
1. Deep thinking & task accomplishment
2. Leadership & delegation
3. Problem solving with alternatives
4. Continuous thinking demonstration
5. Complex goal breakdown
6. Blocker handling
7. Show thinking status

### Python Script

```python
import asyncio
from osa_complete_final import create_complete_osa

async def main():
    # Create OSA instance
    osa = await create_complete_osa()
    
    # Give it a task
    result = await osa.think_and_accomplish(
        "Create a todo list app with user authentication"
    )
    
    print(f"Task completed: {result['summary']}")
    print(f"Thoughts generated: {result['thinking_insights']['total_thoughts']}")

asyncio.run(main())
```

### Web Monitoring

Start the real-time monitoring interface:

```bash
# Terminal 1: Start WebSocket server
python src/osa_logger.py

# Terminal 2: Run OSA
python run_complete_osa.py

# Open in browser
open web/index.html
```

## 🧠 Basic Usage Examples

### Simple Task

```python
# Initialize
osa = await create_complete_osa()

# Simple task
result = await osa.accomplish("Write a Python function to sort a list")
```

### Complex Project

```python
# Lead a project
project = await osa.lead_complex_project(
    project_name="E-Commerce Platform",
    requirements=[
        "User authentication",
        "Product catalog",
        "Shopping cart",
        "Payment processing"
    ],
    team_size=5
)
```

### Problem Solving

```python
# Solve with alternatives
solution = await osa.solve_with_alternatives(
    "Fix database performance issues when indexes are missing"
)

print(f"Solutions found: {solution['alternatives_available']}")
```

### Continuous Thinking

```python
# Let OSA think about a topic
thoughts = await osa.think_continuously_about(
    topic="How to make apps go viral",
    duration_seconds=30
)

print(f"Generated {thoughts['thoughts_generated']} thoughts")
```

## 📊 Understanding the Output

OSA provides detailed insights into its thinking:

```python
result = await osa.think_and_accomplish("Build a chat app")

# Access thinking insights
print(f"Total thoughts: {result['thinking_insights']['total_thoughts']}")
print(f"Reasoning chains: {result['thinking_insights']['reasoning_chains']}")
print(f"Blockers handled: {result['thinking_insights']['blockers_handled']}")
print(f"Alternatives available: {result['thinking_insights']['alternatives_available']}")
print(f"Confidence: {result['thinking_insights']['confidence']:.1%}")

# View thought graph
print(result['thinking_insights']['thinking_visualization'])
```

## 🔧 Troubleshooting

### Common Issues

**Python version error**
```bash
# Check Python version
python --version

# Use python3 if needed
python3 run_complete_osa.py
```

**Memory issues**
```python
# Reduce parallel instances
osa = await create_complete_osa(max_claude_instances=3)
```

**Import errors**
```bash
# Ensure you're in the project directory
cd omnimind

# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Next Steps

- Read the [Architecture Guide](Architecture) to understand OSA's design
- Explore [API Reference](API-Reference) for advanced usage
- Check out [Examples](Examples) for real-world scenarios
- Join the [Discussion](https://github.com/prakashgbid/omnimind/discussions)

## 💡 Tips

1. **Start small**: Begin with simple tasks to understand OSA's capabilities
2. **Watch the monitor**: Use the web interface to see OSA's thinking in real-time
3. **Learn from patterns**: OSA gets smarter with each task
4. **Experiment**: Try different types of problems to see OSA's versatility

---

Need help? [Open an issue](https://github.com/prakashgbid/omnimind/issues) or join our [discussions](https://github.com/prakashgbid/omnimind/discussions)!