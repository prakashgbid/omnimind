#!/usr/bin/env python3
"""
Custom quality checks and anti-pattern detection for OSA project.

This module implements custom linting rules and checks for code quality,
architecture patterns, and project-specific best practices.
"""

import ast
import sys
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Iterator, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityIssue:
    """Represents a code quality issue."""
    
    file_path: str
    line_number: int
    column: int
    severity: str  # 'error', 'warning', 'info'
    rule_id: str
    message: str
    suggestion: str = ""


class OSACodeAnalyzer(ast.NodeVisitor):
    """AST-based analyzer for OSA-specific code patterns."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[QualityIssue] = []
        self.current_class = None
        self.current_function = None
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyze class definitions."""
        self.current_class = node.name
        
        # Check for God classes (too many methods)
        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
        if method_count > 20:
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="warning",
                rule_id="OSA001",
                message=f"Class '{node.name}' has {method_count} methods. Consider splitting into smaller classes.",
                suggestion="Apply Single Responsibility Principle"
            ))
        
        # Check for missing docstrings in public classes
        if not node.name.startswith('_') and not self._has_docstring(node):
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="error",
                rule_id="OSA002",
                message=f"Public class '{node.name}' missing docstring",
                suggestion="Add Google-style docstring"
            ))
        
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function definitions."""
        self.current_function = node.name
        
        # Check for too many parameters
        param_count = len(node.args.args)
        if param_count > 8:
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="warning",
                rule_id="OSA003",
                message=f"Function '{node.name}' has {param_count} parameters. Consider using configuration objects.",
                suggestion="Group related parameters into dataclasses"
            ))
        
        # Check for missing type annotations on public functions
        if not node.name.startswith('_') and not self._has_return_annotation(node):
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="error",
                rule_id="OSA004",
                message=f"Public function '{node.name}' missing return type annotation",
                suggestion="Add -> ReturnType annotation"
            ))
        
        # Check for async functions without await
        if isinstance(node, ast.AsyncFunctionDef):
            has_await = any(isinstance(n, ast.Await) for n in ast.walk(node))
            if not has_await:
                self.issues.append(QualityIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    severity="warning",
                    rule_id="OSA005",
                    message=f"Async function '{node.name}' doesn't use await",
                    suggestion="Consider making function synchronous or add await calls"
                ))
        
        self.generic_visit(node)
        self.current_function = None
    
    def visit_Try(self, node: ast.Try) -> None:
        """Check exception handling patterns."""
        # Check for bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append(QualityIssue(
                    file_path=self.file_path,
                    line_number=handler.lineno,
                    column=handler.col_offset,
                    severity="error",
                    rule_id="OSA006",
                    message="Bare except clause catches all exceptions",
                    suggestion="Catch specific exception types"
                ))
            
            # Check for pass in except blocks
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.issues.append(QualityIssue(
                    file_path=self.file_path,
                    line_number=handler.lineno,
                    column=handler.col_offset,
                    severity="warning",
                    rule_id="OSA007",
                    message="Empty except block silences errors",
                    suggestion="Log the exception or re-raise with context"
                ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check import patterns."""
        for alias in node.names:
            # Check for dangerous imports
            dangerous_modules = ['os', 'subprocess', 'eval', 'exec']
            if alias.name in dangerous_modules:
                self.issues.append(QualityIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    severity="warning",
                    rule_id="OSA008",
                    message=f"Importing potentially dangerous module '{alias.name}'",
                    suggestion="Ensure secure usage or consider alternatives"
                ))
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function call patterns."""
        # Check for synchronous HTTP calls in async context
        if (isinstance(node.func, ast.Attribute) and 
            hasattr(node.func.value, 'id') and 
            node.func.value.id == 'requests' and
            self.current_function and
            self.current_function.startswith('async')):
            
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="error",
                rule_id="OSA009",
                message="Synchronous HTTP call in async function blocks event loop",
                suggestion="Use aiohttp or httpx for async HTTP calls"
            ))
        
        # Check for print statements (should use logging)
        if (isinstance(node.func, ast.Name) and 
            node.func.id == 'print' and 
            not self.file_path.endswith('_test.py')):
            
            self.issues.append(QualityIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity="warning",
                rule_id="OSA010",
                message="Use logging instead of print statements",
                suggestion="Replace with logger.info() or appropriate log level"
            ))
        
        self.generic_visit(node)
    
    def _has_docstring(self, node: ast.ClassDef) -> bool:
        """Check if a class has a docstring."""
        return (node.body and 
                isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str))
    
    def _has_return_annotation(self, node: ast.FunctionDef) -> bool:
        """Check if a function has return type annotation."""
        return node.returns is not None


class ArchitectureAnalyzer:
    """Analyzer for architectural patterns and violations."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[QualityIssue] = []
    
    def analyze(self) -> List[QualityIssue]:
        """Analyze the entire project for architectural issues."""
        self._check_circular_imports()
        self._check_layer_violations()
        self._check_dependency_violations()
        self._check_file_organization()
        return self.issues
    
    def _check_circular_imports(self) -> None:
        """Detect circular import dependencies."""
        # Implementation would use import graph analysis
        # For now, we'll do a simple regex-based check
        py_files = list(self.project_root.rglob("*.py"))
        
        for file_path in py_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for potential circular imports
            imports = re.findall(r'^from (\S+) import', content, re.MULTILINE)
            for imp in imports:
                if imp.startswith('src.') and 'circular' in imp.lower():
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=1,
                        column=0,
                        severity="error",
                        rule_id="ARCH001",
                        message=f"Potential circular import detected: {imp}",
                        suggestion="Restructure imports or use late binding"
                    ))
    
    def _check_layer_violations(self) -> None:
        """Check for architectural layer violations."""
        # Define layer hierarchy
        layers = {
            'presentation': ['cli', 'web_ui'],
            'application': ['core', 'services'],
            'domain': ['models', 'entities'],
            'infrastructure': ['providers', 'repositories']
        }
        
        # Check that lower layers don't import from higher layers
        for file_path in self.project_root.rglob("*.py"):
            relative_path = file_path.relative_to(self.project_root)
            
            # Determine current layer
            current_layer = None
            for layer, dirs in layers.items():
                if any(part in str(relative_path) for part in dirs):
                    current_layer = layer
                    break
            
            if current_layer:
                self._check_layer_imports(file_path, current_layer, layers)
    
    def _check_layer_imports(self, file_path: Path, current_layer: str, layers: Dict[str, List[str]]) -> None:
        """Check imports for a specific file's layer."""
        layer_hierarchy = ['infrastructure', 'domain', 'application', 'presentation']
        current_level = layer_hierarchy.index(current_layer)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        imports = re.findall(r'^from src\.(\w+)', content, re.MULTILINE)
        
        for imp in imports:
            for layer, dirs in layers.items():
                if imp in dirs:
                    imported_level = layer_hierarchy.index(layer)
                    if imported_level > current_level:
                        self.issues.append(QualityIssue(
                            file_path=str(file_path),
                            line_number=1,
                            column=0,
                            severity="error",
                            rule_id="ARCH002",
                            message=f"Layer violation: {current_layer} layer importing from {layer} layer",
                            suggestion="Move shared code to appropriate layer or use dependency injection"
                        ))
    
    def _check_dependency_violations(self) -> None:
        """Check for dependency rule violations."""
        # Check that core business logic doesn't depend on external libraries
        core_files = list(self.project_root.glob("src/core/**/*.py"))
        
        forbidden_imports = ['requests', 'aiohttp', 'anthropic', 'openai']
        
        for file_path in core_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for forbidden in forbidden_imports:
                if re.search(rf'^import {forbidden}|^from {forbidden}', content, re.MULTILINE):
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=1,
                        column=0,
                        severity="error",
                        rule_id="ARCH003",
                        message=f"Core domain depends on external library: {forbidden}",
                        suggestion="Use dependency injection or move to infrastructure layer"
                    ))
    
    def _check_file_organization(self) -> None:
        """Check file and directory organization."""
        # Check for files that are too large
        for file_path in self.project_root.rglob("*.py"):
            if file_path.stat().st_size > 10000:  # 10KB
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                if line_count > 500:
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=1,
                        column=0,
                        severity="warning",
                        rule_id="ARCH004",
                        message=f"File has {line_count} lines, consider splitting",
                        suggestion="Split into smaller, focused modules"
                    ))


class SecurityAnalyzer:
    """Custom security pattern analyzer."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[QualityIssue] = []
    
    def analyze(self) -> List[QualityIssue]:
        """Analyze for security issues."""
        self._check_hardcoded_secrets()
        self._check_sql_injection()
        self._check_path_traversal()
        self._check_unsafe_deserialization()
        return self.issues
    
    def _check_hardcoded_secrets(self) -> None:
        """Check for hardcoded secrets and credentials."""
        secret_patterns = [
            (r'api_key\s*=\s*["\'][^"\']{20,}["\']', "API key"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Password"),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', "Secret"),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', "Token"),
            (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API key"),
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.issues.append(QualityIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            column=0,
                            severity="error",
                            rule_id="SEC001",
                            message=f"Potential hardcoded {secret_type} detected",
                            suggestion="Use environment variables or secure key management"
                        ))
    
    def _check_sql_injection(self) -> None:
        """Check for SQL injection vulnerabilities."""
        for file_path in self.project_root.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for string formatting in SQL queries
            sql_patterns = [
                r'execute\(["\'].+%s.+["\']',
                r'execute\(["\'].+\{.+\}.+["\']',
                r'execute\(.+\+.+\)',
            ]
            
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        column=match.start(),
                        severity="error",
                        rule_id="SEC002",
                        message="Potential SQL injection vulnerability",
                        suggestion="Use parameterized queries"
                    ))
    
    def _check_path_traversal(self) -> None:
        """Check for path traversal vulnerabilities."""
        dangerous_patterns = [
            r'open\(["\']\.\./',
            r'with\s+open\(["\']\.\./',
            r'os\.path\.join\([^)]*\.\.[^)]*\)',
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in dangerous_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        column=match.start(),
                        severity="warning",
                        rule_id="SEC003",
                        message="Potential path traversal vulnerability",
                        suggestion="Validate and sanitize file paths"
                    ))
    
    def _check_unsafe_deserialization(self) -> None:
        """Check for unsafe deserialization."""
        unsafe_patterns = [
            r'pickle\.loads?',
            r'yaml\.load\(',
            r'eval\(',
            r'exec\(',
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in unsafe_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        column=match.start(),
                        severity="error",
                        rule_id="SEC004",
                        message="Unsafe deserialization detected",
                        suggestion="Use safe alternatives like json.loads or yaml.safe_load"
                    ))


def analyze_file(file_path: str) -> List[QualityIssue]:
    """Analyze a single Python file."""
    if not file_path.endswith('.py'):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        analyzer = OSACodeAnalyzer(file_path)
        analyzer.visit(tree)
        
        return analyzer.issues
    except (SyntaxError, UnicodeDecodeError) as e:
        logger.error(f"Failed to analyze {file_path}: {e}")
        return []


def main():
    """Run all quality checks."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    all_issues = []
    
    # Analyze individual Python files
    for file_path in Path(project_root).rglob("*.py"):
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
        
        issues = analyze_file(str(file_path))
        all_issues.extend(issues)
    
    # Analyze architecture
    arch_analyzer = ArchitectureAnalyzer(project_root)
    all_issues.extend(arch_analyzer.analyze())
    
    # Analyze security
    sec_analyzer = SecurityAnalyzer(project_root)
    all_issues.extend(sec_analyzer.analyze())
    
    # Report issues
    if all_issues:
        print(f"\n🚨 Found {len(all_issues)} quality issues:")
        
        for issue in sorted(all_issues, key=lambda x: (x.file_path, x.line_number)):
            severity_emoji = {
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            
            print(f"{severity_emoji[issue.severity]} {issue.file_path}:{issue.line_number}:{issue.column}")
            print(f"   {issue.rule_id}: {issue.message}")
            if issue.suggestion:
                print(f"   💡 {issue.suggestion}")
            print()
        
        # Exit with error code if there are errors
        error_count = sum(1 for issue in all_issues if issue.severity == 'error')
        if error_count > 0:
            print(f"❌ {error_count} errors found. Please fix before committing.")
            sys.exit(1)
        else:
            print("✅ No critical errors found.")
    else:
        print("✅ No quality issues found!")


if __name__ == "__main__":
    main()