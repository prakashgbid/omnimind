#!/bin/bash

echo "🚀 ChatGPT Terminal Access Setup"
echo "================================"
echo ""
echo "This script will help you set up ChatGPT with full terminal access"
echo "using the best method for your system."
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup ChatGPT Desktop App (macOS)
setup_desktop_app() {
    echo "📱 Setting up ChatGPT Desktop App (Recommended for macOS)"
    echo "========================================================="
    
    if [ -d "/Applications/ChatGPT.app" ]; then
        echo "✅ ChatGPT Desktop App already installed"
    else
        echo "Installing ChatGPT Desktop App..."
        
        if command_exists brew; then
            brew install --cask chatgpt
        else
            echo "❌ Homebrew not found. Install manually from:"
            echo "   https://openai.com/chatgpt/desktop/"
            return 1
        fi
    fi
    
    echo ""
    echo "📋 Setup Instructions:"
    echo "1. Open ChatGPT Desktop App"
    echo "2. Log in with your ChatGPT Plus/Pro account"
    echo "3. Switch to GPT-5 or enable Agent Mode"
    echo "4. Go to Settings → Features → Work with Apps → Enable"
    echo "5. Grant permissions for Terminal, VS Code, and file access"
    echo ""
    echo "🔒 Security Tip: Create a dedicated macOS user for agent tasks"
    echo ""
    
    # Open the app
    open -a ChatGPT 2>/dev/null || echo "Launch ChatGPT manually to continue setup"
    
    return 0
}

# Function to setup API Computer Use
setup_api_computer_use() {
    echo "🔧 Setting up OpenAI API Computer Use"
    echo "======================================"
    
    # Check for API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ No OpenAI API key found"
        echo ""
        echo "To set up:"
        echo "1. Get your API key from: https://platform.openai.com/api-keys"
        echo "2. Add to your environment:"
        echo "   export OPENAI_API_KEY='sk-...'"
        echo "3. Or add to ~/.omnimind/.env file"
        echo ""
        read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
        
        if [ -n "$api_key" ]; then
            echo "OPENAI_API_KEY=$api_key" >> ~/.omnimind/.env
            echo "✅ API key saved to ~/.omnimind/.env"
            export OPENAI_API_KEY="$api_key"
        else
            return 1
        fi
    else
        echo "✅ OpenAI API key found"
    fi
    
    # Install Python package
    echo "Installing OpenAI Python library..."
    pip3 install openai
    
    echo ""
    echo "✅ Computer Use API ready!"
    echo ""
    echo "Usage:"
    echo "  python3 -c \"from src.agents.specialized.chatgpt_terminal_agent import *; asyncio.run(demo())\""
    
    return 0
}

# Function to setup OpenAI Codex CLI
setup_codex_cli() {
    echo "💻 Setting up OpenAI Codex CLI"
    echo "=============================="
    
    if command_exists openai-codex; then
        echo "✅ OpenAI Codex CLI already installed"
    else
        echo "Installing OpenAI Codex CLI..."
        
        if [ "$OS_TYPE" = "Darwin" ] && command_exists brew; then
            brew install openai-codex
        else
            pip3 install openai-codex-cli
        fi
    fi
    
    # Configure if not already done
    if [ ! -f ~/.openai-codex/config.json ]; then
        echo ""
        echo "Configuring OpenAI Codex CLI..."
        openai-codex configure
    fi
    
    echo ""
    echo "✅ Codex CLI ready!"
    echo ""
    echo "Usage examples:"
    echo "  openai-codex 'Create a Python web server'"
    echo "  openai-codex 'Fix the bug in main.py'"
    echo "  openai-codex 'Write unit tests for calculator.py'"
    
    return 0
}

# Function to setup ShellGPT
setup_shellgpt() {
    echo "🐚 Setting up ShellGPT"
    echo "====================="
    
    if command_exists sgpt; then
        echo "✅ ShellGPT already installed"
    else
        echo "Installing ShellGPT..."
        pip3 install shell-gpt
    fi
    
    # Check for API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo ""
        echo "⚠️ ShellGPT needs an OpenAI API key"
        read -p "Enter your OpenAI API key: " api_key
        
        if [ -n "$api_key" ]; then
            echo "export OPENAI_API_KEY='$api_key'" >> ~/.bashrc
            echo "export OPENAI_API_KEY='$api_key'" >> ~/.zshrc 2>/dev/null
            export OPENAI_API_KEY="$api_key"
            echo "✅ API key configured"
        else
            echo "❌ API key required for ShellGPT"
            return 1
        fi
    fi
    
    echo ""
    echo "✅ ShellGPT ready!"
    echo ""
    echo "Usage examples:"
    echo "  sgpt 'List all Python files'"
    echo "  sgpt --shell 'Find files larger than 100MB'"
    echo "  sgpt --code 'Write a sorting algorithm'"
    echo "  sgpt --execute 'Update all npm packages'"
    
    return 0
}

# Function to create sandbox environment
create_sandbox() {
    echo "🔒 Creating secure sandbox environment..."
    
    SANDBOX_DIR="$HOME/.omnimind/chatgpt_sandbox"
    mkdir -p "$SANDBOX_DIR"
    
    # Create sandbox README
    cat > "$SANDBOX_DIR/README.md" << 'EOF'
# ChatGPT Sandbox Directory

This is a safe directory for ChatGPT to execute commands and create files.
All agent operations should be contained within this directory for security.

## Security Guidelines
- Always review commands before approval
- Keep sensitive data outside this directory
- Use Git to track changes
- Regularly clean up test files

## Quick Commands
- cd ~/.omnimind/chatgpt_sandbox  # Enter sandbox
- git init                        # Track changes
- git add -A && git commit        # Save snapshot
- rm -rf test_*                   # Clean test files
EOF
    
    echo "✅ Sandbox created at: $SANDBOX_DIR"
    echo ""
}

# Main setup flow
main() {
    echo "Select your preferred ChatGPT terminal access method:"
    echo ""
    echo "1) ChatGPT Desktop App (Easiest - macOS only)"
    echo "2) OpenAI API Computer Use (Most powerful)"
    echo "3) OpenAI Codex CLI (Lightweight)"
    echo "4) ShellGPT (Community option)"
    echo "5) Auto-detect best option"
    echo "6) Install all available methods"
    echo ""
    
    read -p "Enter your choice (1-6): " choice
    echo ""
    
    # Create sandbox regardless of choice
    create_sandbox
    
    case $choice in
        1)
            if [ "$OS_TYPE" = "Darwin" ]; then
                setup_desktop_app
            else
                echo "❌ Desktop App only available on macOS"
                echo "   Try option 2 (API) or 3 (CLI) instead"
            fi
            ;;
        2)
            setup_api_computer_use
            ;;
        3)
            setup_codex_cli
            ;;
        4)
            setup_shellgpt
            ;;
        5)
            echo "🔍 Auto-detecting best option..."
            echo ""
            
            if [ "$OS_TYPE" = "Darwin" ]; then
                setup_desktop_app || setup_api_computer_use || setup_codex_cli || setup_shellgpt
            else
                setup_api_computer_use || setup_codex_cli || setup_shellgpt
            fi
            ;;
        6)
            echo "📦 Installing all available methods..."
            echo ""
            
            [ "$OS_TYPE" = "Darwin" ] && setup_desktop_app
            setup_api_computer_use
            setup_codex_cli
            setup_shellgpt
            ;;
        *)
            echo "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "✅ ChatGPT Terminal Setup Complete!"
    echo "========================================="
    echo ""
    echo "🎯 Quick Test Commands:"
    echo ""
    
    if [ "$OS_TYPE" = "Darwin" ] && [ -d "/Applications/ChatGPT.app" ]; then
        echo "Desktop App:"
        echo "  Open ChatGPT → 'Create a Python hello world and run it'"
        echo ""
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "API Computer Use:"
        echo "  python3 ~/Documents/projects/omnimind/src/agents/specialized/chatgpt_terminal_agent.py"
        echo ""
    fi
    
    if command_exists openai-codex; then
        echo "Codex CLI:"
        echo "  openai-codex 'Create a web server'"
        echo ""
    fi
    
    if command_exists sgpt; then
        echo "ShellGPT:"
        echo "  sgpt 'List all Python files'"
        echo ""
    fi
    
    echo "📚 Documentation:"
    echo "  ~/Documents/projects/omnimind/CHATGPT_TERMINAL_GUIDE.md"
    echo ""
    echo "🔒 Security Reminder:"
    echo "  Always review commands before approval!"
    echo "  Work in sandbox: ~/.omnimind/chatgpt_sandbox/"
}

# Run main function
main