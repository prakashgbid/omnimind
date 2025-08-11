#!/usr/bin/env python3
"""
OmniMind Main Entry Point

This is the main file that starts OmniMind.
It provides options to run the CLI, Web UI, or use as a library.
"""

import sys
import os
import argparse
from typing import Optional

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import OmniMindCLI
from src.web_ui import OmniMindWebUI
from src.core.omnimind_enhanced import OmniMindEnhanced as OmniMind


def print_banner():
    """Print the OmniMind banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🧠 OmniMind v2.0 🧠               ║
    ║                                           ║
    ║   Your FREE Persistent Intelligence       ║
    ║   5 Local LLMs • Perfect Memory • $0/mo   ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)


def quick_demo():
    """Run a quick demo of OmniMind capabilities."""
    print_banner()
    print("\n📋 Running OmniMind Demo...\n")
    
    try:
        # Initialize OmniMind
        print("1️⃣ Initializing OmniMind...")
        om = OmniMind()
        print("   ✅ OmniMind ready!\n")
        
        # Store some memories
        print("2️⃣ Storing sample memories...")
        
        memories = [
            "Decided to use TypeScript for the new project for better type safety",
            "WebSockets are better than SSE for our real-time features",
            "We should use PostgreSQL instead of MySQL for better JSON support",
            "Authentication will use JWT tokens with refresh token rotation"
        ]
        
        for memory in memories:
            memory_id = om.remember(memory, context={"demo": True})
            print(f"   ✅ Stored: {memory[:50]}...")
        
        print()
        
        # Search memories
        print("3️⃣ Testing semantic search...")
        results = om.search_memories("database choice", limit=3)
        print(f"   Found {len(results)} relevant memories")
        if results:
            print(f"   Top result (score {results[0]['score']:.2f}): {results[0]['content'][:60]}...")
        
        print()
        
        # Ask a question
        print("4️⃣ Testing contextual thinking...")
        response = om.think("What database should we use and why?", use_consensus=False)
        print(f"   Response: {response[:200]}...")
        
        print("\n✨ Demo complete! OmniMind is working correctly.\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("   Make sure Ollama is running and models are downloaded.")
        print("   Run: ./scripts/setup.sh")
        return False
    
    return True


def main():
    """Main entry point for OmniMind."""
    parser = argparse.ArgumentParser(
        description="OmniMind - Your Persistent Intelligence System",
        epilog="For more information, visit the README.md file"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='mode', help='OmniMind modes')
    
    # CLI mode
    cli_parser = subparsers.add_parser('cli', help='Run interactive CLI')
    cli_parser.add_argument('--no-banner', action='store_true', help='Skip banner')
    
    # Web mode
    web_parser = subparsers.add_parser('web', help='Launch web interface')
    web_parser.add_argument('--port', type=int, default=7860, help='Port for web server')
    web_parser.add_argument('--share', action='store_true', help='Create public URL')
    web_parser.add_argument('--no-browser', action='store_true', help="Don't open browser")
    
    # Demo mode
    demo_parser = subparsers.add_parser('demo', help='Run quick demo')
    
    # Direct query mode
    query_parser = subparsers.add_parser('ask', help='Ask a single question')
    query_parser.add_argument('question', nargs='+', help='Your question')
    query_parser.add_argument('--consensus', action='store_true', help='Use consensus')
    query_parser.add_argument('--model', type=str, help='Specific model to use')
    
    # Search mode
    search_parser = subparsers.add_parser('search', help='Search memories')
    search_parser.add_argument('query', nargs='+', help='Search query')
    search_parser.add_argument('--limit', type=int, default=5, help='Max results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default to CLI if no mode specified
    if not args.mode:
        print_banner()
        print("\nChoose a mode:")
        print("  1. CLI - Interactive command line")
        print("  2. Web - Browser interface")
        print("  3. Demo - Quick demonstration")
        print()
        
        choice = input("Enter choice (1/2/3) or 'q' to quit: ").strip()
        
        if choice == '1':
            args.mode = 'cli'
        elif choice == '2':
            args.mode = 'web'
        elif choice == '3':
            args.mode = 'demo'
        else:
            print("Goodbye!")
            return
    
    # Execute chosen mode
    if args.mode == 'cli':
        if not args.no_banner:
            print_banner()
        cli = OmniMindCLI()
        cli.run()
        
    elif args.mode == 'web':
        print_banner()
        print(f"\n🌐 Starting web interface on port {args.port}...")
        ui = OmniMindWebUI()
        interface = ui.create_interface()
        interface.launch(
            server_port=args.port,
            share=args.share,
            inbrowser=not args.no_browser
        )
        
    elif args.mode == 'demo':
        success = quick_demo()
        if success:
            print("Try running:")
            print("  python src/main.py cli    # For interactive CLI")
            print("  python src/main.py web    # For web interface")
        
    elif args.mode == 'ask':
        # Single question mode
        question = ' '.join(args.question)
        print(f"\n💭 Question: {question}\n")
        
        try:
            om = OmniMind()
            kwargs = {'use_consensus': args.consensus}
            if hasattr(args, 'model') and args.model:
                kwargs['model'] = args.model
                print(f"Using model: {args.model}\n")
            response = om.think(question, **kwargs)
            print(f"🧠 OmniMind says:\n\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    elif args.mode == 'search':
        # Search mode
        query = ' '.join(args.query)
        print(f"\n🔍 Searching for: {query}\n")
        
        try:
            om = OmniMind()
            results = om.search_memories(query, limit=args.limit)
            
            if not results:
                print("No memories found.")
            else:
                for i, result in enumerate(results, 1):
                    score = result['score']
                    content = result['content'][:150]
                    print(f"{i}. [Score: {score:.2f}] {content}...")
                    print()
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()