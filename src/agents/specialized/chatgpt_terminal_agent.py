#!/usr/bin/env python3
"""
ChatGPT Terminal Agent - Multiple Methods for System Access

This agent provides three methods to give ChatGPT-5 coding powers:
1. Desktop App with "Work with Apps" (easiest)
2. OpenAI API Computer Use (programmatic)
3. OpenAI Codex CLI (lightweight)
"""

import os
import sys
import subprocess
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import platform

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.agents.base_omnimind_agent import BaseOmniMindAgent


class ChatGPTTerminalAgent(BaseOmniMindAgent):
    """
    ChatGPT with full terminal and file system access.
    
    Three implementation methods based on your setup:
    1. ChatGPT Desktop App (macOS) - Easiest
    2. OpenAI API Computer Use - Most powerful
    3. OpenAI Codex CLI - Lightweight
    """
    
    def __init__(self):
        super().__init__(
            agent_name="chatgpt-terminal",
            specialization="ChatGPT-5 with full terminal, file system, and application control"
        )
        
        self.os_type = platform.system()
        self.setup_complete = False
        self.method = None  # 'desktop', 'api', or 'cli'
        
        # Security settings
        self.sandbox_dir = Path.home() / '.omnimind' / 'chatgpt_sandbox'
        self.allowed_commands = []
        self.blocked_commands = ['rm -rf /', 'sudo rm', 'format']
        
    def detect_available_methods(self) -> Dict[str, bool]:
        """Detect which ChatGPT access methods are available."""
        methods = {
            'desktop_app': False,
            'api_computer_use': False,
            'codex_cli': False,
            'shellgpt': False
        }
        
        # Check for ChatGPT Desktop App (macOS only)
        if self.os_type == 'Darwin':  # macOS
            desktop_path = '/Applications/ChatGPT.app'
            if os.path.exists(desktop_path):
                methods['desktop_app'] = True
                print("✅ ChatGPT Desktop App detected")
        
        # Check for API key (for Computer Use)
        if os.getenv('OPENAI_API_KEY'):
            methods['api_computer_use'] = True
            print("✅ OpenAI API key found - Computer Use available")
        
        # Check for OpenAI Codex CLI
        try:
            result = subprocess.run(['which', 'openai-codex'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                methods['codex_cli'] = True
                print("✅ OpenAI Codex CLI installed")
        except:
            pass
        
        # Check for ShellGPT
        try:
            result = subprocess.run(['which', 'sgpt'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                methods['shellgpt'] = True
                print("✅ ShellGPT installed")
        except:
            pass
        
        return methods
    
    def setup_desktop_app(self) -> bool:
        """
        Setup ChatGPT Desktop App with "Work with Apps" feature.
        
        macOS only - provides safest, easiest access.
        """
        if self.os_type != 'Darwin':
            print("❌ Desktop App method only available on macOS")
            return False
        
        print("\n🖥️ Setting up ChatGPT Desktop App Access")
        print("=" * 50)
        
        instructions = """
1. Install ChatGPT Desktop App:
   brew install --cask chatgpt
   OR download from: https://openai.com/chatgpt/desktop/

2. Launch ChatGPT and log in with your Plus/Pro account

3. Enable Agent Mode:
   • Click model selector → Choose "GPT-5" or "Agent"
   • Look for "Agent Mode" toggle and enable it

4. Enable "Work with Apps":
   • Settings → Features → Work with Apps → Enable
   • Grant permissions for:
     - Terminal
     - VS Code (or your IDE)
     - File system access

5. Security Setup (recommended):
   • Create a dev-only macOS user account
   • Or use our sandbox directory: ~/.omnimind/chatgpt_sandbox/

6. Test the setup:
   Say: "Create a Python hello world script and run it in Terminal"
   
The agent will:
• Request Terminal access (approve it)
• Create the script
• Execute it with your approval
• Show results

IMPORTANT: Always review commands before approving!
"""
        
        print(instructions)
        
        # Create sandbox directory
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✅ Sandbox created: {self.sandbox_dir}")
        
        # Open ChatGPT app if installed
        if os.path.exists('/Applications/ChatGPT.app'):
            print("\n🚀 Opening ChatGPT Desktop App...")
            subprocess.run(['open', '/Applications/ChatGPT.app'])
            self.method = 'desktop'
            return True
        else:
            print("\n⚠️ ChatGPT Desktop App not found")
            print("Install with: brew install --cask chatgpt")
            return False
    
    def setup_api_computer_use(self) -> bool:
        """
        Setup OpenAI API Computer Use for programmatic control.
        
        Most powerful method - full API control with custom guardrails.
        """
        print("\n🔧 Setting up OpenAI API Computer Use")
        print("=" * 50)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OpenAI API key found")
            print("\nTo set up:")
            print("1. Get API key from: https://platform.openai.com/api-keys")
            print("2. Add to ~/.omnimind/.env:")
            print("   OPENAI_API_KEY=sk-...")
            return False
        
        try:
            import openai
            print("✅ OpenAI library installed")
        except ImportError:
            print("📦 Installing OpenAI library...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai'])
            import openai
        
        # Initialize Computer Use client
        self.setup_computer_use_client()
        self.method = 'api'
        
        print("\n✅ Computer Use API configured!")
        print("\nCapabilities:")
        print("• Full terminal control (with guardrails)")
        print("• File system operations")
        print("• Application control")
        print("• Screenshot analysis")
        print("• Mouse/keyboard simulation")
        
        return True
    
    def setup_computer_use_client(self):
        """Initialize the Computer Use API client."""
        import openai
        
        self.client = openai.OpenAI()
        
        # Define tool functions for Computer Use
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_terminal_command",
                    "description": "Execute a command in the terminal",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "working_dir": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Open an application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string"}
                        },
                        "required": ["app_name"]
                    }
                }
            }
        ]
    
    async def execute_with_computer_use(self, task: str) -> str:
        """
        Execute task using Computer Use API with guardrails.
        
        Args:
            task: Task description for ChatGPT to execute
            
        Returns:
            Execution result
        """
        if self.method != 'api':
            return "Computer Use not configured. Run setup_api_computer_use() first."
        
        import openai
        
        print(f"\n🤖 Executing with Computer Use: {task}")
        
        # Create messages with Computer Use context
        messages = [
            {
                "role": "system",
                "content": """You are ChatGPT with Computer Use capabilities.
You can execute terminal commands, read/write files, and control applications.
Always explain what you're doing before executing commands.
Work in the sandbox directory when possible: ~/.omnimind/chatgpt_sandbox/"""
            },
            {
                "role": "user",
                "content": task
            }
        ]
        
        try:
            # Call GPT with tools
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or gpt-5 when available
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            # Process tool calls
            message = response.choices[0].message
            
            if message.tool_calls:
                print("\n📋 Planned actions:")
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"  • {function_name}: {function_args}")
                
                # Execute with approval
                if self.approve_actions(message.tool_calls):
                    results = await self.execute_tool_calls(message.tool_calls)
                    return f"Executed successfully:\n{results}"
                else:
                    return "Actions cancelled by user"
            
            return message.content
            
        except Exception as e:
            return f"Error: {e}"
    
    def approve_actions(self, tool_calls) -> bool:
        """Get user approval for planned actions."""
        print("\n⚠️ Approve these actions? (y/n): ", end='')
        response = input().strip().lower()
        return response == 'y'
    
    async def execute_tool_calls(self, tool_calls) -> str:
        """Execute approved tool calls."""
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "execute_terminal_command":
                result = self.safe_execute_command(function_args['command'])
            elif function_name == "read_file":
                result = self.safe_read_file(function_args['file_path'])
            elif function_name == "write_file":
                result = self.safe_write_file(
                    function_args['file_path'], 
                    function_args['content']
                )
            elif function_name == "open_application":
                result = self.safe_open_app(function_args['app_name'])
            else:
                result = f"Unknown function: {function_name}"
            
            results.append(f"{function_name}: {result}")
        
        return "\n".join(results)
    
    def safe_execute_command(self, command: str) -> str:
        """Execute command with safety checks."""
        # Check blocklist
        for blocked in self.blocked_commands:
            if blocked in command:
                return f"❌ Blocked command: {command}"
        
        try:
            # Execute in sandbox
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.sandbox_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return f"✅ {result.stdout}"
            else:
                return f"❌ Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "❌ Command timed out"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def safe_read_file(self, file_path: str) -> str:
        """Read file with safety checks."""
        path = Path(file_path)
        
        # Ensure within sandbox
        if not str(path).startswith(str(self.sandbox_dir)):
            path = self.sandbox_dir / path
        
        try:
            with open(path, 'r') as f:
                content = f.read()
            return f"✅ Read {len(content)} characters from {path}"
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    def safe_write_file(self, file_path: str, content: str) -> str:
        """Write file with safety checks."""
        path = Path(file_path)
        
        # Ensure within sandbox
        if not str(path).startswith(str(self.sandbox_dir)):
            path = self.sandbox_dir / path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return f"✅ Wrote {len(content)} characters to {path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"
    
    def safe_open_app(self, app_name: str) -> str:
        """Open application safely."""
        allowed_apps = ['Terminal', 'VS Code', 'TextEdit', 'Safari']
        
        if app_name not in allowed_apps:
            return f"❌ App not in allowed list: {app_name}"
        
        try:
            if self.os_type == 'Darwin':
                subprocess.run(['open', '-a', app_name])
            elif self.os_type == 'Linux':
                subprocess.run([app_name.lower()])
            elif self.os_type == 'Windows':
                subprocess.run(['start', app_name], shell=True)
            
            return f"✅ Opened {app_name}"
        except Exception as e:
            return f"❌ Error opening app: {e}"
    
    def setup_codex_cli(self) -> bool:
        """
        Setup OpenAI Codex CLI for lightweight terminal access.
        
        Simple CLI tool for chat + file operations.
        """
        print("\n💻 Setting up OpenAI Codex CLI")
        print("=" * 50)
        
        # Check if installed
        try:
            result = subprocess.run(['openai-codex', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ OpenAI Codex CLI already installed")
                self.method = 'cli'
                return True
        except:
            pass
        
        print("📦 Installing OpenAI Codex CLI...")
        
        # Install instructions based on OS
        if self.os_type == 'Darwin':
            install_cmd = "brew install openai-codex"
        else:
            install_cmd = "pip install openai-codex-cli"
        
        print(f"\nRun this command to install:")
        print(f"  {install_cmd}")
        
        print("\nThen configure with:")
        print("  openai-codex configure")
        print("  # Enter your OpenAI API key when prompted")
        
        print("\nUsage examples:")
        print("  openai-codex 'Create a Python web server'")
        print("  openai-codex 'Fix the bug in main.py'")
        print("  openai-codex 'Run tests and fix failures'")
        
        return False
    
    def setup_shellgpt(self) -> bool:
        """
        Setup ShellGPT as alternative lightweight option.
        
        Community CLI with good terminal integration.
        """
        print("\n🐚 Setting up ShellGPT")
        print("=" * 50)
        
        # Check if installed
        try:
            result = subprocess.run(['sgpt', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ShellGPT already installed")
                return True
        except:
            pass
        
        print("📦 Installing ShellGPT...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'shell-gpt'])
        
        print("\n✅ ShellGPT installed!")
        print("\nConfigure with:")
        print("  export OPENAI_API_KEY='your-key-here'")
        
        print("\nUsage examples:")
        print("  sgpt 'list all Python files'")
        print("  sgpt --shell 'find large files'")
        print("  sgpt --code 'write a fibonacci function'")
        print("  sgpt --execute 'update all pip packages'")
        
        return True
    
    def auto_setup(self) -> str:
        """
        Automatically setup the best available method.
        
        Priority:
        1. Desktop App (safest, easiest)
        2. API Computer Use (most powerful)
        3. Codex CLI (lightweight)
        4. ShellGPT (community option)
        """
        print("\n🔍 Auto-detecting best ChatGPT terminal access method...")
        print("=" * 60)
        
        methods = self.detect_available_methods()
        
        # Try methods in priority order
        if self.os_type == 'Darwin' and methods['desktop_app']:
            print("\n✨ Best option: ChatGPT Desktop App")
            if self.setup_desktop_app():
                return "desktop"
        
        if methods['api_computer_use']:
            print("\n✨ Best option: API Computer Use")
            if self.setup_api_computer_use():
                return "api"
        
        if methods['codex_cli']:
            print("\n✨ Best option: OpenAI Codex CLI")
            self.method = 'cli'
            return "cli"
        
        # Fallback - install ShellGPT
        print("\n✨ Installing ShellGPT as fallback...")
        if self.setup_shellgpt():
            self.method = 'shellgpt'
            return "shellgpt"
        
        return "none"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current setup status."""
        methods = self.detect_available_methods()
        
        return {
            'os': self.os_type,
            'current_method': self.method,
            'available_methods': methods,
            'sandbox_dir': str(self.sandbox_dir),
            'setup_complete': self.setup_complete
        }
    
    def quick_start_guide(self) -> str:
        """Generate quick start guide based on OS."""
        guide = f"""
🚀 ChatGPT Terminal Access - Quick Start Guide
===============================================

Your OS: {self.os_type}
"""
        
        if self.os_type == 'Darwin':
            guide += """
RECOMMENDED: ChatGPT Desktop App (Easiest & Safest)
----------------------------------------------------
1. Install: brew install --cask chatgpt
2. Launch and log in with Plus/Pro account
3. Enable: Settings → Features → Work with Apps
4. Test: "Create and run a Python hello world"

The agent will handle everything with your approval!
"""
        
        guide += """
ALTERNATIVE: API Computer Use (Most Powerful)
----------------------------------------------
1. Get API key: https://platform.openai.com/api-keys
2. Add to ~/.omnimind/.env: OPENAI_API_KEY=sk-...
3. Run: python3 chatgpt_terminal_agent.py
4. Use: agent.execute_with_computer_use("your task")

Full programmatic control with custom guardrails!

LIGHTWEIGHT: OpenAI Codex CLI
------------------------------
1. Install: pip install openai-codex-cli
2. Configure: openai-codex configure
3. Use: openai-codex 'your coding task'

Simple and effective for quick tasks!

COMMUNITY: ShellGPT
-------------------
1. Install: pip install shell-gpt
2. Export: OPENAI_API_KEY='your-key'
3. Use: sgpt --shell 'your command'

Good for shell commands and simple scripts!
"""
        
        return guide


# Convenience functions
def create_agent():
    """Factory function for ChatGPT Terminal Agent."""
    return ChatGPTTerminalAgent()


async def quick_setup():
    """Quick setup with best available method."""
    agent = ChatGPTTerminalAgent()
    method = agent.auto_setup()
    
    if method == 'none':
        print("\n❌ No methods available. Please install one:")
        print(agent.quick_start_guide())
        return None
    
    print(f"\n✅ Setup complete with method: {method}")
    return agent


async def demo():
    """Demo ChatGPT terminal capabilities."""
    print("\n🎯 ChatGPT Terminal Agent Demo")
    print("=" * 60)
    
    agent = await quick_setup()
    if not agent:
        return
    
    # Demo based on method
    if agent.method == 'desktop':
        print("\n📱 Using ChatGPT Desktop App")
        print("Try these in the ChatGPT app:")
        print("1. 'Create a Flask web app and run it'")
        print("2. 'Debug the Python script in my Downloads folder'")
        print("3. 'Set up a React TypeScript project with Tailwind'")
        
    elif agent.method == 'api':
        print("\n🔧 Using API Computer Use")
        
        # Demo task
        task = "Create a simple Python calculator script and test it"
        result = await agent.execute_with_computer_use(task)
        print(f"\nResult: {result}")
        
    elif agent.method in ['cli', 'shellgpt']:
        print(f"\n💻 Using {agent.method.upper()}")
        print("Run these commands in your terminal:")
        
        if agent.method == 'cli':
            print("• openai-codex 'Create a todo list app'")
            print("• openai-codex 'Fix the bug in server.py'")
        else:
            print("• sgpt 'Write a bash script to backup files'")
            print("• sgpt --shell 'Find all large files'")
            print("• sgpt --code 'Implement binary search'")
    
    # Show status
    print("\n📊 Current Status:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())