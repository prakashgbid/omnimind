#!/bin/bash

# Quick API Key Setup for OmniMind

echo "🔑 OmniMind API Key Setup"
echo "========================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

echo "Choose your LLM provider:"
echo "1. Anthropic (Claude) - Paid"
echo "2. OpenAI (GPT-4) - Free trial available"
echo "3. Google (Gemini) - Free tier available"
echo "4. Local only (Ollama) - Free"
echo ""

read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Get your Anthropic key from:"
        echo "https://console.anthropic.com/settings/keys"
        echo ""
        read -p "Enter your Anthropic API key: " key
        sed -i '' "s/ANTHROPIC_API_KEY=/ANTHROPIC_API_KEY=$key/" .env
        echo "✅ Anthropic key saved"
        ;;
    2)
        echo ""
        echo "Get your OpenAI key from:"
        echo "https://platform.openai.com/api-keys"
        echo ""
        read -p "Enter your OpenAI API key: " key
        sed -i '' "s/OPENAI_API_KEY=/OPENAI_API_KEY=$key/" .env
        echo "✅ OpenAI key saved"
        ;;
    3)
        echo ""
        echo "Get your Google key from:"
        echo "https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Enter your Google API key: " key
        sed -i '' "s/GOOGLE_API_KEY=/GOOGLE_API_KEY=$key/" .env
        echo "✅ Google key saved"
        ;;
    4)
        echo ""
        echo "Using local models only (no API keys needed)"
        sed -i '' "s/USE_LOCAL_MODELS=true/USE_LOCAL_MODELS=true/" .env
        echo ""
        echo "Make sure Ollama is installed:"
        echo "brew install ollama"
        echo "ollama pull llama3.2:3b"
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "Test your configuration:"
echo "python3 test_omnimind.py"
echo ""
echo "Start OmniMind:"
echo "python3 src/main.py cli  # Terminal interface"
echo "python3 src/main.py web  # Browser interface"