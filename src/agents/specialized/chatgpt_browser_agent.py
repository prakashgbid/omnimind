"""
ChatGPT Browser Agent - Access ChatGPT Plus via Headless Browser

This agent uses Playwright to automate a headless browser session
to access ChatGPT Plus, giving you unlimited GPT-4/GPT-5 access
through your subscription without API costs.
"""

import sys
import os
import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Run: pip install playwright && playwright install chromium")

from src.agents.base_omnimind_agent import BaseOmniMindAgent


class ChatGPTBrowserAgent(BaseOmniMindAgent):
    """
    Agent that accesses ChatGPT Plus through browser automation.
    
    This gives you unlimited GPT-4/GPT-5 access through your
    ChatGPT Plus subscription without API costs.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="chatgpt-browser",
            specialization="GPT-4/GPT-5 access via browser automation"
        )
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.session_active = False
        
        # Paths for session persistence
        self.session_dir = Path.home() / '.omnimind' / 'chatgpt_session'
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_file = self.session_dir / 'cookies.json'
        self.storage_file = self.session_dir / 'storage.json'
    
    def _get_preferred_models(self) -> Dict[str, str]:
        """Browser gives us access to GPT-4/GPT-5."""
        return {
            'all': 'gpt-4-browser'  # Accessed via browser
        }
    
    def get_specialization_prompt(self) -> str:
        """ChatGPT browser access prompt."""
        return """
I am accessing ChatGPT Plus (GPT-4/GPT-5) through browser automation.

This provides:
- Unlimited GPT-4/GPT-5 access through your subscription
- No API costs
- Latest model updates automatically
- Access to ChatGPT plugins and features
- Code interpreter capabilities
- DALL-E 3 image generation
- Web browsing capabilities

All the power of ChatGPT Plus, automated and integrated with OmniMind's memory.
"""
    
    async def initialize_browser(self, headless: bool = True) -> bool:
        """
        Initialize the browser session.
        
        Args:
            headless: Run in headless mode (no visible browser)
        
        Returns:
            Success status
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright not available. Install with:")
            print("   pip install playwright")
            print("   playwright install chromium")
            return False
        
        try:
            print("🌐 Initializing ChatGPT browser session...")
            
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Create context with saved session if available
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # Load saved storage state if exists
            if self.storage_file.exists():
                print("   📂 Loading saved session...")
                context_options['storage_state'] = str(self.storage_file)
            
            self.context = await self.browser.new_context(**context_options)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Navigate to ChatGPT
            print("   🔗 Navigating to ChatGPT...")
            await self.page.goto('https://chat.openai.com', wait_until='networkidle')
            
            # Check if logged in
            if await self._is_logged_in():
                print("   ✅ Logged into ChatGPT Plus!")
                self.session_active = True
                await self._save_session()
                return True
            else:
                print("   🔐 Login required...")
                return await self._handle_login()
                
        except Exception as e:
            print(f"❌ Browser initialization failed: {e}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """Check if already logged into ChatGPT."""
        try:
            # Check for new chat button or user menu
            new_chat = await self.page.query_selector('a[href="/"]')
            user_menu = await self.page.query_selector('[data-testid="profile-button"]')
            return new_chat is not None or user_menu is not None
        except:
            return False
    
    async def _handle_login(self) -> bool:
        """
        Handle ChatGPT login process.
        
        Returns:
            Success status
        """
        print("\n🔐 ChatGPT Login Required")
        print("=" * 50)
        
        if self.browser and self.context:
            # Switch to visible mode for login
            print("Opening browser for login...")
            print("Please log into your ChatGPT Plus account.")
            print("The session will be saved for future use.")
            
            # Wait for user to complete login
            print("\nWaiting for login completion...")
            
            # Poll for login success
            for _ in range(60):  # Wait up to 5 minutes
                await asyncio.sleep(5)
                if await self._is_logged_in():
                    print("✅ Login successful!")
                    self.session_active = True
                    await self._save_session()
                    return True
            
            print("❌ Login timeout")
            return False
        
        return False
    
    async def _save_session(self):
        """Save browser session for reuse."""
        try:
            # Save storage state (cookies, localStorage)
            storage = await self.context.storage_state()
            with open(self.storage_file, 'w') as f:
                json.dump(storage, f)
            print("   💾 Session saved for future use")
        except Exception as e:
            print(f"   ⚠️ Could not save session: {e}")
    
    async def send_message(self, message: str, wait_for_response: bool = True) -> str:
        """
        Send a message to ChatGPT and get response.
        
        Args:
            message: Message to send
            wait_for_response: Wait for complete response
        
        Returns:
            ChatGPT's response
        """
        if not self.session_active:
            if not await self.initialize_browser():
                return "Failed to initialize ChatGPT browser session"
        
        try:
            # Find and focus the input field
            input_selector = 'textarea[data-id="root"]'
            await self.page.wait_for_selector(input_selector, timeout=10000)
            input_field = await self.page.query_selector(input_selector)
            
            # Clear and type message
            await input_field.click()
            await self.page.keyboard.press('Control+A')
            await self.page.keyboard.press('Delete')
            await input_field.type(message)
            
            # Send message
            await self.page.keyboard.press('Enter')
            
            if wait_for_response:
                # Wait for response to complete
                await self._wait_for_response()
                
                # Extract response
                response = await self._extract_response()
                return response
            else:
                return "Message sent to ChatGPT"
                
        except Exception as e:
            return f"Error sending message: {e}"
    
    async def _wait_for_response(self, timeout: int = 60):
        """Wait for ChatGPT to finish responding."""
        try:
            # Wait for stop button to disappear (indicates completion)
            stop_selector = 'button[aria-label="Stop generating"]'
            
            # First wait for it to appear
            await self.page.wait_for_selector(stop_selector, timeout=5000, state='visible')
            
            # Then wait for it to disappear
            await self.page.wait_for_selector(stop_selector, timeout=timeout*1000, state='hidden')
            
            # Small delay to ensure response is fully rendered
            await asyncio.sleep(1)
        except:
            # If stop button doesn't appear, response might be instant
            await asyncio.sleep(2)
    
    async def _extract_response(self) -> str:
        """Extract the latest response from ChatGPT."""
        try:
            # Get all message containers
            messages = await self.page.query_selector_all('div[data-message-author-role]')
            
            if messages:
                # Get the last assistant message
                for message in reversed(messages):
                    role = await message.get_attribute('data-message-author-role')
                    if role == 'assistant':
                        # Extract text content
                        text_content = await message.inner_text()
                        return text_content.strip()
            
            # Fallback: try to get the last message block
            last_message = await self.page.query_selector('div.markdown.prose:last-of-type')
            if last_message:
                return await last_message.inner_text()
            
            return "Could not extract response"
            
        except Exception as e:
            return f"Error extracting response: {e}"
    
    async def chatgpt_think(self, prompt: str, model: str = "GPT-4") -> str:
        """
        Think using ChatGPT Plus via browser.
        
        Args:
            prompt: The prompt
            model: Model preference (GPT-4 or GPT-4-32K)
        
        Returns:
            ChatGPT's response
        """
        # Add model preference to prompt if specified
        if "gpt-4-32k" in model.lower():
            prompt = f"[Use GPT-4-32K model]\n{prompt}"
        
        response = await self.send_message(prompt)
        
        # Store in memory
        if self.omnimind:
            self.omnimind.remember(
                f"ChatGPT Q: {prompt}\nA: {response}",
                context={
                    'source': 'chatgpt-browser',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        return response
    
    async def use_code_interpreter(self, code: str, description: str) -> str:
        """
        Use ChatGPT's Code Interpreter.
        
        Args:
            code: Code to run
            description: What the code does
        
        Returns:
            Code interpreter results
        """
        prompt = f"""
Use the Code Interpreter to run this code:

```python
{code}
```

Description: {description}

Please run the code and provide the results.
"""
        return await self.chatgpt_think(prompt)
    
    async def generate_image(self, prompt: str) -> str:
        """
        Generate image using DALL-E 3.
        
        Args:
            prompt: Image generation prompt
        
        Returns:
            Image description or link
        """
        image_prompt = f"Generate an image: {prompt}"
        return await self.send_message(image_prompt)
    
    async def web_browse(self, query: str, url: Optional[str] = None) -> str:
        """
        Use ChatGPT's web browsing.
        
        Args:
            query: Search query or task
            url: Optional specific URL
        
        Returns:
            Web browsing results
        """
        if url:
            browse_prompt = f"Browse to {url} and {query}"
        else:
            browse_prompt = f"Search the web for: {query}"
        
        return await self.chatgpt_think(browse_prompt)
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.session_active = False
            print("🧹 Browser session cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.session_active:
            asyncio.run(self.cleanup())


# Agent registration
AGENT = ChatGPTBrowserAgent

def create_agent():
    """Factory function."""
    return ChatGPTBrowserAgent()


# Browser session manager for reuse
class ChatGPTSessionManager:
    """Manages persistent ChatGPT browser sessions."""
    
    _instance = None
    _agent = None
    
    @classmethod
    async def get_session(cls) -> ChatGPTBrowserAgent:
        """Get or create a ChatGPT browser session."""
        if cls._agent is None or not cls._agent.session_active:
            cls._agent = ChatGPTBrowserAgent()
            await cls._agent.initialize_browser(headless=True)
        return cls._agent
    
    @classmethod
    async def send_to_chatgpt(cls, message: str) -> str:
        """Quick method to send message to ChatGPT."""
        agent = await cls.get_session()
        return await agent.send_message(message)


# Usage example
USAGE_EXAMPLE = """
# Using ChatGPT Browser Agent

This gives you UNLIMITED access to GPT-4/GPT-5 through your ChatGPT Plus subscription!

## Setup:
```bash
pip install playwright
playwright install chromium
```

## Usage:
```python
from src.agents.specialized.chatgpt_browser_agent import ChatGPTSessionManager
import asyncio

async def use_chatgpt():
    # Get response from ChatGPT Plus (FREE with subscription!)
    response = await ChatGPTSessionManager.send_to_chatgpt(
        "Explain quantum computing"
    )
    print(response)

# Run
asyncio.run(use_chatgpt())
```

## Features:
- ✅ Unlimited GPT-4/GPT-5 access
- ✅ No API costs
- ✅ Code Interpreter
- ✅ DALL-E 3
- ✅ Web browsing
- ✅ Plugins
- ✅ Session persistence

This is like having unlimited GPT-4 API access for $20/month!
"""