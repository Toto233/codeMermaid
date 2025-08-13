# Technical Design - Mermaid Flowchart Generator

## Architecture Overview

### High-Level Components - Java LLM-Enhanced Version
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Parser    │────│  Java Extractor  │────│  LLM Client    │
│   (click)       │    │ (javalang AST)   │    │  (OpenAI API)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐              │
         └──────────────│  Output Manager  │──────────────┘
                        │  (Conditional)   │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │  File Writer     │
                        │  (Comments/PNG)  │
                        └──────────────────┘
```

### Core Classes - LLM-Enhanced

#### 1. FlowchartGenerator (Main Entry Point)
- **Purpose**: Orchestrates the LLM-powered flowchart generation process
- **Responsibilities**:
  - Coordinate parsing, LLM calls, and conditional output
  - Handle error propagation
  - Manage output control based on CLI flags

#### 2. JavaCodeExtractor
- **Purpose**: Extract Java method context for LLM analysis using javalang
- **Key Methods**:
  - `extract_method_context(filepath: str, class_name: str, method_name: str) -> JavaCodeContext`
  - `get_method_signature(method: javalang.tree.MethodDeclaration) -> str`
  - `get_method_body_with_context(method: javalang.tree.MethodDeclaration) -> str`
  - `parse_java_file(filepath: str) -> javalang.tree.CompilationUnit`

#### 3. LLMClient
- **Purpose**: Interface with OpenAI-compatible API for Mermaid generation
- **Key Methods**:
  - `generate_flowchart(code_context: CodeContext, prompt_template: str) -> str`
  - `validate_mermaid_syntax(mermaid_code: str) -> bool`
  - `handle_api_errors(error: Exception) -> str`

## Java-Specific LLM Prompt Engineering

### Java Method Context Template
```python
JAVA_METHOD_PROMPT = """
Analyze this Java method and generate a Mermaid flowchart.

Class: {class_name}
Method: {method_name}
Signature: {method_signature}
Return Type: {return_type}
Parameters: {parameters}

Source code:
{method_body}

Important Java constructs to include:
1. if/else if/else statements
2. for/while/do-while loops
3. try/catch/finally blocks
4. switch statements
5. return statements
6. exception handling paths
7. method calls (show as process boxes)

Generate a flowchart TD diagram that shows all possible execution paths.
Use appropriate shapes:
- Rectangle [Process] for operations
- Diamond {Decision} for conditions
- Circle ((Start/End)) for flow control
- Parallelogram [/Input/Output\] for I/O operations

Include Java-specific elements:
- Exception handling paths
- Stream operations (.map(), .filter(), etc.)
- Lambda expressions
- Generic type flows
- Resource management (try-with-resources)

Return only valid Mermaid syntax, no explanations.
"""
```

#### 4. OutputManager
- **Purpose**: Control what gets generated based on CLI flags
- **Key Methods**:
  - `should_generate_comments() -> bool`
  - `should_generate_images() -> bool`
  - `apply_output_config(flags: Dict[str, bool])`

#### 5. FileWriter
- **Purpose**: Handle file operations conditionally
- **Key Methods**:
  - `write_comments_if_enabled(comments: str, target_file: str)`
  - `write_png_if_enabled(mermaid_code: str, output_path: str)`
  - `cleanup_on_error()`

## Data Flow - Java LLM-Enhanced

### 1. Input Processing
```python
# CLI Input with output flags
class_name, method_name, flags = parse_cli_args()
source_file = locate_java_file()
```

### 2. Java Parsing
```python
# Java AST Extraction with javalang
tree = javalang.parse.parse(source_code)
class_node = find_java_class(tree, class_name)
method_node = find_java_method(class_node, method_name)
```

### 3. LLM Context Preparation
```python
# Java method context for LLM
context = {
    'class_name': class_name,
    'method_name': method_name,
    'signature': extract_java_signature(method_node),
    'body': extract_java_body(method_node),
    'imports': get_java_imports(tree),
    'fields': get_class_fields(class_node)
}
```

### 4. LLM Mermaid Generation
```python
# OpenAI API call
prompt = build_llm_prompt(context)
mermaid_code = llm_client.generate_flowchart(prompt)
```

### 5. Conditional Output
```python
# Output control based on flags
if output_manager.should_generate_comments():
    write_java_comments(mermaid_code, target_file)

if output_manager.should_generate_images():
    render_mermaid_to_png(mermaid_code, output_path)
```

## Error Handling Strategy

### 1. Parse Errors
- **SyntaxError**: Catch and report with line numbers
- **ImportError**: Handle missing dependencies gracefully
- **FileNotFoundError**: Provide helpful error messages

### 2. AST Analysis Errors
- **AttributeError**: Handle missing AST nodes
- **ValueError**: Validate method/class names
- **TypeError**: Ensure correct AST node types

### 3. Rendering Errors
- **MermaidError**: Handle Mermaid syntax issues
- **ImageError**: Manage PNG generation failures
- **PermissionError**: Handle file system issues

## Extension Points

### 1. New Node Types
- Add visitor pattern for new AST nodes
- Extend MermaidBuilder with new shapes
- Implement custom rendering for specific patterns

### 2. Output Formats
- SVG generation
- PDF export
- Interactive HTML

### 3. Custom Styling
- Theme configuration
- Custom node styles
- Color schemes

## Testing Strategy

### 1. Unit Tests
- AST parsing accuracy
- Flow extraction correctness
- Mermaid syntax validation
- PNG generation quality

### 2. Integration Tests
- End-to-end workflow
- CLI argument handling
- File I/O operations
- Error scenarios

### 3. Performance Tests
- Large method parsing
- Memory usage monitoring
- Timing benchmarks

## Deployment

### 1. Package Structure
- Single executable with dependencies
- Cross-platform compatibility
- Virtual environment support

### 2. Distribution
- PyPI package
- Docker container
- Standalone executable