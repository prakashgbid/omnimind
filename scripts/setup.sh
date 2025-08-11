#!/bin/bash

# OmniMind Setup Script
# This script sets up everything you need for OmniMind

echo "🧠 OmniMind Setup Starting..."
echo "================================"
echo ""

# Step 1: Check if Homebrew is installed
echo "📦 Step 1: Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "   ❌ Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "   ✅ Homebrew is installed"
fi

# Step 2: Install Ollama for local LLMs
echo ""
echo "🤖 Step 2: Installing Ollama (Local LLM Runner)..."
echo "   Ollama lets us run LLMs locally without API keys"
if ! command -v ollama &> /dev/null; then
    brew install ollama
    echo "   ✅ Ollama installed"
else
    echo "   ✅ Ollama already installed"
fi

# Step 3: Start Ollama service
echo ""
echo "🚀 Step 3: Starting Ollama service..."
ollama serve &>/dev/null &
sleep 2
echo "   ✅ Ollama service started"

# Step 4: Download AI models
echo ""
echo "📥 Step 4: Downloading AI Models (this takes time and space)..."
echo ""
echo "   We'll download 3 models for different purposes:"
echo "   1. Llama 3.2 (3B) - Fast, good for quick queries (2GB)"
echo "   2. Mixtral (8x7B) - Balanced, good quality (26GB)"  
echo "   3. DeepSeek Coder (7B) - Specialized for code (4GB)"
echo ""
echo "   Note: You can skip any model if you're low on space"
echo ""

# Model 1: Llama 3.2 (small and fast)
read -p "   Download Llama 3.2 3B (2GB)? [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ollama pull llama3.2:3b
    echo "   ✅ Llama 3.2 downloaded"
fi

# Model 2: Mixtral (high quality)
read -p "   Download Mixtral 8x7B (26GB)? [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ollama pull mixtral:8x7b
    echo "   ✅ Mixtral downloaded"
fi

# Model 3: DeepSeek Coder (for code)
read -p "   Download DeepSeek Coder 7B (4GB)? [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ollama pull deepseek-coder:6.7b
    echo "   ✅ DeepSeek Coder downloaded"
fi

# Step 5: Install Python dependencies
echo ""
echo "🐍 Step 5: Installing Python packages..."
echo "   These packages provide:"
echo "   - ChromaDB: Vector database for semantic search"
echo "   - NetworkX: Knowledge graph connections"
echo "   - Gradio: Web interface"
echo "   - Rich: Beautiful CLI output"
echo ""

cd /Users/MAC/Documents/projects/omnimind
pip install -r requirements.txt
echo "   ✅ Python packages installed"

# Step 6: Create data directories
echo ""
echo "📁 Step 6: Creating data directories..."
mkdir -p data/{chromadb,sqlite,graphs,backups}
mkdir -p models/custom
mkdir -p logs
echo "   ✅ Directories created"

# Step 7: Initialize databases
echo ""
echo "💾 Step 7: Initializing databases..."
python3 << EOF
import sqlite3
import os

# Create SQLite database
db_path = '/Users/MAC/Documents/projects/omnimind/data/sqlite/omnimind.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    thought TEXT NOT NULL,
    response TEXT,
    context TEXT,
    embedding_id TEXT,
    tags TEXT,
    project TEXT,
    importance INTEGER DEFAULT 5
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    decision TEXT NOT NULL,
    reasoning TEXT,
    alternatives TEXT,
    outcome TEXT,
    project TEXT,
    participants TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    connection_type TEXT,
    strength REAL,
    FOREIGN KEY (source_id) REFERENCES memories (id),
    FOREIGN KEY (target_id) REFERENCES memories (id)
)
''')

conn.commit()
conn.close()
print("   ✅ SQLite database initialized")
EOF

# Step 8: Create configuration file
echo ""
echo "⚙️ Step 8: Creating configuration..."
cat > /Users/MAC/Documents/projects/omnimind/.env << EOF
# OmniMind Configuration

# Models (local - no API keys needed!)
PRIMARY_MODEL=llama3.2:3b
CONSENSUS_MODELS=llama3.2:3b,mixtral:8x7b,deepseek-coder:6.7b

# Storage
CHROMADB_PATH=./data/chromadb
SQLITE_PATH=./data/sqlite/omnimind.db
GRAPH_PATH=./data/graphs

# Settings
MEMORY_SEARCH_LIMIT=20
CONSENSUS_THRESHOLD=0.7
AUTO_BACKUP=true
BACKUP_INTERVAL_HOURS=24

# UI
WEB_PORT=7860
CLI_HISTORY_FILE=~/.omnimind_history
EOF
echo "   ✅ Configuration created"

# Step 9: Verify installation
echo ""
echo "🔍 Step 9: Verifying installation..."
python3 -c "
import ollama
import chromadb
import networkx
import gradio
print('   ✅ All core packages working')
"

echo ""
echo "================================"
echo "🎉 OmniMind Setup Complete!"
echo "================================"
echo ""
echo "📚 What we've installed:"
echo "   • Ollama: Runs AI models locally"
echo "   • Local LLMs: AI models that work offline"
echo "   • ChromaDB: Searches memories by meaning"
echo "   • SQLite: Stores structured data"
echo "   • NetworkX: Maps knowledge connections"
echo "   • Gradio: Provides web interface"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: python src/main.py"
echo "   2. Open: http://localhost:7860"
echo "   3. Start remembering!"
echo ""
echo "💡 Tips:"
echo "   • Everything is local - no internet needed"
echo "   • Your data is in: ./data/"
echo "   • Add more models: ollama list"
echo ""