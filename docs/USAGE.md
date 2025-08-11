# OmniMind Usage Guide 🧠

## What is OmniMind?

OmniMind is your **personal AI with perfect memory**. Unlike ChatGPT or Claude which forget everything between sessions, OmniMind remembers:
- Every conversation you've had
- Every decision and the reasoning behind it
- How different thoughts connect to each other
- The evolution of your ideas over time

**Best part:** It runs 100% locally on your Mac - no internet, no API keys, completely private!

## Quick Start

```bash
# Easiest way to start
./start.sh

# Or run directly
python src/main.py
```

## Core Concepts Explained

### 1. **Memories** 📝
Everything you tell OmniMind is stored as a "memory". These aren't just saved as text - they're converted into mathematical representations (vectors) that capture meaning, allowing OmniMind to find related thoughts even if they use different words.

**Example:**
- You say: "We should use PostgreSQL for the project"
- Later ask: "What database did we choose?"
- OmniMind finds the connection even though "PostgreSQL" ≠ "database"

### 2. **Thinking with Context** 🤔
When you ask OmniMind a question, it:
1. Searches all memories for relevant context
2. Builds a comprehensive understanding
3. Consults one or more AI models
4. Provides an answer that considers your entire history

**Example:**
```
You: "Should we add real-time features?"
OmniMind: *searches memories*
  - Finds: "We chose WebSockets over SSE in March"
  - Finds: "Performance is a key priority"
  - Finds: "Users requested live updates"
Response: "Yes, and we should use WebSockets as we decided in March because..."
```

### 3. **Multi-Model Consensus** 🤝
OmniMind can query multiple AI models and synthesize their responses:
- **Llama 3.2**: Fast, good for quick queries
- **Mixtral**: Balanced, high quality responses
- **DeepSeek Coder**: Specialized for code

The models debate internally and reach a consensus, giving you more reliable answers.

### 4. **Knowledge Graph** 🕸️
Your thoughts don't exist in isolation - they connect! OmniMind builds a graph showing how ideas relate:
```
[Authentication Decision] → influenced → [Security Policy]
                         ↘ led to → [JWT Implementation]
```

## Usage Modes

### CLI Mode (Terminal) 💻

Perfect for developers who live in the terminal.

```bash
python src/main.py cli
```

**Commands:**
- Just type to chat
- `/search [query]` - Search memories
- `/timeline 2024-03-15` - See what you thought on a date
- `/stats` - Memory statistics
- `/help` - All commands
- `/exit` - Quit

**Example Session:**
```
[OmniMind] > Why did we choose React over Vue?

🤔 Thinking...

OmniMind Response:
Based on our discussion from March 2024, we chose React because:
1. Team already had React experience (mentioned March 10)
2. Better ecosystem for our needs (March 12 analysis)
3. TypeScript support was superior (March 15 decision)

[OmniMind] > /search TypeScript decisions

Search Results:
1. [0.92] 2024-03-15: Decided to use TypeScript with strict mode...
2. [0.87] 2024-03-20: TypeScript config should include...
```

### Web UI Mode (Browser) 🌐

Beautiful interface accessible from any browser.

```bash
python src/main.py web
# Opens http://localhost:7860
```

**Features:**
- **Chat Tab**: Conversation with history
- **Search Tab**: Semantic memory search
- **Timeline Tab**: Browse memories by date
- **Knowledge Graph**: Visualize connections
- **Settings**: Configure and export

### API Mode (Python) 🐍

Use OmniMind in your own Python code:

```python
from omnimind import OmniMind

# Initialize
om = OmniMind()

# Remember something
om.remember("Decided to use AWS over GCP for better enterprise features")

# Ask with context
response = om.think("What cloud provider should we use for the new service?")
print(response)
# Output: "Based on our previous decision, we should use AWS because..."

# Search memories
memories = om.search_memories("cloud decisions")
for m in memories:
    print(f"[{m['score']:.2f}] {m['content']}")

# Get timeline
timeline = om.get_timeline("2024-03-01", "2024-03-31")
```

### Quick Query Mode ⚡

For one-off questions:

```bash
# Ask a single question
python src/main.py ask "What framework did we choose?"

# Search memories
python src/main.py search "authentication" --limit 10
```

## Practical Examples

### Example 1: Project Decision Tracking

```python
# Monday: Research phase
om.remember("Evaluated 3 payment providers: Stripe, PayPal, Square")
om.remember("Stripe has best developer experience but 2.9% fees")
om.remember("PayPal has wide adoption but poor API")
om.remember("Square good for retail but limited international")

# Wednesday: Decision time
response = om.think("Which payment provider should we choose?")
# OmniMind responds with context from Monday's research

# Friday: Implementation
om.remember("Implemented Stripe, took 2 days not 1 as expected")

# Month later
response = om.think("How long do payment integrations usually take?")
# OmniMind remembers the Stripe experience
```

### Example 2: Learning from Mistakes

```python
# First project
om.remember("MongoDB was a bad choice - no ACID transactions")

# Next project
response = om.think("Should we use MongoDB?")
# OmniMind warns based on previous experience
```

### Example 3: Building on Ideas

```python
# January
om.remember("Users want a mobile app")

# March
om.remember("Budget approved for mobile development")

# May
response = om.think("What should we prioritize next quarter?")
# OmniMind connects the dots between user request and budget
```

## Advanced Features

### Consensus Building

When accuracy matters, use multiple models:

```python
# Important decision - use consensus
response = om.think(
    "Should we rewrite the entire codebase?",
    use_consensus=True  # Queries 3 models
)
```

### Contextual Projects

Tag memories with projects:

```python
om.remember(
    "Using Next.js for the frontend",
    context={"project": "e-commerce", "tags": "tech-stack,frontend"}
)

# Later, search by project
memories = om.search_memories("project:e-commerce frontend")
```

### Timeline Analysis

See how thoughts evolved:

```python
# What did I think about microservices over time?
jan_thoughts = om.get_timeline("2024-01-01", "2024-01-31")
jun_thoughts = om.get_timeline("2024-06-01", "2024-06-30")

# Compare how perspective changed
```

## Tips & Best Practices

### 1. Be Descriptive
❌ "Use React"
✅ "Decided to use React for the admin dashboard because of team expertise and component reusability needs"

### 2. Record Reasoning
❌ "PostgreSQL is better"
✅ "PostgreSQL is better for our use case because we need JSONB support and complex queries"

### 3. Tag Important Decisions
```python
om.remember(
    "Final decision: PostgreSQL for main database",
    context={"importance": 10, "type": "decision", "final": True}
)
```

### 4. Regular Brain Dumps
Weekly practice:
```python
om.remember("This week I learned: " + weekly_learnings)
om.remember("Mistakes to avoid: " + weekly_mistakes)
om.remember("Ideas to explore: " + weekly_ideas)
```

### 5. Ask "Why" Questions
- "Why did we choose X?"
- "What was our reasoning for Y?"
- "What problems did Z solve?"

## Troubleshooting

### OmniMind won't start
```bash
# Check Ollama is running
ollama serve

# Check you have models
ollama list

# If no models, download one
ollama pull llama3.2:3b
```

### Slow responses
- First response is always slow (model loading)
- Use smaller model: `PRIMARY_MODEL=llama3.2:3b` in .env
- Disable consensus for speed: `use_consensus=False`

### Out of memory
- Use smaller models
- Reduce `MEMORY_SEARCH_LIMIT` in .env
- Clear old memories periodically

### Can't find old memories
- Memories are searched semantically, not by keywords
- Try different phrasings
- Use `/timeline` to browse by date

## Privacy & Security

✅ **100% Local** - No data leaves your machine
✅ **No Internet Required** - Works offline
✅ **No API Keys** - No external services
✅ **Your Data** - Stored in `./data/` folder
✅ **Exportable** - Take your memories anywhere

## Integration Ideas

### With Your IDE
```bash
# Add to .zshrc or .bashrc
alias remember="python ~/omnimind/src/main.py ask"

# Then in terminal
remember "TODO: Refactor auth module to use JWT"
```

### With Git Commits
```bash
# In .gitmessage
git commit -m "feat: add auth" -m "$(remember 'Why did we add auth?')"
```

### With Note-Taking
```python
# Daily notes script
om.remember(f"Daily standup {date}: {standup_notes}")
om.remember(f"Blockers: {blockers}")
```

## Architecture Decisions Explained

### Why Local LLMs?
- **Privacy**: Your thoughts stay yours
- **Cost**: Free after initial setup
- **Speed**: No network latency
- **Reliability**: Works offline

### Why ChromaDB?
- Embedded vector database (no server)
- Fast semantic search
- Persistent storage
- Easy to backup

### Why Multiple Models?
- Different perspectives
- Reduced hallucination
- Specialized capabilities
- Consensus building

### Why Python?
- Best AI ecosystem
- Easy to extend
- Cross-platform
- Great libraries

## Next Steps

1. **Start Using It**: The more you remember, the smarter it gets
2. **Customize Models**: Try different models for your needs
3. **Build Habits**: Daily/weekly memory sessions
4. **Export Insights**: Use the data for reports
5. **Extend It**: Add your own features

## Get Help

- Check README.md for setup
- Run `python src/main.py demo` for quick test
- Look at examples in `examples/` folder
- Submit issues on GitHub

---

Remember: OmniMind is like a second brain - the more you use it, the more valuable it becomes! 🧠✨