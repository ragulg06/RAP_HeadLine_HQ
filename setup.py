"""
Setup script for RAP IQ - AI News Intelligence Platform
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="rap-iq",
    version="1.0.0",
    author="RAP IQ Team",
    author_email="support@rap-iq.com",
    description="AI News Intelligence Platform with multi-source crawling and conversational AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rap-iq",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "accelerate>=0.20.0",
            "bitsandbytes>=0.41.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rap-iq=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords=[
        "ai", "news", "intelligence", "nlp", "machine-learning",
        "financial", "business", "crawling", "analysis", "chatbot"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/rap-iq/issues",
        "Source": "https://github.com/yourusername/rap-iq",
        "Documentation": "https://github.com/yourusername/rap-iq/wiki",
    },
) 