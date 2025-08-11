#!/usr/bin/env python3
"""
OSA Command Approval System
Interactive command approval with countdown timer like Claude Code
"""

import asyncio
import sys
import select
import termios
import tty
import time
from typing import Optional, Tuple, List
from enum import Enum


class ApprovalChoice(Enum):
    """User's approval choice"""
    YES = 1
    NO = 2
    TIMEOUT = 3
    CANCELLED = 4


class CommandApproval:
    """Interactive command approval with countdown timer"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.original_settings = None
        
    def draw_approval_box(self, command: str, description: str = "", 
                         countdown: int = -1, selected: int = 1) -> None:
        """Draw the approval dialog box"""
        # Clear previous output
        print('\033[2J\033[H', end='')
        
        # Calculate box width
        lines = command.split('\n')
        max_width = max(len(line) for line in lines) if lines else 80
        box_width = min(max(max_width + 4, 80), 170)
        
        # Top border
        print(f"╭{'─' * (box_width - 2)}╮")
        
        # Title
        title = "│ Bash command"
        print(f"{title}{' ' * (box_width - len(title) - 1)}│")
        print(f"│{' ' * (box_width - 2)}│")
        
        # Command content
        for line in lines:
            if len(line) > box_width - 6:
                # Wrap long lines
                wrapped = [line[i:i+box_width-6] for i in range(0, len(line), box_width-6)]
                for wrap_line in wrapped:
                    print(f"│   {wrap_line}{' ' * (box_width - len(wrap_line) - 4)}│")
            else:
                print(f"│   {line}{' ' * (box_width - len(line) - 4)}│")
        
        # Description if provided
        if description:
            print(f"│{' ' * (box_width - 2)}│")
            print(f"│   {description}{' ' * (box_width - len(description) - 4)}│")
        
        print(f"│{' ' * (box_width - 2)}│")
        
        # Question
        question = "│ Do you want to proceed?"
        if countdown >= 0:
            question += f" (auto-proceeding in {countdown}s)"
        print(f"{question}{' ' * (box_width - len(question) - 1)}│")
        
        # Options
        option1 = "   1. Yes"
        option2 = "   2. No, and explain what to do differently"
        
        if selected == 1:
            option1 = " ❯ 1. Yes ✓"  # Show checkmark for default
            print(f"│ \033[32m{option1}\033[0m{' ' * (box_width - len(option1) - 2)}│")
        else:
            print(f"│ {option1}{' ' * (box_width - len(option1) - 2)}│")
            
        if selected == 2:
            option2 = " ❯ 2. No, and explain what to do differently"
            print(f"│ \033[31m{option2}\033[0m{' ' * (box_width - len(option2) - 2)}│")
        else:
            print(f"│ {option2} (esc){' ' * (box_width - len(option2) - 7)}│")
        
        # Bottom border
        print(f"╰{'─' * (box_width - 2)}╯")
        
        # Instructions
        if countdown >= 0:
            print(f"\n\033[2mPress 1 for Yes, 2 or ESC for No, or wait {countdown}s for auto-proceed\033[0m")
        else:
            print("\n\033[2mPress 1 for Yes, 2 or ESC for No\033[0m")
    
    def get_char_with_timeout(self, timeout: float) -> Optional[str]:
        """Get a single character with timeout"""
        if sys.platform == 'win32':
            # Windows implementation
            import msvcrt
            start_time = time.time()
            while True:
                if msvcrt.kbhit():
                    return msvcrt.getch().decode('utf-8', errors='ignore')
                if time.time() - start_time > timeout:
                    return None
                time.sleep(0.01)
        else:
            # Unix/Linux/Mac implementation
            try:
                # Set terminal to raw mode
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                
                # Check for input with timeout
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                
                if rlist:
                    char = sys.stdin.read(1)
                    return char
                else:
                    return None
            finally:
                # Restore terminal settings
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    async def get_approval(self, command: str, description: str = "",
                          auto_approve: bool = True) -> Tuple[ApprovalChoice, Optional[str]]:
        """
        Get user approval for a command with countdown timer
        
        Args:
            command: The command to approve
            description: Optional description of what the command does
            auto_approve: Whether to auto-approve after timeout
            
        Returns:
            Tuple of (choice, explanation) where explanation is only set if user chose NO
        """
        selected = 1  # Default to Yes
        countdown = self.timeout if auto_approve else -1
        start_time = time.time()
        
        try:
            while True:
                # Update countdown
                if auto_approve:
                    elapsed = time.time() - start_time
                    countdown = max(0, self.timeout - int(elapsed))
                    
                    # Auto-approve on timeout
                    if elapsed >= self.timeout:
                        print("\n\033[32m✓ Auto-proceeding with command...\033[0m")
                        return (ApprovalChoice.TIMEOUT, None)
                
                # Draw the dialog
                self.draw_approval_box(command, description, countdown, selected)
                
                # Get user input with short timeout for countdown update
                char = self.get_char_with_timeout(0.1)
                
                if char:
                    if char == '1':
                        print("\n\033[32m✓ Proceeding with command...\033[0m")
                        return (ApprovalChoice.YES, None)
                    elif char == '2' or char == '\x1b':  # 2 or ESC
                        print("\n\033[31m✗ Command cancelled.\033[0m")
                        explanation = input("What should be done differently? ")
                        return (ApprovalChoice.NO, explanation)
                    elif char == '\x03':  # Ctrl+C
                        print("\n\033[33m⚠ Cancelled by user\033[0m")
                        return (ApprovalChoice.CANCELLED, None)
                    elif char in ['j', 'J']:  # Down arrow alternative
                        selected = 2
                    elif char in ['k', 'K']:  # Up arrow alternative  
                        selected = 1
                    elif char == '\r' or char == '\n':  # Enter
                        if selected == 1:
                            print("\n\033[32m✓ Proceeding with command...\033[0m")
                            return (ApprovalChoice.YES, None)
                        else:
                            print("\n\033[31m✗ Command cancelled.\033[0m")
                            explanation = input("What should be done differently? ")
                            return (ApprovalChoice.NO, explanation)
                        
        except KeyboardInterrupt:
            print("\n\033[33m⚠ Cancelled by user\033[0m")
            return (ApprovalChoice.CANCELLED, None)
        except Exception as e:
            print(f"\n\033[31m✗ Error: {e}\033[0m")
            return (ApprovalChoice.CANCELLED, None)
    
    def format_command_for_display(self, command: str, max_width: int = 160) -> List[str]:
        """Format a command for display in the approval box"""
        lines = []
        for line in command.split('\n'):
            if len(line) > max_width:
                # Wrap long lines
                while len(line) > max_width:
                    # Try to break at a space
                    break_point = line.rfind(' ', 0, max_width)
                    if break_point == -1:
                        break_point = max_width
                    lines.append(line[:break_point])
                    line = line[break_point:].lstrip()
                if line:
                    lines.append(line)
            else:
                lines.append(line)
        return lines


class SmartCommandAnalyzer:
    """Analyzes commands to determine if they need approval"""
    
    # Safe commands that don't need approval
    SAFE_COMMANDS = [
        'ls', 'pwd', 'echo', 'cat', 'grep', 'find', 'which',
        'date', 'whoami', 'uname', 'hostname', 'df', 'du',
        'ps', 'top', 'htop', 'free', 'uptime', 'w', 'who'
    ]
    
    # Dangerous commands that always need approval
    DANGEROUS_COMMANDS = [
        'rm', 'sudo', 'chmod', 'chown', 'dd', 'format',
        'mkfs', 'fdisk', 'parted', 'shutdown', 'reboot',
        'kill', 'killall', 'systemctl', 'service'
    ]
    
    # Commands that modify files/state
    MODIFYING_COMMANDS = [
        'mv', 'cp', 'mkdir', 'touch', 'sed', 'awk',
        'git', 'npm', 'pip', 'apt', 'yum', 'brew',
        'docker', 'kubectl', 'terraform'
    ]
    
    @classmethod
    def needs_approval(cls, command: str) -> bool:
        """Determine if a command needs user approval"""
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm -rf', 'rm -fr', 'sudo rm',
            '> /dev/', 'dd if=', 'mkfs',
            ':(){:|:&};:', 'fork bomb'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return True
        
        # Get the base command
        base_command = command_lower.split()[0] if command_lower else ""
        base_command = base_command.split('/')[-1]  # Handle full paths
        
        # Always approve dangerous commands
        if base_command in cls.DANGEROUS_COMMANDS:
            return True
        
        # Check modifying commands
        if base_command in cls.MODIFYING_COMMANDS:
            return True
        
        # Check for piping to dangerous commands
        if '|' in command:
            parts = command.split('|')
            for part in parts[1:]:  # Check all parts after first pipe
                part_cmd = part.strip().split()[0] if part.strip() else ""
                if part_cmd in cls.DANGEROUS_COMMANDS:
                    return True
        
        # Check for output redirection to system files
        if '>' in command or '>>' in command:
            # Check if redirecting to system directories
            system_dirs = ['/etc', '/usr', '/bin', '/sbin', '/boot', '/sys', '/proc']
            for sys_dir in system_dirs:
                if sys_dir in command:
                    return True
        
        # Safe by default for simple/safe commands
        if base_command in cls.SAFE_COMMANDS:
            return False
        
        # Default to requiring approval for unknown commands
        return True
    
    @classmethod
    def get_risk_level(cls, command: str) -> str:
        """Get the risk level of a command"""
        command_lower = command.lower().strip()
        base_command = command_lower.split()[0] if command_lower else ""
        
        if base_command in cls.DANGEROUS_COMMANDS or 'sudo' in command_lower:
            return "HIGH"
        elif base_command in cls.MODIFYING_COMMANDS:
            return "MEDIUM"
        elif base_command in cls.SAFE_COMMANDS:
            return "LOW"
        else:
            return "UNKNOWN"


# Example usage
async def test_approval():
    """Test the approval system"""
    approver = CommandApproval(timeout=5)
    
    # Test different commands
    test_commands = [
        ("ls -la", "List all files in current directory"),
        ("git add -A && git commit -m 'Test commit'", "Stage and commit all changes"),
        ("rm -rf /tmp/test", "Remove test directory")
    ]
    
    for cmd, desc in test_commands:
        print(f"\n{'='*60}")
        print(f"Testing command: {cmd}")
        
        if SmartCommandAnalyzer.needs_approval(cmd):
            risk = SmartCommandAnalyzer.get_risk_level(cmd)
            print(f"Risk level: {risk}")
            
            choice, explanation = await approver.get_approval(cmd, desc)
            
            if choice == ApprovalChoice.YES or choice == ApprovalChoice.TIMEOUT:
                print(f"✓ Command approved: {cmd}")
            elif choice == ApprovalChoice.NO:
                print(f"✗ Command rejected: {cmd}")
                if explanation:
                    print(f"  User feedback: {explanation}")
            else:
                print("⚠ Command cancelled")
        else:
            print(f"✓ Safe command, auto-executing: {cmd}")


if __name__ == "__main__":
    # Test the approval system
    asyncio.run(test_approval())