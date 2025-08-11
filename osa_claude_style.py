#!/usr/bin/env python3
"""
OSA Terminal with Claude Code-style interface
Professional terminal UI with distinct input areas and formatted responses
"""

import os
import sys
import asyncio
import json
import readline
import atexit
import textwrap
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

# Add the src directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from core.osa_autonomous import OSAAutonomous, IntentType
from core.logger import setup_logger

# Terminal colors and styles
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_GRAY = '\033[100m'
    
    # Special
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'


class ResponseType(Enum):
    """Types of responses OSA can show"""
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"


class OSAClaudeTerminal:
    """OSA Terminal with Claude Code-style interface"""
    
    def __init__(self):
        self.osa = None
        self.config = self.load_config()
        self.setup_readline()
        self.running = True
        self.session_start = datetime.now()
        self.interaction_count = 0
        self.terminal_width = shutil.get_terminal_size().columns
        
        # Configuration
        self.CONFIG_DIR = Path.home() / ".osa"
        self.CONFIG_FILE = self.CONFIG_DIR / "config.json"
        self.HISTORY_FILE = self.CONFIG_DIR / "history.txt"
    
    def load_config(self) -> Dict[str, Any]:
        """Load or create configuration."""
        CONFIG_DIR = Path.home() / ".osa"
        CONFIG_FILE = CONFIG_DIR / "config.json"
        CONFIG_DIR.mkdir(exist_ok=True)
        
        default_config = {
            "model": "llama3.2:3b",
            "auto_save": True,
            "verbose": False,
            "max_history": 1000,
            "theme": "claude",
            "show_timestamps": False
        }
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def save_config(self):
        """Save configuration."""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_readline(self):
        """Setup readline for better input handling."""
        readline.parse_and_bind("tab: complete")
        
        if self.HISTORY_FILE.exists():
            try:
                readline.read_history_file(str(self.HISTORY_FILE))
            except (PermissionError, IOError):
                pass
        else:
            try:
                self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                self.HISTORY_FILE.touch()
                self.HISTORY_FILE.chmod(0o600)
            except:
                pass
        
        readline.set_history_length(self.config.get("max_history", 1000))
        atexit.register(self.save_history)
    
    def save_history(self):
        """Save command history."""
        try:
            readline.write_history_file(str(self.HISTORY_FILE))
        except (PermissionError, IOError):
            pass
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_banner(self):
        """Print minimal OSA banner."""
        self.clear_screen()
        print(f"\n{Colors.BOLD}OSA{Colors.RESET} - Autonomous AI Assistant")
        print(f"{Colors.DIM}I understand what you need automatically{Colors.RESET}\n")
    
    async def initialize_osa(self):
        """Initialize the OSA instance."""
        self.show_thinking("Initializing OSA systems...")
        
        try:
            self.osa = OSAAutonomous(self.config)
            await self.osa.initialize()
            self.clear_thinking()
            return True
        except Exception as e:
            self.show_error(f"Failed to initialize: {e}")
            return False
    
    def draw_input_box(self) -> str:
        """Draw a distinct input box like Claude Code."""
        width = min(self.terminal_width - 4, 100)
        
        # Top border
        print(f"\n{Colors.DIM}╭{'─' * (width - 2)}╮{Colors.RESET}")
        
        # Input area with styled prompt
        prompt = f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}{Colors.CYAN}You{Colors.RESET} "
        
        # Calculate padding for right border
        visible_prompt_len = 5  # "You " without color codes
        padding = width - visible_prompt_len - 3
        
        return prompt
    
    def close_input_box(self, text_len: int = 0):
        """Close the input box after input."""
        width = min(self.terminal_width - 4, 100)
        # Bottom border
        print(f"{Colors.DIM}╰{'─' * (width - 2)}╯{Colors.RESET}")
    
    def show_thinking(self, message: str = "Thinking..."):
        """Show thinking indicator like Claude Code."""
        print(f"\n{Colors.YELLOW}✻{Colors.RESET} {Colors.DIM}{message}{Colors.RESET}", end='', flush=True)
    
    def clear_thinking(self):
        """Clear the thinking line."""
        print('\r' + ' ' * self.terminal_width + '\r', end='', flush=True)
    
    def show_tool_call(self, tool_name: str, params: str = ""):
        """Show tool call like Claude Code."""
        print(f"\n{Colors.CYAN}⏺{Colors.RESET} {Colors.BOLD}{tool_name}{Colors.RESET}", end='')
        if params:
            print(f"{Colors.DIM}({params}){Colors.RESET}")
        else:
            print()
    
    def show_tool_output(self, output: str, collapsed: bool = True):
        """Show tool output with Claude Code style."""
        lines = output.strip().split('\n')
        width = min(self.terminal_width - 6, 94)
        
        # Connector line
        print(f"  {Colors.DIM}⎿{Colors.RESET}  ", end='')
        
        if collapsed and len(lines) > 5:
            # Show first 3 lines
            for i, line in enumerate(lines[:3]):
                if i > 0:
                    print("     ", end='')
                # Truncate long lines
                if len(line) > width:
                    line = line[:width-3] + "..."
                print(line)
            
            # Show collapse indicator
            remaining = len(lines) - 3
            print(f"     {Colors.DIM}… +{remaining} lines (ctrl+r to expand){Colors.RESET}")
        else:
            # Show all lines
            for i, line in enumerate(lines):
                if i > 0:
                    print("     ", end='')
                # Wrap long lines
                if len(line) > width:
                    wrapped = textwrap.wrap(line, width)
                    print(wrapped[0])
                    for wrap_line in wrapped[1:]:
                        print("     " + wrap_line)
                else:
                    print(line)
    
    def show_response(self, response: str, intent_type: Optional[IntentType] = None):
        """Show main response with Claude Code style."""
        # Show tool call for processing
        if intent_type:
            emoji = self.get_intent_emoji(intent_type)
            self.show_tool_call(f"{emoji} {intent_type.value.replace('_', ' ').title()}")
        
        # Format and display response
        lines = response.strip().split('\n')
        
        # For code responses, use code block formatting
        if intent_type in [IntentType.CODE_GENERATION, IntentType.CODE_DEBUG, IntentType.CODE_REFACTOR]:
            self.show_code_response(response)
        else:
            self.show_text_response(response)
    
    def show_code_response(self, code: str):
        """Show code response with syntax highlighting hints."""
        print(f"  {Colors.DIM}⎿{Colors.RESET}  ", end='')
        
        lines = code.strip().split('\n')
        in_code_block = False
        
        for i, line in enumerate(lines):
            if i > 0:
                print("     ", end='')
            
            # Detect code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                print(f"{Colors.DIM}{line}{Colors.RESET}")
            elif in_code_block:
                # Highlight code
                print(f"{Colors.GREEN}{line}{Colors.RESET}")
            else:
                print(line)
    
    def show_text_response(self, text: str):
        """Show text response with proper formatting."""
        print(f"  {Colors.DIM}⎿{Colors.RESET}  ", end='')
        
        lines = text.strip().split('\n')
        width = min(self.terminal_width - 6, 94)
        
        for i, line in enumerate(lines):
            if i > 0:
                print("     ", end='')
            
            # Wrap long lines
            if len(line) > width:
                wrapped = textwrap.wrap(line, width)
                print(wrapped[0])
                for wrap_line in wrapped[1:]:
                    print("     " + wrap_line)
            else:
                print(line)
    
    def show_error(self, error: str):
        """Show error message."""
        print(f"\n{Colors.RED}✗{Colors.RESET} {Colors.BOLD}Error:{Colors.RESET} {error}")
    
    def show_status(self, message: str):
        """Show status message."""
        print(f"\n{Colors.GREEN}✓{Colors.RESET} {message}")
    
    def get_intent_emoji(self, intent: IntentType) -> str:
        """Get emoji for intent type."""
        emoji_map = {
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
        return emoji_map.get(intent, "🤖")
    
    async def process_input(self, user_input: str):
        """Process user input autonomously."""
        self.interaction_count += 1
        
        # Check for exit
        if user_input.lower() in ['exit', 'quit', 'bye', '/exit']:
            await self.shutdown()
            return
        
        # Check for help
        if user_input.lower() in ['help', '/help', '?']:
            self.show_help()
            return
        
        # Show thinking
        self.show_thinking("OSA is analyzing your request...")
        
        try:
            # Process autonomously
            response = await self.osa.process_autonomously(user_input)
            
            # Clear thinking indicator
            self.clear_thinking()
            
            # Parse response to get intent info
            lines = response.split('\n\n', 1)
            if len(lines) > 1:
                status_line = lines[0]
                content = lines[1]
                
                # Extract intent type from status
                intent_type = None
                for intent in IntentType:
                    if intent.value.replace('_', ' ').lower() in status_line.lower():
                        intent_type = intent
                        break
                
                # Show response
                self.show_response(content, intent_type)
            else:
                self.show_response(response)
                
        except Exception as e:
            self.clear_thinking()
            self.show_error(str(e))
    
    def show_help(self):
        """Show help information."""
        help_text = """
╭─────────────────────────────────────────────────────╮
│ OSA Help                                            │
├─────────────────────────────────────────────────────┤
│ Just type naturally - OSA understands:             │
│                                                     │
│ • "Write a Python function..."  → Code generation  │
│ • "Fix this error..."           → Debugging        │
│ • "How can I optimize..."       → Refactoring      │
│ • "Think about..."              → Deep thinking    │
│ • "How do I solve..."           → Problem solving  │
│ • "Teach me about..."           → Learning         │
│ • "What is..."                  → Explanation      │
│ • "Create a story..."           → Creative         │
│ • "Analyze..."                  → Analysis         │
│                                                     │
│ Commands:                                          │
│ • exit, quit - Exit OSA                            │
│ • help, ?    - Show this help                      │
│                                                     │
│ Tips:                                              │
│ • Use arrow keys to navigate history               │
│ • Press Tab for auto-completion                    │
│ • Ctrl+C to cancel current operation               │
│ • Ctrl+D to exit                                    │
╰─────────────────────────────────────────────────────╯
"""
        print(help_text)
    
    async def shutdown(self):
        """Shutdown OSA gracefully."""
        self.show_status("Shutting down OSA...")
        
        # Show session stats
        duration = datetime.now() - self.session_start
        
        print(f"\n{Colors.DIM}Session Summary:{Colors.RESET}")
        print(f"  Duration: {str(duration).split('.')[0]}")
        print(f"  Interactions: {self.interaction_count}")
        
        self.save_history()
        self.save_config()
        
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Goodbye!")
        self.running = False
    
    async def run(self):
        """Main run loop."""
        self.print_banner()
        
        # Initialize OSA
        if not await self.initialize_osa():
            return
        
        # Main interaction loop
        while self.running:
            try:
                # Draw input box and get input
                prompt = self.draw_input_box()
                
                # Get user input with styled prompt
                try:
                    # Use readline for better input handling
                    user_input = input(prompt)
                    
                    # Add right border after input
                    cursor_pos = len("You ") + len(user_input)
                    width = min(self.terminal_width - 4, 100)
                    padding = width - cursor_pos - 2
                    
                    # Move cursor up and add right border
                    print(f"\033[A\033[{cursor_pos + 3}C{' ' * padding}{Colors.DIM}│{Colors.RESET}")
                    
                except EOFError:
                    print()  # New line after prompt
                    await self.shutdown()
                    break
                
                # Close input box
                self.close_input_box()
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Process input
                await self.process_input(user_input.strip())
                
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print(f"\n\n{Colors.YELLOW}!{Colors.RESET} Use 'exit' or Ctrl+D to quit")
                continue
            except Exception as e:
                self.show_error(str(e))
                continue


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OSA - Autonomous AI Assistant with Claude Code-style interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use (e.g., llama3.2:3b)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="OSA Claude-Style 3.0"
    )
    
    args = parser.parse_args()
    
    # Create terminal instance
    terminal = OSAClaudeTerminal()
    
    # Apply arguments
    if args.model:
        terminal.config['model'] = args.model
    
    if args.verbose:
        terminal.config['verbose'] = True
    
    # Run terminal
    try:
        await terminal.run()
    except Exception as e:
        print(f"{Colors.RED}Fatal error:{Colors.RESET} {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Goodbye!")
        sys.exit(0)