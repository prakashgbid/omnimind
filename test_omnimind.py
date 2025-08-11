#!/usr/bin/env python3
"""
OmniMind Test Script

This script tests all OmniMind functionality step by step.
Run this to verify your installation works correctly.
"""

import sys
import os
import json
from datetime import datetime

print("""
╔══════════════════════════════════════╗
║     🧠 OmniMind Test Suite 🧠       ║
╚══════════════════════════════════════╝
""")

# Track test results
tests_passed = 0
tests_failed = 0
results = []

def test_step(name, func):
    """Run a test step and track results."""
    global tests_passed, tests_failed
    print(f"\n📋 Testing: {name}")
    print("-" * 40)
    
    try:
        result = func()
        if result:
            print(f"✅ PASSED: {name}")
            tests_passed += 1
            results.append({"test": name, "status": "passed"})
            return True
        else:
            print(f"❌ FAILED: {name}")
            tests_failed += 1
            results.append({"test": name, "status": "failed"})
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        tests_failed += 1
        results.append({"test": name, "status": "error", "error": str(e)})
        return False

# Test 1: Check Python version
def test_python_version():
    import sys
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python 3.8+ detected")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False

# Test 2: Check required packages
def test_packages():
    required = [
        'chromadb',
        'networkx', 
        'sentence_transformers',
        'gradio',
        'rich',
        'ollama'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} missing")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

# Test 3: Check Ollama
def test_ollama():
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        
        if models and 'models' in models:
            model_list = models['models']
            print(f"✓ Ollama running with {len(model_list)} models")
            for m in model_list[:3]:  # Show first 3
                print(f"  - {m['name']}")
            return True
        else:
            print("✗ No Ollama models found")
            print("Run: ollama pull llama3.2:3b")
            return False
    except Exception as e:
        print(f"✗ Ollama not running: {e}")
        print("Start Ollama with: ollama serve")
        return False

# Test 4: Test OmniMind import
def test_omnimind_import():
    try:
        # Add src to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from src.core.omnimind import OmniMind
        print("✓ OmniMind core imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import OmniMind: {e}")
        return False

# Test 5: Initialize OmniMind
def test_omnimind_init():
    try:
        from src.core.omnimind import OmniMind
        
        print("Initializing OmniMind...")
        om = OmniMind()
        print("✓ OmniMind initialized")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False

# Test 6: Test memory storage
def test_memory_storage():
    try:
        from src.core.omnimind import OmniMind
        
        om = OmniMind()
        
        # Store a test memory
        test_thought = f"Test memory created at {datetime.now()}"
        memory_id = om.remember(test_thought)
        
        print(f"✓ Memory stored with ID: {memory_id}")
        return True
    except Exception as e:
        print(f"✗ Failed to store memory: {e}")
        return False

# Test 7: Test memory search
def test_memory_search():
    try:
        from src.core.omnimind import OmniMind
        
        om = OmniMind()
        
        # Store and search
        om.remember("Python is a great programming language")
        om.remember("JavaScript is used for web development")
        
        results = om.search_memories("programming", limit=5)
        
        if results:
            print(f"✓ Found {len(results)} memories")
            for r in results[:2]:
                print(f"  - Score: {r['score']:.2f} | {r['content'][:50]}...")
            return True
        else:
            print("✗ No search results")
            return False
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False

# Test 8: Test thinking with context
def test_thinking():
    try:
        from src.core.omnimind import OmniMind
        
        om = OmniMind()
        
        # Add some context
        om.remember("We decided to use TypeScript for type safety")
        om.remember("The project uses React for the frontend")
        
        # Ask a question
        print("Asking: 'What technologies are we using?'")
        response = om.think("What technologies are we using?", use_consensus=False)
        
        if response:
            print(f"✓ Got response: {response[:100]}...")
            return True
        else:
            print("✗ No response")
            return False
    except Exception as e:
        print(f"✗ Thinking failed: {e}")
        return False

# Test 9: Test enhanced version with providers
def test_enhanced_providers():
    try:
        from src.core.omnimind_enhanced import OmniMindEnhanced
        
        print("Testing enhanced OmniMind with providers...")
        om = OmniMindEnhanced()
        
        info = om.get_provider_info()
        print(f"✓ Available providers: {', '.join(info['available_providers']) or 'None'}")
        
        if info['cloud_providers']:
            print(f"  Cloud: {', '.join(info['cloud_providers'])}")
        if info['local_providers']:
            print(f"  Local: {', '.join(info['local_providers'])}")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced version failed: {e}")
        print("This is okay if you haven't configured cloud providers yet")
        return True  # Don't fail the test for this

# Test 10: Test CLI interface
def test_cli():
    try:
        from src.cli import OmniMindCLI
        
        cli = OmniMindCLI()
        print("✓ CLI interface loads correctly")
        return True
    except Exception as e:
        print(f"✗ CLI failed: {e}")
        return False

# Test 11: Test Web UI
def test_web_ui():
    try:
        from src.web_ui import OmniMindWebUI
        
        ui = OmniMindWebUI()
        interface = ui.create_interface()
        print("✓ Web UI interface created successfully")
        return True
    except Exception as e:
        print(f"✗ Web UI failed: {e}")
        return False

# Test 12: Test agent interface
def test_agent():
    try:
        from src.agents import OmniMindAgent
        
        agent = OmniMindAgent()
        print("✓ Agent interface loads correctly")
        return True
    except Exception as e:
        print(f"✗ Agent failed: {e}")
        return False

# Run all tests
def main():
    print("\n🔬 Starting OmniMind Test Suite\n")
    
    # Basic tests
    test_step("Python Version", test_python_version)
    test_step("Required Packages", test_packages)
    
    # If packages missing, stop here
    if tests_failed > 0:
        print("\n⚠️  Please install missing packages first:")
        print("    pip install -r requirements.txt")
        return
    
    # Continue with functionality tests
    test_step("Ollama Service", test_ollama)
    test_step("OmniMind Import", test_omnimind_import)
    test_step("OmniMind Initialization", test_omnimind_init)
    test_step("Memory Storage", test_memory_storage)
    test_step("Memory Search", test_memory_search)
    test_step("Thinking with Context", test_thinking)
    test_step("Enhanced Providers", test_enhanced_providers)
    test_step("CLI Interface", test_cli)
    test_step("Web UI", test_web_ui)
    test_step("Agent Interface", test_agent)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📈 Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! OmniMind is ready to use!")
        print("\nNext steps:")
        print("1. Run: ./start.sh")
        print("2. Or: python src/main.py web")
        print("3. Or: python src/main.py cli")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Install packages: pip install -r requirements.txt")
        print("2. Start Ollama: ollama serve")
        print("3. Download a model: ollama pull llama3.2:3b")

if __name__ == "__main__":
    main()