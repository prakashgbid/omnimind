"""
Backend Architect Agent - OmniMind Powered

Specializes in API design, databases, microservices, and scalable architectures.
Remembers all architectural decisions, patterns, and performance optimizations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, List, Optional
from src.agents.base_omnimind_agent import BaseOmniMindAgent


class BackendArchitectAgent(BaseOmniMindAgent):
    """
    Backend architecture specialist with perfect memory.
    
    Capabilities:
    - API design (REST, GraphQL, gRPC)
    - Database design and optimization
    - Microservices architecture
    - Message queues and event-driven systems
    - Security and authentication
    - Performance and scaling
    """
    
    def __init__(self):
        super().__init__(
            agent_name="backend-architect",
            specialization="APIs, databases, microservices, cloud architecture, and system design"
        )
        
        # Backend-specific context
        self.architecture_patterns = []
        self.api_standards = {}
        self.database_schemas = {}
    
    def _get_preferred_models(self) -> Dict[str, str]:
        """Backend-optimized model selection."""
        return {
            'code': 'deepseek-coder:6.7b',  # For implementation
            'reasoning': 'mistral:7b',       # For architecture decisions
            'quick': 'llama3.2:3b',         # For quick responses
            'general': 'mistral:7b',        # For system design
            'database': 'mistral:7b'        # For data modeling
        }
    
    def get_specialization_prompt(self) -> str:
        """Backend-specific expertise prompt."""
        return """
I am a Backend Architect Agent specializing in scalable system design.

My expertise includes:
- RESTful APIs, GraphQL, gRPC, and WebSockets
- Database design (PostgreSQL, MongoDB, Redis, Elasticsearch)
- Microservices and service mesh architectures
- Message queues (RabbitMQ, Kafka, Redis Pub/Sub)
- Cloud platforms (AWS, GCP, Azure)
- Authentication and authorization (OAuth2, JWT, RBAC)
- Caching strategies and performance optimization
- CI/CD pipelines and DevOps practices
- Security best practices and compliance

I remember all past architectural decisions, scaling solutions, and performance optimizations to provide consistent, robust backend solutions.
"""
    
    def design_api(self, resource: str, operations: List[str], 
                   requirements: Optional[str] = None) -> str:
        """
        Design a RESTful or GraphQL API.
        
        Args:
            resource: The resource to design API for
            operations: CRUD operations needed
            requirements: Additional requirements
        
        Returns:
            API design with endpoints and schemas
        """
        # Search for similar API designs
        similar_apis = self.search_knowledge(f"API design {resource}")
        
        context = ""
        if similar_apis:
            context = "\nRelated API designs from memory:\n"
            context += "\n".join([m['content'][:150] for m in similar_apis[:3]])
        
        prompt = f"""
Design API for resource: {resource}
Operations needed: {', '.join(operations)}
Requirements: {requirements if requirements else 'Standard RESTful practices'}
{context}

Provide:
1. Endpoint definitions with HTTP methods
2. Request/response schemas
3. Error handling approach
4. Authentication requirements
5. Rate limiting strategy
6. Versioning approach
7. Example implementations

Follow our established API patterns and OpenAPI spec.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this API design
        self.remember_decision(
            f"Designed API for {resource}",
            f"Operations: {operations}, Requirements: {requirements}",
            tags=['api', 'architecture', resource]
        )
        
        return response
    
    def optimize_database(self, schema: str, query_patterns: str, 
                         issues: Optional[str] = None) -> str:
        """
        Optimize database schema and queries.
        
        Args:
            schema: Current database schema
            query_patterns: Common query patterns
            issues: Current performance issues
        
        Returns:
            Optimization recommendations
        """
        # Search for similar optimization cases
        past_optimizations = self.search_knowledge("database optimization")
        
        prompt = f"""
Optimize this database design:

Schema:
```sql
{schema[:1500]}  # Truncated
```

Query patterns: {query_patterns}
Current issues: {issues if issues else 'General optimization needed'}

Past successful optimizations:
{chr(10).join([m['content'][:100] for m in past_optimizations[:3]]) if past_optimizations else 'None'}

Provide:
1. Index recommendations
2. Schema denormalization opportunities
3. Partitioning strategies
4. Query optimization suggestions
5. Caching layer recommendations
6. Migration plan if needed

Focus on scalability and performance.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Learn from this optimization
        self.learn_from_feedback(
            f"Database optimization for {query_patterns[:50]}",
            "Optimization strategies applied",
            "Techniques for future reference"
        )
        
        return response
    
    def design_microservice(self, service_name: str, responsibilities: str,
                           interactions: Optional[str] = None) -> str:
        """
        Design a microservice with proper boundaries.
        
        Args:
            service_name: Name of the service
            responsibilities: What the service handles
            interactions: How it interacts with other services
        
        Returns:
            Microservice design with implementation details
        """
        # Check for existing service patterns
        existing_patterns = self.search_knowledge("microservice design pattern")
        
        prompt = f"""
Design microservice: {service_name}
Responsibilities: {responsibilities}
Interactions: {interactions if interactions else 'Standalone service'}

Consider:
1. Service boundaries and data ownership
2. API contract (REST/gRPC/Events)
3. Data consistency strategy
4. Service discovery and communication
5. Resilience patterns (circuit breaker, retry, timeout)
6. Monitoring and observability
7. Deployment and scaling strategy

Past successful patterns:
{chr(10).join([m['content'][:100] for m in existing_patterns[:3]]) if existing_patterns else 'None'}

Provide complete microservice design.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this architecture
        self.remember_decision(
            f"Designed {service_name} microservice",
            f"Responsibilities: {responsibilities}",
            tags=['microservice', 'architecture', service_name]
        )
        
        return response
    
    def implement_auth_system(self, requirements: str, 
                              user_types: Optional[List[str]] = None) -> str:
        """
        Design and implement authentication/authorization system.
        
        Args:
            requirements: Security requirements
            user_types: Different types of users
        
        Returns:
            Complete auth system design
        """
        # Search for past auth implementations
        past_auth = self.search_knowledge("authentication authorization implementation")
        
        prompt = f"""
Design authentication and authorization system.
Requirements: {requirements}
User types: {', '.join(user_types) if user_types else 'Standard users'}

Implement:
1. Authentication method (JWT, OAuth2, SAML)
2. Session management strategy
3. Role-based access control (RBAC)
4. Token refresh mechanism
5. Security headers and CORS
6. Rate limiting and brute force protection
7. Audit logging
8. Password policies and MFA

Include code examples and security best practices.
"""
        
        return self.think(prompt, use_specialization=True, use_consensus=True)
    
    def scaling_strategy(self, current_load: str, expected_growth: str,
                        constraints: Optional[str] = None) -> str:
        """
        Develop scaling strategy for the system.
        
        Args:
            current_load: Current system load
            expected_growth: Expected growth pattern
            constraints: Budget or technical constraints
        
        Returns:
            Comprehensive scaling strategy
        """
        # Get past scaling decisions
        past_scaling = self.search_knowledge("scaling strategy performance")
        
        prompt = f"""
Develop scaling strategy:
Current load: {current_load}
Expected growth: {expected_growth}
Constraints: {constraints if constraints else 'None'}

Address:
1. Horizontal vs vertical scaling decisions
2. Database scaling (read replicas, sharding)
3. Caching strategy (Redis, CDN)
4. Load balancing approach
5. Auto-scaling policies
6. Message queue for async processing
7. Cost optimization
8. Monitoring and alerting

Past successful strategies:
{chr(10).join([m['content'][:150] for m in past_scaling[:3]]) if past_scaling else 'None'}

Provide detailed implementation plan.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this scaling decision
        self.remember_decision(
            f"Scaling strategy for {expected_growth}",
            response[:300],
            tags=['scaling', 'performance', 'architecture']
        )
        
        return response
    
    def review_architecture(self, architecture_doc: str, 
                           focus_areas: Optional[List[str]] = None) -> str:
        """
        Review system architecture with expert knowledge.
        
        Args:
            architecture_doc: Architecture documentation
            focus_areas: Specific areas to focus on
        
        Returns:
            Detailed architecture review
        """
        if not focus_areas:
            focus_areas = ['scalability', 'security', 'maintainability', 'performance']
        
        prompt = f"""
Review this system architecture:

```
{architecture_doc[:2000]}  # Truncated
```

Focus areas: {', '.join(focus_areas)}

Evaluate:
1. Scalability bottlenecks
2. Security vulnerabilities
3. Single points of failure
4. Data consistency issues
5. Performance concerns
6. Complexity and maintainability
7. Cost optimization opportunities
8. Monitoring gaps

Provide specific recommendations based on best practices and past experiences.
"""
        
        return self.think(prompt, use_specialization=True, use_consensus=True)


# Agent registration for Claude Code
AGENT = BackendArchitectAgent

def create_agent():
    """Factory function for Claude Code."""
    return BackendArchitectAgent()