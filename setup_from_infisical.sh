#!/bin/bash

# Setup OmniMind with API Keys from Infisical

echo "🔐 OmniMind API Key Setup from Infisical"
echo "========================================"
echo ""
echo "Please get your API keys from Infisical:"
echo "https://app.infisical.com/projects/secret-management/74508327-34e2-43c2-b5d1-dda08dad998b/overview"
echo ""
echo "Look for these keys in your Infisical dashboard:"
echo "  • OPENAI_API_KEY"
echo "  • ANTHROPIC_API_KEY"
echo "  • GOOGLE_API_KEY or GEMINI_API_KEY"
echo ""

# Function to update .env file
update_env() {
    local key_name=$1
    local key_value=$2
    
    if grep -q "^${key_name}=" .env 2>/dev/null; then
        # Update existing key
        sed -i '' "s/^${key_name}=.*/${key_name}=${key_value}/" .env
    else
        # Add new key
        echo "${key_name}=${key_value}" >> .env
    fi
}

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || touch .env
fi

echo "Enter the API keys from Infisical (or press Enter to skip):"
echo ""

# OpenAI
read -p "1. OpenAI API Key (sk-...): " openai_key
if [ ! -z "$openai_key" ]; then
    update_env "OPENAI_API_KEY" "$openai_key"
    echo "   ✅ OpenAI key added"
fi

# Anthropic
read -p "2. Anthropic API Key (sk-ant-...): " anthropic_key
if [ ! -z "$anthropic_key" ]; then
    update_env "ANTHROPIC_API_KEY" "$anthropic_key"
    echo "   ✅ Anthropic key added"
fi

# Google/Gemini
read -p "3. Google/Gemini API Key (AIza...): " google_key
if [ ! -z "$google_key" ]; then
    update_env "GOOGLE_API_KEY" "$google_key"
    echo "   ✅ Google key added"
fi

echo ""
echo "✅ Configuration updated!"
echo ""

# Test the setup
echo "Testing OmniMind with your API keys..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

openai = os.getenv('OPENAI_API_KEY', '')
anthropic = os.getenv('ANTHROPIC_API_KEY', '')
google = os.getenv('GOOGLE_API_KEY', '')

print('API Key Status:')
print(f'  OpenAI:    {'✅ Set' if openai else '❌ Not set'} {f'({len(openai)} chars)' if openai else ''}')
print(f'  Anthropic: {'✅ Set' if anthropic else '❌ Not set'} {f'({len(anthropic)} chars)' if anthropic else ''}')
print(f'  Google:    {'✅ Set' if google else '❌ Not set'} {f'({len(google)} chars)' if google else ''}')
" 2>/dev/null || echo "Note: Install python-dotenv for verification: pip install python-dotenv"

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo "1. Test OmniMind with cloud LLMs:"
echo "   python3 test_with_llm.py"
echo ""
echo "2. Start using OmniMind:"
echo "   python3 src/main.py cli  # Terminal interface"
echo "   python3 src/main.py web  # Web interface"
echo ""
echo "3. For future updates from Infisical:"
echo "   You can also use Infisical CLI to sync secrets automatically"
echo "   See: https://infisical.com/docs/cli/overview"