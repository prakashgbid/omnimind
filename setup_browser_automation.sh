#!/bin/bash

echo "🌐 Setting up Browser Automation for ChatGPT Plus Access"
echo "========================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "📦 Installing Playwright for browser automation..."
pip3 install playwright

echo ""
echo "🌐 Installing Chromium browser..."
playwright install chromium

echo ""
echo "📱 Installing browser dependencies..."
playwright install-deps

echo ""
echo "✅ Browser automation setup complete!"
echo ""
echo "🚀 You can now use ChatGPT Plus through browser automation!"
echo ""
echo "Usage:"
echo "------"
echo "1. Run the free premium access script:"
echo "   python3 free_premium_access.py"
echo ""
echo "2. First time setup:"
echo "   - The browser will open"
echo "   - Log into your ChatGPT Plus account"
echo "   - Session will be saved for future use"
echo ""
echo "3. After login, you have unlimited access to:"
echo "   • GPT-4/GPT-5"
echo "   • Code Interpreter"
echo "   • DALL-E 3"
echo "   • Web Browsing"
echo "   • All ChatGPT Plus features"
echo ""
echo "All for $0 API costs using your $20/month subscription!"