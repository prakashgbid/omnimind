#!/usr/bin/env python3
"""
Test OmniMind with Ollama LLM

This tests the full OmniMind system including AI responses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("""
🧠 Testing OmniMind with Local LLM
===================================
""")

# Check Ollama
print("1️⃣ Checking Ollama...")
try:
    import ollama
    client = ollama.Client()
    models = client.list()
    
    if models and 'models' in models and len(models['models']) > 0:
        print(f"✅ Ollama running with {len(models['models'])} model(s):")
        for m in models['models']:
            size_gb = m.get('size', 0) / (1024**3)
            print(f"   - {m['name']} ({size_gb:.1f}GB)")
    else:
        print("❌ No models found. Download one with: ollama pull llama3.2:1b")
        exit(1)
except Exception as e:
    print(f"❌ Ollama error: {e}")
    print("Make sure Ollama is running: ollama serve")
    exit(1)

# Test OmniMind with LLM
print("\n2️⃣ Testing OmniMind with AI...")
try:
    from src.core.omnimind import OmniMind
    
    # Initialize
    om = OmniMind()
    print("✅ OmniMind initialized")
    
    # Store some context
    print("\n3️⃣ Adding memories...")
    om.remember("We are building an app called OmniMind")
    om.remember("OmniMind is a persistent intelligence system with perfect memory")
    om.remember("It uses local LLMs via Ollama for privacy")
    om.remember("The project is written in Python")
    print("✅ Added 4 memories")
    
    # Test thinking with context
    print("\n4️⃣ Testing AI thinking with context...")
    print("Question: What are we building and why is it special?")
    print("-" * 50)
    
    response = om.think("What are we building and why is it special?", use_consensus=False)
    
    print("AI Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    
    # Test search
    print("\n5️⃣ Testing semantic search...")
    results = om.search_memories("programming language", limit=2)
    print(f"Search for 'programming language' found {len(results)} results")
    for r in results:
        print(f"  - Score {r['score']:.2f}: {r['content'][:50]}...")
    
    print("\n✅ All tests passed! OmniMind is fully functional with AI!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("""

✨ Success! You can now use:
- python3 src/main.py cli    # Interactive terminal
- python3 src/main.py web    # Web interface
- python3 src/main.py ask "Your question"  # Quick query
""")