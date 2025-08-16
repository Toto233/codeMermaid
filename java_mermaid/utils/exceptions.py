"""
Custom exceptions for the Java Mermaid flowchart generator.

Provides specific exception types for different error scenarios.
"""


class JavaMermaidError(Exception):
    """Base exception for Java Mermaid flowchart generator."""
    pass


class JavaParsingError(JavaMermaidError):
    """Raised when Java parsing fails."""
    
    def __init__(self, message: str, line_number: int = None, filename: str = None):
        super().__init__(message)
        self.line_number = line_number
        self.filename = filename
    
    def __str__(self):
        if self.line_number and self.filename:
            return f"{self.args[0]} at line {self.line_number} in {self.filename}"
        return str(self.args[0])


class LLMError(JavaMermaidError):
    """Raised when LLM API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OutputError(JavaMermaidError):
    """Raised when output generation fails."""
    pass


class FileOperationError(JavaMermaidError):
    """Raised when file operations fail."""
    pass


class ValidationError(JavaMermaidError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(JavaMermaidError):
    """Raised when configuration is invalid."""
    pass


class MethodNotFoundError(JavaMermaidError):
    """Raised when specified method is not found."""
    
    def __init__(self, method_name: str, class_name: str, available_methods: list = None):
        message = f"Method '{method_name}' not found in class '{class_name}'"
        if available_methods:
            message += f". Available methods: {', '.join(available_methods)}"
        super().__init__(message)
        self.method_name = method_name
        self.class_name = class_name
        self.available_methods = available_methods


class ClassNotFoundError(JavaMermaidError):
    """Raised when specified class is not found."""
    
    def __init__(self, class_name: str, available_classes: list = None):
        message = f"Class '{class_name}' not found"
        if available_classes:
            message += f". Available classes: {', '.join(available_classes)}"
        super().__init__(message)
        self.class_name = class_name
        self.available_classes = available_classes


class MermaidSyntaxError(JavaMermaidError):
    """Raised when generated Mermaid syntax is invalid."""
    
    def __init__(self, message: str, mermaid_code: str = None):
        super().__init__(message)
        self.mermaid_code = mermaid_code