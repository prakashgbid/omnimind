#!/usr/bin/env python3
"""
Quick fix to make OSA work immediately
"""

import subprocess
import sys

# Check if Ollama is running
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=2)
    if result.returncode == 0:
        print("✅ Ollama is running")
        # Parse models
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        models = [line.split()[0] for line in lines if line.strip()]
        print(f"Available models: {models}")
        
        if "llama3.2:3b" in models:
            print("✅ llama3.2:3b model is available")
        else:
            print("⚠️ llama3.2:3b not found, using first available model")
            
except Exception as e:
    print(f"❌ Ollama not running: {e}")
    print("Start it with: ollama serve")
    sys.exit(1)

# Update the osa_minimal.py to use a fixed model
import os
os.chdir('/Users/MAC/Documents/projects/omnimind')

# Create a simpler OSA launcher
with open('osa_working.py', 'w') as f:
    f.write('''#!/usr/bin/env python3
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
    
    print("\\nType your questions (or 'exit' to quit):")
    print("-" * 50)
    
    while True:
        try:
            prompt = input("\\n> ").strip()
            
            if prompt.lower() in ['exit', 'quit']:
                print("\\n👋 Goodbye!")
                break
            
            if not prompt:
                continue
            
            print("\\n🤔 Thinking...")
            
            # Generate response
            response = client.generate(
                model=model,
                prompt=prompt
            )
            
            print("\\n" + "="*50)
            print(response['response'])
            print("="*50)
            
        except KeyboardInterrupt:
            print("\\n\\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
''')

print("\n✅ Created osa_working.py")
print("\nTo run the working OSA:")
print("  python3 osa_working.py")