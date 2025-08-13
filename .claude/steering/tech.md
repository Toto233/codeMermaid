# Technical Stack - Java Mermaid Flowchart Generator

## Core Technologies
- **Python 3.6**: Primary language for tool development (legacy compatibility)
- **JavaParser**: Java source code parsing and AST analysis
- **Mermaid**: Diagramming and charting library for flowcharts

## Dependencies (Python 3.6 Compatible)
- **click==7.1.2**: CLI interface and argument parsing
- **javalang==0.13.1**: Java parser for AST analysis
- **requests==2.25.1**: HTTP client for LLM API calls
- **Pillow==8.4.0**: Image processing and PNG generation
- **colorama==0.4.4**: Cross-platform colored terminal output
- **pytest==6.2.5**: Testing framework
- **typing-extensions==3.10.0.2**: Backported type hints for Python 3.6

## Architecture Components
- **JavaParser**: Java source code parsing and AST analysis
- **LLM Client**: OpenAI-compatible API integration for Mermaid generation
- **Image Renderer**: PNG generation from Mermaid
- **CLI Interface**: Command-line argument handling with output control
- **File Manager**: Java source file operations

## Technical Constraints - Python 3.6/Java
- Python 3.6 syntax and library compatibility
- Support Java 8+ language features
- Handle Java generics, streams, lambdas
- Process methods with up to 2000 LOC (LLM limits)
- Generate readable flowcharts for complex Java logic
- Zero external dependencies beyond specified packages

## Performance Requirements - Python 3.6/Java
- Java parsing in under 1 second for typical methods
- LLM API call timeout: 30 seconds max
- Memory usage under 150MB for Java parsing + LLM
- Cross-platform compatibility (Windows, Linux, macOS)

## Error Handling
- Java syntax error handling with line numbers
- LLM API failure recovery
- Fallback to rule-based generation if LLM unavailable
- File encoding detection for Java source files