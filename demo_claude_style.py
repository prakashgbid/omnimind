#!/usr/bin/env python3
"""
Demo of OSA's Claude Code-style interface
Shows the beautiful terminal formatting and autonomous features
"""

import time

# Terminal colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'

def print_demo():
    print("\n" + "="*80)
    print("OSA CLAUDE CODE-STYLE INTERFACE DEMO")
    print("="*80)
    print("\nThis demo shows OSA's beautiful terminal interface inspired by Claude Code.\n")
    
    # Demo 1: Code Generation
    print("─" * 80)
    print("Demo 1: Code Generation Request")
    print("─" * 80)
    
    # Input box
    width = 78
    print(f"\n{Colors.DIM}╭{'─' * width}╮{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} Write a Python function to reverse a string{' ' * 28}{Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}╰{'─' * width}╯{Colors.RESET}")
    
    time.sleep(0.5)
    
    # Thinking
    print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}OSA is analyzing your request...{Colors.RESET}")
    
    time.sleep(1)
    
    # Clear thinking and show response
    print("\r" + " " * 50 + "\r", end='')
    
    print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}💻 Code Generation{Colors.RESET} {Colors.DIM}(confidence: 95%){Colors.RESET}")
    print(f"  {Colors.DIM}⎿{Colors.RESET}  def reverse_string(s):")
    print("         \"\"\"Reverse a string efficiently.\"\"\"")
    print("         return s[::-1]")
    print("     ")
    print("     # Example usage:")
    print("     result = reverse_string(\"Hello World\")")
    print("     print(result)  # Output: \"dlroW olleH\"")
    
    time.sleep(1)
    
    # Demo 2: Debugging
    print("\n" + "─" * 80)
    print("Demo 2: Debug Request")
    print("─" * 80)
    
    print(f"\n{Colors.DIM}╭{'─' * width}╮{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} Why does my list index throw an error?{' ' * 33}{Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}╰{'─' * width}╯{Colors.RESET}")
    
    time.sleep(0.5)
    
    print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}Thinking...{Colors.RESET}")
    
    time.sleep(1)
    
    print("\r" + " " * 50 + "\r", end='')
    
    print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}🐛 Code Debug{Colors.RESET} {Colors.DIM}(confidence: 88%){Colors.RESET}")
    print(f"  {Colors.DIM}⎿{Colors.RESET}  List index errors typically occur when:")
    print("     • Accessing index beyond list length")
    print("     • Using negative index incorrectly")
    print("     • Empty list access")
    print(f"     {Colors.DIM}… +15 lines (ctrl+r to expand){Colors.RESET}")
    
    time.sleep(1)
    
    # Demo 3: Deep Thinking
    print("\n" + "─" * 80)
    print("Demo 3: Deep Thinking Request")
    print("─" * 80)
    
    print(f"\n{Colors.DIM}╭{'─' * width}╮{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} Think about the nature of consciousness{' ' * 33}{Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}╰{'─' * width}╯{Colors.RESET}")
    
    time.sleep(0.5)
    
    print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}Engaging deep thinking mode...{Colors.RESET}")
    
    time.sleep(1.5)
    
    print("\r" + " " * 50 + "\r", end='')
    
    print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}🧠 Deep Thinking{Colors.RESET} {Colors.DIM}(confidence: 92%){Colors.RESET}")
    print(f"  {Colors.DIM}⎿{Colors.RESET}  Consciousness represents one of the most profound mysteries in")
    print("     philosophy and neuroscience. At its core, consciousness involves")
    print("     subjective experience - the \"what it is like\" quality of awareness.")
    print(f"     {Colors.DIM}… +42 lines (ctrl+r to expand){Colors.RESET}")
    
    time.sleep(1)
    
    # Show session summary
    print("\n" + "─" * 80)
    print("Session Summary")
    print("─" * 80)
    
    print(f"\n{Colors.GREEN}✓{Colors.RESET} 3 requests processed successfully")
    print(f"{Colors.CYAN}ℹ{Colors.RESET} Intent detection accuracy: 91.7%")
    print(f"{Colors.YELLOW}⚡{Colors.RESET} Average response time: 1.2s")
    
    print("\n" + "="*80)
    print("KEY FEATURES DEMONSTRATED:")
    print("="*80)
    print("✅ Distinct input boxes with professional borders")
    print("✅ Thinking indicators during processing")
    print("✅ Tool call display with intent detection")
    print("✅ Collapsible output with line counts")
    print("✅ Status messages with colored icons")
    print("✅ Automatic intent detection - no manual modes!")
    
    print("\n" + "="*80)
    print("OSA: Professional AI assistance with Claude Code elegance!")
    print("="*80 + "\n")

if __name__ == "__main__":
    print_demo()