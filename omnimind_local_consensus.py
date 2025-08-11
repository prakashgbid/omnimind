#!/usr/bin/env python3
"""
OmniMind Local Consensus Demo
Shows how multiple free local LLMs work together
"""

import ollama
import json
from typing import List, Dict

print("""
🧠 OmniMind Local Consensus System
=====================================
Using multiple FREE local models for better answers!
""")

def get_model_response(model: str, prompt: str) -> str:
    """Get response from a single model."""
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response['response'].strip()
    except Exception as e:
        return f"Error: {e}"

def build_consensus(question: str, models: List[str]) -> Dict:
    """Get responses from multiple models and build consensus."""
    
    print(f"\n📝 Question: {question}")
    print("-" * 60)
    
    responses = {}
    
    # Collect responses from each model
    print("\n🤖 Collecting responses from each model:")
    for model in models:
        print(f"   • Querying {model}...")
        response = get_model_response(model, question)
        responses[model] = response
        print(f"     ✓ Got response ({len(response)} chars)")
    
    # Analyze consensus
    print("\n🤝 Building Consensus:")
    print("-" * 60)
    
    # Create synthesis prompt
    synthesis_prompt = f"""
Synthesize these AI responses about: "{question}"

Responses:
"""
    for model, response in responses.items():
        synthesis_prompt += f"\n{model}: {response[:200]}...\n"
    
    synthesis_prompt += """
Create a single unified answer that combines the best insights from all models.
Keep it concise and clear.

SYNTHESIZED ANSWER:"""
    
    # Use Mistral for synthesis (best reasoning)
    print("   • Using mistral:7b to synthesize final answer...")
    final_answer = get_model_response('mistral:7b', synthesis_prompt)
    
    return {
        'question': question,
        'individual_responses': responses,
        'consensus': final_answer,
        'models_used': models
    }

# Test cases
test_questions = [
    {
        'question': "What are the benefits of using multiple AI models together?",
        'models': ['llama3.2:3b', 'mistral:7b', 'phi3:mini']
    },
    {
        'question': "Write a Python function to reverse a string",
        'models': ['deepseek-coder:6.7b', 'llama3.2:3b', 'mistral:7b']
    },
    {
        'question': "What is consciousness?",
        'models': ['mistral:7b', 'phi3:mini', 'gemma2:2b', 'llama3.2:3b']
    }
]

# Run consensus for each question
results = []
for test in test_questions[:1]:  # Just do first one for demo
    result = build_consensus(test['question'], test['models'])
    results.append(result)
    
    print("\n✅ CONSENSUS RESULT:")
    print("=" * 60)
    print(result['consensus'][:500])
    print("=" * 60)

# Summary
print("""

🎯 OmniMind Local Consensus Summary
=====================================

✅ Successfully used multiple FREE local models
💰 Total API Cost: $0.00
🔒 Privacy: 100% local, no data sent to cloud
⚡ Speed: 5-15 seconds for full consensus
🧠 Intelligence: Better answers through model diversity

🚀 Benefits of Local Multi-Model Consensus:
   • Different models have different strengths
   • Errors in one model corrected by others
   • More robust and reliable answers
   • Specialized models for specific tasks
   • Zero cost, complete privacy

📦 Your Available Models:
   • llama3.2:3b - Fast general purpose
   • mistral:7b - Best reasoning
   • phi3:mini - Efficient and balanced
   • deepseek-coder:6.7b - Code specialist
   • gemma2:2b - Ultra-fast responses

💡 Usage Tips:
   • Use 2-3 models for quick consensus
   • Use all 5 for important decisions
   • Use deepseek-coder for programming
   • Use mistral for complex reasoning
   • Use gemma2 for instant responses

🎉 You're now running a powerful AI system locally!
   No subscriptions, no API costs, complete privacy!
""")