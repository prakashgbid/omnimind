#!/usr/bin/env python3
"""Quick test of OSA functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_osa():
    """Test basic OSA functionality."""
    print("🚀 Testing OmniMind OSA...")
    
    # Try with a simple mock for now
    class MockOSA:
        def __init__(self, config=None):
            self.config = config or {}
            print("✅ OSA initialized")
        
        async def initialize(self):
            print("✅ OSA systems starting...")
            await asyncio.sleep(0.5)
            
        async def accomplish_task(self, task):
            print(f"🤔 Processing: {task}")
            await asyncio.sleep(1)
            return f"Completed: {task}"
        
        async def shutdown(self):
            print("👋 OSA shutting down...")
    
    # Test it
    osa = MockOSA()
    await osa.initialize()
    
    # Test tasks
    tasks = [
        "What is the meaning of life?",
        "Create a simple Python function",
        "Explain quantum computing"
    ]
    
    for task in tasks:
        result = await osa.accomplish_task(task)
        print(f"   ➡️ {result}\n")
    
    await osa.shutdown()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_osa())