"""Setup configuration for persistent-ai-memory."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="persistent-ai-memory",
    version="1.0.0",
    author="OSA Contributors",
    author_email="osa@omnimind.ai",
    description="Persistent memory system for AI agents - never lose context again",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prakashgbid/persistent-ai-memory",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "chromadb>=0.4.22",
        "sentence-transformers>=2.3.1",
        "numpy>=1.24.0",
        "sqlite3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-memory=persistent_ai_memory.cli:main",
        ],
    },
    keywords="ai memory persistence context llm agent chromadb vector-database",
    project_urls={
        "Bug Reports": "https://github.com/prakashgbid/persistent-ai-memory/issues",
        "Source": "https://github.com/prakashgbid/persistent-ai-memory",
        "Documentation": "https://persistent-ai-memory.readthedocs.io",
    },
)