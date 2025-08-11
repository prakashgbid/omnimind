#!/bin/bash
# OSA Local Installation Script (No sudo required)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     OSA Local Installation Script        ║${NC}"
echo -e "${BLUE}║    (No admin permissions required)       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found${NC}"
    echo "   Install from: https://ollama.ai"
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Install Python dependencies
echo
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install --user ollama chromadb networkx aiohttp httpx python-dotenv pyyaml numpy scikit-learn 2>/dev/null || true
pip3 install --user rich 2>/dev/null || echo -e "${YELLOW}Note: rich not installed (optional for better UI)${NC}"

# Create user directories
echo -e "${YELLOW}Setting up OSA...${NC}"
mkdir -p ~/.osa
mkdir -p ~/bin

# Create wrapper script
cat > ~/bin/osa << 'EOF'
#!/bin/bash
# OSA Launcher
OSA_DIR="$(dirname "$(readlink -f "$0")")/../Documents/projects/omnimind"
cd "$OSA_DIR" && python3 osa "$@"
EOF

chmod +x ~/bin/osa

# Update the actual osa script path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
sed -i '' "s|OSA_DIR=.*|OSA_DIR=\"$SCRIPT_DIR\"|" ~/bin/osa 2>/dev/null || \
sed -i "s|OSA_DIR=.*|OSA_DIR=\"$SCRIPT_DIR\"|" ~/bin/osa

# Create config if doesn't exist
if [ ! -f ~/.osa/config.json ]; then
    cat > ~/.osa/config.json << 'EOF'
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
    echo -e "${GREEN}✓ Created configuration${NC}"
fi

# Check if ~/bin is in PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo
    echo -e "${YELLOW}Adding ~/bin to PATH...${NC}"
    
    # Detect shell
    if [ -f ~/.zshrc ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
        echo -e "${GREEN}✓ Added to ~/.zshrc${NC}"
        SHELL_RC="~/.zshrc"
    elif [ -f ~/.bashrc ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        echo -e "${GREEN}✓ Added to ~/.bashrc${NC}"
        SHELL_RC="~/.bashrc"
    else
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.profile
        echo -e "${GREEN}✓ Added to ~/.profile${NC}"
        SHELL_RC="~/.profile"
    fi
fi

# Check for Ollama models
if command -v ollama &> /dev/null; then
    if ! ollama list 2>/dev/null | grep -q "llama3.2:3b"; then
        echo
        echo -e "${YELLOW}No models found. To download the default model:${NC}"
        echo "  ollama pull llama3.2:3b"
    fi
fi

echo
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ OSA Installation Complete!        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

# Instructions based on whether PATH needs updating
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo -e "${YELLOW}⚠️  IMPORTANT: Reload your shell configuration:${NC}"
    echo -e "${BLUE}   source $SHELL_RC${NC}"
    echo -e "${BLUE}   OR restart your terminal${NC}"
    echo
fi

echo -e "${BLUE}To start OSA:${NC}"
if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
    echo "  osa"
else
    echo "  ~/bin/osa"
    echo
    echo "After reloading shell:"
    echo "  osa"
fi

echo
echo -e "${BLUE}Quick Start:${NC}"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Pull a model (if needed): ollama pull llama3.2:3b"
echo "  3. Start OSA: osa"
echo
echo -e "${BLUE}Commands:${NC}"
echo "  /help  - Show all commands"
echo "  /code  - Enter code mode"
echo "  /think - Enter thinking mode"
echo "  /exit  - Exit OSA"
echo
echo -e "${GREEN}Enjoy using OSA! 🚀${NC}"