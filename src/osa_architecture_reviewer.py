#!/usr/bin/env python3
"""
OSA Daily Architecture Self-Review System

This component enables OSA to:
1. Daily review its own architecture
2. Research latest tools and patterns
3. Compare with industry best practices
4. Self-improve and update
5. Always use best available tools (minimum custom coding)

Core Philosophy:
- Research first, build only if necessary
- Use the best tool for each job
- Continuously improve architecture
- Stay current with technology
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from packaging import version

# For web research
import aiohttp
from bs4 import BeautifulSoup
import feedparser


class ReviewCategory(Enum):
    """Categories for architecture review"""
    PATTERNS = "patterns"
    TOOLS = "tools"
    FRAMEWORKS = "frameworks"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    COST = "cost"


@dataclass
class ArchitectureComponent:
    """Represents a component in OSA's architecture"""
    name: str
    category: str
    current_version: str
    current_tool: str
    purpose: str
    last_reviewed: datetime
    performance_score: float
    alternatives: List[Dict] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    
    def needs_review(self) -> bool:
        """Check if component needs review"""
        days_since_review = (datetime.now() - self.last_reviewed).days
        return days_since_review > 7 or self.performance_score < 0.7


@dataclass
class ToolEvaluation:
    """Evaluation of a tool or technology"""
    name: str
    version: str
    category: str
    pros: List[str]
    cons: List[str]
    score: float
    github_stars: Optional[int] = None
    last_commit: Optional[datetime] = None
    community_size: Optional[str] = None
    documentation_quality: Optional[str] = None
    learning_curve: Optional[str] = None
    
    def is_better_than(self, other: 'ToolEvaluation') -> bool:
        """Compare with another tool"""
        return self.score > other.score * 1.1  # 10% better threshold


@dataclass
class ArchitectureReview:
    """Daily architecture review results"""
    id: str
    timestamp: datetime
    components_reviewed: List[str]
    improvements_found: List[Dict]
    tools_to_replace: Dict[str, str]
    patterns_to_adopt: List[str]
    estimated_improvement: float
    action_items: List[Dict]


class DailyArchitectureReviewer:
    """
    OSA's self-improvement system that:
    - Reviews architecture daily
    - Researches better tools
    - Implements improvements
    - Stays current with best practices
    """
    
    def __init__(self):
        # Architecture inventory
        self.components: Dict[str, ArchitectureComponent] = {}
        self.reviews: List[ArchitectureReview] = []
        
        # Research sources
        self.research_sources = {
            'github_trending': 'https://github.com/trending',
            'hackernews': 'https://news.ycombinator.com',
            'dev_to': 'https://dev.to',
            'product_hunt': 'https://www.producthunt.com/topics/developer-tools',
            'awesome_lists': 'https://github.com/sindresorhus/awesome',
            'tech_radar': 'https://www.thoughtworks.com/radar',
            'state_of_js': 'https://stateofjs.com',
            'npm_trends': 'https://npmtrends.com',
            'pypi_stats': 'https://pypistats.org'
        }
        
        # Best practices knowledge base
        self.best_practices = {
            'patterns': [
                'microservices',
                'event-driven',
                'serverless',
                'jamstack',
                'composable',
                'headless',
                'api-first',
                'cloud-native'
            ],
            'principles': [
                'DRY (Don\'t Repeat Yourself)',
                'SOLID principles',
                'KISS (Keep It Simple)',
                'YAGNI (You Aren\'t Gonna Need It)',
                'Minimum custom coding',
                'Use existing tools',
                'Composition over inheritance'
            ]
        }
        
        # Tool preferences (always prefer existing tools)
        self.tool_preferences = {
            'web_backend': {
                'current': 'FastAPI',
                'alternatives': ['Next.js API', 'Supabase', 'Hasura', 'Directus'],
                'criteria': ['performance', 'developer_experience', 'ecosystem']
            },
            'web_frontend': {
                'current': 'Next.js',
                'alternatives': ['Remix', 'SvelteKit', 'Astro', 'Nuxt'],
                'criteria': ['performance', 'seo', 'developer_experience']
            },
            'database': {
                'current': 'PostgreSQL + Supabase',
                'alternatives': ['PlanetScale', 'Neon', 'CockroachDB', 'EdgeDB'],
                'criteria': ['scalability', 'ease_of_use', 'cost']
            },
            'authentication': {
                'current': 'Supabase Auth',
                'alternatives': ['Clerk', 'Auth0', 'Firebase Auth', 'Lucia'],
                'criteria': ['security', 'ease_of_integration', 'features']
            },
            'deployment': {
                'current': 'Vercel',
                'alternatives': ['Railway', 'Fly.io', 'Render', 'Netlify'],
                'criteria': ['ease_of_use', 'performance', 'cost']
            },
            'ai_orchestration': {
                'current': 'LangChain',
                'alternatives': ['Haystack', 'LlamaIndex', 'Semantic Kernel', 'AutoGen'],
                'criteria': ['flexibility', 'ecosystem', 'performance']
            },
            'monitoring': {
                'current': 'Sentry',
                'alternatives': ['Datadog', 'New Relic', 'Grafana Cloud', 'Axiom'],
                'criteria': ['features', 'cost', 'ease_of_use']
            },
            'testing': {
                'current': 'Playwright',
                'alternatives': ['Cypress', 'TestCafe', 'Puppeteer', 'WebdriverIO'],
                'criteria': ['reliability', 'speed', 'developer_experience']
            }
        }
        
        # Review schedule
        self.review_schedule = {
            'daily': time(2, 0),  # 2 AM daily
            'enabled': True,
            'last_review': None
        }
        
        # Setup logging
        self.logger = logging.getLogger('OSA-ArchitectureReview')
        
        # Initialize components
        self._initialize_architecture()
    
    def _initialize_architecture(self):
        """Initialize current architecture components"""
        
        for category, config in self.tool_preferences.items():
            component = ArchitectureComponent(
                name=category,
                category=category,
                current_version='latest',
                current_tool=config['current'],
                purpose=category.replace('_', ' '),
                last_reviewed=datetime.now() - timedelta(days=8),  # Force initial review
                performance_score=0.8,
                alternatives=[{'name': alt} for alt in config['alternatives']]
            )
            self.components[category] = component
    
    async def perform_daily_review(self) -> ArchitectureReview:
        """
        Perform comprehensive daily architecture review.
        
        This is OSA's self-improvement routine.
        """
        
        self.logger.info("🔍 Starting daily architecture review...")
        
        review = ArchitectureReview(
            id=hashlib.md5(f"review_{datetime.now()}".encode()).hexdigest()[:8],
            timestamp=datetime.now(),
            components_reviewed=[],
            improvements_found=[],
            tools_to_replace={},
            patterns_to_adopt=[],
            estimated_improvement=0,
            action_items=[]
        )
        
        # Phase 1: Review each component
        for component_name, component in self.components.items():
            if component.needs_review():
                self.logger.info(f"  Reviewing: {component_name}")
                
                improvement = await self._review_component(component)
                if improvement:
                    review.improvements_found.append(improvement)
                    review.components_reviewed.append(component_name)
                    
                    if improvement.get('replacement'):
                        review.tools_to_replace[component_name] = improvement['replacement']
        
        # Phase 2: Research new patterns and tools
        new_discoveries = await self._research_new_tools()
        for discovery in new_discoveries:
            if self._should_adopt(discovery):
                review.patterns_to_adopt.append(discovery['name'])
                review.action_items.append({
                    'action': 'evaluate',
                    'target': discovery['name'],
                    'reason': discovery.get('reason', 'Promising new technology')
                })
        
        # Phase 3: Check industry best practices
        best_practices_check = await self._check_best_practices()
        for practice in best_practices_check:
            if not practice['implemented']:
                review.action_items.append({
                    'action': 'implement',
                    'target': practice['name'],
                    'priority': practice.get('priority', 'medium')
                })
        
        # Phase 4: Performance analysis
        performance_analysis = self._analyze_performance()
        if performance_analysis['issues']:
            for issue in performance_analysis['issues']:
                review.action_items.append({
                    'action': 'optimize',
                    'target': issue['component'],
                    'metric': issue['metric'],
                    'current': issue['current'],
                    'target_value': issue['target']
                })
        
        # Calculate estimated improvement
        review.estimated_improvement = self._calculate_improvement_potential(review)
        
        # Store review
        self.reviews.append(review)
        self.review_schedule['last_review'] = datetime.now()
        
        # Generate summary
        self.logger.info(f"✅ Review complete:")
        self.logger.info(f"   Components reviewed: {len(review.components_reviewed)}")
        self.logger.info(f"   Improvements found: {len(review.improvements_found)}")
        self.logger.info(f"   Tools to replace: {len(review.tools_to_replace)}")
        self.logger.info(f"   Estimated improvement: {review.estimated_improvement:.1f}%")
        
        return review
    
    async def _review_component(self, component: ArchitectureComponent) -> Optional[Dict]:
        """Review a single architecture component"""
        
        improvement = {
            'component': component.name,
            'current_tool': component.current_tool,
            'issues': [],
            'alternatives_evaluated': []
        }
        
        # Evaluate current tool
        current_eval = await self._evaluate_tool(
            component.current_tool,
            component.category
        )
        
        # Research alternatives
        for alt in component.alternatives:
            alt_eval = await self._evaluate_tool(
                alt['name'],
                component.category
            )
            
            improvement['alternatives_evaluated'].append({
                'name': alt['name'],
                'score': alt_eval.score,
                'better': alt_eval.is_better_than(current_eval)
            })
            
            # If significantly better, recommend replacement
            if alt_eval.is_better_than(current_eval):
                improvement['replacement'] = alt['name']
                improvement['improvement_score'] = alt_eval.score - current_eval.score
                improvement['reasons'] = alt_eval.pros[:3]
        
        # Update component
        component.last_reviewed = datetime.now()
        component.performance_score = current_eval.score
        
        return improvement if improvement.get('replacement') or improvement['issues'] else None
    
    async def _evaluate_tool(self, tool_name: str, category: str) -> ToolEvaluation:
        """Evaluate a tool comprehensively"""
        
        evaluation = ToolEvaluation(
            name=tool_name,
            version='latest',
            category=category,
            pros=[],
            cons=[],
            score=0.5  # Base score
        )
        
        # Fetch tool information (would use real APIs in production)
        tool_info = await self._fetch_tool_info(tool_name)
        
        # Evaluate based on multiple criteria
        
        # 1. Popularity and community
        if tool_info.get('github_stars', 0) > 10000:
            evaluation.pros.append('Large community')
            evaluation.score += 0.15
        elif tool_info.get('github_stars', 0) > 1000:
            evaluation.pros.append('Active community')
            evaluation.score += 0.1
        
        # 2. Maintenance
        last_commit = tool_info.get('last_commit')
        if last_commit:
            days_since = (datetime.now() - last_commit).days
            if days_since < 7:
                evaluation.pros.append('Actively maintained')
                evaluation.score += 0.15
            elif days_since < 30:
                evaluation.pros.append('Recently updated')
                evaluation.score += 0.1
            elif days_since > 180:
                evaluation.cons.append('Not actively maintained')
                evaluation.score -= 0.1
        
        # 3. Documentation
        if tool_info.get('documentation_quality') == 'excellent':
            evaluation.pros.append('Excellent documentation')
            evaluation.score += 0.1
        elif tool_info.get('documentation_quality') == 'poor':
            evaluation.cons.append('Poor documentation')
            evaluation.score -= 0.1
        
        # 4. Performance (category-specific)
        if category in ['web_backend', 'database']:
            if 'fast' in tool_name.lower() or 'performance' in str(tool_info):
                evaluation.pros.append('High performance')
                evaluation.score += 0.15
        
        # 5. Ease of use (important for minimum custom coding principle)
        if tool_info.get('learning_curve') == 'easy':
            evaluation.pros.append('Easy to learn')
            evaluation.score += 0.15
        elif tool_info.get('learning_curve') == 'steep':
            evaluation.cons.append('Steep learning curve')
            evaluation.score -= 0.1
        
        # 6. Existing solution vs custom (core principle)
        if 'framework' in tool_name.lower() or 'platform' in tool_name.lower():
            evaluation.pros.append('Complete solution (minimal custom code)')
            evaluation.score += 0.2
        
        # 7. Integration capabilities
        if tool_info.get('integrations', 0) > 10:
            evaluation.pros.append('Many integrations')
            evaluation.score += 0.1
        
        # Cap score at 1.0
        evaluation.score = min(evaluation.score, 1.0)
        
        return evaluation
    
    async def _fetch_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Fetch information about a tool"""
        
        # In production, this would:
        # 1. Check GitHub API for stars, commits, etc.
        # 2. Check npm/PyPI for download stats
        # 3. Scrape documentation sites
        # 4. Check Stack Overflow for questions/answers
        
        # For now, return mock data based on known tools
        known_tools = {
            'FastAPI': {
                'github_stars': 65000,
                'last_commit': datetime.now() - timedelta(days=1),
                'documentation_quality': 'excellent',
                'learning_curve': 'moderate',
                'integrations': 50
            },
            'Next.js': {
                'github_stars': 115000,
                'last_commit': datetime.now() - timedelta(hours=6),
                'documentation_quality': 'excellent',
                'learning_curve': 'moderate',
                'integrations': 100
            },
            'Supabase': {
                'github_stars': 60000,
                'last_commit': datetime.now() - timedelta(hours=12),
                'documentation_quality': 'good',
                'learning_curve': 'easy',
                'integrations': 30
            },
            'Vercel': {
                'github_stars': 12000,
                'last_commit': datetime.now() - timedelta(days=2),
                'documentation_quality': 'excellent',
                'learning_curve': 'easy',
                'integrations': 50
            },
            'Railway': {
                'github_stars': 3000,
                'last_commit': datetime.now() - timedelta(days=3),
                'documentation_quality': 'good',
                'learning_curve': 'easy',
                'integrations': 25
            },
            'Clerk': {
                'github_stars': 5000,
                'last_commit': datetime.now() - timedelta(days=1),
                'documentation_quality': 'excellent',
                'learning_curve': 'easy',
                'integrations': 20
            }
        }
        
        # Return known data or defaults
        return known_tools.get(tool_name, {
            'github_stars': 1000,
            'last_commit': datetime.now() - timedelta(days=30),
            'documentation_quality': 'unknown',
            'learning_curve': 'moderate',
            'integrations': 5
        })
    
    async def _research_new_tools(self) -> List[Dict[str, Any]]:
        """Research new tools and technologies"""
        
        discoveries = []
        
        # Would actually scrape these sources in production
        # For now, simulate discoveries
        
        trending_tools = [
            {'name': 'Bun', 'category': 'runtime', 'reason': 'Faster than Node.js'},
            {'name': 'Astro', 'category': 'web_frontend', 'reason': 'Better performance'},
            {'name': 'Drizzle ORM', 'category': 'database', 'reason': 'Type-safe SQL'},
            {'name': 'tRPC', 'category': 'api', 'reason': 'End-to-end typesafety'},
            {'name': 'Zod', 'category': 'validation', 'reason': 'Runtime type checking'}
        ]
        
        for tool in trending_tools:
            # Check if we should investigate further
            if tool['category'] in self.tool_preferences:
                discoveries.append(tool)
        
        self.logger.info(f"🔬 Discovered {len(discoveries)} new tools to evaluate")
        
        return discoveries
    
    def _should_adopt(self, discovery: Dict[str, Any]) -> bool:
        """Determine if a new tool should be adopted"""
        
        # Criteria for adoption
        criteria = {
            'matches_need': discovery.get('category') in self.tool_preferences,
            'mature_enough': True,  # Would check actual metrics
            'better_than_current': discovery.get('reason', '').lower().count('better') > 0,
            'minimal_custom_code': 'framework' in discovery.get('name', '').lower()
        }
        
        # Need at least 3 criteria met
        return sum(criteria.values()) >= 3
    
    async def _check_best_practices(self) -> List[Dict[str, Any]]:
        """Check implementation of best practices"""
        
        practices_check = []
        
        for principle in self.best_practices['principles']:
            # Check if principle is being followed
            implemented = self._is_principle_implemented(principle)
            
            practices_check.append({
                'name': principle,
                'implemented': implemented,
                'priority': 'high' if 'custom coding' in principle else 'medium'
            })
        
        for pattern in self.best_practices['patterns']:
            # Check if pattern is applicable and implemented
            applicable = self._is_pattern_applicable(pattern)
            if applicable:
                implemented = self._is_pattern_implemented(pattern)
                practices_check.append({
                    'name': pattern,
                    'implemented': implemented,
                    'priority': 'medium'
                })
        
        return practices_check
    
    def _is_principle_implemented(self, principle: str) -> bool:
        """Check if a principle is implemented"""
        
        # Simple checks for now
        if 'custom coding' in principle.lower():
            # Check if we're using mostly existing tools
            custom_ratio = self._calculate_custom_code_ratio()
            return custom_ratio < 0.2  # Less than 20% custom code
        
        # Default to True for other principles
        return True
    
    def _calculate_custom_code_ratio(self) -> float:
        """Calculate ratio of custom code vs using tools"""
        
        # Count components using existing tools vs custom
        using_tools = 0
        custom = 0
        
        for component in self.components.values():
            if component.current_tool in ['custom', 'built-in-house', 'proprietary']:
                custom += 1
            else:
                using_tools += 1
        
        total = using_tools + custom
        return custom / total if total > 0 else 0
    
    def _is_pattern_applicable(self, pattern: str) -> bool:
        """Check if a pattern is applicable to current architecture"""
        
        # Pattern applicability rules
        applicability = {
            'microservices': len(self.components) > 5,
            'serverless': 'deployment' in self.components,
            'event-driven': 'messaging' in self.components or 'queue' in self.components,
            'api-first': 'api' in [c.category for c in self.components.values()],
            'cloud-native': True,  # Always applicable
            'jamstack': 'web_frontend' in self.components,
            'composable': True,  # Always good
            'headless': 'cms' in self.components or 'content' in self.components
        }
        
        return applicability.get(pattern, False)
    
    def _is_pattern_implemented(self, pattern: str) -> bool:
        """Check if a pattern is implemented"""
        
        # Simple checks for pattern implementation
        if pattern == 'microservices':
            return len(self.components) > 5 and 'api' in self.components
        elif pattern == 'serverless':
            return any('vercel' in c.current_tool.lower() or 'lambda' in c.current_tool.lower() 
                      for c in self.components.values())
        elif pattern == 'cloud-native':
            return any('cloud' in c.current_tool.lower() or 'vercel' in c.current_tool.lower() 
                      for c in self.components.values())
        
        return False
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance of current architecture"""
        
        analysis = {
            'overall_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Check each component's performance
        total_score = 0
        for component in self.components.values():
            total_score += component.performance_score
            
            if component.performance_score < 0.7:
                analysis['issues'].append({
                    'component': component.name,
                    'metric': 'performance_score',
                    'current': component.performance_score,
                    'target': 0.8
                })
        
        # Calculate overall score
        if self.components:
            analysis['overall_score'] = total_score / len(self.components)
        
        # Generate recommendations
        if analysis['overall_score'] < 0.8:
            analysis['recommendations'].append('Consider upgrading underperforming components')
        
        if len(analysis['issues']) > 3:
            analysis['recommendations'].append('Multiple components need attention')
        
        return analysis
    
    def _calculate_improvement_potential(self, review: ArchitectureReview) -> float:
        """Calculate potential improvement from review findings"""
        
        improvement = 0
        
        # Each tool replacement adds improvement
        improvement += len(review.tools_to_replace) * 10
        
        # Each new pattern adds improvement
        improvement += len(review.patterns_to_adopt) * 5
        
        # Each action item adds small improvement
        improvement += len(review.action_items) * 2
        
        # Cap at 100%
        return min(improvement, 100)
    
    async def implement_improvements(self, review: ArchitectureReview) -> Dict[str, Any]:
        """
        Implement the improvements found in review.
        
        This is where OSA actually updates itself.
        """
        
        self.logger.info("🔧 Implementing architecture improvements...")
        
        implementation_results = {
            'tools_replaced': [],
            'patterns_adopted': [],
            'actions_completed': [],
            'success_rate': 0
        }
        
        # Replace tools
        for component_name, new_tool in review.tools_to_replace.items():
            try:
                self.logger.info(f"  Replacing {component_name} with {new_tool}")
                
                # Update component
                if component_name in self.components:
                    old_tool = self.components[component_name].current_tool
                    self.components[component_name].current_tool = new_tool
                    
                    # Update tool preferences
                    if component_name in self.tool_preferences:
                        self.tool_preferences[component_name]['current'] = new_tool
                    
                    implementation_results['tools_replaced'].append({
                        'component': component_name,
                        'old': old_tool,
                        'new': new_tool
                    })
                    
            except Exception as e:
                self.logger.error(f"  Failed to replace {component_name}: {e}")
        
        # Adopt patterns
        for pattern in review.patterns_to_adopt:
            try:
                self.logger.info(f"  Adopting pattern: {pattern}")
                
                # Add to best practices
                if pattern not in self.best_practices['patterns']:
                    self.best_practices['patterns'].append(pattern)
                
                implementation_results['patterns_adopted'].append(pattern)
                
            except Exception as e:
                self.logger.error(f"  Failed to adopt {pattern}: {e}")
        
        # Execute action items
        for action in review.action_items[:5]:  # Limit to 5 per review
            try:
                self.logger.info(f"  Executing: {action['action']} on {action['target']}")
                
                # Simulate action execution
                implementation_results['actions_completed'].append(action)
                
            except Exception as e:
                self.logger.error(f"  Failed action: {e}")
        
        # Calculate success rate
        total_items = (len(review.tools_to_replace) + 
                      len(review.patterns_to_adopt) + 
                      len(review.action_items[:5]))
        
        completed_items = (len(implementation_results['tools_replaced']) +
                          len(implementation_results['patterns_adopted']) +
                          len(implementation_results['actions_completed']))
        
        if total_items > 0:
            implementation_results['success_rate'] = completed_items / total_items
        
        self.logger.info(f"✅ Implementation complete: {implementation_results['success_rate']:.1%} success rate")
        
        return implementation_results
    
    def get_architecture_status(self) -> Dict[str, Any]:
        """Get current architecture status"""
        
        status = {
            'components': {},
            'overall_health': 0,
            'last_review': self.review_schedule['last_review'].isoformat() if self.review_schedule['last_review'] else None,
            'custom_code_ratio': self._calculate_custom_code_ratio(),
            'using_best_practices': True,
            'recommendations': []
        }
        
        # Component status
        total_score = 0
        for name, component in self.components.items():
            status['components'][name] = {
                'tool': component.current_tool,
                'score': component.performance_score,
                'needs_review': component.needs_review()
            }
            total_score += component.performance_score
        
        # Overall health
        if self.components:
            status['overall_health'] = total_score / len(self.components)
        
        # Check best practices
        if status['custom_code_ratio'] > 0.3:
            status['using_best_practices'] = False
            status['recommendations'].append('Reduce custom code by using more existing tools')
        
        if status['overall_health'] < 0.8:
            status['recommendations'].append('Several components need improvement')
        
        # Add recent review findings
        if self.reviews:
            recent_review = self.reviews[-1]
            if recent_review.tools_to_replace:
                status['recommendations'].append(f"Consider replacing: {list(recent_review.tools_to_replace.keys())}")
        
        return status
    
    async def research_specific_need(self, need: str) -> Dict[str, Any]:
        """
        Research tools for a specific need.
        
        This implements the principle: always find existing tools first.
        """
        
        self.logger.info(f"🔍 Researching tools for: {need}")
        
        research_result = {
            'need': need,
            'recommended_tools': [],
            'build_vs_buy': 'buy',  # Default to using existing tools
            'reasoning': []
        }
        
        # Search for existing tools
        existing_tools = await self._search_existing_tools(need)
        
        if existing_tools:
            # Evaluate each tool
            for tool in existing_tools[:5]:  # Top 5
                evaluation = await self._evaluate_tool(tool['name'], need)
                
                if evaluation.score > 0.7:
                    research_result['recommended_tools'].append({
                        'name': tool['name'],
                        'score': evaluation.score,
                        'pros': evaluation.pros[:3],
                        'url': tool.get('url', '')
                    })
            
            if research_result['recommended_tools']:
                research_result['reasoning'].append('Found excellent existing tools')
                research_result['reasoning'].append('No need for custom development')
                best_tool = max(research_result['recommended_tools'], key=lambda x: x['score'])
                research_result['recommendation'] = f"Use {best_tool['name']}"
            else:
                # No good tools found, might need custom
                research_result['build_vs_buy'] = 'build_minimal'
                research_result['reasoning'].append('No perfect fit found')
                research_result['reasoning'].append('Recommend minimal custom wrapper around closest tool')
                research_result['recommendation'] = 'Build minimal custom solution on top of existing tools'
        else:
            # Very rare case - no tools at all
            research_result['build_vs_buy'] = 'build_minimal'
            research_result['reasoning'].append('Unique requirement')
            research_result['reasoning'].append('Build minimal solution using existing libraries')
        
        return research_result
    
    async def _search_existing_tools(self, need: str) -> List[Dict[str, Any]]:
        """Search for existing tools that meet the need"""
        
        # In production, this would search:
        # - GitHub
        # - npm/PyPI
        # - Product Hunt
        # - Google
        
        # For now, use knowledge base
        tool_database = {
            'authentication': [
                {'name': 'Clerk', 'url': 'https://clerk.dev'},
                {'name': 'Auth0', 'url': 'https://auth0.com'},
                {'name': 'Supabase Auth', 'url': 'https://supabase.com'},
                {'name': 'Firebase Auth', 'url': 'https://firebase.google.com'},
                {'name': 'Lucia', 'url': 'https://lucia-auth.com'}
            ],
            'database': [
                {'name': 'Supabase', 'url': 'https://supabase.com'},
                {'name': 'PlanetScale', 'url': 'https://planetscale.com'},
                {'name': 'Neon', 'url': 'https://neon.tech'},
                {'name': 'Railway', 'url': 'https://railway.app'},
                {'name': 'Turso', 'url': 'https://turso.tech'}
            ],
            'deployment': [
                {'name': 'Vercel', 'url': 'https://vercel.com'},
                {'name': 'Netlify', 'url': 'https://netlify.com'},
                {'name': 'Railway', 'url': 'https://railway.app'},
                {'name': 'Fly.io', 'url': 'https://fly.io'},
                {'name': 'Render', 'url': 'https://render.com'}
            ],
            'payment': [
                {'name': 'Stripe', 'url': 'https://stripe.com'},
                {'name': 'Lemonsqueezy', 'url': 'https://lemonsqueezy.com'},
                {'name': 'Paddle', 'url': 'https://paddle.com'},
                {'name': 'PayPal', 'url': 'https://paypal.com'}
            ],
            'email': [
                {'name': 'Resend', 'url': 'https://resend.com'},
                {'name': 'SendGrid', 'url': 'https://sendgrid.com'},
                {'name': 'Postmark', 'url': 'https://postmarkapp.com'},
                {'name': 'AWS SES', 'url': 'https://aws.amazon.com/ses'}
            ]
        }
        
        # Find matching category
        need_lower = need.lower()
        for category, tools in tool_database.items():
            if category in need_lower or any(word in need_lower for word in category.split('_')):
                return tools
        
        # Search by keywords
        keywords = need_lower.split()
        matching_tools = []
        
        for category, tools in tool_database.items():
            for tool in tools:
                if any(keyword in tool['name'].lower() for keyword in keywords):
                    matching_tools.append(tool)
        
        return matching_tools


# Integration function for OSA
async def enhance_osa_with_architecture_review(osa_instance):
    """Enhance OSA with daily architecture review"""
    
    reviewer = DailyArchitectureReviewer()
    
    # Add reviewer to OSA
    osa_instance.architecture_reviewer = reviewer
    
    # Schedule daily review
    async def daily_review_task():
        while True:
            # Wait until review time (2 AM)
            now = datetime.now()
            review_time = datetime.combine(now.date(), reviewer.review_schedule['daily'])
            
            if now > review_time:
                # Next day
                review_time += timedelta(days=1)
            
            wait_seconds = (review_time - now).total_seconds()
            
            # Wait until review time
            await asyncio.sleep(wait_seconds)
            
            # Perform review
            review = await reviewer.perform_daily_review()
            
            # Implement improvements
            await reviewer.implement_improvements(review)
            
            # Log results
            logging.info(f"Daily architecture review completed: {review.estimated_improvement:.1f}% improvement potential")
    
    # Start daily review task
    asyncio.create_task(daily_review_task())
    
    # Override OSA accomplish method to use best tools
    original_accomplish = osa_instance.accomplish
    
    async def enhanced_accomplish(goal: str) -> Dict[str, Any]:
        # First, research if we need any new tools
        needs = extract_needs_from_goal(goal)
        
        for need in needs:
            research = await reviewer.research_specific_need(need)
            
            if research['recommended_tools']:
                logging.info(f"📚 Found tools for {need}: {research['recommendation']}")
        
        # Execute with best tools
        return await original_accomplish(goal)
    
    osa_instance.accomplish = enhanced_accomplish
    
    return osa_instance


def extract_needs_from_goal(goal: str) -> List[str]:
    """Extract needs from goal description"""
    
    needs = []
    goal_lower = goal.lower()
    
    # Common needs
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