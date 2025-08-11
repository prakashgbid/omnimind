#!/bin/bash
set -e

echo "🚀 Installing OSA Development Tools..."

# Make sure we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install pre-commit and dev dependencies
echo "📦 Installing development dependencies..."
pip install pre-commit black isort flake8 pylint mypy bandit safety pytest pytest-cov pytest-asyncio

# Install and setup pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Make tools executable
echo "🔧 Making tools executable..."
chmod +x tools/*.py
chmod +x scripts/*.sh

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Run initial quality check
echo "✅ Running initial quality check..."
python tools/quality_checks.py || echo "⚠️ Quality issues found - please review"

# Run dependency check
echo "🔍 Running dependency security check..."
python tools/dependency_check.py || echo "⚠️ Dependency issues found - please review"

echo "🎉 Development tools installed successfully!"
echo ""
echo "📋 Available commands:"
echo "  ./scripts/check-quality.sh     - Run all quality checks"
echo "  ./scripts/run-tests.sh         - Run test suite"
echo "  ./scripts/format-code.sh       - Format code"
echo "  ./scripts/security-scan.sh     - Security scan"
echo "  python tools/quality_checks.py - Custom quality checks"
echo "  python tools/dependency_check.py - Dependency analysis"
echo ""
echo "🔄 Pre-commit hooks are now active for all commits!"