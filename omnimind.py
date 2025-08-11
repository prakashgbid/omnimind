#!/usr/bin/env python3
"""
OmniMind - Human-like Thinking AI System
Main entry point for the application.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.osa_minimal import OSACompleteFinal
from core.logger import setup_logger

# Setup logger
logger = setup_logger("omnimind")


async def main():
    """Main entry point for OmniMind."""
    parser = argparse.ArgumentParser(
        description="OmniMind - Human-like Thinking AI System"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to accomplish (interactive mode if not provided)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="Model to use (default: llama3.2:3b)"
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable continuous thinking"
    )
    parser.add_argument(
        "--no-learning",
        action="store_true",
        help="Disable continuous learning"
    )
    
    args = parser.parse_args()
    
    # Initialize OSA
    logger.info("Initializing OmniMind Super Agent...")
    
    config = {
        "model": args.model,
        "enable_thinking": not args.no_thinking,
        "enable_learning": not args.no_learning,
        "verbose": args.verbose
    }
    
    osa = OSACompleteFinal(config)
    
    # Start OSA
    await osa.initialize()
    
    if args.task:
        # Single task mode
        logger.info(f"Processing task: {args.task}")
        result = await osa.accomplish_task(args.task)
        print(f"\nResult: {result}")
    else:
        # Interactive mode
        logger.info("Starting interactive mode...")
        print("\n" + "="*60)
        print("OmniMind Interactive Mode")
        print("Type 'exit' or 'quit' to stop")
        print("="*60 + "\n")
        
        while True:
            try:
                task = input("\n📝 Enter task: ").strip()
                
                if task.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    break
                
                if not task:
                    continue
                
                result = await osa.accomplish_task(task)
                print(f"\n✅ Result: {result}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error: {e}")
    
    # Cleanup
    await osa.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown requested...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)