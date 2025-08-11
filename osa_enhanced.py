#!/usr/bin/env python3
"""
OSA Enhanced Features - Extensions beyond Claude Code
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

class OSAEnhancedFeatures:
    """Enhanced features that go beyond Claude Code."""
    
    def __init__(self, osa_instance):
        self.osa = osa_instance
        self.workspace_context = {}
        self.active_projects = []
        self.code_snippets = {}
        self.learning_notes = []
    
    async def auto_complete_code(self, partial_code: str, language: str = "python") -> str:
        """Auto-complete code snippets intelligently."""
        prompt = f"""Complete this {language} code intelligently:
```{language}
{partial_code}
```

Provide the completed code with explanations."""
        
        return await self.osa.accomplish_task(prompt)
    
    async def explain_error(self, error_message: str, code_context: str = "") -> str:
        """Explain errors and provide fixes."""
        prompt = f"""Explain this error and provide a fix:

Error: {error_message}

Context:
{code_context}

Provide:
1. What the error means
2. Why it occurred
3. How to fix it
4. Prevention tips"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def refactor_code(self, code: str, language: str = "python") -> str:
        """Refactor code for better quality."""
        prompt = f"""Refactor this {language} code for better quality:

```{language}
{code}
```

Improvements to make:
- Better naming
- Improved structure
- Performance optimization
- Better error handling
- Documentation"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def generate_tests(self, code: str, language: str = "python") -> str:
        """Generate unit tests for code."""
        prompt = f"""Generate comprehensive unit tests for this {language} code:

```{language}
{code}
```

Include:
- Edge cases
- Error conditions
- Performance tests if applicable"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analyze a project structure and provide insights."""
        analysis = {
            "path": str(project_path),
            "languages": [],
            "file_count": 0,
            "total_lines": 0,
            "structure": {},
            "suggestions": []
        }
        
        # Count files and detect languages
        for ext in ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.go']:
            files = list(project_path.rglob(ext))
            if files:
                lang = ext[2:]
                analysis["languages"].append(lang)
                analysis["file_count"] += len(files)
        
        # Get project structure
        prompt = f"""Analyze this project structure and provide insights:
Project: {project_path.name}
Languages: {', '.join(analysis['languages'])}
Files: {analysis['file_count']}

Provide:
1. Architecture assessment
2. Best practices check
3. Improvement suggestions
4. Security considerations"""
        
        insights = await self.osa.accomplish_task(prompt)
        analysis["insights"] = insights
        
        return analysis
    
    async def create_project(self, project_type: str, name: str, path: Path) -> bool:
        """Create a new project with boilerplate."""
        project_templates = {
            "python-api": {
                "files": ["app.py", "requirements.txt", "README.md", ".gitignore"],
                "structure": ["src", "tests", "docs"]
            },
            "react-app": {
                "files": ["package.json", "README.md", ".gitignore"],
                "structure": ["src", "public", "tests"]
            },
            "cli-tool": {
                "files": ["main.py", "setup.py", "README.md"],
                "structure": ["src", "tests", "docs"]
            }
        }
        
        if project_type not in project_templates:
            return False
        
        # Create project directory
        project_dir = path / name
        project_dir.mkdir(exist_ok=True)
        
        # Create structure
        template = project_templates[project_type]
        for folder in template["structure"]:
            (project_dir / folder).mkdir(exist_ok=True)
        
        # Generate files with OSA
        for file in template["files"]:
            prompt = f"Generate content for {file} in a {project_type} project named {name}"
            content = await self.osa.accomplish_task(prompt)
            
            with open(project_dir / file, 'w') as f:
                f.write(content)
        
        return True
    
    async def debug_code(self, code: str, issue: str) -> str:
        """Interactive debugging assistance."""
        prompt = f"""Debug this code with the following issue:

Code:
```
{code}
```

Issue: {issue}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Fixed code
4. Explanation of the fix"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def optimize_performance(self, code: str) -> str:
        """Optimize code for performance."""
        prompt = f"""Optimize this code for better performance:

```
{code}
```

Focus on:
1. Time complexity improvements
2. Space complexity improvements
3. Algorithmic optimizations
4. Caching opportunities
5. Parallel processing if applicable"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def generate_documentation(self, code: str, style: str = "markdown") -> str:
        """Generate comprehensive documentation."""
        prompt = f"""Generate comprehensive {style} documentation for this code:

```
{code}
```

Include:
1. Overview
2. Installation/Setup
3. Usage examples
4. API reference
5. Contributing guidelines"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def learn_from_code(self, code: str) -> Dict[str, Any]:
        """Learn patterns and best practices from code."""
        prompt = f"""Analyze this code and extract learning points:

```
{code}
```

Identify:
1. Design patterns used
2. Best practices demonstrated
3. Potential improvements
4. Key concepts illustrated"""
        
        analysis = await self.osa.accomplish_task(prompt)
        
        # Store in learning notes
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "code_sample": code[:200],
            "learnings": analysis
        }
        self.learning_notes.append(learning_entry)
        
        return learning_entry
    
    async def suggest_next_steps(self, current_task: str) -> List[str]:
        """Suggest next steps based on current task."""
        prompt = f"""Based on this current task: {current_task}

Suggest the next 5 logical steps to continue development:"""
        
        suggestions = await self.osa.accomplish_task(prompt)
        return suggestions.split('\n')
    
    async def review_security(self, code: str) -> str:
        """Security review of code."""
        prompt = f"""Perform a security review of this code:

```
{code}
```

Check for:
1. Input validation issues
2. Authentication/authorization problems
3. Data exposure risks
4. Injection vulnerabilities
5. Best practice violations

Provide specific fixes for any issues found."""
        
        return await self.osa.accomplish_task(prompt)
    
    def save_snippet(self, name: str, code: str, language: str = "python"):
        """Save a code snippet for later use."""
        self.code_snippets[name] = {
            "code": code,
            "language": language,
            "saved_at": datetime.now().isoformat()
        }
        
        # Persist to file
        snippets_file = Path.home() / ".osa" / "snippets.json"
        with open(snippets_file, 'w') as f:
            json.dump(self.code_snippets, f, indent=2)
    
    def load_snippet(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a saved code snippet."""
        return self.code_snippets.get(name)
    
    async def translate_code(self, code: str, from_lang: str, to_lang: str) -> str:
        """Translate code between languages."""
        prompt = f"""Translate this {from_lang} code to {to_lang}:

```{from_lang}
{code}
```

Provide:
1. Translated code
2. Language-specific adjustments
3. Notes on differences"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def explain_concept(self, concept: str, level: str = "beginner") -> str:
        """Explain programming concepts at different levels."""
        prompt = f"""Explain {concept} at a {level} level.

Include:
1. Core definition
2. Why it's important
3. Real-world analogy
4. Code example
5. Common use cases"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def generate_regex(self, description: str) -> str:
        """Generate regex from description."""
        prompt = f"""Generate a regex pattern for: {description}

Provide:
1. The regex pattern
2. Explanation of each part
3. Test examples
4. Common variations"""
        
        return await self.osa.accomplish_task(prompt)
    
    async def convert_format(self, data: str, from_format: str, to_format: str) -> str:
        """Convert between data formats (JSON, YAML, XML, etc.)."""
        prompt = f"""Convert this {from_format} to {to_format}:

```
{data}
```

Ensure proper formatting and validity."""
        
        return await self.osa.accomplish_task(prompt)