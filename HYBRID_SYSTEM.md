# 🚀 OmniMind Hybrid Intelligence System

**The Best of Both Worlds: FREE Local Models + Premium AI When Needed**

## 🎯 What We Built

A smart hybrid system that combines:
- **5 FREE Local Models** for 80% of tasks (no cost)
- **Premium Models** (ChatGPT 5/GPT-4, Claude Opus) for critical tasks
- **Intelligent Routing** that minimizes costs while maximizing quality
- **Perfect Memory** across all models
- **Automatic Fallback** when premium unavailable

## 📊 How It Works

### Intelligent Task Analysis
The system analyzes each query to determine:
1. **Complexity Level** (simple/medium/complex)
2. **Quality Requirements** (standard/critical)
3. **Best Model Match** (local vs premium)
4. **Cost Optimization** (budget checking)

### Routing Decision Tree
```
Query Received
     ↓
Is it critical? (production, legal, medical)
     ├─ YES → Use Premium Model (GPT-4/Claude Opus)
     └─ NO → Continue Analysis
              ↓
         Is it complex?
              ├─ YES → Check Budget
              │         ├─ Budget OK → Premium Model
              │         └─ Over Budget → Best Local Model
              └─ NO → Use Local Model (FREE)
```

## 💰 Cost Optimization

### Typical Usage Patterns
| Task Type | Model Used | Cost |
|-----------|------------|------|
| Simple questions | Llama 3.2 (local) | $0.00 |
| Code writing | DeepSeek Coder (local) | $0.00 |
| Bug fixing | Mistral (local) | $0.00 |
| Documentation | Llama 3.2 (local) | $0.00 |
| Complex analysis | GPT-4 Turbo | $0.03 |
| Creative writing | Claude Opus | $0.075 |
| Production code | GPT-4/Claude | $0.03-0.075 |

### Monthly Cost Estimates
- **Light Usage**: $0-2/month (95% local)
- **Normal Usage**: $2-5/month (85% local)
- **Heavy Usage**: $5-10/month (80% local)
- **Local Only Mode**: $0/month (100% local)

## 🤖 Available Models

### Local Models (FREE)
```python
# Always available, no API needed
models = {
    'llama3.2:3b': 'General purpose, fast',
    'mistral:7b': 'Complex reasoning',
    'deepseek-coder:6.7b': 'Programming specialist',
    'phi3:mini': 'Efficient tasks',
    'gemma2:2b': 'Ultra-fast responses'
}
```

### Premium Models (When Needed)
```python
# Requires API keys
premium_models = {
    # OpenAI
    'gpt-5': 'Most advanced (coming soon)',
    'gpt-4-turbo': 'Advanced reasoning',
    'gpt-3.5-turbo': 'Fast, cheaper option',
    
    # Anthropic
    'claude-3-opus': 'Best for nuanced tasks',
    'claude-3-sonnet': 'Balanced performance',
    'claude-3-haiku': 'Fast simple tasks'
}
```

## 🎮 Usage Examples

### Basic Usage
```python
from src.providers.intelligent_router import smart_complete
import asyncio

# Let the system decide (80% will use free local)
response = await smart_complete("Write a Python function to sort a list")
print(f"Model used: {response.model}")
print(f"Cost: ${response.cost}")  # Likely $0.00

# Force high quality for critical task
response = await smart_complete(
    "Design production authentication system",
    require_quality=True
)
print(f"Model used: {response.model}")  # GPT-4 or Claude Opus
print(f"Cost: ${response.cost}")  # ~$0.03-0.075

# Force local for privacy
response = await smart_complete(
    "Analyze this confidential data",
    force_local=True
)
print(f"Cost: ${response.cost}")  # Always $0.00
```

### With Claude Code Agents
```python
from src.agents.agent_registry import get_agent

# Agents automatically use hybrid routing
agent = get_agent('backend-architect')

# Simple task - uses local model (FREE)
response = agent.think("How do I create a REST endpoint?")

# Critical task - uses premium model
response = agent.think("Design production-ready payment processing system")
```

## 📈 Routing Statistics

### Check Usage and Costs
```python
from src.providers.intelligent_router import get_router_stats

stats = get_router_stats()
print(f"Month cost: ${stats['current_month_cost']}")
print(f"Budget remaining: ${stats['budget_remaining']}")
print(f"Available providers: {stats['available_providers']}")
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Budget Control
MONTHLY_BUDGET_USD=10.0        # Monthly budget for premium models
MAX_COST_PER_QUERY=0.50       # Max cost per single query
PREFER_LOCAL_MODELS=true       # Prefer local when possible

# Premium Model Keys (Optional)
OPENAI_API_KEY=sk-...          # For GPT-4/GPT-5
ANTHROPIC_API_KEY=sk-ant-...   # For Claude Opus
PREFER_OPUS=false              # Prefer Claude Opus over GPT-4

# Local Models (Always Free)
USE_LOCAL_MODELS=true          # Enable local models
PRIMARY_MODEL=llama3.2:3b      # Default local model
```

## 🎯 Routing Rules

### Tasks That Use Premium Models
- ❗ Contains "critical", "production", "customer-facing"
- ❗ Legal, medical, or financial analysis
- ❗ Complex creative writing
- ❗ Deep philosophical reasoning
- ❗ When `require_quality=True`

### Tasks That Use Local Models
- ✅ General questions and explanations
- ✅ Code writing and debugging
- ✅ Documentation
- ✅ Testing and refactoring
- ✅ Simple analysis
- ✅ When `force_local=True`
- ✅ When budget exceeded

## 🔒 Privacy Options

### Three Privacy Levels
1. **Full Local** (`force_local=True`)
   - 100% private, no data leaves machine
   - $0 cost
   - Good quality for most tasks

2. **Smart Hybrid** (default)
   - 80% local, 20% cloud
   - ~$5/month typical cost
   - Best quality for critical tasks

3. **Premium Priority** (`require_quality=True`)
   - Uses best available model
   - Higher cost but best results
   - For critical decisions

## 📊 Benefits Summary

### vs Pure Cloud Solutions
| Aspect | Pure Cloud | OmniMind Hybrid |
|--------|------------|-----------------|
| Monthly Cost | $20-100+ | $0-10 |
| Privacy | No | Configurable |
| Offline Work | No | Yes (local) |
| Rate Limits | Yes | No (local) |
| Quality | High | High when needed |

### vs Pure Local Solutions
| Aspect | Pure Local | OmniMind Hybrid |
|--------|------------|-----------------|
| Cost | $0 | $0-10 |
| Max Quality | Limited | Premium available |
| Flexibility | Low | High |
| Critical Tasks | Risky | Premium backup |

## 🚀 Getting Started

### 1. Basic Setup (Local Only - FREE)
```bash
# Just need Ollama
ollama serve
python3 src/main.py
```

### 2. Hybrid Setup (Local + Premium)
```bash
# Add API keys to .env
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Run with hybrid routing
python3 src/main.py
```

### 3. Monitor Usage
```python
# Check costs anytime
from src.providers.intelligent_router import intelligent_router
print(f"This month: ${intelligent_router.current_month_cost}")
print(f"Budget left: ${intelligent_router.monthly_budget - intelligent_router.current_month_cost}")
```

## 💡 Tips for Cost Optimization

1. **Set Monthly Budget**: System automatically uses local when approaching limit
2. **Use force_local**: For non-critical tasks, force local to save money
3. **Batch Simple Tasks**: Group simple queries to use local models
4. **Review Router Stats**: Check what's using premium models
5. **Adjust Routing Rules**: Customize what triggers premium models

## 🎉 Conclusion

You now have an intelligent system that:
- **Saves Money**: 80-95% of queries use FREE local models
- **Maintains Quality**: Premium models for critical tasks
- **Preserves Privacy**: Local option for sensitive data
- **Scales Smartly**: Automatic budget management
- **Falls Back Gracefully**: Local backup if premium fails

**Typical savings: $40-90/month compared to pure cloud solutions!**

---
*OmniMind Hybrid - Smart AI that respects your budget and privacy*