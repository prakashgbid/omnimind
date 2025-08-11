#!/bin/bash
"""
OSA Installation Script
Installs OSA system-wide like Claude Code
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_DIR="/usr/local/lib/osa"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.osa"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        OSA Installation Script           ║${NC}"
echo -e "${BLUE}║    OmniMind Super Agent Terminal         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo

# Check for Python 3
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. OSA works best with Ollama installed${NC}"
    echo "   Install from: https://ollama.ai"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is required but not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

echo
echo -e "${YELLOW}Installing OSA...${NC}"

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying OSA files..."
sudo cp -r src "$INSTALL_DIR/"
sudo cp -r tests "$INSTALL_DIR/"
sudo cp -r tools "$INSTALL_DIR/"
sudo cp -r web "$INSTALL_DIR/"
sudo cp -r docs "$INSTALL_DIR/"
sudo cp osa "$INSTALL_DIR/"
sudo cp requirements.txt "$INSTALL_DIR/"
sudo cp setup.py "$INSTALL_DIR/"
sudo cp README.md "$INSTALL_DIR/"
sudo cp LICENSE "$INSTALL_DIR/"

# Make OSA executable
sudo chmod +x "$INSTALL_DIR/osa"

# Create symbolic link
echo "Creating system command..."
sudo ln -sf "$INSTALL_DIR/osa" "$BIN_DIR/osa"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user ollama chromadb networkx aiohttp httpx python-dotenv pyyaml numpy scikit-learn

# Try to install optional rich library for better UI
pip3 install --user rich 2>/dev/null || echo -e "${YELLOW}Note: 'rich' library not installed (optional, for better UI)${NC}"

# Create user config directory
echo "Setting up user configuration..."
mkdir -p "$CONFIG_DIR"

# Create default config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cat > "$CONFIG_DIR/config.json" << 'EOF'
{
  "model": "llama3.2:3b",
  "theme": "dark",
  "verbose": false,
  "auto_save": true,
  "enable_thinking": true,
  "enable_learning": true,
  "max_history": 1000
}
EOF
    echo -e "${GREEN}✓ Created default configuration${NC}"
fi

# Download a model if Ollama is installed and no models exist
if command -v ollama &> /dev/null; then
    if ! ollama list 2>/dev/null | grep -q "llama3.2:3b"; then
        echo -e "${YELLOW}Downloading default model (llama3.2:3b)...${NC}"
        echo "This may take a few minutes..."
        ollama pull llama3.2:3b || echo -e "${YELLOW}⚠️  Could not download model. Please run: ollama pull llama3.2:3b${NC}"
    fi
fi

echo
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ OSA Installation Complete!        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Usage:${NC}"
echo "  osa              # Start OSA terminal"
echo "  osa --help       # Show help"
echo "  osa --model <m>  # Use specific model"
echo
echo -e "${BLUE}Quick Commands:${NC}"
echo "  /help     - Show commands"
echo "  /code     - Code mode"
echo "  /think    - Thinking mode"
echo "  /exit     - Exit OSA"
echo
echo -e "${YELLOW}First time setup:${NC}"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Pull a model if needed: ollama pull llama3.2:3b"
echo "  3. Start OSA: osa"
echo
echo -e "${GREEN}Enjoy using OSA! 🚀${NC}"