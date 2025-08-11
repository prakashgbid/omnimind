#!/usr/bin/env python3
"""
Run OSA Enhanced - The Complete Self-Improving System

This script runs the fully enhanced OSA with:
- Continuous learning
- Daily architecture review
- Smart optimization
- Minimum custom coding principle
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osa_enhanced import OSAEnhanced, create_enhanced_osa


async def interactive_session():
    """Run an interactive session with enhanced OSA"""
    
    print("=" * 80)
    print("🧠 OSA Enhanced - Interactive Session")
    print("=" * 80)
    print("\nInitializing the self-improving super agent...")
    
    # Create enhanced OSA
    osa = await create_enhanced_osa(max_claude_instances=10)
    
    print("\n" + "=" * 80)
    print("OSA is ready! You can give it any task and it will:")
    print("  1. Check if it's done similar work before (pattern recognition)")
    print("  2. Research the best existing tools (minimum custom coding)")
    print("  3. Complete the task autonomously")
    print("  4. Learn from the experience")
    print("  5. Self-improve its architecture daily")
    print("=" * 80)
    
    while True:
        print("\n" + "-" * 60)
        print("Options:")
        print("  1. Give OSA a task to complete")
        print("  2. Ask OSA to optimize a task")
        print("  3. Start an internal debate")
        print("  4. Trigger architecture review")
        print("  5. Check OSA status")
        print("  6. Exit")
        print("-" * 60)
        
        try:
            choice = input("\n🎯 Your choice (1-6): ").strip()
            
            if choice == "1":
                task = input("\n📋 What task should OSA complete? ").strip()
                if task:
                    print("\n🚀 OSA is taking over...")
                    result = await osa.accomplish(task)
                    print(f"\n✅ Task completed!")
                    print(f"Summary: {result['summary']}")
                    print(f"Instances used: {result['instances_used']}")
                    
            elif choice == "2":
                task = input("\n🔍 What task should OSA optimize? ").strip()
                if task:
                    print("\n🧠 Analyzing optimization opportunities...")
                    optimization = await osa.think_about_optimization(task)
                    
                    print(f"\n📊 Optimization Analysis:")
                    print(f"Strategy: {optimization['smart_approach']['strategy']}")
                    print(f"Time savings: {optimization['estimated_savings']} minutes")
                    
                    if optimization['recommended_tools']:
                        print(f"\nRecommended tools:")
                        for tool in optimization['recommended_tools'][:3]:
                            print(f"  • {tool['name']} (score: {tool['score']:.2f})")
                    
                    if optimization['learned_patterns']:
                        print(f"\n♻️ Recognized patterns - can reuse previous solutions!")
                    
            elif choice == "3":
                topic = input("\n💭 Debate topic: ").strip()
                options_str = input("Options (comma-separated): ").strip()
                
                if topic and options_str:
                    options = [opt.strip() for opt in options_str.split(",")]
                    print("\n🤔 Conducting internal debate...")
                    
                    debate = await osa.internal_debate(topic, options)
                    
                    print(f"\n🏆 Debate Result:")
                    print(f"Winner: {debate['winner']}")
                    print(f"Reasoning: {', '.join(debate['reasoning'][:2])}")
                    
            elif choice == "4":
                print("\n🔍 Triggering architecture review...")
                review = await osa.review_and_improve()
                
                if 'review' in review:
                    print(f"\n📊 Review Results:")
                    print(f"Components reviewed: {len(review['review']['components_reviewed'])}")
                    print(f"Improvements found: {review['review']['improvements_found']}")
                    print(f"Potential improvement: {review['review']['estimated_improvement']:.1f}%")
                    
                    if review['review']['tools_to_replace']:
                        print(f"\nTools to replace:")
                        for comp, tool in review['review']['tools_to_replace'].items():
                            print(f"  • {comp}: → {tool}")
                    
            elif choice == "5":
                print("\n📊 OSA Enhanced Status:")
                status = osa.get_enhanced_status()
                
                print(f"\nCore Systems:")
                print(f"  • Brain: Active")
                print(f"  • Claude Orchestrator: {status['claude_orchestrator']['active_instances']}/{status['claude_orchestrator']['max_instances']} instances")
                print(f"  • Completed tasks: {status['completed_tasks']}")
                
                if 'learning' in status:
                    print(f"\nLearning System:")
                    print(f"  • Patterns recognized: {status['learning']['patterns_recognized']}")
                    print(f"  • Cached solutions: {status['learning']['cached_solutions']}")
                    print(f"  • Total efficiency gains: {status['learning']['efficiency_gains']:.1f} minutes")
                
                if 'architecture' in status:
                    print(f"\nArchitecture Health:")
                    print(f"  • Overall health: {status['architecture']['overall_health']:.1%}")
                    print(f"  • Custom code ratio: {status['architecture']['custom_code_ratio']:.1%} (lower is better)")
                    print(f"  • Best practices: {'✅' if status['architecture']['using_best_practices'] else '⚠️'}")
                    
                    if status['architecture']['recommendations']:
                        print(f"\nRecommendations:")
                        for rec in status['architecture']['recommendations'][:3]:
                            print(f"  • {rec}")
                
            elif choice == "6":
                print("\n👋 Goodbye! OSA will continue learning and improving.")
                break
                
            else:
                print("Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\nUse option 6 to exit properly.")
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def automated_demo():
    """Run an automated demonstration of OSA's capabilities"""
    
    print("=" * 80)
    print("🎬 OSA Enhanced - Automated Demonstration")
    print("=" * 80)
    
    osa = await create_enhanced_osa(max_claude_instances=5)
    
    # Demo tasks that show learning
    tasks = [
        "Create a user authentication system",
        "Build a REST API with CRUD operations",
        "Create another authentication system",  # Should recognize pattern
        "Build another REST API",  # Should reuse solution
        "Add payment processing to an app"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{'='*60}")
        print(f"Demo {i}/{len(tasks)}: {task}")
        print("="*60)
        
        # First, analyze optimization
        optimization = await osa.think_about_optimization(task)
        
        if optimization['learned_patterns']:
            print("✨ Pattern recognized! Reusing previous solution.")
            print(f"   Time saved: {optimization['estimated_savings']} minutes")
        elif optimization['recommended_tools']:
            print("🛠️ Found existing tools to use:")
            for tool in optimization['recommended_tools'][:2]:
                print(f"   • {tool['name']}")
        
        # Execute task
        print("\n🚀 Executing task...")
        result = await osa.accomplish(task)
        print(f"✅ Completed in {result.get('execution_time', 'N/A')}")
        
        # Brief pause
        await asyncio.sleep(2)
    
    # Show final learning summary
    print("\n" + "="*80)
    print("📊 Learning Summary After Demo")
    print("="*80)
    
    status = osa.get_enhanced_status()
    
    if 'learning' in status:
        print(f"\nLearning Achievements:")
        print(f"  • Patterns learned: {status['learning']['patterns_recognized']}")
        print(f"  • Solutions cached: {status['learning']['cached_solutions']}")
        print(f"  • Total time saved: {status['learning']['efficiency_gains']:.1f} minutes")
        print("\n✨ OSA is now smarter and will work more efficiently on similar tasks!")
    
    print("\n" + "="*80)
    print("Demo complete! OSA Enhanced is ready for production use.")
    print("="*80)


async def main():
    """Main entry point"""
    
    print("\n🧠 OSA Enhanced - The Self-Improving Super Agent\n")
    print("Select mode:")
    print("  1. Interactive session")
    print("  2. Automated demo")
    print("  3. Quick test")
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == "1":
        await interactive_session()
    elif choice == "2":
        await automated_demo()
    elif choice == "3":
        # Quick test
        print("\n🚀 Quick Test: Building a task management app...")
        osa = await create_enhanced_osa(max_claude_instances=5)
        result = await osa.accomplish("Build a simple task management web app with user accounts")
        print(f"\n✅ Test completed!")
        print(f"Result: {result['summary']}")
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 OSA Enhanced shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()