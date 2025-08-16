#!/usr/bin/env python3
"""
Setup script for Java Mermaid Flowchart Generator.
"""

import os
import sys
from setuptools import setup, find_packages

# Ensure Python 3.6+
if sys.version_info < (3, 6):
    sys.exit('Python 3.6 or higher is required.')

# Read README file
def read_file(filename):
    """Read file contents."""
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='java-mermaid-flowchart',
    version='1.0.0',
    description='Generate Mermaid flowcharts from Java methods using LLM analysis',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Java Mermaid Team',
    author_email='team@javamermaid.com',
    url='https://github.com/java-mermaid/flowchart-generator',
    
    packages=find_packages(),
    include_package_data=True,
    
    python_requires='>=3.6',
    
    install_requires=read_requirements('requirements.txt'),
    
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'pytest-cov>=3.0.0',
            'black>=22.8.0',
            'flake8>=4.0.1',
        ]
    },
    
    entry_points={
        'console_scripts': [
            'java-mermaid=java_mermaid.__main__:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Code Generators',
    ],
    
    keywords='java mermaid flowchart documentation llm ai',
    
    project_urls={
        'Bug Reports': 'https://github.com/java-mermaid/flowchart-generator/issues',
        'Source': 'https://github.com/java-mermaid/flowchart-generator',
        'Documentation': 'https://github.com/java-mermaid/flowchart-generator/blob/main/README.md',
    },
)