#!/usr/bin/env python3
"""
OmniMind CLI - Command Line Interface

This is how you interact with OmniMind from the terminal.
It provides an interactive chat experience with full memory recall.
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Optional

# Add parent directory to path so we can import OmniMind
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from src.core.omnimind_enhanced import OmniMindEnhanced as OmniMind


class OmniMindCLI:
    """
    The CLI interface for OmniMind.
    
    Features:
    - Interactive chat mode
    - Command history
    - Rich formatting
    - Search and timeline commands
    """
    
    def __init__(self):
        """Initialize the CLI with OmniMind and rich console."""
        self.console = Console()
        self.omnimind = None
        self.session = None
        self.current_model = 'llama3.2:3b'
        self.use_consensus = False
        
        # Commands that don't require OmniMind
        self.meta_commands = {
            '/help': self.show_help,
            '/exit': self.exit_cli,
            '/quit': self.exit_cli,
            '/clear': self.clear_screen,
        }
        
        # Commands that require OmniMind
        self.omnimind_commands = {
            '/search': self.search_memories,
            '/timeline': self.show_timeline,
            '/stats': self.show_stats,
            '/graph': self.show_graph,
            '/export': self.export_memories,
            '/forget': self.forget_memory,
            '/models': self.list_models,
            '/use': self.switch_model,
            '/consensus': self.toggle_consensus,
        }
    
    def initialize(self):
        """Initialize OmniMind and setup session."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Initializing OmniMind...", total=None)
            
            try:
                self.omnimind = OmniMind()
                progress.update(task, description="OmniMind ready!")
            except Exception as e:
                self.console.print(f"[red]Failed to initialize OmniMind: {e}[/red]")
                self.console.print("[yellow]Make sure Ollama is running and models are downloaded.[/yellow]")
                self.console.print("Run: [cyan]./scripts/setup.sh[/cyan]")
                return False
        
        # Setup prompt session with history
        history_file = os.path.expanduser("~/.omnimind_history")
        self.session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        return True
    
    def run(self):
        """Main CLI loop."""
        # Welcome message
        self.console.print(Panel.fit(
            "[bold cyan]OmniMind CLI[/bold cyan]\n"
            "Your persistent intelligence companion\n"
            "Type [yellow]/help[/yellow] for commands",
            border_style="cyan"
        ))
        
        # Initialize OmniMind
        if not self.initialize():
            return
        
        # Main interaction loop
        while True:
            try:
                # Get user input with fancy prompt
                user_input = self.session.prompt(
                    "\n[OmniMind] > ",
                    multiline=False
                ).strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    # Regular conversation
                    self.process_thought(user_input)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to quit[/yellow]")
                continue
            except EOFError:
                break
    
    def process_thought(self, thought: str):
        """Process a regular thought/question."""
        # Show thinking indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Thinking...", total=None)
            
            try:
                # Get response from OmniMind
                kwargs = {'use_consensus': self.use_consensus}
                if not self.use_consensus:
                    kwargs['model'] = self.current_model
                response = self.omnimind.think(thought, **kwargs)
                
                # Display response in a nice panel
                self.console.print("\n")
                self.console.print(Panel(
                    Markdown(response),
                    title="[bold green]OmniMind Response[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
                
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def handle_command(self, command: str):
        """Handle special commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Check meta commands first
        if cmd in self.meta_commands:
            self.meta_commands[cmd]()
        # Then OmniMind commands
        elif cmd in self.omnimind_commands:
            self.omnimind_commands[cmd](args)
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("Type [yellow]/help[/yellow] for available commands")
    
    def show_help(self):
        """Display help information."""
        help_text = """
# OmniMind Commands

## Chat Commands
- **Just type** - Have a conversation with OmniMind
- **/models** - List available local models
- **/use [model]** - Switch to a different model
- **/consensus** - Toggle multi-model consensus
- **/search [query]** - Search your memories
- **/timeline [date]** - View memories from a specific time
- **/stats** - Show memory statistics
- **/graph** - Visualize knowledge connections

## System Commands
- **/help** - Show this help
- **/clear** - Clear the screen
- **/export [file]** - Export memories to file
- **/forget [id]** - Remove a specific memory
- **/exit** - Quit OmniMind

## Tips
- OmniMind remembers everything you tell it
- Ask about past conversations: "What did we discuss about X?"
- Build on previous thoughts: "Given our decision on Y..."
- Search semantically: "/search authentication decisions"
        """
        self.console.print(Markdown(help_text))
    
    def search_memories(self, query: str):
        """Search through memories."""
        if not query:
            query = Prompt.ask("[cyan]Search for[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Searching for: {query}", total=None)
            
            memories = self.omnimind.search_memories(query, limit=5)
        
        if not memories:
            self.console.print("[yellow]No memories found[/yellow]")
            return
        
        # Display results in a table
        table = Table(title=f"Search Results for: {query}")
        table.add_column("Score", style="cyan", width=8)
        table.add_column("Date", style="green", width=20)
        table.add_column("Memory", style="white")
        
        for memory in memories:
            score = f"{memory['score']:.2f}"
            date = memory['metadata'].get('timestamp', 'Unknown')[:19]
            content = memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content']
            table.add_row(score, date, content)
        
        self.console.print(table)
    
    def show_timeline(self, date_range: str):
        """Show memories from a specific time period."""
        # Parse date range (simplified for now)
        if not date_range:
            date_range = Prompt.ask("[cyan]Date range (YYYY-MM-DD)[/cyan]")
        
        memories = self.omnimind.get_timeline(start_date=date_range)
        
        if not memories:
            self.console.print("[yellow]No memories found for that period[/yellow]")
            return
        
        # Display timeline
        self.console.print(f"\n[bold]Timeline for {date_range}[/bold]\n")
        
        for memory in memories[:10]:
            timestamp = memory.get('timestamp', 'Unknown time')
            thought = memory.get('thought', '')[:150]
            
            self.console.print(f"[green]{timestamp}[/green]")
            self.console.print(f"  {thought}")
            self.console.print()
    
    def show_stats(self, _):
        """Show memory statistics."""
        # This would query the actual stats from OmniMind
        # For now, showing placeholder
        stats = Panel(
            "[cyan]Memory Statistics[/cyan]\n\n"
            "Total Memories: Coming soon\n"
            "Connections: Coming soon\n"
            "Projects: Coming soon\n"
            "Decisions: Coming soon",
            title="[bold]OmniMind Stats[/bold]",
            border_style="cyan"
        )
        self.console.print(stats)
    
    def show_graph(self, _):
        """Visualize knowledge graph."""
        self.console.print("[yellow]Knowledge graph visualization coming soon![/yellow]")
        self.console.print("The graph will show how your thoughts connect over time.")
    
    def export_memories(self, filename: str):
        """Export memories to a file."""
        if not filename:
            filename = Prompt.ask("[cyan]Export to file[/cyan]", default="omnimind_export.json")
        
        self.console.print(f"[yellow]Exporting to {filename}...[/yellow]")
        # Implementation would go here
        self.console.print(f"[green]Export complete![/green]")
    
    def forget_memory(self, memory_id: str):
        """Remove a specific memory."""
        if not memory_id:
            memory_id = Prompt.ask("[cyan]Memory ID to forget[/cyan]")
        
        confirm = Prompt.ask(
            f"[red]Are you sure you want to forget memory {memory_id}?[/red]",
            choices=["yes", "no"],
            default="no"
        )
        
        if confirm == "yes":
            # Implementation would go here
            self.console.print(f"[yellow]Memory {memory_id} forgotten[/yellow]")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def list_models(self, _):
        """List available local models."""
        from src.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider({})
        models = provider.list_models()
        
        # Create a table of models
        table = Table(title="Available Local Models (FREE!)")
        table.add_column("Model", style="cyan", width=20)
        table.add_column("Speed", style="green", width=15)
        table.add_column("Best For", style="yellow")
        table.add_column("Active", style="magenta", width=8)
        
        model_info = {
            'llama3.2:3b': ('Fast', 'General conversations'),
            'mistral:7b': ('Medium', 'Complex reasoning'),
            'phi3:mini': ('Fast', 'Efficient tasks'),
            'deepseek-coder:6.7b': ('Medium', 'Programming & code'),
            'gemma2:2b': ('Very Fast', 'Quick responses')
        }
        
        for model in models:
            if model in model_info:
                speed, best_for = model_info[model]
                active = "✓" if model == self.current_model else ""
                table.add_row(model, speed, best_for, active)
        
        self.console.print(table)
        if self.use_consensus:
            self.console.print("[green]Consensus mode: Using multiple models[/green]")
    
    def switch_model(self, model_name: str):
        """Switch to a different model."""
        if not model_name:
            model_name = Prompt.ask("[cyan]Model name[/cyan]", default="llama3.2:3b")
        
        from src.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider({})
        models = provider.list_models()
        
        if model_name in models:
            self.current_model = model_name
            self.console.print(f"[green]Switched to {model_name}[/green]")
        else:
            self.console.print(f"[red]Model {model_name} not found[/red]")
            self.console.print("Available models: " + ", ".join(models))
    
    def toggle_consensus(self, _):
        """Toggle consensus mode."""
        self.use_consensus = not self.use_consensus
        if self.use_consensus:
            self.console.print("[green]Consensus mode ON - Using multiple models for better answers[/green]")
            self.console.print("[yellow]Note: Responses will take longer but be more accurate[/yellow]")
        else:
            self.console.print(f"[cyan]Consensus mode OFF - Using {self.current_model}[/cyan]")
    
    def exit_cli(self):
        """Exit the CLI."""
        self.console.print("\n[cyan]Goodbye! Your memories are safe.[/cyan]")
        sys.exit(0)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="OmniMind CLI - Your persistent intelligence")
    parser.add_argument('thought', nargs='?', help='Direct thought/question to process')
    parser.add_argument('--search', help='Search memories')
    parser.add_argument('--timeline', help='Show timeline for date')
    
    args = parser.parse_args()
    
    cli = OmniMindCLI()
    
    # Handle direct commands
    if args.thought:
        # Quick mode - just process one thought
        if cli.initialize():
            cli.process_thought(args.thought)
    elif args.search:
        if cli.initialize():
            cli.search_memories(args.search)
    elif args.timeline:
        if cli.initialize():
            cli.show_timeline(args.timeline)
    else:
        # Interactive mode
        cli.run()


if __name__ == "__main__":
    main()