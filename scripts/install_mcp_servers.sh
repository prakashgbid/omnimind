#!/bin/bash
# OSA MCP Server Installation Script
# Installs official and popular MCP servers for OSA integration

echo "================================================"
echo "OSA MCP Server Installation"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install Node.js first.${NC}"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ npm found${NC}"
echo ""

# Function to install an MCP server
install_server() {
    local package=$1
    local name=$2
    
    echo -e "${YELLOW}Installing ${name}...${NC}"
    
    if npm list -g "$package" &> /dev/null; then
        echo -e "${GREEN}✓ ${name} is already installed${NC}"
    else
        npm install -g "$package"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ ${name} installed successfully${NC}"
        else
            echo -e "${RED}❌ Failed to install ${name}${NC}"
            return 1
        fi
    fi
    echo ""
}

# Core MCP Servers
echo "📦 Installing Core MCP Servers..."
echo "================================"

# Official Anthropic/ModelContextProtocol servers
install_server "@modelcontextprotocol/server-filesystem" "Filesystem Server"
install_server "@modelcontextprotocol/server-git" "Git Server"
install_server "@modelcontextprotocol/server-github" "GitHub Server"
install_server "@modelcontextprotocol/server-memory" "Memory Server"

# Browser Automation
echo "🌐 Installing Browser Automation Servers..."
echo "==========================================="
install_server "@microsoft/playwright-mcp" "Playwright Server (Microsoft)"
install_server "@modelcontextprotocol/server-puppeteer" "Puppeteer Server"

# Database Servers
echo "🗄️ Installing Database Servers..."
echo "==================================="
install_server "@modelcontextprotocol/server-sqlite" "SQLite Server"

# Note: PostgreSQL server might be in archived repos
echo -e "${YELLOW}Note: PostgreSQL MCP server may need manual installation from archived repos${NC}"
echo ""

# Communication Servers (if available)
echo "💬 Installing Communication Servers..."
echo "======================================="

# Check for Slack MCP server
if npm search slack-mcp-server &> /dev/null; then
    install_server "slack-mcp-server" "Slack Server"
else
    echo -e "${YELLOW}Slack MCP server not found in npm registry${NC}"
fi

echo ""

# Create configuration directory
CONFIG_DIR="$HOME/.osa"
MCP_CONFIG="$CONFIG_DIR/mcp_config.json"

echo "📁 Setting up configuration..."
echo "==============================="

if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}✓ Created configuration directory: $CONFIG_DIR${NC}"
fi

# Create default MCP configuration if it doesn't exist
if [ ! -f "$MCP_CONFIG" ]; then
    cat > "$MCP_CONFIG" << 'EOF'
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$HOME/Documents",
        "$PWD"
      ],
      "enabled": true,
      "auto_start": true
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "enabled": true,
      "auto_start": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": ""
      },
      "enabled": false,
      "auto_start": false
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "enabled": true,
      "auto_start": true
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@microsoft/playwright-mcp"],
      "config": {
        "headless": false,
        "isolated": true
      },
      "enabled": true,
      "auto_start": false
    },
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "$HOME/.osa/osa.db"
      ],
      "enabled": true,
      "auto_start": false
    }
  }
}
EOF
    echo -e "${GREEN}✓ Created default MCP configuration: $MCP_CONFIG${NC}"
else
    echo -e "${GREEN}✓ MCP configuration already exists: $MCP_CONFIG${NC}"
fi

echo ""

# Check for environment variables
echo "🔑 Checking environment variables..."
echo "====================================="

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠ GITHUB_TOKEN not set. GitHub MCP server will not work without it.${NC}"
    echo "  To set it, add to your ~/.bashrc or ~/.zshrc:"
    echo "  export GITHUB_TOKEN='your_github_token_here'"
else
    echo -e "${GREEN}✓ GITHUB_TOKEN is set${NC}"
fi

echo ""

# Summary
echo "================================================"
echo "📊 Installation Summary"
echo "================================================"

# Count installed servers
INSTALLED_COUNT=$(npm list -g --depth=0 2>/dev/null | grep -c "@modelcontextprotocol\|@microsoft/playwright-mcp\|slack-mcp")

echo -e "${GREEN}✓ Installed MCP servers: $INSTALLED_COUNT${NC}"
echo ""
echo "Configuration file: $MCP_CONFIG"
echo ""
echo "To start using MCP servers with OSA:"
echo "1. Edit $MCP_CONFIG to customize server settings"
echo "2. Set any required environment variables (like GITHUB_TOKEN)"
echo "3. Run OSA and the MCP servers will be available"
echo ""
echo -e "${GREEN}✅ MCP server installation complete!${NC}"