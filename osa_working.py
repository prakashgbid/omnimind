#!/usr/bin/env python3
"""Working OSA with fixed model detection"""

import asyncio
import ollama
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

async def main():
    print("🚀 OSA Quick Start")
    print("=" * 50)
    
    # Initialize Ollama client
    client = ollama.Client()
    
    # Use a known working model
    model = "llama3.2:3b"
    print(f"Using model: {model}")
    
    print("\nType your questions (or 'exit' to quit):")
    print("-" * 50)
    
    while True:
        try:
            prompt = input("\n> ").strip()
            
            if prompt.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break
            
            if not prompt:
                continue
            
            print("\n🤔 Thinking...")
            
            # Generate response
            response = client.generate(
                model=model,
                prompt=prompt
            )
            
            print("\n" + "="*50)
            print(response['response'])
            print("="*50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
