#!/usr/bin/env python3
"""Test the Claude-style interface formatting"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'

print("\n=== Claude Code Style Test ===\n")

# Test input box
width = 78
print(f"{Colors.DIM}╭{'─' * (width - 2)}╮{Colors.RESET}")
print(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} Write a Python function to calculate fibonacci{' ' * 24}{Colors.DIM}│{Colors.RESET}")
print(f"{Colors.DIM}╰{'─' * (width - 2)}╯{Colors.RESET}")

# Test thinking indicator
print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}OSA is analyzing your request...{Colors.RESET}")

# Test tool call
print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}💻 Code Generation{Colors.RESET}")

# Test output with connector
print(f"  {Colors.DIM}⎿{Colors.RESET}  def fibonacci(n):")
print("         \"\"\"Calculate the nth Fibonacci number.\"\"\"")
print("         if n <= 0:")
print("             return 0")
print(f"     {Colors.DIM}… +15 lines (ctrl+r to expand){Colors.RESET}")

print("\n=== Alternative Symbols Test ===\n")

# Test with different connector symbols
symbols = ['⎿', '⎾', '├', '└', '╰', '⤷']
for sym in symbols:
    print(f"  {Colors.DIM}{sym}{Colors.RESET}  Sample output line with connector: {sym}")

print("\n=== Status Messages Test ===\n")

# Test status messages
print(f"{Colors.GREEN}✓{Colors.RESET} Operation completed successfully")
print(f"{Colors.RED}✗{Colors.RESET} {Colors.BOLD}Error:{Colors.RESET} Something went wrong")
print(f"{Colors.YELLOW}!{Colors.RESET} Warning: Be careful")
print(f"{Colors.CYAN}ℹ{Colors.RESET} Info: Just so you know")

print("\n=== Complete Example ===\n")

# Complete example
print(f"{Colors.DIM}╭{'─' * 78}╮{Colors.RESET}")
print(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} What is a neural network?{' ' * 47}{Colors.DIM}│{Colors.RESET}")
print(f"{Colors.DIM}╰{'─' * 78}╯{Colors.RESET}")

print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}Thinking...{Colors.RESET}")

print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}💡 Explanation{Colors.RESET}")
print(f"  {Colors.DIM}⎿{Colors.RESET}  A neural network is a computational model inspired by biological neural")
print("     networks in the brain. It consists of interconnected nodes (neurons)")
print("     organized in layers:")
print("     ")
print("     • Input Layer: Receives the initial data")
print("     • Hidden Layers: Process and transform the data")
print("     • Output Layer: Produces the final result")
print(f"     {Colors.DIM}… +25 lines (ctrl+r to expand){Colors.RESET}")

print(f"\n{Colors.GREEN}✓{Colors.RESET} Response delivered")

print("\n=== Test Complete ===\n")