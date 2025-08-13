# Project Structure - Mermaid Flowchart Generator

## Directory Layout
```
mermaid-flowchart-generator/
├── src/
│   ├── __init__.py
│   ├── cli.py                 # CLI interface
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── ast_analyzer.py    # AST parsing and analysis
│   │   └── flow_extractor.py  # Control flow extraction
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── mermaid_builder.py # Mermaid syntax generation
│   │   └── renderer.py        # PNG image generation
│   └── utils/
│       ├── __init__.py
│       ├── file_ops.py        # File I/O operations
│       └── logger.py          # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_generator.py
│   └── fixtures/
│       ├── sample_classes.py
│       └── expected_outputs/
├── examples/
│   ├── sample_class.py
│   └── usage_examples.py
├── docs/
│   ├── README.md
│   ├── API.md
│   └── CONTRIBUTING.md
├── requirements.txt
├── setup.py
├── pyproject.toml
└── .gitignore
```

## Naming Conventions
- **Classes**: PascalCase (e.g., `FlowchartGenerator`)
- **Functions/Methods**: snake_case (e.g., `generate_flowchart`)
- **Variables**: snake_case (e.g., `method_name`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_OUTPUT_DIR`)
- **Files**: snake_case.py (e.g., `ast_analyzer.py`)

## Code Organization Principles
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: External dependencies injected for testing
- **Error Boundaries**: Clear error handling at module boundaries
- **Type Safety**: Full type annotations with mypy compliance
- **Test Coverage**: Minimum 80% test coverage for all modules

## Output Structure
```
output/
├── ClassName_method1.png
├── ClassName_method2.png
├── AnotherClass_method1.png
└── mermaid_snippets/
    ├── ClassName_method1.mmd
    └── AnotherClass_method1.mmd
```