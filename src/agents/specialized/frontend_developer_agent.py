"""
Frontend Developer Agent - OmniMind Powered

Specializes in React, Vue, UI/UX, and frontend best practices.
Remembers all design decisions, component patterns, and user feedback.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, Optional, List
from src.agents.base_omnimind_agent import BaseOmniMindAgent


class FrontendDeveloperAgent(BaseOmniMindAgent):
    """
    Frontend development specialist with perfect memory.
    
    Capabilities:
    - React/Vue/Angular expertise
    - Component architecture decisions
    - UI/UX best practices
    - Performance optimization
    - Accessibility standards
    - Design system management
    """
    
    def __init__(self):
        super().__init__(
            agent_name="frontend-developer",
            specialization="React, Vue, UI/UX, responsive design, and frontend performance"
        )
        
        # Frontend-specific context
        self.framework_preferences = {}
        self.design_system = {}
        self.component_patterns = []
    
    def _get_preferred_models(self) -> Dict[str, str]:
        """Frontend-optimized model selection."""
        return {
            'code': 'deepseek-coder:6.7b',  # For component code
            'reasoning': 'mistral:7b',       # For architecture decisions
            'quick': 'gemma2:2b',           # For quick CSS/HTML
            'general': 'llama3.2:3b',       # For general frontend tasks
            'design': 'mistral:7b'          # For design decisions
        }
    
    def get_specialization_prompt(self) -> str:
        """Frontend-specific expertise prompt."""
        return """
I am a Frontend Developer Agent specializing in modern web development.

My expertise includes:
- React, Vue.js, Angular, and Next.js
- Component architecture and design systems
- CSS-in-JS, Tailwind, and responsive design
- State management (Redux, Zustand, Pinia)
- Performance optimization and code splitting
- Accessibility (WCAG) and SEO
- Testing (Jest, React Testing Library, Cypress)
- Build tools (Webpack, Vite, Rollup)

I remember all past UI decisions, component patterns, and user feedback to provide consistent, high-quality frontend solutions.
"""
    
    def create_component(self, name: str, description: str, 
                        framework: str = "react") -> str:
        """
        Create a new component with best practices.
        
        Args:
            name: Component name
            description: What the component does
            framework: react/vue/angular
        
        Returns:
            Component code with explanation
        """
        # Search for similar components
        similar = self.search_knowledge(f"component {name} {description}")
        
        context = ""
        if similar:
            context = f"\nConsider these similar components:\n"
            context += "\n".join([m['content'][:100] for m in similar[:3]])
        
        prompt = f"""
Create a {framework} component named {name}.
Description: {description}
{context}

Requirements:
1. Follow our established component patterns
2. Include TypeScript types
3. Make it accessible (ARIA)
4. Add proper error handling
5. Include basic tests
6. Follow our naming conventions

Generate the component with explanation.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this component pattern
        self.remember_decision(
            f"Created {name} component",
            f"Framework: {framework}, Purpose: {description}",
            tags=['component', framework, 'frontend']
        )
        
        return response
    
    def optimize_performance(self, code: str, metrics: Optional[Dict] = None) -> str:
        """
        Optimize frontend code for performance.
        
        Args:
            code: Code to optimize
            metrics: Current performance metrics
        
        Returns:
            Optimized code with explanation
        """
        prompt = f"""
Optimize this frontend code for performance:

```
{code[:1000]}  # Truncated for context
```

Current metrics: {metrics if metrics else 'Not provided'}

Focus on:
1. Bundle size reduction
2. Render performance
3. Code splitting opportunities
4. Lazy loading
5. Memoization needs
6. Virtual DOM optimization

Provide optimized code with explanations.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Learn from this optimization
        self.learn_from_feedback(
            "Performance optimization",
            "Applied optimization techniques",
            "Techniques used for future reference"
        )
        
        return response
    
    def design_system_decision(self, component_type: str, 
                               requirements: str) -> str:
        """
        Make design system decisions with consistency.
        
        Args:
            component_type: Type of component
            requirements: Design requirements
        
        Returns:
            Design decision with rationale
        """
        # Search for related design decisions
        past_decisions = self.search_knowledge(f"design system {component_type}")
        
        prompt = f"""
Design system decision needed for {component_type}.
Requirements: {requirements}

Past related decisions:
{chr(10).join([m['content'][:150] for m in past_decisions[:3]]) if past_decisions else 'None'}

Provide recommendation that:
1. Maintains consistency with existing design system
2. Follows accessibility standards
3. Supports theming and customization
4. Is performant and maintainable

Decision and rationale:
"""
        
        return self.think(prompt, use_specialization=True)
    
    def review_ui_code(self, code: str, focus_areas: Optional[List[str]] = None) -> str:
        """
        Review frontend code with specialized knowledge.
        
        Args:
            code: Code to review
            focus_areas: Specific areas to focus on
        
        Returns:
            Detailed review with suggestions
        """
        if not focus_areas:
            focus_areas = ['performance', 'accessibility', 'best practices']
        
        prompt = f"""
Review this frontend code:

```
{code[:2000]}  # Truncated
```

Focus areas: {', '.join(focus_areas)}

Check for:
1. React/Vue best practices
2. Performance issues (re-renders, bundle size)
3. Accessibility violations
4. Security concerns (XSS, injection)
5. Code maintainability
6. Testing coverage needs

Provide detailed review with specific improvements.
"""
        
        return self.think(prompt, use_specialization=True)
    
    def suggest_state_management(self, app_complexity: str, 
                                 requirements: str) -> str:
        """
        Suggest appropriate state management solution.
        
        Args:
            app_complexity: simple/medium/complex
            requirements: Specific requirements
        
        Returns:
            State management recommendation
        """
        # Check past state management decisions
        past_decisions = self.search_knowledge("state management decision")
        
        prompt = f"""
Recommend state management for {app_complexity} application.
Requirements: {requirements}

Consider:
- Redux vs Zustand vs Context API vs Pinia
- Server state (React Query, SWR)
- Local vs global state needs
- Performance implications
- Developer experience
- Our past decisions and their outcomes

Recommendation with implementation example:
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this decision
        self.remember_decision(
            f"State management for {app_complexity} app",
            response[:200],
            tags=['state-management', 'architecture']
        )
        
        return response


# Agent registration for Claude Code
AGENT = FrontendDeveloperAgent

def create_agent():
    """Factory function for Claude Code."""
    return FrontendDeveloperAgent()