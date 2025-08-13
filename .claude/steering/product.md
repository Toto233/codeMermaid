# Product Vision - Java Mermaid Flowchart Generator

## Overview
A Python CLI tool (Python 3.6 compatible) that automatically generates Mermaid flowchart comments and corresponding PNG images from Java method logic.

## Target Users
- Python developers who want visual documentation
- Development teams needing automated code visualization
- Technical writers creating documentation
- Students learning programming concepts

## Core Features
- Parse Python class methods and extract control flow logic
- Generate Mermaid flowchart syntax as method comments
- Create PNG images of flowcharts with naming format `ClassName_methodName.png`
- CLI interface for processing single classes or entire modules
- Configurable output directory and styling options

## Business Goals
- Reduce manual documentation effort by 80%
- Improve code understanding for new team members
- Enable automated documentation generation in CI/CD pipelines
- Support educational use cases for programming concepts

## Success Metrics
- Successfully parses 95% of Python methods
- Generates readable flowcharts for complex logic
- Processes files within 2 seconds for typical class sizes
- Zero crashes on malformed or edge-case code