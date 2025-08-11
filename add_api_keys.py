#!/usr/bin/env python3
"""
Add API Keys to OmniMind

This script helps you securely add API keys to your .env file.
"""

import os
import getpass

print("""
🔑 OmniMind API Key Setup
========================

This will help you add API keys for cloud LLMs.

Options:
1. OpenAI (GPT-4) - Has free trial credits
2. Anthropic (Claude) - Requires payment
3. Google (Gemini) - Has free tier
4. Skip and use local models only

""")

def add_key_to_env(key_name, key_value):
    """Add or update a key in .env file."""
    env_file = '.env'
    
    # Read existing content
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        # Copy from example if .env doesn't exist
        os.system('cp .env.example .env')
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update the key
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key_name}="):
            lines[i] = f"{key_name}={key_value}\n"
            updated = True
            break
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    return updated

# Get user choice
while True:
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        print("\n📘 OpenAI Setup")
        print("Get your key from: https://platform.openai.com/api-keys")
        print("New accounts get $5 free credits!")
        key = getpass.getpass("Enter your OpenAI API key (hidden): ").strip()
        if key:
            add_key_to_env("OPENAI_API_KEY", key)
            print("✅ OpenAI key added to .env")
    
    elif choice == '2':
        print("\n🤖 Anthropic Setup")
        print("Get your key from: https://console.anthropic.com/settings/keys")
        print("Note: Requires payment setup (minimum $5)")
        key = getpass.getpass("Enter your Anthropic API key (hidden): ").strip()
        if key:
            add_key_to_env("ANTHROPIC_API_KEY", key)
            print("✅ Anthropic key added to .env")
    
    elif choice == '3':
        print("\n🌐 Google Gemini Setup")
        print("Get your key from: https://makersuite.google.com/app/apikey")
        print("Free tier available!")
        key = getpass.getpass("Enter your Google API key (hidden): ").strip()
        if key:
            add_key_to_env("GOOGLE_API_KEY", key)
            print("✅ Google key added to .env")
    
    elif choice == '4':
        print("\n🏠 Using local models only")
        add_key_to_env("USE_LOCAL_MODELS", "true")
        print("Set to use local models")
        break
    
    else:
        print("Invalid choice")
        continue
    
    another = input("\nAdd another API key? (y/n): ").strip().lower()
    if another != 'y':
        break

print("\n✅ Setup complete!")
print("\nYour configuration:")
print("-" * 30)

# Show what's configured
env_file = '.env'
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if 'API_KEY=' in line:
                key_name = line.split('=')[0]
                has_value = len(line.split('=')[1].strip()) > 0
                status = "✅ Set" if has_value else "❌ Not set"
                print(f"{key_name}: {status}")

print("\n📝 Next Steps:")
print("-" * 30)
print("1. Install Ollama for local models (free):")
print("   brew install ollama")
print("   ollama serve")
print("   ollama pull llama3.2:3b")
print()
print("2. Test OmniMind:")
print("   python3 test_omnimind.py")
print()
print("3. Start using OmniMind:")
print("   python3 src/main.py cli  # Terminal")
print("   python3 src/main.py web  # Browser")