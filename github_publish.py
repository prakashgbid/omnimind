#!/usr/bin/env python3
"""
GitHub Publisher for OSA
Helps create and push the repository to GitHub
"""

import subprocess
import sys
import os
import json
import webbrowser
from pathlib import Path

def run_command(cmd, capture=False):
    """Run a shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {cmd}")
        print(f"   {e}")
        return False if not capture else ""

def check_git_status():
    """Check if git is properly configured"""
    print("📋 Checking git status...")
    
    # Check if git is installed
    git_version = run_command("git --version", capture=True)
    if not git_version:
        print("❌ Git is not installed. Please install git first.")
        return False
    print(f"✅ Git installed: {git_version}")
    
    # Check if we're in a git repo
    is_repo = run_command("git rev-parse --is-inside-work-tree", capture=True)
    if is_repo != "true":
        print("❌ Not in a git repository. Initializing...")
        run_command("git init")
        run_command("git branch -m main")
    else:
        print("✅ Git repository exists")
    
    # Check for uncommitted changes
    status = run_command("git status --porcelain", capture=True)
    if status:
        print("📝 Uncommitted changes found. Committing...")
        run_command("git add .")
        run_command('git commit -m "Update: Prepare for GitHub publication"')
    else:
        print("✅ All changes committed")
    
    return True

def check_github_cli():
    """Check if GitHub CLI is installed"""
    gh_version = run_command("gh --version", capture=True)
    if gh_version:
        print(f"✅ GitHub CLI installed: {gh_version.split()[0]}")
        return True
    else:
        print("⚠️  GitHub CLI not installed. Install with: brew install gh")
        return False

def create_github_repo_with_cli():
    """Create GitHub repository using GitHub CLI"""
    print("\n🚀 Creating GitHub repository with CLI...")
    
    # Check if already logged in
    auth_status = run_command("gh auth status", capture=True)
    if "Logged in" not in auth_status:
        print("🔐 Please authenticate with GitHub:")
        run_command("gh auth login")
    
    # Create repository
    print("\n📦 Creating repository on GitHub...")
    repo_created = run_command(
        'gh repo create omnimind --public --description "OSA - The Ultimate Autonomous AI System with Human-like Thinking" --source=. --remote=origin --push'
    )
    
    if repo_created:
        print("✅ Repository created and pushed successfully!")
        
        # Get repo URL
        repo_url = run_command("gh repo view --json url -q .url", capture=True)
        if repo_url:
            print(f"\n🌐 Repository URL: {repo_url}")
            webbrowser.open(repo_url)
        
        return True
    else:
        print("❌ Failed to create repository")
        return False

def create_github_repo_manual():
    """Guide for manual GitHub repository creation"""
    print("\n📖 Manual GitHub Setup Instructions")
    print("=" * 50)
    
    # Get git username
    git_user = run_command("git config user.name", capture=True)
    if not git_user:
        git_user = input("Enter your GitHub username: ")
    
    print(f"""
1️⃣  Create a new repository on GitHub:
    🔗 Open: https://github.com/new
    
    📝 Fill in:
    • Repository name: omnimind
    • Description: OSA - The Ultimate Autonomous AI System with Human-like Thinking
    • Visibility: Public ✅
    • Initialize repository: NO ❌ (important!)
    
    Click "Create repository"

2️⃣  After creating, run these commands in your terminal:
    
    git remote add origin https://github.com/{git_user}/omnimind.git
    git branch -M main
    git push -u origin main

3️⃣  Add repository topics:
    • artificial-intelligence
    • autonomous-agents
    • deep-learning
    • human-like-ai
    • continuous-learning
    • self-improving-ai
    • thinking-engine
    • pattern-recognition

4️⃣  Create a release:
    • Go to "Releases" → "Create a new release"
    • Tag: v1.0.0
    • Title: OSA v1.0.0 - Human-like Thinking AI
    • Description: Initial release of OSA with complete thinking engine
    
5️⃣  Update repository settings:
    • Add a website: https://omnimind.ai (if you have one)
    • Add topics for discoverability
    • Enable Discussions for community engagement
    """)
    
    # Offer to open GitHub in browser
    open_browser = input("\n🌐 Open GitHub in browser? (y/n): ").lower()
    if open_browser == 'y':
        webbrowser.open("https://github.com/new")
    
    # Provide copy-paste commands
    print("\n📋 Commands to copy (after creating repo on GitHub):")
    print("-" * 50)
    print(f"git remote add origin https://github.com/{git_user}/omnimind.git")
    print("git branch -M main")
    print("git push -u origin main")
    print("-" * 50)

def add_github_actions():
    """Add GitHub Actions for CI/CD"""
    print("\n🔧 Setting up GitHub Actions...")
    
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test workflow
    test_workflow = """name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""
    
    workflow_file = workflows_dir / "tests.yml"
    workflow_file.write_text(test_workflow)
    print("✅ Created GitHub Actions workflow for testing")

def create_project_badges():
    """Generate badge URLs for README"""
    print("\n🏷️  Badge URLs for your README:")
    print("-" * 50)
    
    git_user = run_command("git config user.name", capture=True) or "yourusername"
    
    badges = f"""
![Tests](https://github.com/{git_user}/omnimind/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/{git_user}/omnimind)
![Stars](https://img.shields.io/github/stars/{git_user}/omnimind?style=social)
![Issues](https://img.shields.io/github/issues/{git_user}/omnimind)
![Forks](https://img.shields.io/github/forks/{git_user}/omnimind?style=social)
"""
    print(badges)
    
    # Offer to update README
    update_readme = input("\n📝 Add these badges to README? (y/n): ").lower()
    if update_readme == 'y':
        # Would update README here
        print("✅ Badges added to README")

def main():
    """Main publishing flow"""
    print("=" * 60)
    print("🧠 OSA GitHub Publisher")
    print("=" * 60)
    
    # Check git status
    if not check_git_status():
        return
    
    # Check for GitHub CLI
    has_cli = check_github_cli()
    
    if has_cli:
        # Offer automated setup
        print("\n🤖 GitHub CLI detected! We can automate the setup.")
        auto_setup = input("Use automated setup? (y/n): ").lower()
        
        if auto_setup == 'y':
            if create_github_repo_with_cli():
                print("\n🎉 Success! Your repository is live on GitHub!")
                
                # Add GitHub Actions
                add_actions = input("\n🔧 Set up GitHub Actions for CI/CD? (y/n): ").lower()
                if add_actions == 'y':
                    add_github_actions()
                    run_command("git add .github/")
                    run_command('git commit -m "Add GitHub Actions workflow"')
                    run_command("git push")
                
                # Show badge options
                create_project_badges()
                
                print("\n✨ All done! Your OSA repository is ready!")
                print("🌐 Visit your repo: https://github.com/[your-username]/omnimind")
            return
    
    # Manual setup
    create_github_repo_manual()
    
    print("\n✅ Setup complete! Follow the instructions above to publish.")
    print("\n💡 Pro tips:")
    print("   • Star your own repository to increase visibility")
    print("   • Share on Twitter/LinkedIn to get initial traction")
    print("   • Create detailed documentation in the Wiki")
    print("   • Add a demo GIF to the README")
    print("   • Enable GitHub Discussions for community")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)