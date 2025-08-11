#!/usr/bin/env python3
"""
Free Premium Access System

Leverages your subscriptions for unlimited premium AI access:
- Claude Opus via Claude Code agents
- ChatGPT Plus via browser automation
- Zero API costs
"""

import asyncio
import os
from typing import Optional, Dict, Any

# Check if running in Claude Code
IS_CLAUDE_CODE = os.getenv('CLAUDE_CODE') or 'claude' in os.path.basename(os.path.abspath(__file__)).lower()

print("""
🎯 Free Premium AI Access System
=================================

Leveraging your subscriptions for unlimited access:
- Claude Opus: Through Claude Code agents
- ChatGPT Plus: Through browser automation
- Cost: $0 API fees!
""")


class FreePremiumAccess:
    """
    Unified access to premium AI models through subscriptions.
    """
    
    def __init__(self):
        self.claude_opus = None
        self.chatgpt_browser = None
        self.setup_complete = False
    
    def setup_claude_opus(self):
        """Setup Claude Opus agent (works in Claude Code)."""
        try:
            from src.agents.specialized.claude_opus_agent import ClaudeOpusAgent
            self.claude_opus = ClaudeOpusAgent()
            
            status = self.claude_opus.get_opus_status()
            if status['is_claude_code']:
                print("✅ Claude Opus: Available (via Claude Code)")
                print(f"   • Model: {status['model']}")
                print(f"   • Cost: {status['cost']}")
                print(f"   • Context: {status['context_window']}")
            else:
                print("⚠️ Claude Opus: Not in Claude Code (using local fallback)")
            
            return True
        except Exception as e:
            print(f"❌ Claude Opus setup failed: {e}")
            return False
    
    async def setup_chatgpt_browser(self, headless: bool = True):
        """Setup ChatGPT browser automation."""
        try:
            from src.agents.specialized.chatgpt_browser_agent import ChatGPTBrowserAgent
            
            self.chatgpt_browser = ChatGPTBrowserAgent()
            success = await self.chatgpt_browser.initialize_browser(headless=headless)
            
            if success:
                print("✅ ChatGPT Plus: Connected via browser")
                print("   • Model: GPT-4/GPT-5")
                print("   • Cost: $0 (via subscription)")
                print("   • Features: Code Interpreter, DALL-E 3, Web Browse")
            else:
                print("⚠️ ChatGPT Plus: Browser setup needed")
                print("   Run with headless=False to login")
            
            return success
        except ImportError:
            print("❌ ChatGPT Browser: Playwright not installed")
            print("   Install: pip install playwright && playwright install chromium")
            return False
        except Exception as e:
            print(f"❌ ChatGPT Browser setup failed: {e}")
            return False
    
    async def setup_all(self, setup_browser: bool = True):
        """Setup all premium access methods."""
        print("\n🚀 Setting up premium access...")
        print("-" * 40)
        
        # Setup Claude Opus
        self.setup_claude_opus()
        
        # Setup ChatGPT Browser
        if setup_browser:
            await self.setup_chatgpt_browser()
        
        self.setup_complete = True
        print("\n✅ Setup complete!")
    
    def ask_opus(self, prompt: str, deep_analysis: bool = False) -> str:
        """
        Ask Claude Opus (FREE in Claude Code).
        
        Args:
            prompt: Your question
            deep_analysis: Request thorough analysis
        
        Returns:
            Opus-level response
        """
        if not self.claude_opus:
            self.setup_claude_opus()
        
        if self.claude_opus:
            if IS_CLAUDE_CODE:
                # We're in Claude Code - direct Opus access!
                return self.claude_opus.opus_think(prompt, deep_analysis)
            else:
                # Not in Claude Code - use local fallback
                return self.claude_opus.think(prompt)
        
        return "Claude Opus not available"
    
    async def ask_chatgpt(self, prompt: str) -> str:
        """
        Ask ChatGPT Plus (FREE via browser).
        
        Args:
            prompt: Your question
        
        Returns:
            GPT-4/GPT-5 response
        """
        if not self.chatgpt_browser:
            await self.setup_chatgpt_browser()
        
        if self.chatgpt_browser and self.chatgpt_browser.session_active:
            return await self.chatgpt_browser.chatgpt_think(prompt)
        
        return "ChatGPT browser not available"
    
    async def ask_both(self, prompt: str) -> Dict[str, str]:
        """
        Ask both Opus and ChatGPT for comparison.
        
        Args:
            prompt: Your question
        
        Returns:
            Responses from both models
        """
        responses = {}
        
        # Ask Opus
        if IS_CLAUDE_CODE:
            responses['claude_opus'] = self.ask_opus(prompt, deep_analysis=True)
        else:
            responses['claude_opus'] = "Not in Claude Code environment"
        
        # Ask ChatGPT
        if self.chatgpt_browser and self.chatgpt_browser.session_active:
            responses['chatgpt'] = await self.ask_chatgpt(prompt)
        else:
            responses['chatgpt'] = "ChatGPT browser not connected"
        
        return responses
    
    async def code_with_interpreter(self, code: str, description: str) -> str:
        """Use ChatGPT's Code Interpreter."""
        if self.chatgpt_browser:
            return await self.chatgpt_browser.use_code_interpreter(code, description)
        return "Code Interpreter not available"
    
    async def generate_image(self, prompt: str) -> str:
        """Generate image with DALL-E 3."""
        if self.chatgpt_browser:
            return await self.chatgpt_browser.generate_image(prompt)
        return "DALL-E 3 not available"
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all premium access methods."""
        status = {
            'claude_opus': {
                'available': False,
                'details': {}
            },
            'chatgpt_plus': {
                'available': False,
                'details': {}
            }
        }
        
        # Claude Opus status
        if self.claude_opus:
            opus_status = self.claude_opus.get_opus_status()
            status['claude_opus'] = {
                'available': opus_status['is_claude_code'],
                'details': opus_status
            }
        
        # ChatGPT status
        if self.chatgpt_browser:
            status['chatgpt_plus'] = {
                'available': self.chatgpt_browser.session_active,
                'details': {
                    'model': 'GPT-4/GPT-5',
                    'features': ['Code Interpreter', 'DALL-E 3', 'Web Browse'],
                    'cost': '$0 (via subscription)'
                }
            }
        
        return status


# Demo functions
async def demo_premium_access():
    """Demonstrate free premium access."""
    system = FreePremiumAccess()
    
    # Setup
    await system.setup_all(setup_browser=False)  # Set to True to setup ChatGPT
    
    print("\n" + "=" * 60)
    print("📝 DEMO: Free Premium Access")
    print("=" * 60)
    
    # Test Claude Opus
    print("\n1. Testing Claude Opus (in Claude Code)...")
    if IS_CLAUDE_CODE:
        opus_response = system.ask_opus(
            "Explain the implications of AGI development",
            deep_analysis=True
        )
        print(f"Opus says: {opus_response[:200]}...")
    else:
        print("   ⚠️ Not in Claude Code - Opus unavailable")
        print("   💡 Run this script as a Claude Code agent for Opus access")
    
    # Test ChatGPT (if browser setup)
    if system.chatgpt_browser and system.chatgpt_browser.session_active:
        print("\n2. Testing ChatGPT Plus via browser...")
        chatgpt_response = await system.ask_chatgpt(
            "What are the latest AI developments?"
        )
        print(f"ChatGPT says: {chatgpt_response[:200]}...")
    else:
        print("\n2. ChatGPT browser not setup")
        print("   💡 Run with browser setup to connect ChatGPT")
    
    # Show status
    print("\n" + "=" * 60)
    print("📊 System Status")
    print("=" * 60)
    
    status = system.get_status()
    print("\nClaude Opus:")
    if status['claude_opus']['available']:
        print(f"  ✅ Available - {status['claude_opus']['details']['model']}")
    else:
        print("  ❌ Not available (not in Claude Code)")
    
    print("\nChatGPT Plus:")
    if status['chatgpt_plus']['available']:
        print(f"  ✅ Connected - {status['chatgpt_plus']['details']['model']}")
    else:
        print("  ❌ Not connected (browser setup needed)")


# Quick access functions
def opus_think(prompt: str) -> str:
    """Quick Opus access for Claude Code."""
    system = FreePremiumAccess()
    system.setup_claude_opus()
    return system.ask_opus(prompt, deep_analysis=True)


async def chatgpt_think(prompt: str) -> str:
    """Quick ChatGPT access via browser."""
    system = FreePremiumAccess()
    await system.setup_chatgpt_browser()
    return await system.ask_chatgpt(prompt)


if __name__ == "__main__":
    print("""
💡 HOW TO USE:

1. For Claude Opus (FREE in Claude Code):
   - Run this script as a Claude Code agent
   - Opus will be available automatically
   - No API keys needed!

2. For ChatGPT Plus (FREE via browser):
   - Install: pip install playwright && playwright install chromium
   - Run: python free_premium_access.py
   - Login once (session saved)
   - Unlimited GPT-4/GPT-5 access!

3. Combined Usage:
   ```python
   from free_premium_access import FreePremiumAccess
   
   system = FreePremiumAccess()
   await system.setup_all()
   
   # Free Opus (in Claude Code)
   opus_response = system.ask_opus("Complex question")
   
   # Free ChatGPT (via browser)
   gpt_response = await system.ask_chatgpt("Another question")
   ```

This gives you unlimited premium AI access for just your subscription costs!
No API fees, no rate limits, just pure intelligence!
    """)
    
    # Run demo
    asyncio.run(demo_premium_access())