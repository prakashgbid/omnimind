#!/usr/bin/env python3
"""
OSA Enhanced - Complete System with Learning & Architecture Review

This integrates:
1. OSA Core (Brain + Orchestrator)
2. Continuous Learning System
3. Daily Architecture Reviewer

The ultimate autonomous system that learns and improves itself.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

# Core OSA components
from osa_complete import OSA, create_osa
from osa_continuous_learning import enhance_osa_with_learning
from osa_architecture_reviewer import enhance_osa_with_architecture_review


class OSAEnhanced(OSA):
    """
    Enhanced OSA with all advanced capabilities:
    - Continuous learning from interactions
    - Daily architecture self-review
    - Smart work optimization
    - Minimum custom coding principle
    """
    
    def __init__(self, max_claude_instances: int = 10):
        super().__init__(max_claude_instances)
        
        # Enhanced configuration
        self.config.update({
            'continuous_learning': True,
            'architecture_review': True,
            'smart_optimization': True,
            'minimum_custom_coding': True
        })
        
        self.logger.info("🚀 Initializing OSA Enhanced with Learning & Architecture Review")
    
    async def initialize(self):
        """Initialize enhanced OSA with all subsystems"""
        
        # Initialize base OSA
        await super().initialize()
        
        # Add continuous learning
        self.logger.info("🧠 Adding continuous learning capabilities...")
        await enhance_osa_with_learning(self)
        
        # Add architecture review
        self.logger.info("🔍 Adding architecture review capabilities...")
        await enhance_osa_with_architecture_review(self)
        
        self.logger.info("✨ OSA Enhanced fully operational with self-improvement capabilities!")
        
        return self._get_enhanced_greeting()
    
    def _get_enhanced_greeting(self) -> str:
        """Generate enhanced OSA greeting"""
        return """
🧠 OSA Enhanced - The Self-Improving Super Agent!

I'm your autonomous intelligence that:
- Completes any task end-to-end
- Learns from every interaction
- Reviews and improves my own architecture daily
- Works smarter, not harder
- Always finds existing tools before building

Special Capabilities:
✨ Continuous Learning: I remember patterns and avoid repetition
🔍 Architecture Review: I self-improve daily at 2 AM
🚀 Smart Optimization: I recognize when to reuse solutions
🛠️ Tool Research: I find the best existing tools first

Just tell me what you want, and I'll handle everything intelligently!
"""
    
    async def accomplish(self, goal: str) -> Dict[str, Any]:
        """
        Enhanced accomplish with learning and smart optimization.
        
        This method now:
        1. Checks for pattern recognition
        2. Applies learned optimizations
        3. Researches tools before building
        4. Learns from execution
        """
        
        self.logger.info(f"🎯 OSA Enhanced received goal: {goal}")
        
        # Check if we have a smart approach
        if hasattr(self, 'learning_system'):
            smart_approach = self.learning_system.get_smart_approach(goal)
            
            if smart_approach['strategy'] == 'reuse':
                self.logger.info(f"♻️ Reusing previous solution, saving {smart_approach['estimated_time_saved']} minutes")
                return smart_approach.get('cached_solution', await super().accomplish(goal))
            
            if smart_approach['optimizations']:
                self.logger.info(f"🚀 Applying optimizations: {smart_approach['optimizations']}")
        
        # Check if we need new tools
        if hasattr(self, 'architecture_reviewer'):
            needs = self._extract_needs_from_goal(goal)
            for need in needs:
                research = await self.architecture_reviewer.research_specific_need(need)
                if research['recommended_tools']:
                    self.logger.info(f"📚 Using tool for {need}: {research['recommendation']}")
        
        # Execute with base OSA
        result = await super().accomplish(goal)
        
        # Learn from execution
        if hasattr(self, 'learning_system'):
            await self.learning_system.learn_from_user({
                'task': goal,
                'solution': result,
                'execution_time': result.get('execution_time', 10),
                'user_input': goal,
                'response': result.get('summary', ''),
                'feedback': 'completed'
            })
            
            # Store solution for future reuse
            self.learning_system.store_solution(goal, result)
        
        return result
    
    def _extract_needs_from_goal(self, goal: str) -> List[str]:
        """Extract needs from goal description"""
        needs = []
        goal_lower = goal.lower()
        
        need_keywords = {
            'authentication': ['auth', 'login', 'user', 'signin'],
            'database': ['database', 'data', 'store', 'persist'],
            'payment': ['payment', 'billing', 'subscription', 'checkout'],
            'email': ['email', 'mail', 'notification', 'send'],
            'deployment': ['deploy', 'host', 'launch', 'publish'],
            'monitoring': ['monitor', 'track', 'analytics', 'metrics'],
            'testing': ['test', 'quality', 'validation']
        }
        
        for need, keywords in need_keywords.items():
            if any(keyword in goal_lower for keyword in keywords):
                needs.append(need)
        
        return needs
    
    async def think_about_optimization(self, task: str) -> Dict[str, Any]:
        """
        Special method to think about how to optimize a task.
        Uses both learning and architecture review insights.
        """
        
        optimization_analysis = {
            'task': task,
            'learned_patterns': [],
            'recommended_tools': [],
            'smart_approach': None,
            'estimated_savings': 0
        }
        
        # Get insights from learning system
        if hasattr(self, 'learning_system'):
            # Check for patterns
            repetition = self.learning_system.check_for_repetition(task)
            if repetition:
                optimization_analysis['learned_patterns'].append(repetition)
                optimization_analysis['estimated_savings'] += repetition.get('time_saved', 0)
            
            # Get smart approach
            smart_approach = self.learning_system.get_smart_approach(task)
            optimization_analysis['smart_approach'] = smart_approach
            optimization_analysis['estimated_savings'] += smart_approach['estimated_time_saved']
        
        # Get tool recommendations
        if hasattr(self, 'architecture_reviewer'):
            needs = self._extract_needs_from_goal(task)
            for need in needs:
                research = await self.architecture_reviewer.research_specific_need(need)
                if research['recommended_tools']:
                    optimization_analysis['recommended_tools'].extend(research['recommended_tools'])
        
        return optimization_analysis
    
    async def internal_debate(self, topic: str, options: List[str]) -> Dict[str, Any]:
        """
        Conduct internal debate on a decision.
        Uses learning system's debate mechanism.
        """
        
        if hasattr(self, 'learning_system'):
            debate = await self.learning_system.conduct_internal_debate(topic, options)
            return {
                'topic': topic,
                'winner': debate.winner,
                'conclusion': debate.conclusion,
                'reasoning': debate.arguments_for[debate.winner]
            }
        
        # Fallback if no learning system
        return {
            'topic': topic,
            'winner': options[0] if options else None,
            'conclusion': 'Selected first option as default',
            'reasoning': ['No learning system available for debate']
        }
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get comprehensive status including learning and architecture"""
        
        base_status = self.get_status()
        
        # Add learning status
        if hasattr(self, 'learning_system'):
            learning_summary = self.learning_system.summarize_learnings()
            base_status['learning'] = {
                'total_learnings': learning_summary['total_learnings'],
                'patterns_recognized': learning_summary['total_patterns'],
                'cached_solutions': learning_summary['cached_solutions'],
                'efficiency_gains': learning_summary['efficiency_gains']
            }
        
        # Add architecture status
        if hasattr(self, 'architecture_reviewer'):
            arch_status = self.architecture_reviewer.get_architecture_status()
            base_status['architecture'] = {
                'overall_health': arch_status['overall_health'],
                'custom_code_ratio': arch_status['custom_code_ratio'],
                'using_best_practices': arch_status['using_best_practices'],
                'recommendations': arch_status['recommendations']
            }
        
        return base_status
    
    async def review_and_improve(self):
        """
        Manually trigger architecture review and improvement.
        Useful for on-demand optimization.
        """
        
        self.logger.info("🔍 Starting manual architecture review...")
        
        if hasattr(self, 'architecture_reviewer'):
            # Perform review
            review = await self.architecture_reviewer.perform_daily_review()
            
            # Implement improvements
            implementation = await self.architecture_reviewer.implement_improvements(review)
            
            return {
                'review': {
                    'components_reviewed': review.components_reviewed,
                    'improvements_found': len(review.improvements_found),
                    'tools_to_replace': review.tools_to_replace,
                    'estimated_improvement': review.estimated_improvement
                },
                'implementation': implementation
            }
        
        return {'message': 'Architecture reviewer not available'}


# Convenience functions
async def create_enhanced_osa(max_claude_instances: int = 10) -> OSAEnhanced:
    """Create and initialize enhanced OSA"""
    osa = OSAEnhanced(max_claude_instances=max_claude_instances)
    await osa.initialize()
    return osa


# Demo showcasing all capabilities
async def demo_enhanced_osa():
    """Demonstrate OSA Enhanced with all capabilities"""
    
    print("=" * 70)
    print("🧠 OSA Enhanced - Self-Improving Super Agent Demo")
    print("=" * 70)
    
    # Create enhanced OSA
    osa = await create_enhanced_osa(max_claude_instances=5)
    
    # 1. Show smart optimization
    print("\n📊 Smart Optimization Demo")
    print("-" * 40)
    
    task1 = "Create a user authentication system with login and signup"
    optimization = await osa.think_about_optimization(task1)
    
    print(f"Task: {task1}")
    print(f"Recommended tools: {[t['name'] for t in optimization['recommended_tools'][:3]]}")
    print(f"Smart approach: {optimization['smart_approach']['strategy']}")
    print(f"Estimated time saved: {optimization['estimated_savings']} minutes")
    
    # 2. Internal debate
    print("\n🤔 Internal Debate Demo")
    print("-" * 40)
    
    debate_result = await osa.internal_debate(
        "Which authentication method to use?",
        ["Clerk (existing tool)", "Auth0 (existing tool)", "Build custom (more work)"]
    )
    
    print(f"Topic: {debate_result['topic']}")
    print(f"Winner: {debate_result['winner']}")
    print(f"Reasoning: {debate_result['reasoning'][:2]}")
    
    # 3. Execute task with learning
    print("\n🚀 Task Execution with Learning")
    print("-" * 40)
    
    task2 = "Build a simple REST API with CRUD operations"
    print(f"Task: {task2}")
    print("OSA is working autonomously with optimization...")
    
    result = await osa.accomplish(task2)
    
    print(f"✅ Completed!")
    print(f"Used approach: Intelligent with pattern recognition")
    print(f"Instances used: {result['instances_used']}")
    
    # 4. Show learning from repetition
    print("\n♻️ Pattern Recognition Demo")
    print("-" * 40)
    
    # Try similar task - should recognize pattern
    task3 = "Create another REST API with CRUD functionality"
    optimization2 = await osa.think_about_optimization(task3)
    
    if optimization2['learned_patterns']:
        print(f"✨ Recognized pattern from previous task!")
        print(f"Can reuse solution, saving {optimization2['estimated_savings']} minutes")
    
    # 5. Architecture review
    print("\n🔍 Architecture Review Demo")
    print("-" * 40)
    
    review_result = await osa.review_and_improve()
    
    if 'review' in review_result:
        print(f"Components reviewed: {len(review_result['review']['components_reviewed'])}")
        print(f"Improvements found: {review_result['review']['improvements_found']}")
        print(f"Potential improvement: {review_result['review']['estimated_improvement']:.1f}%")
    
    # 6. Final status
    print("\n📊 Enhanced OSA Status")
    print("-" * 40)
    
    status = osa.get_enhanced_status()
    
    print(f"Brain status: Active")
    print(f"Claude orchestrator: Ready")
    print(f"Learning system:")
    if 'learning' in status:
        print(f"  - Patterns recognized: {status['learning']['patterns_recognized']}")
        print(f"  - Cached solutions: {status['learning']['cached_solutions']}")
        print(f"  - Efficiency gains: {status['learning']['efficiency_gains']:.1f} minutes")
    
    print(f"Architecture health:")
    if 'architecture' in status:
        print(f"  - Overall health: {status['architecture']['overall_health']:.1%}")
        print(f"  - Custom code ratio: {status['architecture']['custom_code_ratio']:.1%}")
        print(f"  - Using best practices: {status['architecture']['using_best_practices']}")
    
    print("\n" + "=" * 70)
    print("✨ OSA Enhanced Demo Complete!")
    print("The system will continue learning and improving autonomously.")
    print("=" * 70)


if __name__ == "__main__":
    # Run enhanced demo
    asyncio.run(demo_enhanced_osa())