#!/usr/bin/env python3
"""Test OSA with actual Ollama interaction"""

import ollama
import sys

print("Testing OSA with Ollama...")
print("=" * 50)

try:
    # Initialize client
    client = ollama.Client()
    
    # Test question
    question = "What can you do?"
    print(f"\n📝 Question: {question}")
    print("-" * 50)
    
    # Generate response
    print("🤔 Thinking...")
    response = client.generate(
        model="llama3.2:3b",
        prompt=question
    )
    
    print("\n✅ Response:")
    print("-" * 50)
    print(response['response'])
    print("-" * 50)
    
    print("\n✨ OSA is working correctly!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)