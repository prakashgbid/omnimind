#!/bin/bash
# Test interactive mode with multiple commands

(
echo "What is machine learning?"
sleep 2
echo "Create a simple REST API"
sleep 2
echo "exit"
) | python3 omnimind.py 2>&1 | grep -E "Result:|Enter task:|OmniMind|exit"