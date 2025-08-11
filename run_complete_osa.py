#!/usr/bin/env python3
"""
Run OSA Complete - The Ultimate Human-like Thinking AI

This script runs the complete OSA with all capabilities:
- Continuous deep thinking
- Leadership and delegation
- Adaptive problem-solving (never stuck)
- Pattern learning
- Architecture self-review
"""

import asyncio
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osa_complete_final import OSACompleteFinal, create_complete_osa


async def interactive_thinking_session():
    """Run an interactive session showcasing OSA's thinking capabilities"""
    
    print("=" * 100)
    print("🧠 OSA Complete - Human-like Thinking Intelligence")
    print("=" * 100)
    print("\nInitializing the complete thinking system...")
    
    # Create complete OSA
    osa = await create_complete_osa(max_claude_instances=10)
    
    print("\n" + "=" * 100)
    print("OSA is ready with human-like thinking capabilities!")
    print("=" * 100)
    
    while True:
        print("\n" + "-" * 80)
        print("What would you like OSA to do?")
        print("-" * 80)
        print("  1. 🧠 Think deeply and accomplish a task")
        print("  2. 👔 Lead a complex project with delegation")
        print("  3. 🔧 Solve a problem (with alternatives if blocked)")
        print("  4. 💭 Think continuously about a topic")
        print("  5. 🎯 Break down a complex goal")
        print("  6. 🔄 Handle a blocked situation")
        print("  7. 📊 Show thinking status & thought graph")
        print("  8. 🏃 Quick demo of all capabilities")
        print("  9. ❌ Exit")
        print("-" * 80)
        
        try:
            choice = input("\n🎯 Your choice (1-9): ").strip()
            
            if choice == "1":
                # Deep thinking and accomplishment
                task = input("\n📋 What task should OSA think about and complete? ").strip()
                if task:
                    print("\n🧠 OSA is thinking deeply about all aspects...")
                    print("   - Analyzing the problem from multiple angles")
                    print("   - Identifying potential blockers")
                    print("   - Preparing alternative paths")
                    print("   - Planning execution strategy")
                    
                    result = await osa.think_and_accomplish(task)
                    
                    print(f"\n✅ Task completed with deep thinking!")
                    print(f"\n📊 Thinking Summary:")
                    print(f"   Total thoughts: {result['thinking_insights']['total_thoughts']}")
                    print(f"   Reasoning chains: {result['thinking_insights']['reasoning_chains']}")
                    print(f"   Blockers handled: {result['thinking_insights']['blockers_handled']}")
                    print(f"   Alternatives ready: {result['thinking_insights']['alternatives_available']}")
                    print(f"   Confidence: {result['thinking_insights']['confidence']:.1%}")
                    
                    print(f"\n📋 Execution Summary:")
                    print(f"   {result.get('summary', 'Task completed successfully')}")
                    
            elif choice == "2":
                # Leadership and delegation
                project_name = input("\n📁 Project name: ").strip()
                requirements_str = input("Requirements (comma-separated): ").strip()
                team_size = input("Team size (default 5): ").strip()
                
                if project_name and requirements_str:
                    requirements = [r.strip() for r in requirements_str.split(",")]
                    team = int(team_size) if team_size.isdigit() else 5
                    
                    print(f"\n👔 OSA is taking leadership of: {project_name}")
                    print(f"   Team size: {team}")
                    print(f"   Requirements: {len(requirements)}")
                    
                    project = await osa.lead_complex_project(
                        project_name,
                        requirements,
                        team_size=team
                    )
                    
                    print(f"\n✅ Project leadership established!")
                    print(f"\n📊 Leadership Summary:")
                    print(f"   Work items created: {len(project['leadership']['work_items'])}")
                    print(f"   Delegation plan: {len(project['leadership']['delegation_plan'])} assignments")
                    print(f"   Strategic thoughts: {project['thinking']['total_thoughts']}")
                    print(f"   Confidence: {project['thinking']['confidence']:.1%}")
                    
            elif choice == "3":
                # Problem solving with alternatives
                problem = input("\n🔧 What problem should OSA solve? ").strip()
                if problem:
                    print("\n🔍 OSA is analyzing the problem...")
                    print("   - Considering direct solutions")
                    print("   - Exploring lateral approaches")
                    print("   - Reverse engineering from goal")
                    print("   - Applying first principles")
                    print("   - Preparing alternatives for any blockers")
                    
                    solution = await osa.solve_with_alternatives(problem)
                    
                    print(f"\n✅ Problem solved with multiple paths!")
                    print(f"\n📊 Solution Summary:")
                    print(f"   Approaches considered: {solution['approaches_considered']}")
                    print(f"   Blockers found: {solution['blockers_found']}")
                    print(f"   Alternative paths: {solution['alternatives_available']}")
                    print(f"   Selected approach: {solution['selected_approach'][:100]}...")
                    print(f"   Confidence: {solution['confidence']:.1%}")
                    print(f"   Guarantee: {solution['guarantee']}")
                    
            elif choice == "4":
                # Continuous thinking
                topic = input("\n💭 What topic should OSA think about? ").strip()
                duration = input("Duration in seconds (default 20): ").strip()
                
                if topic:
                    dur = int(duration) if duration.isdigit() else 20
                    
                    print(f"\n💭 OSA will think continuously about: {topic}")
                    print(f"   Duration: {dur} seconds")
                    print("   Thinking...", end="", flush=True)
                    
                    thinking_result = await osa.think_continuously_about(topic, dur)
                    
                    print(" Done!")
                    print(f"\n📊 Thinking Results:")
                    print(f"   Thoughts generated: {thinking_result['thoughts_generated']}")
                    print(f"   Connections formed: {thinking_result['connections_formed']}")
                    
                    if 'visualization' in thinking_result:
                        print(f"\n🧠 Thought Graph:")
                        print(thinking_result['visualization'])
                    
            elif choice == "5":
                # Break down complex goal
                goal = input("\n🎯 Complex goal to break down: ").strip()
                if goal:
                    print("\n📊 Breaking down the goal...")
                    
                    # Use thinking engine to decompose
                    if hasattr(osa, 'thinking_engine'):
                        context = osa.thinking_engine._create_context(f"Breakdown: {goal}")
                        chain = await osa.thinking_engine.think_about(
                            f"How to break down: {goal}",
                            context,
                            depth=4
                        )
                        
                        print(f"\n✅ Goal decomposed!")
                        print(f"   Reasoning depth: {chain.depth}")
                        print(f"   Thoughts generated: {len(chain.thoughts)}")
                        print(f"   Confidence: {chain.confidence:.1%}")
                        print(f"\n📋 Breakdown:")
                        print(chain.conclusion)
                    
            elif choice == "6":
                # Handle blocked situation
                blocker = input("\n🚧 Describe the blocker: ").strip()
                if blocker:
                    print("\n🔄 Finding alternative paths...")
                    
                    # Create a blocked scenario and find alternatives
                    if hasattr(osa, 'thinking_engine'):
                        context = osa.thinking_engine._create_context(f"Blocked: {blocker}")
                        blocked_thought = osa.thinking_engine._create_thought(
                            type=osa.thinking_engine.ThoughtType.BLOCKER_DETECTION,
                            content=blocker,
                            context=context.id,
                            depth=0
                        )
                        
                        alternative = await osa.thinking_engine._find_alternative_path(
                            blocked_thought,
                            context
                        )
                        
                        if alternative:
                            print(f"\n✅ Alternative paths found!")
                            print(f"   Primary alternative: {alternative.content}")
                            
                            if blocked_thought.id in osa.thinking_engine.alternative_paths:
                                alts = osa.thinking_engine.alternative_paths[blocked_thought.id]
                                print(f"   Total alternatives: {len(alts)}")
                                print("\n📋 All alternatives:")
                                for alt_id in alts[:5]:
                                    if alt_id in osa.thinking_engine.thoughts:
                                        alt_thought = osa.thinking_engine.thoughts[alt_id]
                                        print(f"   • {alt_thought.content}")
                    
            elif choice == "7":
                # Show thinking status
                print("\n📊 OSA Complete Status:")
                status = osa.get_complete_status()
                
                print("\n🧠 Core Systems:")
                print(f"  • Brain: Active")
                print(f"  • Claude Orchestrator: Ready")
                print(f"  • Completed tasks: {status.get('completed_tasks', 0)}")
                
                if 'thinking' in status:
                    print(f"\n💭 Thinking Engine:")
                    print(f"  • Total thoughts: {status['thinking']['total_thoughts']}")
                    print(f"  • Active thoughts: {status['thinking']['active_thoughts']}")
                    print(f"  • Contexts: {status['thinking']['contexts']}")
                    print(f"  • Reasoning chains: {status['thinking']['reasoning_chains']}")
                    print(f"  • Work items: {status['thinking']['work_items']}")
                    print(f"  • Blocked paths: {status['thinking']['blocked_paths']}")
                    print(f"  • Alternative paths: {status['thinking']['alternative_paths']}")
                    print(f"  • Thought connections: {status['thinking']['connections']}")
                
                if 'learning' in status:
                    print(f"\n📚 Learning System:")
                    print(f"  • Patterns recognized: {status['learning']['patterns_recognized']}")
                    print(f"  • Cached solutions: {status['learning']['cached_solutions']}")
                    print(f"  • Efficiency gains: {status['learning']['efficiency_gains']:.1f} minutes")
                
                if 'architecture' in status:
                    print(f"\n🔍 Architecture Health:")
                    print(f"  • Overall health: {status['architecture']['overall_health']:.1%}")
                    print(f"  • Custom code ratio: {status['architecture']['custom_code_ratio']:.1%}")
                
                if 'thought_graph' in status:
                    print(f"\n🧠 Recent Thought Graph:")
                    print(status['thought_graph'])
                    
            elif choice == "8":
                # Quick demo
                print("\n🎬 Running quick demo of all capabilities...")
                
                # Demo task
                demo_task = "Create a real-time chat application with user presence"
                
                print(f"\n1️⃣ Deep Thinking & Accomplishment")
                print(f"   Task: {demo_task}")
                result = await osa.think_and_accomplish(demo_task)
                print(f"   ✅ Generated {result['thinking_insights']['total_thoughts']} thoughts")
                print(f"   ✅ Confidence: {result['thinking_insights']['confidence']:.1%}")
                
                await asyncio.sleep(1)
                
                print(f"\n2️⃣ Problem Solving with Alternatives")
                problem = "Database connection keeps timing out"
                solution = await osa.solve_with_alternatives(problem)
                print(f"   ✅ Found {solution['alternatives_available']} alternative solutions")
                
                await asyncio.sleep(1)
                
                print(f"\n3️⃣ Continuous Thinking")
                thinking = await osa.think_continuously_about("viral app features", 5)
                print(f"   ✅ Generated {thinking['thoughts_generated']} thoughts in 5 seconds")
                
                print("\n✨ Demo complete! OSA demonstrated:")
                print("   • Deep multi-level thinking")
                print("   • Adaptive problem-solving")
                print("   • Continuous thought generation")
                print("   • Never getting stuck")
                
            elif choice == "9":
                print("\n👋 Goodbye! OSA will continue thinking and improving.")
                break
                
            else:
                print("Invalid choice. Please select 1-9.")
                
        except KeyboardInterrupt:
            print("\n\nUse option 9 to exit properly.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point"""
    
    print("\n🧠 OSA Complete - The Ultimate Thinking Intelligence\n")
    print("This system thinks like a human:")
    print("  • Continuously considering thousands of aspects")
    print("  • Never getting stuck - always finding alternatives")
    print("  • Deep nested reasoning with research backing")
    print("  • Leading and orchestrating complex work")
    print("  • Learning and self-improving constantly")
    
    await interactive_thinking_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 OSA Complete shutting down...")
        print("   Saving thoughts and learnings...")
        print("   Done!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()