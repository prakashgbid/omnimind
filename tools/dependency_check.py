#!/usr/bin/env python3
"""
Dependency management and security checker for OSA project.

This tool analyzes project dependencies for security vulnerabilities,
license compatibility, and version management.
"""

import json
import subprocess
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from packaging import version
import re


@dataclass
class Vulnerability:
    """Represents a security vulnerability in a dependency."""
    
    id: str
    package: str
    current_version: str
    vulnerable_versions: str
    severity: str
    description: str
    fix_version: Optional[str] = None
    cve: Optional[str] = None


@dataclass
class DependencyIssue:
    """Represents an issue with a dependency."""
    
    package: str
    current_version: str
    issue_type: str  # 'vulnerability', 'license', 'outdated', 'unused'
    severity: str    # 'critical', 'high', 'medium', 'low', 'info'
    description: str
    recommendation: str
    details: Dict[str, Any] = None


class DependencyAnalyzer:
    """Analyzes project dependencies for various issues."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.requirements_file = self.project_root / "requirements.txt"
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.issues: List[DependencyIssue] = []
    
    def analyze(self) -> List[DependencyIssue]:
        """Run complete dependency analysis."""
        dependencies = self._get_dependencies()
        
        if not dependencies:
            print("⚠️ No dependencies found!")
            return []
        
        print(f"🔍 Analyzing {len(dependencies)} dependencies...")
        
        # Run all checks
        self._check_vulnerabilities(dependencies)
        self._check_licenses(dependencies)
        self._check_outdated_packages(dependencies)
        self._check_unused_dependencies(dependencies)
        self._check_dependency_conflicts(dependencies)
        
        return self.issues
    
    def _get_dependencies(self) -> List[Dict[str, str]]:
        """Extract dependencies from requirements files."""
        dependencies = []
        
        # Check requirements.txt
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dep = self._parse_requirement(line)
                        if dep:
                            dependencies.append(dep)
        
        # Check pyproject.toml for additional dependencies
        if self.pyproject_file.exists():
            import toml
            try:
                data = toml.load(self.pyproject_file)
                project_deps = data.get('project', {}).get('dependencies', [])
                for dep_line in project_deps:
                    dep = self._parse_requirement(dep_line)
                    if dep:
                        dependencies.append(dep)
            except Exception as e:
                print(f"⚠️ Could not parse pyproject.toml: {e}")
        
        return dependencies
    
    def _parse_requirement(self, requirement: str) -> Optional[Dict[str, str]]:
        """Parse a requirement string into package and version."""
        # Handle git URLs, local paths, etc.
        if any(prefix in requirement for prefix in ['git+', 'http', '/', '.']):
            return None
        
        # Extract package name and version constraint
        match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]+.*)?', requirement)
        if match:
            package = match.group(1).lower()
            version_spec = match.group(2) or ""
            
            # Get installed version
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            installed_version = line.split(':', 1)[1].strip()
                            return {
                                'name': package,
                                'version': installed_version,
                                'spec': version_spec,
                                'requirement': requirement
                            }
            except Exception:
                pass
            
            return {
                'name': package,
                'version': 'unknown',
                'spec': version_spec,
                'requirement': requirement
            }
        
        return None
    
    def _check_vulnerabilities(self, dependencies: List[Dict[str, str]]) -> None:
        """Check for known security vulnerabilities."""
        print("🔒 Checking for security vulnerabilities...")
        
        try:
            # Use safety package if available
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 and result.stdout:
                try:
                    vulns = json.loads(result.stdout)
                    for vuln in vulns:
                        self.issues.append(DependencyIssue(
                            package=vuln.get('package'),
                            current_version=vuln.get('installed_version'),
                            issue_type='vulnerability',
                            severity=self._severity_from_score(vuln.get('advisory', {}).get('cve')),
                            description=vuln.get('advisory', {}).get('advisory', ''),
                            recommendation=f"Update to version {vuln.get('advisory', {}).get('safe_versions', ['latest'])[0]}",
                            details=vuln
                        ))
                except json.JSONDecodeError:
                    print("⚠️ Could not parse safety output")
                    
        except FileNotFoundError:
            print("ℹ️ Safety not installed, skipping vulnerability check")
            self.issues.append(DependencyIssue(
                package="safety",
                current_version="not installed",
                issue_type="tool_missing",
                severity="info",
                description="Security scanning tool not available",
                recommendation="Install safety: pip install safety"
            ))
    
    def _check_licenses(self, dependencies: List[Dict[str, str]]) -> None:
        """Check license compatibility."""
        print("📄 Checking license compatibility...")
        
        # Define license compatibility matrix
        compatible_licenses = {
            'MIT', 'BSD-3-Clause', 'BSD-2-Clause', 'Apache-2.0', 
            'ISC', 'Python Software Foundation License'
        }
        
        problematic_licenses = {
            'GPL-3.0': 'Copyleft license may require project to be GPL',
            'AGPL-3.0': 'Strong copyleft license with network use clause',
            'SSPL': 'Server Side Public License has restrictions',
            'Commons Clause': 'Restricts commercial use'
        }
        
        for dep in dependencies:
            if dep['version'] == 'unknown':
                continue
                
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", dep['name']],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    license_info = None
                    for line in result.stdout.split('\n'):
                        if line.startswith('License:'):
                            license_info = line.split(':', 1)[1].strip()
                            break
                    
                    if license_info:
                        if license_info in problematic_licenses:
                            self.issues.append(DependencyIssue(
                                package=dep['name'],
                                current_version=dep['version'],
                                issue_type='license',
                                severity='medium',
                                description=f"License '{license_info}' may be incompatible",
                                recommendation=problematic_licenses[license_info],
                                details={'license': license_info}
                            ))
                        elif license_info not in compatible_licenses and license_info != 'UNKNOWN':
                            self.issues.append(DependencyIssue(
                                package=dep['name'],
                                current_version=dep['version'],
                                issue_type='license',
                                severity='low',
                                description=f"License '{license_info}' needs review",
                                recommendation="Review license for compatibility with project",
                                details={'license': license_info}
                            ))
                            
            except Exception as e:
                print(f"⚠️ Could not check license for {dep['name']}: {e}")
    
    def _check_outdated_packages(self, dependencies: List[Dict[str, str]]) -> None:
        """Check for outdated packages."""
        print("📅 Checking for outdated packages...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                
                for package in outdated:
                    # Check if it's a major version update
                    current = version.parse(package['version'])
                    latest = version.parse(package['latest_version'])
                    
                    severity = 'info'
                    if latest.major > current.major:
                        severity = 'medium'  # Major version update
                    elif latest.minor > current.minor:
                        severity = 'low'     # Minor version update
                    
                    self.issues.append(DependencyIssue(
                        package=package['name'],
                        current_version=package['version'],
                        issue_type='outdated',
                        severity=severity,
                        description=f"Package is outdated (latest: {package['latest_version']})",
                        recommendation=f"Consider updating to {package['latest_version']}",
                        details=package
                    ))
                    
        except Exception as e:
            print(f"⚠️ Could not check outdated packages: {e}")
    
    def _check_unused_dependencies(self, dependencies: List[Dict[str, str]]) -> None:
        """Check for unused dependencies."""
        print("🗑️ Checking for unused dependencies...")
        
        try:
            # This is a simplified check - a full implementation would
            # analyze import statements in the code
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                installed = set()
                for line in result.stdout.split('\n')[2:]:  # Skip header
                    if line.strip():
                        package = line.split()[0].lower()
                        installed.add(package)
                
                required = {dep['name'] for dep in dependencies}
                
                # Find packages that are installed but not in requirements
                extra_packages = installed - required - {'pip', 'setuptools', 'wheel'}
                
                for package in extra_packages:
                    self.issues.append(DependencyIssue(
                        package=package,
                        current_version='unknown',
                        issue_type='unused',
                        severity='info',
                        description="Package installed but not in requirements",
                        recommendation="Add to requirements.txt or uninstall if unused"
                    ))
                    
        except Exception as e:
            print(f"⚠️ Could not check unused packages: {e}")
    
    def _check_dependency_conflicts(self, dependencies: List[Dict[str, str]]) -> None:
        """Check for dependency conflicts."""
        print("⚔️ Checking for dependency conflicts...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and result.stdout:
                conflicts = result.stdout.strip().split('\n')
                for conflict in conflicts:
                    if conflict.strip():
                        self.issues.append(DependencyIssue(
                            package='multiple',
                            current_version='various',
                            issue_type='conflict',
                            severity='high',
                            description=conflict,
                            recommendation="Resolve version conflicts in requirements"
                        ))
                        
        except Exception as e:
            print(f"⚠️ Could not check dependency conflicts: {e}")
    
    def _severity_from_score(self, cve_info: Optional[str]) -> str:
        """Determine severity from CVE information."""
        if not cve_info:
            return 'medium'
        
        # This is simplified - real implementation would query CVE database
        if 'critical' in cve_info.lower():
            return 'critical'
        elif 'high' in cve_info.lower():
            return 'high'
        elif 'low' in cve_info.lower():
            return 'low'
        else:
            return 'medium'


def generate_report(issues: List[DependencyIssue]) -> None:
    """Generate a comprehensive dependency report."""
    if not issues:
        print("✅ No dependency issues found!")
        return
    
    # Group issues by severity
    by_severity = {}
    for issue in issues:
        if issue.severity not in by_severity:
            by_severity[issue.severity] = []
        by_severity[issue.severity].append(issue)
    
    severity_order = ['critical', 'high', 'medium', 'low', 'info']
    severity_emojis = {
        'critical': '💀',
        'high': '🔥',
        'medium': '⚠️',
        'low': '📝',
        'info': 'ℹ️'
    }
    
    print(f"\n📊 Dependency Analysis Report")
    print("=" * 50)
    
    total_issues = len(issues)
    critical_count = len(by_severity.get('critical', []))
    high_count = len(by_severity.get('high', []))
    
    print(f"Total issues: {total_issues}")
    print(f"Critical: {critical_count}, High: {high_count}")
    print()
    
    for severity in severity_order:
        if severity in by_severity:
            severity_issues = by_severity[severity]
            print(f"{severity_emojis[severity]} {severity.upper()} ({len(severity_issues)} issues)")
            print("-" * 30)
            
            for issue in severity_issues:
                print(f"📦 {issue.package} ({issue.current_version})")
                print(f"   Type: {issue.issue_type}")
                print(f"   Issue: {issue.description}")
                print(f"   Fix: {issue.recommendation}")
                print()
    
    # Exit with appropriate code
    if critical_count > 0:
        print("❌ Critical vulnerabilities found! Fix immediately.")
        sys.exit(1)
    elif high_count > 0:
        print("⚠️ High severity issues found! Review and fix.")
        sys.exit(1)
    else:
        print("✅ No critical security issues found.")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    analyzer = DependencyAnalyzer(project_root)
    issues = analyzer.analyze()
    generate_report(issues)


if __name__ == "__main__":
    main()