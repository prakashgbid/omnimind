#!/bin/bash

# OmniMind Startup Script
# Run your FREE local AI system!

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║                                            ║"
echo "║        🧠 OmniMind v2.0 🧠                ║"
echo "║                                            ║"
echo "║   Your FREE Persistent Intelligence        ║"
echo "║   5 Local LLMs • Perfect Memory • \$0/mo    ║"
echo "║                                            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo "Please install Ollama first:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Start Ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama service..."
    ollama serve &>/dev/null &
    sleep 3
fi

# Check available models
echo "📦 Checking local models..."
MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
if [ "$MODELS" -eq 0 ]; then
    echo "⚠️  No models found. Download them with:"
    echo "  ./download_best_models.sh"
    echo ""
fi

# Show available models
echo ""
echo "Available Local Models (FREE!):"
ollama list 2>/dev/null | grep -E "(llama3.2|mistral|phi3|deepseek|gemma2)" | while read -r line; do
    echo "  ✅ $line"
done

echo ""
echo "Choose how to run OmniMind:"
echo ""
echo "  1) 💬 CLI - Interactive terminal"
echo "  2) 🌐 Web - Browser interface (recommended)"
echo "  3) 🎯 Quick - Ask a single question"
echo "  4) 🧪 Demo - Run quick demo"
echo "  5) 📊 Info - Show system info"
echo ""

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Starting CLI interface..."
        echo "Commands: /help, /models, /consensus, /search"
        echo ""
        python3 src/main.py cli
        ;;
    2)
        echo ""
        echo "Starting web interface..."
        echo "Opening browser at http://localhost:7860"
        echo "Press Ctrl+C to stop"
        echo ""
        python3 src/main.py web
        ;;
    3)
        echo ""
        read -p "Ask your question: " question
        echo ""
        python3 src/main.py ask "$question"
        ;;
    4)
        echo ""
        echo "Running demo..."
        python3 src/main.py demo
        ;;
    5)
        echo ""
        echo "System Information:"
        echo "==================="
        echo ""
        echo "🖥️  System:"
        echo "  • OS: $(uname -s)"
        echo "  • Python: $(python3 --version)"
        echo "  • Ollama: $(ollama --version 2>/dev/null | head -1)"
        echo ""
        echo "📦 Models:"
        ollama list 2>/dev/null | tail -n +2 | head -5
        echo ""
        echo "💾 Storage:"
        echo "  • Models: $(du -sh ~/.ollama/models 2>/dev/null | cut -f1)"
        echo "  • OmniMind Data: $(du -sh data 2>/dev/null | cut -f1)"
        echo ""
        echo "💰 Cost Analysis:"
        echo "  • API Costs: \$0/month"
        echo "  • Rate Limits: None"
        echo "  • Privacy: 100% local"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac