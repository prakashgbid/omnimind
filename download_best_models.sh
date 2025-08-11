#!/bin/bash

# Download the 5 Best Free Local LLMs for OmniMind

echo "🤖 Downloading Top 5 Free Local LLMs"
echo "====================================="
echo ""
echo "This will download the best models for different use cases:"
echo ""
echo "1. Llama 3.2 (3B) - Fast general purpose"
echo "2. Mistral (7B) - Excellent reasoning"
echo "3. Phi-3 (3.8B) - Microsoft's efficient model"
echo "4. DeepSeek Coder (6.7B) - Best for code"
echo "5. Gemma 2 (2B) - Google's lightweight model"
echo ""
echo "Total download size: ~20GB"
echo "Storage needed: ~25GB"
echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &>/dev/null &
    sleep 3
fi

# Function to download and report
download_model() {
    local model=$1
    local description=$2
    local size=$3
    
    echo ""
    echo "📥 Downloading: $model"
    echo "   Description: $description"
    echo "   Size: $size"
    echo "   Downloading..."
    
    if ollama pull $model; then
        echo "   ✅ $model downloaded successfully!"
    else
        echo "   ❌ Failed to download $model"
    fi
}

# Download each model
echo ""
echo "Starting downloads (this will take 10-20 minutes)..."
echo "====================================================="

# 1. Llama 3.2 - Meta's latest, very capable
download_model "llama3.2:3b" "Fast, great for conversations" "2GB"

# 2. Mistral - Excellent reasoning and instruction following
download_model "mistral:7b" "Strong reasoning, balanced" "4.1GB"

# 3. Phi-3 - Microsoft's small but powerful
download_model "phi3:mini" "Microsoft's efficient model" "2.3GB"

# 4. DeepSeek Coder - Best for programming
download_model "deepseek-coder:6.7b" "Specialized for code" "3.8GB"

# 5. Gemma 2 - Google's efficient model
download_model "gemma2:2b" "Google's fast lightweight model" "1.6GB"

echo ""
echo "====================================================="
echo "📊 Checking downloaded models..."
echo ""

ollama list

echo ""
echo "✅ Model download complete!"
echo ""
echo "🎯 Model Recommendations:"
echo "========================="
echo ""
echo "For SPEED: Use llama3.2:3b or gemma2:2b"
echo "For QUALITY: Use mistral:7b"
echo "For CODE: Use deepseek-coder:6.7b"
echo "For EFFICIENCY: Use phi3:mini"
echo "For CONSENSUS: Use all 5 together!"
echo ""
echo "🚀 Test the models:"
echo "   ollama run llama3.2:3b"
echo "   ollama run mistral:7b"
echo ""
echo "Or use with OmniMind:"
echo "   python3 src/main.py cli"