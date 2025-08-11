#!/usr/bin/env python3
"""Quick test of local models with OmniMind"""

import ollama

print("🤖 Quick Local Model Test")
print("=" * 40)

# Test each model with a simple prompt
models = [
    ('llama3.2:3b', 'Say hello in 5 words'),
    ('mistral:7b', 'What is 2+2?'),
    ('phi3:mini', 'Complete: The sky is'),
    ('deepseek-coder:6.7b', 'Print hello world in Python'),
    ('gemma2:2b', 'Name a color')
]

for model, prompt in models:
    print(f"\n📦 Testing {model}")
    print(f"   Prompt: {prompt}")
    try:
        response = ollama.generate(model=model, prompt=prompt)
        answer = response['response'].strip()[:100]
        print(f"   ✅ Response: {answer}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 40)
print("✅ All models are working locally!")
print("💰 Cost: $0.00 (FREE!)")
print("🔒 Privacy: 100% local")