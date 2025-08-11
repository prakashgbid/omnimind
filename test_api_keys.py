#!/usr/bin/env python3
"""
Simple test to verify API keys are working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔑 Testing API Keys")
print("=" * 50)

# Check which keys are set
openai_key = os.getenv('OPENAI_API_KEY', '')
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
google_key = os.getenv('GOOGLE_API_KEY', '')

print("\n✅ API Keys Loaded:")
print(f"  • OpenAI:    {'✅ Set' if openai_key else '❌ Missing'} ({len(openai_key)} chars)")
print(f"  • Anthropic: {'✅ Set' if anthropic_key else '❌ Missing'} ({len(anthropic_key)} chars)")
print(f"  • Google:    {'✅ Set' if google_key else '❌ Missing'} ({len(google_key)} chars)")

# Test OpenAI
if openai_key:
    print("\n🧪 Testing OpenAI...")
    try:
        import openai
        # Note: OpenAI library v1.0+ has different API
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI works!'"}],
            max_tokens=10
        )
        print(f"  ✅ OpenAI Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"  ❌ OpenAI Error: {e}")

# Test Google Gemini
if google_key:
    print("\n🧪 Testing Google Gemini...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Gemini works!'")
        print(f"  ✅ Gemini Response: {response.text}")
    except Exception as e:
        print(f"  ❌ Gemini Error: {e}")

# Test Anthropic
if anthropic_key:
    print("\n🧪 Testing Anthropic...")
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'Claude works!'"}]
        )
        print(f"  ✅ Claude Response: {response.content[0].text}")
    except Exception as e:
        print(f"  ❌ Anthropic Error: {e}")

print("\n" + "=" * 50)
print("✨ API Key Test Complete!")
print("\nIf all tests passed, you can now use OmniMind with:")
print("  python3 src/main.py cli")
print("  python3 src/main.py web")