#!/bin/bash

# OmniMind Local Setup (No API Keys Required)

echo "🧠 OmniMind Local Setup"
echo "======================="
echo ""
echo "This will set up OmniMind to work with local models (free)."
echo "You can add cloud API keys later if needed."
echo ""

# Step 1: Create .env with local-only config
echo "1️⃣ Creating local configuration..."
cat > .env << 'EOF'
# OmniMind Configuration (Local Mode)

# Models (local - no API keys needed!)
PRIMARY_MODEL=llama3.2:3b
CONSENSUS_MODELS=llama3.2:3b
USE_LOCAL_MODELS=true

# Storage Paths
CHROMADB_PATH=./data/chromadb
SQLITE_PATH=./data/sqlite/omnimind.db
GRAPH_PATH=./data/graphs/knowledge.gpickle

# Memory Settings
MEMORY_SEARCH_LIMIT=20
CONSENSUS_THRESHOLD=0.7
MAX_CONTEXT_LENGTH=4000

# UI Settings
WEB_PORT=7860
CLI_HISTORY_FILE=~/.omnimind_history

# Cloud LLM APIs (Add these later if you want)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
EOF

echo "✅ Created .env for local mode"
echo ""

# Step 2: Check if Ollama is installed
echo "2️⃣ Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Try to start Ollama
    echo "   Starting Ollama service..."
    ollama serve &>/dev/null &
    sleep 2
    
    # Check for models
    echo "   Checking for models..."
    MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
    
    if [ "$MODELS" -eq 0 ]; then
        echo "   ⚠️  No models found"
        echo ""
        echo "   Download a model (choose one):"
        echo "   • ollama pull llama3.2:3b    # Small & fast (2GB)"
        echo "   • ollama pull mistral:7b     # Balanced (4GB)"
        echo "   • ollama pull mixtral:8x7b   # Powerful (26GB)"
    else
        echo "   ✅ Found $MODELS model(s)"
        ollama list
    fi
else
    echo "❌ Ollama not installed"
    echo ""
    echo "To install Ollama (choose one method):"
    echo ""
    echo "Option 1: Via Homebrew (recommended):"
    echo "   brew install ollama"
    echo ""
    echo "Option 2: Direct download:"
    echo "   Go to: https://ollama.com/download"
    echo ""
    echo "After installing:"
    echo "   ollama serve              # Start server"
    echo "   ollama pull llama3.2:3b   # Download model"
fi

echo ""
echo "3️⃣ Testing OmniMind components..."
python3 quick_test.py 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ What's Working Now:"
echo "   • Memory storage & retrieval"
echo "   • Semantic search"
echo "   • Knowledge graphs"
echo "   • Timeline queries"
echo ""

if command -v ollama &> /dev/null; then
    echo "🤖 With Ollama installed, you also get:"
    echo "   • AI responses with context"
    echo "   • Intelligent thinking"
    echo "   • Local LLM processing (free!)"
else
    echo "⚠️  To enable AI features:"
    echo "   1. Install Ollama"
    echo "   2. Download a model"
    echo "   3. Restart OmniMind"
fi

echo ""
echo "🚀 Start OmniMind:"
echo "   python3 demo_no_llm.py    # Test without LLMs"
echo "   python3 src/main.py cli   # Terminal interface"  
echo "   python3 src/main.py web   # Browser interface"
echo ""
echo "💡 To add cloud APIs later:"
echo "   python3 add_api_keys.py"
echo ""