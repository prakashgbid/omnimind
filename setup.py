"""Setup script for OmniMind package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="omnimind",
    version="1.0.0",
    author="OmniMind Team",
    description="Human-like Thinking AI System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prakashgbid/omnimind",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "asyncio",
        "aiohttp",
        "httpx",
        "chromadb",
        "networkx",
        "ollama",
        "python-dotenv",
        "pyyaml",
        "numpy",
        "scikit-learn",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock",
            "pytest-benchmark",
        ],
    },
    entry_points={
        "console_scripts": [
            "omnimind=omnimind:main",
        ],
    },
)