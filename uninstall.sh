#!/bin/bash
"""
OSA Uninstall Script
"""

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}OSA Uninstall Script${NC}"
echo "This will remove OSA from your system"
read -p "Are you sure? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled"
    exit 0
fi

echo "Removing OSA..."

# Remove installation
sudo rm -rf /usr/local/lib/osa
sudo rm -f /usr/local/bin/osa

# Ask about config
read -p "Remove user configuration and history? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.osa
    echo -e "${GREEN}✓ User data removed${NC}"
fi

echo -e "${GREEN}✓ OSA has been uninstalled${NC}"