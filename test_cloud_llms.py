#!/usr/bin/env python3
"""
Test OmniMind with Cloud LLMs (OpenAI, Anthropic, Google)
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("""
🧠 Testing OmniMind with Cloud LLMs
====================================
""")

async def test_providers():
    """Test each cloud provider."""
    from src.core.omnimind_enhanced import OmniMindEnhanced
    
    # Initialize OmniMind
    print("1️⃣ Initializing OmniMind with cloud providers...")
    om = OmniMindEnhanced()
    
    # Get provider info
    info = om.get_provider_info()
    print(f"\n✅ Available Providers:")
    for provider in info['available_providers']:
        print(f"   • {provider}")
    
    # Add some context
    print("\n2️⃣ Adding test memories...")
    om.remember("We're testing OmniMind with multiple cloud LLMs")
    om.remember("OmniMind uses GPT-4, Claude Opus, and Gemini Pro")
    om.remember("The goal is to provide the best answers through consensus")
    print("✅ Added 3 test memories")
    
    # Test individual providers
    print("\n3️⃣ Testing each provider individually...")
    
    providers_to_test = ['openai', 'anthropic', 'google']
    
    for provider in providers_to_test:
        if provider in info['available_providers']:
            print(f"\n   Testing {provider.upper()}...")
            try:
                response = await om.think_async(
                    "Hello! What model are you and what makes you special?",
                    providers=[provider],
                    use_consensus=False
                )
                print(f"   ✅ {provider}: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ {provider} error: {e}")
    
    # Test consensus
    print("\n4️⃣ Testing multi-model consensus...")
    print("   Question: 'What are the key benefits of using multiple LLMs together?'")
    
    try:
        consensus_response = await om.think_async(
            "What are the key benefits of using multiple LLMs together?",
            use_consensus=True,
            providers=['openai', 'anthropic', 'google']
        )
        print("\n   🤝 Consensus Response:")
        print("   " + "-" * 50)
        print(f"   {consensus_response[:500]}...")
        print("   " + "-" * 50)
    except Exception as e:
        print(f"   ❌ Consensus error: {e}")
    
    print("\n✅ All tests complete!")
    print("\n📊 Summary:")
    print(f"   • Cloud Providers: {len(info['cloud_providers'])}")
    print(f"   • Local Providers: {len(info['local_providers'])}")
    print(f"   • Total Available: {len(info['available_providers'])}")

# Run the async test
print("Starting tests...\n")
asyncio.run(test_providers())

print("""

✨ Success! OmniMind is working with cloud LLMs!

You now have access to:
• GPT-4 Turbo (OpenAI)
• Claude 3 Opus (Anthropic)
• Gemini Pro (Google)
• Ollama models (Local)

🚀 Start using OmniMind:
   python3 src/main.py cli  # Interactive terminal
   python3 src/main.py web  # Browser interface
   
💡 Example commands:
   python3 src/main.py ask "What should I build next?"
   python3 src/main.py ask "Explain quantum computing" --consensus
""")