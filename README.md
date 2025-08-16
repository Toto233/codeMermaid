# Java Mermaid Flowchart Generator

Generate Mermaid flowcharts from Java methods using LLM analysis. This tool analyzes Java source code and creates visual flowcharts that represent the control flow of methods.

## Features

- **🔍 Java Source Analysis**: Uses javalang to parse Java 8+ source code
- **🤖 LLM Integration**: Leverages OpenAI-compatible APIs for intelligent flowchart generation
- **📊 Mermaid Diagrams**: Creates standard Mermaid flowchart syntax
- **🖼️ PNG Generation**: Produces PNG images from Mermaid diagrams
- **📝 JavaDoc Integration**: Inserts Mermaid diagrams as JavaDoc comments
- **⚙️ Configurable Output**: Control what gets generated via CLI flags
- **🔧 Flexible Configuration**: Support for custom LLM endpoints and models

## Installation

### Prerequisites

- Python 3.6 or higher
- Java source files (.java)
- OpenAI API key or compatible LLM service

### Install via pip

```bash
pip install java-mermaid-flowchart
```

### Install from source

```bash
git clone https://github.com/java-mermaid/flowchart-generator.git
cd flowchart-generator
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Generate both PNG and JavaDoc comments
java-mermaid MyClass myMethod MyFile.java

# Generate only PNG images
java-mermaid MyClass myMethod MyFile.java --doc-off

# Generate only JavaDoc comments
java-mermaid MyClass myMethod MyFile.java --pic-off

# Use custom output directory
java-mermaid MyClass myMethod MyFile.java --output-dir ./docs/
```

### Environment Setup

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
# or
export JAVA_MERMAID_API_KEY="your-api-key-here"
```

## Command Line Interface

### Usage

```bash
java-mermaid [OPTIONS] CLASS_NAME METHOD_NAME JAVA_FILE
```

### Arguments

- `CLASS_NAME`: Name of the Java class containing the method
- `METHOD_NAME`: Name of the Java method to analyze
- `JAVA_FILE`: Path to the Java source file

### Options

| Option | Description |
|--------|-------------|
| `--pic-off` | Disable PNG image generation |
| `--doc-off` | Disable JavaDoc comment insertion |
| `--comments-off` | Disable all comment generation |
| `--output-dir DIR` | Specify custom output directory (default: current directory) |
| `--api-key KEY` | OpenAI API key or compatible API key |
| `--api-endpoint URL` | Custom LLM API endpoint (default: https://api.openai.com/v1) |
| `--model MODEL` | LLM model to use (default: gpt-3.5-turbo) |
| `--config FILE` | Load configuration from JSON file |
| `--verbose` | Enable verbose logging |
| `--dry-run` | Show what would be generated without making changes |

### Examples

```bash
# Basic usage
java-mermaid Calculator add Calculator.java

# Generate only PNG images
java-mermaid Calculator add Calculator.java --doc-off

# Use custom LLM endpoint
java-mermaid Calculator add Calculator.java 
  --api-endpoint https://internal-llm.local 
  --model gpt-4

# Custom output directory with verbose logging
java-mermaid Calculator add Calculator.java 
  --output-dir ./flowcharts/ 
  --verbose

# Configuration file usage
java-mermaid Calculator add Calculator.java 
  --config config.json
```

## Configuration

### Configuration File

Create a `config.json` file:

```json
{
  "api_key": "your-api-key",
  "api_endpoint": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo",
  "timeout": 30,
  "max_retries": 3,
  "output_dir": "./mermaid-output/",
  "generate_png": true,
  "generate_comments": true,
  "generate_javadoc": true,
  "theme": "default",
  "width": 1200,
  "height": 800
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `JAVA_MERMAID_API_KEY` | API key for LLM service |
| `JAVA_MERMAID_API_ENDPOINT` | Custom API endpoint |
| `JAVA_MERMAID_MODEL` | LLM model name |
| `JAVA_MERMAID_TIMEOUT` | Request timeout in seconds |
| `JAVA_MERMAID_OUTPUT_DIR` | Default output directory |
| `OPENAI_API_KEY` | Standard OpenAI API key |

## Supported Java Features

### Language Constructs

- **Control Flow**: if/else, switch, loops (for, while, do-while)
- **Exception Handling**: try/catch/finally blocks
- **Method Calls**: Including method chaining and lambda expressions
- **Streams**: Java 8+ Stream API operations
- **Generics**: Type parameters and generic methods
- **Annotations**: Method and parameter annotations
- **Modifiers**: public, private, protected, static, final, etc.

### Code Elements

- Method signatures and parameters
- Return types and values
- Local variables and assignments
- Exception handling paths
- Resource management (try-with-resources)
- Thread synchronization
- I/O operations

## Output Formats

### PNG Images

Generated PNG files include:
- Visual flowchart representation
- Method signature as title
- Color-coded nodes (start/end, processes, decisions)
- Arrow connections showing flow direction

### JavaDoc Comments

Inserted above methods as:

```java
/**
 * Method flowchart visualization.
 *
 * @mermaid
 * ```mermaid
 * flowchart TD
 *     A[Start] --> B{Decision}
 *     B -->|True| C[Process]
 *     C --> D[End]
 *     B -->|False| D
 * ```
 */
public void myMethod() {
    // method implementation
}
```

## Advanced Usage

### Custom LLM Integration

For internal LLM services:

```bash
java-mermaid MyClass myMethod MyFile.java 
  --api-endpoint https://internal-llm.company.com/v1 
  --model custom-model-name
```

### Batch Processing

Process multiple methods:

```bash
# Using shell script
for method in method1 method2 method3; do
    java-mermaid MyClass $method MyFile.java --output-dir ./docs/
done

# Using configuration file
java-mermaid MyClass method1 MyFile.java 
  --config batch-config.json
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Generate Flowcharts
  run: |
    pip install java-mermaid-flowchart
    java-mermaid MyClass processData MyFile.java 
      --api-key ${{ secrets.OPENAI_API_KEY }} 
      --output-dir ./docs/flowcharts/ 
      --doc-off  # Only generate PNGs for CI
```

## Troubleshooting

### Common Issues

#### API Key Required
```
Error: API key is required
```
**Solution**: Set `OPENAI_API_KEY` environment variable or use `--api-key` flag.

#### Java File Not Found
```
Error: Java file 'MyFile.java' does not exist
```
**Solution**: Check file path and ensure file exists.

#### Class Not Found
```
Error: Class 'MyClass' not found. Available classes: [ActualClass1, ActualClass2]
```
**Solution**: Use exact class name from the Java file.

#### Method Not Found
```
Error: Method 'myMethod' not found in class 'MyClass'
```
**Solution**: Check method name spelling and ensure method exists in the class.

### Performance Tips

- **Large Methods**: Consider splitting very large methods (>1000 lines)
- **API Limits**: Use `--dry-run` to test before processing many files
- **PNG Generation**: Disable PNG generation (`--pic-off`) for faster processing
- **Caching**: Results are not cached; consider manual caching for repeated processing

### Debugging

Enable verbose logging:

```bash
java-mermaid MyClass myMethod MyFile.java --verbose
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=java_mermaid --cov-report=html

# Run specific test file
pytest tests/test_java_code_extractor.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/java-mermaid/flowchart-generator.git
cd flowchart-generator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Git Ignore

The `.gitignore` file in this repository ensures that sensitive files and generated artifacts are not committed to version control:

- Configuration files containing API keys (`config.txt`)
- Generated PNG images (`*.png`)
- Generated Mermaid code files (`*.mmd`)
- Python cache and bytecode files
- Node.js dependencies
- Log files
- OS-specific files (`.DS_Store`, `Thumbs.db`)

Always ensure your API keys and credentials are stored in `config.txt` or environment variables, which are excluded from version control.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/java-mermaid/flowchart-generator/issues)
- **Documentation**: [Wiki](https://github.com/java-mermaid/flowchart-generator/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/java-mermaid/flowchart-generator/discussions)

## Changelog

### v1.0.0
- Initial release
- Java source code parsing with javalang
- LLM integration for Mermaid generation
- PNG and JavaDoc output support
- CLI interface with comprehensive options
- Configuration file and environment variable support