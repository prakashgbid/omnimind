"""
DevOps Automator Agent - OmniMind Powered

Specializes in CI/CD, infrastructure as code, monitoring, and automation.
Remembers all deployment patterns, incident responses, and optimization strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, List, Optional
from src.agents.base_omnimind_agent import BaseOmniMindAgent


class DevOpsAutomatorAgent(BaseOmniMindAgent):
    """
    DevOps automation specialist with perfect memory.
    
    Capabilities:
    - CI/CD pipeline design
    - Infrastructure as Code (Terraform, CloudFormation)
    - Container orchestration (Kubernetes, Docker)
    - Monitoring and observability
    - Incident response automation
    - Cloud cost optimization
    """
    
    def __init__(self):
        super().__init__(
            agent_name="devops-automator",
            specialization="CI/CD, Kubernetes, Terraform, monitoring, and cloud automation"
        )
        
        # DevOps-specific context
        self.deployment_patterns = []
        self.incident_playbooks = {}
        self.infrastructure_state = {}
    
    def _get_preferred_models(self) -> Dict[str, str]:
        """DevOps-optimized model selection."""
        return {
            'code': 'deepseek-coder:6.7b',  # For scripts and configs
            'reasoning': 'mistral:7b',       # For architecture decisions
            'quick': 'gemma2:2b',           # For quick commands
            'general': 'llama3.2:3b',       # For general DevOps tasks
            'troubleshooting': 'mistral:7b' # For debugging issues
        }
    
    def get_specialization_prompt(self) -> str:
        """DevOps-specific expertise prompt."""
        return """
I am a DevOps Automator Agent specializing in cloud infrastructure and automation.

My expertise includes:
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
- Infrastructure as Code (Terraform, Pulumi, CloudFormation)
- Container orchestration (Kubernetes, Docker Swarm, ECS)
- Cloud platforms (AWS, GCP, Azure)
- Monitoring (Prometheus, Grafana, DataDog, New Relic)
- Log management (ELK stack, Fluentd)
- Security scanning and compliance
- Disaster recovery and backup strategies
- Cost optimization and resource management

I remember all deployment patterns, incident responses, and optimization strategies to provide reliable, efficient DevOps solutions.
"""
    
    def create_pipeline(self, project_type: str, stages: List[str],
                       requirements: Optional[str] = None) -> str:
        """
        Create CI/CD pipeline configuration.
        
        Args:
            project_type: Type of project (node, python, go, etc.)
            stages: Pipeline stages needed
            requirements: Additional requirements
        
        Returns:
            Complete pipeline configuration
        """
        # Search for similar pipelines
        similar_pipelines = self.search_knowledge(f"pipeline {project_type} CI/CD")
        
        prompt = f"""
Create CI/CD pipeline for {project_type} project.
Stages: {', '.join(stages)}
Requirements: {requirements if requirements else 'Standard deployment'}

Include:
1. Build stage with caching
2. Test stage with parallel execution
3. Security scanning (SAST/DAST)
4. Container build and registry push
5. Deployment strategies (blue-green, canary)
6. Rollback mechanisms
7. Notifications and approvals
8. Environment-specific configurations

Generate GitHub Actions and GitLab CI configurations.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this pipeline pattern
        self.remember_decision(
            f"Created {project_type} pipeline",
            f"Stages: {stages}",
            tags=['cicd', 'pipeline', project_type]
        )
        
        return response
    
    def setup_kubernetes(self, app_name: str, requirements: str,
                        scale_requirements: Optional[str] = None) -> str:
        """
        Create Kubernetes deployment configuration.
        
        Args:
            app_name: Application name
            requirements: Application requirements
            scale_requirements: Scaling needs
        
        Returns:
            Complete K8s manifests
        """
        prompt = f"""
Create Kubernetes configuration for {app_name}.
Requirements: {requirements}
Scaling: {scale_requirements if scale_requirements else 'Standard autoscaling'}

Generate:
1. Deployment with resource limits
2. Service (ClusterIP/LoadBalancer)
3. Ingress with TLS
4. ConfigMap and Secrets
5. HorizontalPodAutoscaler
6. NetworkPolicy
7. PodDisruptionBudget
8. Health checks and probes
9. Monitoring ServiceMonitor

Include Helm chart structure if complex.
"""
        
        return self.think(prompt, use_specialization=True)
    
    def optimize_infrastructure(self, current_setup: str, 
                               metrics: Dict[str, str],
                               budget: Optional[str] = None) -> str:
        """
        Optimize cloud infrastructure for cost and performance.
        
        Args:
            current_setup: Current infrastructure description
            metrics: Current metrics (cost, performance, etc.)
            budget: Budget constraints
        
        Returns:
            Optimization recommendations
        """
        # Search for past optimizations
        past_optimizations = self.search_knowledge("infrastructure optimization cost")
        
        prompt = f"""
Optimize infrastructure:
Current setup: {current_setup}
Metrics: {metrics}
Budget: {budget if budget else 'Optimize for best value'}

Analyze and recommend:
1. Right-sizing instances
2. Reserved instances vs spot instances
3. Auto-scaling policies
4. Storage optimization
5. Network optimization (CDN, caching)
6. Database optimization (RDS vs self-managed)
7. Serverless opportunities
8. Multi-region strategies

Past successful optimizations:
{chr(10).join([m['content'][:150] for m in past_optimizations[:3]]) if past_optimizations else 'None'}

Provide specific actions with expected savings.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Learn from this optimization
        self.learn_from_feedback(
            f"Infrastructure optimization for {current_setup[:50]}",
            f"Applied optimizations with metrics: {metrics}",
            "Cost-saving techniques for future use"
        )
        
        return response
    
    def incident_response(self, incident_type: str, symptoms: str,
                         severity: str = "medium") -> str:
        """
        Generate incident response playbook.
        
        Args:
            incident_type: Type of incident
            symptoms: Observed symptoms
            severity: Incident severity (low/medium/high/critical)
        
        Returns:
            Step-by-step response playbook
        """
        # Search for similar incidents
        past_incidents = self.search_knowledge(f"incident {incident_type} response")
        
        prompt = f"""
Incident Response Required:
Type: {incident_type}
Symptoms: {symptoms}
Severity: {severity}

Past similar incidents:
{chr(10).join([m['content'][:150] for m in past_incidents[:3]]) if past_incidents else 'None'}

Provide:
1. Immediate mitigation steps
2. Root cause analysis approach
3. Communication template
4. Rollback procedures if needed
5. Monitoring checks
6. Post-incident review items
7. Prevention measures

Format as executable runbook.
"""
        
        response = self.think(prompt, use_specialization=True, 
                            model='mistral:7b')  # Use best reasoning model
        
        # Remember this incident
        self.remember_decision(
            f"Incident response for {incident_type}",
            f"Severity: {severity}, Symptoms: {symptoms}",
            tags=['incident', 'response', severity]
        )
        
        return response
    
    def setup_monitoring(self, service_name: str, sla_requirements: str,
                        stack: Optional[str] = None) -> str:
        """
        Set up comprehensive monitoring and alerting.
        
        Args:
            service_name: Service to monitor
            sla_requirements: SLA requirements
            stack: Technology stack
        
        Returns:
            Complete monitoring setup
        """
        prompt = f"""
Set up monitoring for {service_name}.
SLA requirements: {sla_requirements}
Stack: {stack if stack else 'Standard web application'}

Configure:
1. Prometheus metrics and exporters
2. Grafana dashboards
3. Alert rules (critical, warning, info)
4. SLI/SLO definitions
5. Error budget tracking
6. Log aggregation queries
7. Distributed tracing
8. Synthetic monitoring
9. On-call rotation setup

Provide complete configuration files.
"""
        
        return self.think(prompt, use_specialization=True)
    
    def terraform_module(self, resource_type: str, requirements: str,
                        cloud_provider: str = "aws") -> str:
        """
        Create Terraform module for infrastructure.
        
        Args:
            resource_type: Type of resource
            requirements: Resource requirements
            cloud_provider: Cloud provider (aws/gcp/azure)
        
        Returns:
            Complete Terraform module
        """
        prompt = f"""
Create Terraform module for {resource_type} on {cloud_provider}.
Requirements: {requirements}

Include:
1. Main resource configuration
2. Variables with descriptions
3. Outputs for other modules
4. Security best practices
5. Tagging strategy
6. State management
7. Example usage
8. Testing with Terratest

Follow Terraform best practices and our naming conventions.
"""
        
        response = self.think(prompt, use_specialization=True)
        
        # Remember this module
        self.remember_decision(
            f"Created Terraform module for {resource_type}",
            f"Provider: {cloud_provider}",
            tags=['terraform', 'iac', cloud_provider]
        )
        
        return response


# Agent registration for Claude Code
AGENT = DevOpsAutomatorAgent

def create_agent():
    """Factory function for Claude Code."""
    return DevOpsAutomatorAgent()