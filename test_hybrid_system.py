#!/usr/bin/env python3
"""
Test OmniMind Hybrid System

Demonstrates intelligent routing between:
- 5 FREE local models (80% of queries)
- Premium models (ChatGPT 5/GPT-4, Claude Opus) for complex tasks
- Automatic cost optimization
"""

import asyncio
import os
from src.providers.intelligent_router import intelligent_router, smart_complete

print("""
🧠 OmniMind Hybrid Intelligence System
=======================================

Combining:
- 5 FREE Local Models (Llama, Mistral, Phi-3, DeepSeek, Gemma)
- Premium Models (ChatGPT 5.0/GPT-4, Claude 3 Opus)
- Intelligent routing to minimize costs
""")

async def test_routing():
    """Test the intelligent routing system."""
    
    # Test cases with different complexity levels
    test_cases = [
        {
            'query': "What is 2+2?",
            'expected': 'local',
            'reason': 'Simple question - local model sufficient'
        },
        {
            'query': "Write a Python function to sort a list",
            'expected': 'local',
            'reason': 'Code task - DeepSeek Coder (local) is capable'
        },
        {
            'query': "Explain the philosophical implications of consciousness in AI",
            'expected': 'premium',
            'reason': 'Complex philosophical question - benefits from premium model'
        },
        {
            'query': "Debug this React component that has a memory leak",
            'expected': 'local',
            'reason': 'Debugging task - local models can handle'
        },
        {
            'query': "Create a production-ready authentication system with OAuth2",
            'expected': 'premium',
            'reason': 'Production code mentioned - requires premium quality'
        },
        {
            'query': "List 5 benefits of microservices",
            'expected': 'local',
            'reason': 'Simple listing task - local model sufficient'
        }
    ]
    
    print("\n📊 Testing Intelligent Routing")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query'][:50]}...")
        print(f"Expected: {test['expected']} model")
        print(f"Reason: {test['reason']}")
        
        # Analyze the task
        analysis = intelligent_router.analyze_task(test['query'])
        
        print(f"\nAnalysis:")
        print(f"  • Complexity: {analysis['complexity']}")
        print(f"  • Suggested Provider: {analysis['suggested_provider']}")
        print(f"  • Suggested Model: {analysis['suggested_model']}")
        print(f"  • Estimated Cost: ${analysis['estimated_cost']:.4f}")
        print(f"  • Reasoning: {', '.join(analysis['reasoning'][:2])}")
        
        # Actually route the query (if providers are available)
        if analysis['suggested_provider'] == 'local':
            print("  ✅ Using FREE local model - no cost!")
        else:
            print(f"  💰 Would use premium model (${analysis['estimated_cost']:.4f})")
    
    # Show routing statistics
    print("\n" + "=" * 60)
    print("📈 Routing Statistics")
    print("=" * 60)
    
    stats = intelligent_router.get_routing_stats()
    
    print(f"\n💰 Cost Management:")
    print(f"  • Monthly Budget: ${stats['monthly_budget']:.2f}")
    print(f"  • Current Month Cost: ${stats['current_month_cost']:.2f}")
    print(f"  • Budget Remaining: ${stats['budget_remaining']:.2f}")
    
    print(f"\n🔌 Available Providers:")
    for provider in stats['available_providers']:
        print(f"  • {provider}")
    
    if stats['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in stats['recommendations']:
            print(f"  {rec}")
    
    # Demonstrate actual completion (if local models available)
    print("\n" + "=" * 60)
    print("🎯 Live Demo with Local Model")
    print("=" * 60)
    
    try:
        # Force local model for demo
        response = await smart_complete(
            "Explain the benefits of using local LLMs",
            force_local=True
        )
        
        print(f"\nModel Used: {response.model}")
        print(f"Provider: {response.provider}")
        print(f"Cost: ${response.cost:.4f}")
        print(f"Latency: {response.latency_ms:.0f}ms")
        print(f"\nResponse: {response.content[:300]}...")
        
        if 'routing' in response.metadata:
            routing_info = response.metadata['routing']
            print(f"\nRouting Decision:")
            print(f"  • Analysis: {routing_info['analysis']['complexity']} complexity")
            print(f"  • Budget Status: ${routing_info['budget_remaining']:.2f} remaining")
    except Exception as e:
        print(f"\n⚠️ Could not complete demo: {e}")
        print("Make sure Ollama is running for local models")

# Summary
print("\n" + "=" * 60)
print("🎯 HYBRID SYSTEM BENEFITS")
print("=" * 60)

print("""
✅ Cost Optimization:
   • 80% queries use FREE local models
   • Premium models only for complex/critical tasks
   • Monthly budget: $10 (adjustable)
   • Automatic fallback to local when budget exceeded

✅ Quality Assurance:
   • Critical tasks get premium models
   • Production code uses best available
   • Complex reasoning uses GPT-4 or Claude Opus
   • Simple tasks efficiently handled locally

✅ Smart Routing Logic:
   • Analyzes each query for complexity
   • Checks budget before using premium
   • Falls back gracefully if premium unavailable
   • Learns from usage patterns

✅ Available Models:
   LOCAL (FREE):
   • Llama 3.2 - General purpose
   • Mistral 7B - Complex reasoning
   • DeepSeek Coder - Programming
   • Phi-3 - Efficient tasks
   • Gemma 2 - Quick responses
   
   PREMIUM (When needed):
   • ChatGPT 5.0 - Most advanced (when available)
   • GPT-4 Turbo - Advanced reasoning
   • Claude 3 Opus - Nuanced understanding
   • Claude 3 Sonnet - Balanced performance
   • Claude 3 Haiku - Fast simple tasks

💰 Typical Monthly Cost:
   • Heavy usage: $5-10/month
   • Normal usage: $2-5/month
   • Light usage: $0-2/month
   • Local only: $0/month

🔒 Privacy Options:
   • force_local=True - 100% private, no data leaves machine
   • Default - Smart mix of local and cloud
   • require_quality=True - Use best available model
""")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_routing())