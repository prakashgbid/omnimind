#!/usr/bin/env python3
"""
OSA Smart Terminal - Fully Autonomous AI Assistant
No manual mode switching - OSA figures out what you need automatically
"""

import os
import sys
import asyncio
import json
import readline
import atexit
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add the src directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from core.osa_autonomous import OSAAutonomous
from core.logger import setup_logger

# Rich terminal UI (optional)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.spinner import Spinner
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Configuration
CONFIG_DIR = Path.home() / ".osa"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.txt"


class OSASmartTerminal:
    """OSA Smart Terminal - Fully autonomous, no manual modes."""
    
    def __init__(self):
        self.osa = None
        self.config = self.load_config()
        self.setup_readline()
        self.running = True
        self.session_start = datetime.now()
        self.interaction_count = 0
        
    def load_config(self) -> Dict[str, Any]:
        """Load or create configuration."""
        CONFIG_DIR.mkdir(exist_ok=True)
        
        default_config = {
            "model": "llama3.2:3b",
            "auto_save": True,
            "verbose": False,
            "max_history": 1000
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
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_readline(self):
        """Setup readline for better input handling."""
        readline.parse_and_bind("tab: complete")
        
        if HISTORY_FILE.exists():
            try:
                readline.read_history_file(str(HISTORY_FILE))
            except (PermissionError, IOError):
                pass
        else:
            try:
                HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                HISTORY_FILE.touch()
                HISTORY_FILE.chmod(0o600)
            except:
                pass
        
        readline.set_history_length(self.config.get("max_history", 1000))
        atexit.register(self.save_history)
    
    def save_history(self):
        """Save command history."""
        try:
            readline.write_history_file(str(HISTORY_FILE))
        except (PermissionError, IOError):
            pass
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_banner(self):
        """Print OSA banner."""
        self.clear_screen()
        
        if RICH_AVAILABLE:
            banner_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██████  ███████  █████      OSA Smart v2.0              ║
║    ██    ██ ██      ██   ██     Autonomous AI Assistant     ║
║    ██    ██ ███████ ███████                                 ║
║    ██    ██      ██ ██   ██     No modes. Just intelligence.║
║     ██████  ███████ ██   ██     I figure out what you need. ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
            """
            console.print(banner_text, style="bold cyan")
            console.print()
            console.print("[dim]I automatically understand your intent and respond accordingly.[/dim]")
            console.print("[dim]Just tell me what you need - no commands required![/dim]")
            console.print()
        else:
            print("="*60)
            print("OSA Smart v2.0 - Autonomous AI Assistant")
            print("No modes. Just intelligence.")
            print("="*60)
            print("\nI automatically understand your intent and respond accordingly.")
            print("Just tell me what you need - no commands required!\n")
        
        print("Type 'exit' or press Ctrl+D to quit\n")
    
    async def initialize_osa(self):
        """Initialize the OSA instance."""
        if RICH_AVAILABLE:
            with console.status("[bold green]Initializing OSA intelligence...", spinner="dots"):
                try:
                    self.osa = OSAAutonomous(self.config)
                    await self.osa.initialize()
                    console.print("✨ [bold green]OSA is ready to assist you![/bold green]")
                    return True
                except Exception as e:
                    console.print(f"[bold red]❌ Failed to initialize: {e}[/bold red]")
                    return False
        else:
            print("🚀 Initializing OSA intelligence...")
            try:
                self.osa = OSAAutonomous(self.config)
                await self.osa.initialize()
                print("✨ OSA is ready to assist you!")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize: {e}")
                return False
    
    def get_prompt(self) -> str:
        """Get the command prompt."""
        # Simple, clean prompt
        return "You> "
    
    async def process_input(self, user_input: str):
        """Process user input autonomously."""
        self.interaction_count += 1
        
        # Check for exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            await self.shutdown()
            return
        
        # Show thinking indicator
        if RICH_AVAILABLE:
            with console.status("[bold cyan]OSA is thinking...", spinner="dots2"):
                response = await self.osa.process_autonomously(user_input)
        else:
            print("🤔 OSA is thinking...")
            response = await self.osa.process_autonomously(user_input)
        
        # Display response
        if RICH_AVAILABLE:
            # Split status from response
            lines = response.split('\n\n', 1)
            if len(lines) > 1:
                status, content = lines
                console.print(f"\n[dim]{status}[/dim]")
                console.print(Panel(content, title="OSA Response", border_style="green"))
            else:
                console.print(Panel(response, title="OSA Response", border_style="green"))
        else:
            print("\n" + "="*60)
            print(response)
            print("="*60 + "\n")
    
    async def shutdown(self):
        """Shutdown OSA gracefully."""
        print("\n👋 Thanks for using OSA Smart!")
        
        # Show session stats
        duration = datetime.now() - self.session_start
        if RICH_AVAILABLE:
            stats = f"""
Session Statistics:
• Duration: {str(duration).split('.')[0]}
• Interactions: {self.interaction_count}
• Model: {self.config['model']}
"""
            console.print(Panel(stats, title="Session Summary", border_style="dim"))
        else:
            print(f"\nSession Duration: {str(duration).split('.')[0]}")
            print(f"Interactions: {self.interaction_count}")
        
        self.save_history()
        self.save_config()
        
        print("\n✨ Goodbye!")
        self.running = False
    
    async def run(self):
        """Main run loop."""
        self.print_banner()
        
        # Initialize OSA
        if not await self.initialize_osa():
            return
        
        print()
        
        # Main interaction loop
        while self.running:
            try:
                # Get input
                prompt_text = self.get_prompt()
                
                if RICH_AVAILABLE:
                    user_input = console.input(prompt_text)
                else:
                    user_input = input(prompt_text)
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Process input
                await self.process_input(user_input.strip())
                
            except EOFError:
                # Ctrl+D pressed
                await self.shutdown()
                break
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print("\n💡 Type 'exit' or press Ctrl+D to quit")
                continue
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[bold red]❌ Error: {e}[/bold red]")
                else:
                    print(f"❌ Error: {e}")
                continue


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OSA Smart - Autonomous AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
OSA Smart automatically understands what you need.
No manual modes or commands required!

Examples:
  "Write a Python function to sort a list"     → Generates code
  "Why is my code throwing this error?"        → Debugs code
  "Think deeply about consciousness"           → Deep thinking
  "Explain quantum computing"                  → Explanation
  "How do I solve this math problem?"          → Problem solving
  "Create a story about robots"                → Creative writing
        """
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
        version="OSA Smart 2.0"
    )
    
    args = parser.parse_args()
    
    # Create terminal instance
    terminal = OSASmartTerminal()
    
    # Apply arguments
    if args.model:
        terminal.config['model'] = args.model
    
    if args.verbose:
        terminal.config['verbose'] = True
    
    # Run terminal
    try:
        await terminal.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)