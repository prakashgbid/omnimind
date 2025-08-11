#!/usr/bin/env python3
"""
Simplified OSA for testing - Direct Ollama integration
"""

import asyncio
import ollama
from typing import Dict, Any, Optional

class SimpleOSA:
    """Simplified OSA with direct Ollama integration."""
    
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.client = ollama.Client()
        self.context = []
        print(f"🤖 OSA initialized with model: {model}")
    
    async def initialize(self):
        """Initialize OSA systems."""
        print("🚀 Starting OSA systems...")
        # Check if model exists
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models['models']]
            if self.model in model_names:
                print(f"✅ Model {self.model} ready")
            else:
                print(f"⚠️ Model {self.model} not found, available: {model_names}")
        except Exception as e:
            print(f"❌ Error checking models: {e}")
    
    async def think(self, prompt: str) -> str:
        """Process a thought/task with the LLM."""
        try:
            print(f"🧠 Thinking about: {prompt[:50]}...")
            
            # Use Ollama to generate response
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                context=self.context if self.context else None
            )
            
            # Update context for continuity
            if 'context' in response:
                self.context = response['context']
            
            return response['response']
            
        except Exception as e:
            return f"Error: {e}"
    
    async def accomplish_task(self, task: str) -> str:
        """Accomplish a given task."""
        print(f"\n📝 Task: {task}")
        
        # Add some thinking process
        thoughts = [
            f"Understanding the task: {task}",
            "Breaking it down into steps",
            "Generating solution"
        ]
        
        for thought in thoughts:
            print(f"   💭 {thought}")
            await asyncio.sleep(0.5)
        
        # Get actual response from LLM
        result = await self.think(task)
        
        return result
    
    async def shutdown(self):
        """Shutdown OSA."""
        print("\n👋 OSA shutting down...")
        self.context = []


async def main():
    """Test the simplified OSA."""
    print("="*60)
    print("🎯 OmniMind Simple OSA Test")
    print("="*60)
    
    # Initialize OSA
    osa = SimpleOSA(model="llama3.2:3b")
    await osa.initialize()
    
    # Interactive mode
    print("\n💬 Interactive mode (type 'exit' to quit)")
    print("-"*40)
    
    while True:
        try:
            task = input("\n> ").strip()
            
            if task.lower() in ['exit', 'quit']:
                break
            
            if not task:
                continue
            
            result = await osa.accomplish_task(task)
            print(f"\n✅ Result:\n{result[:500]}...")  # Limit output length
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await osa.shutdown()
    print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())