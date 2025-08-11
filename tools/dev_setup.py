#!/usr/bin/env python3
"""
Development environment setup script for OSA project.

This script automates the setup of development tools, pre-commit hooks,
and other quality assurance tools.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


class DevEnvironmentSetup:
    """Setup development environment with all quality tools."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.venv_path = self.project_root / "venv"
        
    def setup(self) -> None:
        """Run complete development environment setup."""
        print("🚀 Setting up OSA development environment...")
        print(f"📁 Project root: {self.project_root}")
        
        steps = [
            ("🐍 Setting up Python virtual environment", self.setup_venv),
            ("📦 Installing dependencies", self.install_dependencies),
            ("🔧 Installing development tools", self.install_dev_tools),
            ("🪝 Setting up pre-commit hooks", self.setup_pre_commit),
            ("🔒 Configuring security tools", self.setup_security_tools),
            ("🧪 Setting up testing framework", self.setup_testing),
            ("📊 Configuring quality tools", self.setup_quality_tools),
            ("📝 Creating development scripts", self.create_dev_scripts),
        ]
        
        for description, step_func in steps:
            print(f"\n{description}...")
            try:
                step_func()
                print("✅ Complete")
            except Exception as e:
                print(f"❌ Failed: {e}")
                if input("Continue anyway? (y/N): ").lower() != 'y':
                    sys.exit(1)
        
        print(f"\n🎉 Development environment setup complete!")
        print(f"\n📋 Next steps:")
        print(f"1. Activate virtual environment: source venv/bin/activate")
        print(f"2. Run quality checks: ./scripts/check-quality.sh")
        print(f"3. Run tests: pytest")
        print(f"4. Start coding! 🚀")
    
    def setup_venv(self) -> None:
        """Create and setup Python virtual environment."""
        if self.venv_path.exists():
            print("   Virtual environment already exists")
            return
        
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        
        # Activate and upgrade pip
        pip_cmd = self.get_pip_command()
        subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=True)
    
    def install_dependencies(self) -> None:
        """Install project dependencies."""
        pip_cmd = self.get_pip_command()
        
        # Install main dependencies
        if (self.project_root / "requirements.txt").exists():
            subprocess.run([*pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        # Install from pyproject.toml if it exists
        if (self.project_root / "pyproject.toml").exists():
            subprocess.run([*pip_cmd, "install", "-e", "."], check=True)
    
    def install_dev_tools(self) -> None:
        """Install development tools."""
        pip_cmd = self.get_pip_command()
        
        dev_tools = [
            # Code formatting
            "black>=24.1.1",
            "isort>=5.13.2",
            
            # Linting
            "flake8>=7.0.0",
            "pylint>=3.0.3",
            "mypy>=1.8.0",
            
            # Security
            "bandit>=1.7.6",
            "safety>=3.0.0",
            
            # Testing
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-xdist>=3.5.0",
            "pytest-benchmark>=4.0.0",
            
            # Pre-commit
            "pre-commit>=3.6.0",
            
            # Documentation
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            
            # Utilities
            "ipython>=8.18.0",
            "rich>=13.7.0",
        ]
        
        print(f"   Installing {len(dev_tools)} development tools...")
        subprocess.run([*pip_cmd, "install"] + dev_tools, check=True)
    
    def setup_pre_commit(self) -> None:
        """Setup pre-commit hooks."""
        if not (self.project_root / ".pre-commit-config.yaml").exists():
            print("   .pre-commit-config.yaml not found, skipping")
            return
        
        pre_commit_cmd = self.get_command("pre-commit")
        subprocess.run([*pre_commit_cmd, "install"], cwd=self.project_root, check=True)
        subprocess.run([*pre_commit_cmd, "install", "--hook-type", "commit-msg"], 
                      cwd=self.project_root, check=True)
    
    def setup_security_tools(self) -> None:
        """Setup security scanning tools."""
        # Initialize secrets baseline
        if not (self.project_root / ".secrets.baseline").exists():
            detect_secrets = self.get_command("detect-secrets")
            subprocess.run([
                *detect_secrets, "scan", "--baseline", ".secrets.baseline"
            ], cwd=self.project_root, check=True)
        
        # Create bandit config if it doesn't exist
        if not (self.project_root / ".bandit").exists():
            print("   Bandit config already created")
    
    def setup_testing(self) -> None:
        """Setup testing framework."""
        # Create test directories
        test_dirs = [
            "tests",
            "tests/unit",
            "tests/integration", 
            "tests/performance",
            "tests/security"
        ]
        
        for test_dir in test_dirs:
            (self.project_root / test_dir).mkdir(parents=True, exist_ok=True)
            init_file = self.project_root / test_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
        
        # Ensure conftest.py exists
        if not (self.project_root / "tests" / "conftest.py").exists():
            print("   conftest.py already created")
    
    def setup_quality_tools(self) -> None:
        """Setup code quality tools."""
        tools_dir = self.project_root / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        # Make tools executable
        for tool_file in tools_dir.glob("*.py"):
            os.chmod(tool_file, 0o755)
    
    def create_dev_scripts(self) -> None:
        """Create development scripts."""
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        scripts = {
            "check-quality.sh": self.get_quality_check_script(),
            "run-tests.sh": self.get_test_script(),
            "format-code.sh": self.get_format_script(),
            "security-scan.sh": self.get_security_script(),
            "dev-server.sh": self.get_dev_server_script(),
        }
        
        for script_name, script_content in scripts.items():
            script_path = scripts_dir / script_name
            script_path.write_text(script_content)
            os.chmod(script_path, 0o755)
    
    def get_pip_command(self) -> List[str]:
        """Get pip command for virtual environment."""
        if os.name == 'nt':  # Windows
            return [str(self.venv_path / "Scripts" / "pip")]
        else:  # Unix/Linux/macOS
            return [str(self.venv_path / "bin" / "pip")]
    
    def get_command(self, command: str) -> List[str]:
        """Get command for virtual environment."""
        if os.name == 'nt':  # Windows
            return [str(self.venv_path / "Scripts" / command)]
        else:  # Unix/Linux/macOS
            return [str(self.venv_path / "bin" / command)]
    
    def get_quality_check_script(self) -> str:
        """Generate quality check script."""
        return '''#!/bin/bash
set -e

echo "🔍 Running code quality checks..."

echo "🎨 Checking code formatting..."
black --check .
isort --check-only .

echo "🔍 Running linters..."
flake8 src/ tests/
pylint src/ --fail-under=8.0

echo "🔒 Running security checks..."
bandit -r src/
safety check

echo "🧪 Running custom quality checks..."
python tools/quality_checks.py

echo "✅ All quality checks passed!"
'''
    
    def get_test_script(self) -> str:
        """Generate test script."""
        return '''#!/bin/bash
set -e

echo "🧪 Running tests..."

# Run unit tests with coverage
echo "📊 Unit tests with coverage..."
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

# Run integration tests
echo "🔗 Integration tests..."
pytest tests/integration/ -v --maxfail=5

# Run performance tests
echo "⚡ Performance tests..."
pytest tests/performance/ -v --benchmark-only

# Run security tests
echo "🔒 Security tests..."
pytest tests/security/ -v

echo "✅ All tests passed!"
'''
    
    def get_format_script(self) -> str:
        """Generate code formatting script."""
        return '''#!/bin/bash
set -e

echo "🎨 Formatting code..."

echo "📦 Sorting imports..."
isort .

echo "🖤 Formatting with Black..."
black .

echo "✅ Code formatting complete!"
'''
    
    def get_security_script(self) -> str:
        """Generate security scanning script."""
        return '''#!/bin/bash
set -e

echo "🔒 Running security scans..."

echo "🕵️ Scanning for secrets..."
detect-secrets scan --baseline .secrets.baseline

echo "🛡️ Analyzing code security..."
bandit -r src/ -f json -o bandit-report.json

echo "🔍 Checking dependencies..."
safety check --json --output safety-report.json

echo "📋 Running custom dependency checks..."
python tools/dependency_check.py

echo "✅ Security scan complete!"
'''
    
    def get_dev_server_script(self) -> str:
        """Generate development server script."""
        return '''#!/bin/bash
set -e

echo "🚀 Starting OSA development environment..."

# Start WebSocket logger in background
echo "📡 Starting WebSocket logger..."
python src/osa_logger.py &
LOGGER_PID=$!

# Start web UI in background
echo "🌐 Starting web interface..."
cd web && python -m http.server 8080 &
WEB_PID=$!

# Start main OSA
echo "🧠 Starting OSA..."
python run_complete_osa.py

# Cleanup on exit
trap 'kill $LOGGER_PID $WEB_PID' EXIT
'''


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup OSA development environment")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    args = parser.parse_args()
    
    setup = DevEnvironmentSetup(args.project_root)
    setup.setup()


if __name__ == "__main__":
    main()