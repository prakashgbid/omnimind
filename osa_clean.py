#!/usr/bin/env python3
"""
OSA Clean - Minimal, clean terminal interface
"""

import os
import sys
import asyncio
import readline
import atexit
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.osa_autonomous import OSAAutonomous, IntentType

# Colors
class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    YELLOW = '\033[33m'

async def main():
    print(f"\n{C.BOLD}OSA{C.RESET} - Autonomous AI Assistant")
    print(f"{C.DIM}Type naturally, I'll understand{C.RESET}\n")
    
    # Initialize
    print(f"{C.DIM}Initializing...{C.RESET}", end='', flush=True)
    
    # Suppress logging
    import logging
    logging.getLogger('OSA-Auto').setLevel(logging.ERROR)
    
    osa = OSAAutonomous({"model": "llama3.2:3b"})
    await osa.initialize()
    
    print(f"\r{C.GREEN}✓ Ready!{C.RESET}      \n")
    
    # Main loop
    while True:
        try:
            # Simple prompt with box
            print(f"{C.DIM}┌─────────────────────────────────────────────────────────────┐{C.RESET}")
            user_input = input(f"{C.DIM}│{C.RESET} {C.BOLD}{C.CYAN}You:{C.RESET} ")
            print(f"{C.DIM}└─────────────────────────────────────────────────────────────┘{C.RESET}")
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{C.GREEN}✓{C.RESET} Goodbye!")
                break
            
            # Process
            print(f"\n{C.YELLOW}◆{C.RESET} {C.DIM}Thinking...{C.RESET}", end='', flush=True)
            
            response = await osa.process_autonomously(user_input)
            
            # Clear thinking
            print('\r' + ' ' * 20 + '\r', end='')
            
            # Parse and display
            lines = response.split('\n\n', 1)
            if len(lines) > 1:
                status = lines[0]
                content = lines[1]
                
                # Extract intent
                for intent in IntentType:
                    if intent.value.replace('_', ' ').lower() in status.lower():
                        emoji = get_emoji(intent)
                        print(f"{C.CYAN}◆{C.RESET} {emoji} {intent.value.replace('_', ' ').title()}")
                        break
                
                # Show response
                print(f"  {C.DIM}└{C.RESET} {content[:200]}...")
                if len(content) > 200:
                    print(f"     {C.DIM}[+{len(content)-200} more characters]{C.RESET}")
            else:
                print(f"  {C.DIM}└{C.RESET} {response[:200]}...")
            
            print()
            
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{C.GREEN}✓{C.RESET} Goodbye!")
            break
        except Exception as e:
            print(f"\n{C.RED}✗ Error:{C.RESET} {e}\n")

def get_emoji(intent):
    emojis = {
        IntentType.CODE_GENERATION: "💻",
        IntentType.CODE_DEBUG: "🐛",
        IntentType.CODE_REFACTOR: "🔧",
        IntentType.DEEP_THINKING: "🧠",
        IntentType.PROBLEM_SOLVING: "🎯",
        IntentType.LEARNING: "📚",
        IntentType.EXPLANATION: "💡",
        IntentType.CREATIVE: "🎨",
        IntentType.ANALYSIS: "🔍",
        IntentType.GENERAL_CHAT: "💬",
        IntentType.SYSTEM_TASK: "⚙️"
    }
    return emojis.get(intent, "🤖")

if __name__ == "__main__":
    asyncio.run(main())