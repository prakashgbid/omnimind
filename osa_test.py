#!/usr/bin/env python3
"""
Test OSA with Ollama - Non-interactive version
"""

import asyncio
import ollama

async def test_osa_with_ollama():
    """Test OSA functionality with Ollama."""
    print("🚀 Testing OmniMind with Ollama")
    print("="*60)
    
    try:
        # Initialize Ollama client
        client = ollama.Client()
        
        # Check available models
        print("\n📦 Available models:")
        try:
            models = client.list()
            if 'models' in models:
                for model in models['models']:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 'unknown')
                    print(f"   • {name} ({size})")
            else:
                # Alternative format
                for model_name in models:
                    print(f"   • {model_name}")
        except Exception as e:
            print(f"   ⚠️ Could not list models: {e}")
        
        # Select a model
        model_name = "llama3.2:3b"
        print(f"\n🤖 Using model: {model_name}")
        
        # Test tasks
        tasks = [
            "Write a Python function to calculate fibonacci numbers",
            "Explain what is machine learning in 2 sentences",
            "Create a simple REST API endpoint example"
        ]
        
        for task in tasks:
            print(f"\n📝 Task: {task}")
            print("-" * 40)
            
            try:
                # Generate response
                response = client.generate(
                    model=model_name,
                    prompt=task
                )
                
                # Print response (limited to 300 chars for readability)
                result = response['response']
                if len(result) > 300:
                    result = result[:300] + "..."
                
                print(f"✅ Response:\n{result}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
        print("✨ Test complete!")
        
    except Exception as e:
        print(f"❌ Error initializing Ollama: {e}")
        print("\nMake sure Ollama is running with: ollama serve")

if __name__ == "__main__":
    asyncio.run(test_osa_with_ollama())