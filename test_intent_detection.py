#!/usr/bin/env python3
"""Test OSA's autonomous intent detection"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from core.osa_autonomous import OSAAutonomous, IntentType

# Test cases with expected intents
test_cases = [
    ("Write a Python function to sort a list", IntentType.CODE_GENERATION),
    ("My code is throwing an error, help me fix it", IntentType.CODE_DEBUG),
    ("How can I make this code run faster?", IntentType.CODE_REFACTOR),
    ("Think deeply about the nature of consciousness", IntentType.DEEP_THINKING),
    ("How do I solve this math equation: 2x + 5 = 15", IntentType.PROBLEM_SOLVING),
    ("Teach me about machine learning", IntentType.LEARNING),
    ("What is quantum computing?", IntentType.EXPLANATION),
    ("Create a story about a robot learning to love", IntentType.CREATIVE),
    ("Analyze the pros and cons of remote work", IntentType.ANALYSIS),
    ("Hello, how are you today?", IntentType.GENERAL_CHAT),
    ("Run a command to list all files", IntentType.SYSTEM_TASK),
]

print("Testing OSA Autonomous Intent Detection")
print("=" * 60)

# Initialize OSA
osa = OSAAutonomous()

# Test each case
correct = 0
for user_input, expected_intent in test_cases:
    detected_intent, confidence = osa.detect_intent(user_input)
    
    # Check if correct
    is_correct = detected_intent == expected_intent
    if is_correct:
        correct += 1
        symbol = "✅"
    else:
        symbol = "❌"
    
    print(f"\n{symbol} Input: {user_input[:50]}...")
    print(f"   Expected: {expected_intent.value}")
    print(f"   Detected: {detected_intent.value} (confidence: {confidence:.0%})")

# Summary
print("\n" + "=" * 60)
accuracy = (correct / len(test_cases)) * 100
print(f"Accuracy: {correct}/{len(test_cases)} ({accuracy:.0f}%)")

if accuracy >= 80:
    print("✨ Intent detection is working well!")
else:
    print("⚠️  Intent detection needs improvement")