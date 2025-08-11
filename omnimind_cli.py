#!/usr/bin/env python3
"""
OmniMind CLI - Interactive interface for your Super Agent peer

Commands:
- chat: Have a conversation
- think: Think about something specific
- brainstorm: Start a brainstorming session  
- recall: Recall memories about a topic
- project: Start or manage projects
- status: Check agent status
- help: Show commands
- exit: Exit
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import readline  # For better input experience
from typing import Optional

from src.omnimind_super_agent import (
    OmniMindSuperAgent,
    ThinkingMode,
    create_omnimind
)


class OmniMindCLI:
    """Command-line interface for OmniMind"""
    
    def __init__(self):
        self.agent: Optional[OmniMindSuperAgent] = None
        self.running = True
        self.commands = {
            'chat': self.chat,
            'think': self.think,
            'brainstorm': self.brainstorm,
            'recall': self.recall,
            'project': self.project,
            'status': self.status,
            'help': self.help,
            'exit': self.exit
        }
        
        # Setup readline for history
        self.history_file = Path.home() / ".omnimind" / "cli_history"
        self.history_file.parent.mkdir(exist_ok=True)
        
        if self.history_file.exists():
            readline.read_history_file(str(self.history_file))
    
    async def initialize(self):
        """Initialize OmniMind agent"""
        print("\n" + "="*60)
        print("🧠 OmniMind Super Agent - Your Intelligent Peer")
        print("="*60)
        print("\nInitializing systems...")
        
        try:
            self.agent = await create_omnimind()
            print("\n✅ All systems online!")
            print("\nType 'help' for commands or just start chatting!")
            print("-"*60 + "\n")
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            print("\nMake sure the ChatGPT MCP server is running:")
            print("  cd ~/Documents/projects/chatgpt-mcp-server")
            print("  ./start_server.sh")
            raise
    
    async def run(self):
        """Main CLI loop"""
        await self.initialize()
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Save to history
                readline.write_history_file(str(self.history_file))
                
                # Check if it's a command
                if user_input.startswith('/'):
                    command = user_input[1:].split()[0]
                    args = user_input[1:].split()[1:]
                    
                    if command in self.commands:
                        await self.commands[command](args)
                    else:
                        print(f"Unknown command: {command}")
                        print("Type '/help' for available commands")
                else:
                    # Regular chat
                    await self.chat([user_input])
                    
            except KeyboardInterrupt:
                print("\n\nUse '/exit' to quit properly")
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def chat(self, args):
        """Chat with OmniMind"""
        if not args:
            print("Usage: /chat <your message> or just type without /")
            return
        
        message = " ".join(args) if isinstance(args, list) else args
        
        print("\n🧠 OmniMind: ", end="", flush=True)
        response = await self.agent.think_with_user(message)
        
        # Print response with formatting
        self._print_formatted(response)
    
    async def think(self, args):
        """Think about something with specific mode"""
        if not args:
            print("Usage: /think <mode> <topic>")
            print("Modes: brainstorm, analytical, strategic, creative, critical, learning")
            return
        
        mode_str = args[0].upper()
        topic = " ".join(args[1:])
        
        try:
            mode = ThinkingMode[mode_str]
        except KeyError:
            print(f"Invalid mode: {mode_str}")
            print("Valid modes: brainstorm, analytical, strategic, creative, critical, learning")
            return
        
        print(f"\n🤔 Thinking ({mode.value})...")
        response = await self.agent.think_with_user(topic, mode=mode, show_thinking=True)
        self._print_formatted(response)
    
    async def brainstorm(self, args):
        """Start brainstorming session"""
        if not args:
            print("Usage: /brainstorm <topic>")
            return
        
        topic = " ".join(args)
        
        print(f"\n🧠 Starting brainstorm session on: {topic}")
        print("Generating ideas from multiple perspectives...\n")
        
        results = await self.agent.brainstorm(topic, duration_minutes=5)
        
        print(f"\n✨ Generated {len(results['ideas'])} ideas!\n")
        
        # Display ideas by source
        for source in ['creative', 'analytical', 'strategic']:
            source_ideas = [i for i in results['ideas'] if i['source'] == source]
            if source_ideas:
                print(f"\n{source.upper()} ideas:")
                for i, idea in enumerate(source_ideas[:5], 1):
                    print(f"  {i}. {idea['idea']}")
        
        print(f"\n📝 Synthesis:")
        self._print_formatted(results['synthesis'][:1000])
    
    async def recall(self, args):
        """Recall memories about a topic"""
        if not args:
            print("Usage: /recall <topic>")
            return
        
        topic = " ".join(args)
        
        print(f"\n🔍 Searching memories about: {topic}")
        memories = await self.agent.recall(topic, limit=5)
        
        if memories:
            print(f"\n📚 Found {len(memories)} relevant memories:\n")
            for i, mem in enumerate(memories, 1):
                print(f"{i}. [{mem['timestamp']}] ({mem['type']})")
                print(f"   {mem['content'][:200]}...")
                print(f"   Relevance: {mem['relevance']:.2%}\n")
        else:
            print("No relevant memories found.")
    
    async def project(self, args):
        """Manage projects"""
        if not args:
            print("Usage: /project new <name> <description>")
            print("       /project list")
            return
        
        subcommand = args[0]
        
        if subcommand == "new":
            if len(args) < 3:
                print("Usage: /project new <name> <description>")
                return
            
            name = args[1]
            description = " ".join(args[2:])
            
            project = await self.agent.start_project(name, description)
            print(f"\n✅ Started project: {project['name']}")
            print(f"   ID: {project['id']}")
            print(f"   Description: {description}")
            
        elif subcommand == "list":
            projects = self.agent.active_projects
            if projects:
                print(f"\n📁 Active Projects ({len(projects)}):\n")
                for pid, proj in projects.items():
                    print(f"  • {proj['name']} (ID: {pid})")
                    print(f"    {proj['description']}")
                    print(f"    Created: {proj['created']}\n")
            else:
                print("No active projects.")
    
    async def status(self, args):
        """Show agent status"""
        status = self.agent.get_status()
        
        print("\n📊 OmniMind Status")
        print("="*40)
        print(f"Session ID: {status['session_id']}")
        print(f"Memory Size: {status['memory_size']} conversations")
        print(f"Active Projects: {len(status['active_projects'])}")
        print(f"Brainstorm Sessions: {status['brainstorm_sessions']}")
        print(f"Current Thoughts: {status['current_thought_count']}")
        print(f"Decision History: {status['decision_history_size']}")
        print(f"\nAvailable Models:")
        for model in status['available_models']:
            print(f"  • {model}")
    
    async def help(self, args):
        """Show help"""
        print("\n📖 OmniMind Commands")
        print("="*40)
        print("Just type normally to chat, or use commands:\n")
        print("/chat <message>     - Chat with OmniMind")
        print("/think <mode> <topic> - Think with specific mode")
        print("/brainstorm <topic> - Start brainstorming")
        print("/recall <topic>     - Recall memories")
        print("/project new <name> <desc> - Start project")
        print("/project list       - List projects")
        print("/status            - Show agent status")
        print("/help              - Show this help")
        print("/exit              - Exit OmniMind")
        print("\nThinking modes: brainstorm, analytical, strategic, creative, critical, learning")
    
    async def exit(self, args):
        """Exit CLI"""
        print("\n👋 Goodbye! OmniMind will remember our conversation.")
        self.running = False
    
    def _print_formatted(self, text):
        """Print text with nice formatting"""
        # Handle thinking markers
        lines = text.split('\n')
        for line in lines:
            if line.startswith('💭') or line.startswith('🧠') or line.startswith('📊') or line.startswith('📚'):
                # Print thinking lines in dim color
                print(f"\033[90m{line}\033[0m")
            elif line.startswith('✅') or line.startswith('✨'):
                # Print success in green
                print(f"\033[92m{line}\033[0m")
            elif line.startswith('❌'):
                # Print errors in red
                print(f"\033[91m{line}\033[0m")
            else:
                # Normal text
                print(line)


async def main():
    """Main entry point"""
    cli = OmniMindCLI()
    
    try:
        await cli.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n✨ Thanks for using OmniMind!")


if __name__ == "__main__":
    asyncio.run(main())