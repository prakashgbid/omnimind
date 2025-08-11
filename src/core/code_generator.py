#!/usr/bin/env python3
"""
OSA Code Generation and Self-Modification System
Enables autonomous code generation, modification, and self-improvement
"""

import ast
import re
import subprocess
import tempfile
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging
import black
import autopep8


class CodeType(Enum):
    """Types of code generation tasks"""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SCRIPT = "script"
    TEST = "test"
    REFACTOR = "refactor"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    SELF_MODIFICATION = "self_modification"


class ProgrammingLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CPP = "cpp"
    SHELL = "shell"


@dataclass
class CodeTemplate:
    """Template for code generation"""
    name: str
    language: ProgrammingLanguage
    template: str
    variables: List[str]
    description: str


@dataclass
class CodeGenerationRequest:
    """Request for code generation"""
    description: str
    code_type: CodeType
    language: ProgrammingLanguage
    requirements: List[str]
    constraints: List[str]
    examples: List[str] = None
    context: Dict[str, Any] = None


@dataclass
class GeneratedCode:
    """Generated code result"""
    code: str
    language: ProgrammingLanguage
    description: str
    tests: Optional[str] = None
    documentation: Optional[str] = None
    complexity_score: float = 0.0
    quality_score: float = 0.0


class CodeGenerator:
    """Advanced code generation system for OSA"""
    
    def __init__(self, langchain_engine=None, config: Dict[str, Any] = None):
        self.config = config or {}
        self.langchain_engine = langchain_engine
        self.logger = logging.getLogger("OSA-CodeGen")
        
        # Code templates library
        self.templates = self._initialize_templates()
        
        # Code analysis tools
        self.analyzers = {
            ProgrammingLanguage.PYTHON: self._analyze_python,
            ProgrammingLanguage.JAVASCRIPT: self._analyze_javascript,
        }
        
        # Code formatters
        self.formatters = {
            ProgrammingLanguage.PYTHON: self._format_python,
            ProgrammingLanguage.JAVASCRIPT: self._format_javascript,
        }
        
        # Self-modification history
        self.modification_history = []
        
        # Generated code cache
        self.code_cache = {}
        
    def _initialize_templates(self) -> Dict[str, CodeTemplate]:
        """Initialize code generation templates"""
        templates = {}
        
        # Python function template
        templates["python_function"] = CodeTemplate(
            name="python_function",
            language=ProgrammingLanguage.PYTHON,
            template='''def {function_name}({parameters}){type_hints}:
    """
    {description}
    
    Args:
        {args_description}
    
    Returns:
        {return_description}
    """
    {implementation}
''',
            variables=["function_name", "parameters", "type_hints", "description", 
                      "args_description", "return_description", "implementation"],
            description="Template for Python functions"
        )
        
        # Python class template
        templates["python_class"] = CodeTemplate(
            name="python_class",
            language=ProgrammingLanguage.PYTHON,
            template='''class {class_name}({base_classes}):
    """
    {description}
    
    Attributes:
        {attributes_description}
    """
    
    def __init__(self, {init_parameters}):
        """Initialize {class_name}"""
        {init_implementation}
    
    {methods}
''',
            variables=["class_name", "base_classes", "description", 
                      "attributes_description", "init_parameters", 
                      "init_implementation", "methods"],
            description="Template for Python classes"
        )
        
        # Python async function template
        templates["python_async"] = CodeTemplate(
            name="python_async",
            language=ProgrammingLanguage.PYTHON,
            template='''async def {function_name}({parameters}){type_hints}:
    """
    {description}
    
    Async function for {purpose}
    """
    {implementation}
''',
            variables=["function_name", "parameters", "type_hints", 
                      "description", "purpose", "implementation"],
            description="Template for async Python functions"
        )
        
        return templates
    
    async def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code based on request"""
        self.logger.info(f"Generating {request.code_type.value} in {request.language.value}")
        
        # Use LangChain for intelligent code generation
        if self.langchain_engine:
            return await self._generate_with_langchain(request)
        
        # Fallback to template-based generation
        return await self._generate_with_templates(request)
    
    async def _generate_with_langchain(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code using LangChain"""
        # Build prompt for code generation
        prompt = self._build_generation_prompt(request)
        
        # Generate code using best LLM for coding
        response, metadata = await self.langchain_engine.query_with_memory(
            prompt, "coding"
        )
        
        # Parse the generated code
        code = self._extract_code_from_response(response, request.language)
        
        # Format the code
        if request.language in self.formatters:
            code = self.formatters[request.language](code)
        
        # Generate tests if requested
        tests = None
        if request.code_type != CodeType.TEST:
            tests = await self._generate_tests(code, request)
        
        # Generate documentation
        documentation = await self._generate_documentation(code, request)
        
        # Analyze code quality
        quality_score = await self._analyze_code_quality(code, request.language)
        
        return GeneratedCode(
            code=code,
            language=request.language,
            description=request.description,
            tests=tests,
            documentation=documentation,
            quality_score=quality_score
        )
    
    async def _generate_with_templates(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code using templates (fallback)"""
        # Find appropriate template
        template_key = f"{request.language.value}_{request.code_type.value}"
        
        if template_key in self.templates:
            template = self.templates[template_key]
            
            # Fill template with basic implementation
            code = template.template.format(
                **self._get_template_variables(request, template)
            )
            
            return GeneratedCode(
                code=code,
                language=request.language,
                description=request.description
            )
        
        # No template available
        return GeneratedCode(
            code=f"# TODO: Implement {request.description}",
            language=request.language,
            description=request.description
        )
    
    def _build_generation_prompt(self, request: CodeGenerationRequest) -> str:
        """Build prompt for code generation"""
        prompt_parts = [
            f"Generate {request.code_type.value} code in {request.language.value}.",
            f"Description: {request.description}",
            "\nRequirements:"
        ]
        
        for req in request.requirements:
            prompt_parts.append(f"- {req}")
        
        if request.constraints:
            prompt_parts.append("\nConstraints:")
            for constraint in request.constraints:
                prompt_parts.append(f"- {constraint}")
        
        if request.examples:
            prompt_parts.append("\nExamples for reference:")
            for example in request.examples:
                prompt_parts.append(f"```\n{example}\n```")
        
        prompt_parts.extend([
            "\nGenerate clean, efficient, well-documented code.",
            "Include error handling and edge cases.",
            "Follow best practices and coding standards.",
            f"Output the code in {request.language.value} format."
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_code_from_response(self, response: str, language: ProgrammingLanguage) -> str:
        """Extract code from LLM response"""
        # Look for code blocks
        code_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks, assume entire response is code
        # Remove any explanation lines
        lines = response.split('\n')
        code_lines = []
        
        for line in lines:
            # Skip obvious explanation lines
            if not any(marker in line.lower() for marker in 
                      ['here', 'this', 'the following', 'code:', 'example:']):
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    async def _generate_tests(self, code: str, request: CodeGenerationRequest) -> Optional[str]:
        """Generate tests for the code"""
        if not self.langchain_engine:
            return None
        
        test_prompt = f"""Generate comprehensive tests for the following {request.language.value} code:

```{request.language.value}
{code}
```

Generate unit tests that:
- Test normal cases
- Test edge cases
- Test error conditions
- Achieve high code coverage
- Follow testing best practices for {request.language.value}
"""
        
        response, _ = await self.langchain_engine.query_with_memory(
            test_prompt, "coding"
        )
        
        return self._extract_code_from_response(response, request.language)
    
    async def _generate_documentation(self, code: str, request: CodeGenerationRequest) -> str:
        """Generate documentation for the code"""
        if not self.langchain_engine:
            return "# Documentation pending"
        
        doc_prompt = f"""Generate comprehensive documentation for the following {request.language.value} code:

```{request.language.value}
{code}
```

Include:
- Overview and purpose
- Usage examples
- Parameter descriptions
- Return value documentation
- Potential errors/exceptions
- Performance considerations
"""
        
        response, _ = await self.langchain_engine.query_with_memory(
            doc_prompt, "documentation"
        )
        
        return response
    
    async def _analyze_code_quality(self, code: str, language: ProgrammingLanguage) -> float:
        """Analyze code quality and return score"""
        if language in self.analyzers:
            return self.analyzers[language](code)
        return 0.5  # Default middle score
    
    def _analyze_python(self, code: str) -> float:
        """Analyze Python code quality"""
        score = 1.0
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Check for docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(node):
                        score -= 0.1
            
            # Check for error handling
            has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
            if not has_try and len(code) > 100:  # Only for non-trivial code
                score -= 0.1
            
            # Check for type hints (simple check)
            if '->' not in code and len(code) > 50:
                score -= 0.05
            
        except SyntaxError:
            score = 0.0  # Invalid Python code
        
        return max(0.0, min(1.0, score))
    
    def _analyze_javascript(self, code: str) -> float:
        """Analyze JavaScript code quality"""
        score = 1.0
        
        # Basic quality checks
        if 'var ' in code:  # Using old var instead of let/const
            score -= 0.1
        
        if 'console.log' in code:  # Left debug statements
            score -= 0.05
        
        if not any(marker in code for marker in ['try', 'catch', '.catch']):
            score -= 0.1  # No error handling
        
        return max(0.0, min(1.0, score))
    
    def _format_python(self, code: str) -> str:
        """Format Python code"""
        try:
            # Use black for formatting
            formatted = black.format_str(code, mode=black.Mode())
            return formatted
        except:
            try:
                # Fallback to autopep8
                return autopep8.fix_code(code)
            except:
                return code
    
    def _format_javascript(self, code: str) -> str:
        """Format JavaScript code"""
        # Would use prettier or similar if available
        return code
    
    def _get_template_variables(self, request: CodeGenerationRequest, template: CodeTemplate) -> Dict[str, str]:
        """Get variables for template filling"""
        variables = {}
        
        for var in template.variables:
            if var == "description":
                variables[var] = request.description
            elif var == "function_name":
                # Extract function name from description
                variables[var] = re.sub(r'[^a-zA-Z0-9_]', '_', 
                                       request.description.lower().replace(' ', '_'))[:30]
            else:
                variables[var] = f"# TODO: {var}"
        
        return variables
    
    async def self_modify(self, target_file: str, modification_request: str) -> bool:
        """Self-modify OSA's own code"""
        self.logger.warning(f"Self-modification requested for {target_file}")
        
        # Safety checks
        if not self._is_safe_to_modify(target_file):
            self.logger.error("Self-modification blocked for safety")
            return False
        
        # Read current code
        target_path = Path(target_file)
        if not target_path.exists():
            self.logger.error(f"Target file {target_file} not found")
            return False
        
        original_code = target_path.read_text()
        
        # Generate modification
        if self.langchain_engine:
            modified_code = await self._generate_modification(
                original_code, modification_request
            )
        else:
            self.logger.error("LangChain engine required for self-modification")
            return False
        
        # Validate the modification
        if not self._validate_modification(original_code, modified_code):
            self.logger.error("Modification validation failed")
            return False
        
        # Create backup
        backup_path = target_path.with_suffix('.bak')
        backup_path.write_text(original_code)
        
        # Apply modification
        target_path.write_text(modified_code)
        
        # Record in history
        self.modification_history.append({
            "file": target_file,
            "request": modification_request,
            "timestamp": asyncio.get_event_loop().time(),
            "backup": str(backup_path)
        })
        
        self.logger.info(f"Successfully self-modified {target_file}")
        return True
    
    def _is_safe_to_modify(self, target_file: str) -> bool:
        """Check if file is safe to modify"""
        # Only allow modification of OSA files
        safe_patterns = [
            "osa_*.py",
            "src/core/*.py",
            "src/plugins/*.py"
        ]
        
        target_path = Path(target_file)
        
        for pattern in safe_patterns:
            if target_path.match(pattern):
                return True
        
        return False
    
    async def _generate_modification(self, original_code: str, request: str) -> str:
        """Generate code modification"""
        prompt = f"""Modify the following code according to the request:

Original Code:
```python
{original_code}
```

Modification Request:
{request}

Requirements:
- Preserve existing functionality unless explicitly changed
- Maintain code style and conventions
- Add appropriate error handling
- Include comments for significant changes
- Ensure backward compatibility

Generate the complete modified code:
"""
        
        response, _ = await self.langchain_engine.query_with_memory(
            prompt, "coding"
        )
        
        return self._extract_code_from_response(response, ProgrammingLanguage.PYTHON)
    
    def _validate_modification(self, original: str, modified: str) -> bool:
        """Validate code modification"""
        try:
            # Check syntax
            ast.parse(modified)
            
            # Check that it's not empty
            if len(modified.strip()) < 10:
                return False
            
            # Check that it's actually different
            if original == modified:
                return False
            
            # Could add more validation (unit tests, etc.)
            
            return True
            
        except SyntaxError:
            return False
    
    async def optimize_code(self, code: str, language: ProgrammingLanguage) -> str:
        """Optimize existing code"""
        if not self.langchain_engine:
            return code
        
        optimize_prompt = f"""Optimize the following {language.value} code for:
- Performance
- Memory usage  
- Readability
- Best practices

Code:
```{language.value}
{code}
```

Generate optimized version:
"""
        
        response, _ = await self.langchain_engine.query_with_memory(
            optimize_prompt, "coding"
        )
        
        optimized = self._extract_code_from_response(response, language)
        
        # Format the optimized code
        if language in self.formatters:
            optimized = self.formatters[language](optimized)
        
        return optimized
    
    async def refactor_code(self, code: str, language: ProgrammingLanguage, 
                           refactor_goals: List[str]) -> str:
        """Refactor code based on specific goals"""
        if not self.langchain_engine:
            return code
        
        goals_str = "\n".join(f"- {goal}" for goal in refactor_goals)
        
        refactor_prompt = f"""Refactor the following {language.value} code to achieve these goals:
{goals_str}

Code:
```{language.value}
{code}
```

Generate refactored version:
"""
        
        response, _ = await self.langchain_engine.query_with_memory(
            refactor_prompt, "coding"
        )
        
        return self._extract_code_from_response(response, language)
    
    def get_modification_history(self) -> List[Dict[str, Any]]:
        """Get history of self-modifications"""
        return self.modification_history.copy()
    
    def rollback_modification(self, file_path: str) -> bool:
        """Rollback a self-modification"""
        # Find the most recent modification for this file
        for mod in reversed(self.modification_history):
            if mod["file"] == file_path:
                backup_path = Path(mod["backup"])
                if backup_path.exists():
                    # Restore from backup
                    target_path = Path(file_path)
                    target_path.write_text(backup_path.read_text())
                    self.logger.info(f"Rolled back {file_path} from {backup_path}")
                    return True
        
        self.logger.error(f"No backup found for {file_path}")
        return False


# Singleton instance
_code_generator = None

def get_code_generator(langchain_engine=None, config: Dict[str, Any] = None) -> CodeGenerator:
    """Get or create the global code generator"""
    global _code_generator
    if _code_generator is None:
        _code_generator = CodeGenerator(langchain_engine, config)
    return _code_generator