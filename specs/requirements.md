# Requirements Specification - Java Mermaid Flowchart Generator

## Functional Requirements

### FR1: Java Class and Method Identification
- **Requirement**: The tool shall accept a Java class and method name as input
- **Acceptance Criteria**:
  - CLI argument parsing for Java class name and method name
  - Validation that Java class exists in specified .java file
  - Validation that method exists in the Java class
  - Support for nested classes and interfaces
  - Error handling for invalid input

### FR2: Java Source Code Parsing
- **Requirement**: The tool shall parse Java source code using javalang library
- **Acceptance Criteria**:
  - Support Java 8+ language features including generics, streams, lambdas
  - Handle Java annotations and modifiers
  - Process try-with-resources and exception handling
  - Extract method signatures and bodies accurately
  - Support package and import statements

### FR3: Java LLM Analysis
- **Requirement**: The tool shall use LLM (OpenAI-compatible) to analyze Java method logic
- **Acceptance Criteria**:
  - Send Java method context to LLM API
  - Receive valid Mermaid flowchart syntax from LLM
  - Handle LLM API rate limits and timeouts
  - Validate Mermaid syntax from LLM response
  - Support configurable LLM endpoints

### FR4: Output Control Flags
- **Requirement**: The tool shall support CLI flags to control output generation
- **Acceptance Criteria**:
  - `--pic-off` flag to disable PNG image generation
  - `--doc-off` flag to disable JavaDoc comment insertion
  - `--comments-off` flag to disable method comments entirely
  - `--output-dir` to specify custom output directory
  - Default behavior: generate both PNG and comments

### FR5: PNG Image Generation
- **Requirement**: The tool shall create PNG images from Mermaid diagrams
- **Acceptance Criteria**:
  - Generate PNG files with naming format `ClassName_methodName.png`
  - Support configurable output directory
  - Handle resolution and sizing options
  - Ensure readable font sizes and spacing
  - Handle long method names gracefully
  - Skip generation when `--pic-off` flag is used

### FR6: JavaDoc Comment Generation
- **Requirement**: The tool shall insert Mermaid diagrams as JavaDoc comments above methods
- **Acceptance Criteria**:
  - Insert JavaDoc comments in correct location (before method definition)
  - Use proper JavaDoc syntax with @mermaid tag
  - Include Mermaid diagram syntax in comments
  - Preserve existing JavaDoc and comments
  - Handle Java method indentation correctly
  - Skip generation when `--doc-off` flag is used

### FR7: LLM Integration
- **Requirement**: The tool shall integrate with OpenAI-compatible APIs
- **Acceptance Criteria**:
  - Support custom API endpoints (e.g., internal LLM services)
  - Configurable API keys and authentication
  - Handle API rate limits and retry logic
  - Provide meaningful error messages for API failures
  - Support model selection (e.g., gpt-3.5-turbo, gpt-4)

## Non-Functional Requirements

### NFR1: Performance (Python 3.6)
- **Requirement**: The tool shall process Java methods efficiently on Python 3.6
- **Acceptance Criteria**:
  - Parse 1000-line Java method in under 2 seconds
  - LLM API call timeout: 30 seconds max
  - Memory usage under 150MB for Java parsing + LLM
  - Support batch processing with rate limiting

### NFR2: Reliability
- **Requirement**: The tool shall handle errors gracefully
- **Acceptance Criteria**:
  - Zero crashes on malformed Java code
  - Informative error messages with Java line numbers
  - Graceful fallback if LLM API unavailable
  - Comprehensive logging for debugging

### NFR3: Compatibility
- **Requirement**: The tool shall work across platforms with Python 3.6
- **Acceptance Criteria**:
  - Support Windows, macOS, and Linux with Python 3.6+
  - Java 8+ compatibility
  - No platform-specific dependencies
  - Cross-platform file path handling

### NFR4: Usability
- **Requirement**: The tool shall be easy to use with clear CLI interface
- **Acceptance Criteria**:
  - Clear CLI help messages for all flags
  - Intuitive command structure
  - Comprehensive documentation with examples
  - Colored terminal output for better UX

### NFR5: LLM Configuration
- **Requirement**: The tool shall support flexible LLM configuration
- **Acceptance Criteria**:
  - Environment variable configuration for API keys
  - Config file support for LLM settings
  - Command-line override for API endpoints
  - Model parameter customization

## User Stories

### US1: Java Basic Flowchart Generation
**As a** Java developer
**I want to** generate a flowchart for a simple Java method
**So that** I can visualize the control flow

**Scenario**: Simple Java method with if-else
- Given a Java method with conditional logic
- When I run the tool with class and method names
- Then I get a PNG flowchart and JavaDoc comments with Mermaid diagrams

### US2: Java Complex Method Handling
**As a** senior Java developer
**I want to** generate flowcharts for complex Java methods
**So that** I can understand and document intricate logic

**Scenario**: Nested loops and exception handling
- Given a Java method with try-catch and loops
- When I process the method with LLM
- Then I get a readable flowchart showing all exception paths

### US3: Output Control
**As a** DevOps engineer
**I want to** control what gets generated
**So that** I can integrate in CI/CD pipelines efficiently

**Scenario**: Generate only PNG images
- Given a Java source file
- When I use `--doc-off` flag
- Then only PNG images are generated, no JavaDoc comments

### US4: Internal LLM Integration
**As a** enterprise developer
**I want to** use our internal LLM service
**So that** data stays within our network

**Scenario**: Custom LLM endpoint
- Given an internal OpenAI-compatible API
- When I configure the tool with custom endpoint
- Then it uses our internal LLM for Mermaid generation

## Edge Cases and Error Handling

### EC1: Java Syntax Errors
- **Scenario**: Invalid Java syntax in source file
- **Expected Behavior**: Clear error message with Java line number
- **Recovery**: Stop processing and report error

### EC2: Missing Java Methods
- **Scenario**: Specified Java method doesn't exist
- **Expected Behavior**: Informative error with available methods
- **Recovery**: List valid Java methods and exit gracefully

### EC3: LLM API Failures
- **Scenario**: LLM API timeout or rate limit
- **Expected Behavior**: Graceful fallback with helpful message
- **Recovery**: Retry with exponential backoff, then skip

### EC4: Long Java Method Names
- **Scenario**: Java method name exceeds file system limits
- **Expected Behavior**: Truncate with hash for uniqueness
- **Recovery**: Generate file with shortened name

### EC5: Java Generics Complexity
- **Scenario**: Complex generic type parameters
- **Expected Behavior**: Simplified flowchart representation
- **Recovery**: Focus on control flow, ignore type complexity

## CLI Flags Specification

### Flag Definitions
```
--pic-off           Disable PNG image generation
--doc-off           Disable JavaDoc comment insertion
--comments-off      Disable all comment generation
--output-dir DIR    Specify custom output directory
--api-endpoint URL  Custom LLM API endpoint
--model MODEL       LLM model to use
--config FILE       Load configuration from file
--verbose           Enable verbose logging
--dry-run           Show what would be generated without changes
```

### Usage Examples
```bash
# Generate both PNG and JavaDoc comments
java-mermaid MyClass myMethod MyFile.java

# Generate only PNG images
java-mermaid MyClass myMethod MyFile.java --doc-off

# Generate only JavaDoc comments
java-mermaid MyClass myMethod MyFile.java --pic-off

# Use custom LLM endpoint
java-mermaid MyClass myMethod MyFile.java --api-endpoint https://internal-llm.local

# Specify output directory
java-mermaid MyClass myMethod MyFile.java --output-dir ./docs/flowcharts/
```

## Configuration Requirements

### CR1: LLM Configuration
- **Requirement**: Configurable LLM settings
- **Options**: API endpoint, model, timeout, retries
- **Default**: OpenAI GPT-3.5-turbo

### CR2: Output Control
- **Requirement**: Configurable output generation
- **Options**: Enable/disable PNG, JavaDoc, comments
- **Default**: Generate both PNG and JavaDoc

### CR3: Image Settings
- **Requirement**: Configurable PNG generation
- **Options**: Resolution, theme, font size
- **Default**: Medium resolution, default theme

### CR4: Java Processing
- **Requirement**: Configurable Java parsing
- **Options**: Encoding, classpath, source version
- **Default**: UTF-8 encoding, Java 8+

## Validation Criteria

### V1: Java Input Validation
- [ ] Valid Java syntax with javalang
- [ ] Existing Java class and method names
- [ ] Readable .java source files
- [ ] Proper file permissions

### V2: LLM Output Validation
- [ ] Valid Mermaid syntax from LLM
- [ ] Complete control flow coverage
- [ ] Readable PNG images
- [ ] Correct JavaDoc formatting

### V3: Flag Handling
- [ ] Correct flag parsing
- [ ] Proper output control
- [ ] Helpful error messages
- [ ] Comprehensive CLI help

### V4: Performance
- [ ] Meets Python 3.6 timing requirements
- [ ] LLM timeout handling
- [ ] Memory usage within limits
- [ ] Efficient resource usage