"""
Java Code Extractor for parsing Java source code and extracting method context.

Uses the javalang library to parse Java AST and extract method information.
"""

import os
import re
from typing import Dict, Any, Optional, List
import javalang
from javalang.tree import CompilationUnit, ClassDeclaration, MethodDeclaration


class JavaCodeContext:
    """Data structure for holding Java method context information."""
    
    def __init__(
        self,
        class_name: str,
        method_name: str,
        method_signature: str,
        return_type: str,
        parameters: List[Dict[str, str]],
        method_body: str,
        imports: List[str],
        class_fields: List[Dict[str, str]],
        annotations: List[str],
        modifiers: List[str]
    ):
        self.class_name = class_name
        self.method_name = method_name
        self.method_signature = method_signature
        self.return_type = return_type
        self.parameters = parameters
        self.method_body = method_body
        self.imports = imports
        self.class_fields = class_fields
        self.annotations = annotations
        self.modifiers = modifiers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for LLM processing."""
        return {
            'class_name': self.class_name,
            'method_name': self.method_name,
            'method_signature': self.method_signature,
            'return_type': self.return_type,
            'parameters': self.parameters,
            'method_body': self.method_body,
            'imports': self.imports,
            'class_fields': self.class_fields,
            'annotations': self.annotations,
            'modifiers': self.modifiers
        }
    
    def __str__(self) -> str:
        return f"{self.class_name}.{self.method_name}()"


class JavaCodeExtractor:
    """
    Extracts Java method context for LLM analysis using javalang AST.
    
    Provides methods to parse Java source files and extract comprehensive
    method information including signatures, bodies, and contextual details.
    """
    
    def __init__(self):
        """Initialize the Java code extractor."""
        pass
    
    def extract_method_context(
        self,
        filepath: str,
        class_name: str,
        method_name: str
    ) -> Optional[JavaCodeContext]:
        """
        Extract comprehensive context for a Java method.
        
        Args:
            filepath: Path to the Java source file
            class_name: Name of the Java class
            method_name: Name of the Java method
            
        Returns:
            JavaCodeContext with method information, or None if method not found
            
        Raises:
            FileNotFoundError: If the Java file doesn't exist
            javalang.parser.JavaSyntaxError: If Java syntax is invalid
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Java file not found: {filepath}")
        
        # Parse the Java file
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            tree = javalang.parse.parse(source_code)
        except javalang.parser.JavaSyntaxError as e:
            raise javalang.parser.JavaSyntaxError(
                f"Invalid Java syntax in {filepath}: {str(e)}"
            )
        
        # Find the target class
        class_node = self._find_class(tree, class_name)
        if not class_node:
            available_classes = self._get_available_classes(tree)
            raise ValueError(
                f"Class '{class_name}' not found. Available classes: {available_classes}"
            )
        
        # Find the target method
        method_node = self._find_method(class_node, method_name)
        if not method_node:
            available_methods = self._get_available_methods(class_node)
            raise ValueError(
                f"Method '{method_name}' not found in class '{class_name}'. "
                f"Available methods: {available_methods}"
            )
        
        # Extract method information
        method_signature = self._get_method_signature(method_node)
        return_type = self._get_return_type(method_node)
        parameters = self._get_parameters(method_node)
        method_body = self._get_method_body(method_node, source_code)
        imports = self._get_imports(tree)
        class_fields = self._get_class_fields(class_node)
        annotations = self._get_annotations(method_node)
        modifiers = self._get_modifiers(method_node)
        
        return JavaCodeContext(
            class_name=class_name,
            method_name=method_name,
            method_signature=method_signature,
            return_type=return_type,
            parameters=parameters,
            method_body=method_body,
            imports=imports,
            class_fields=class_fields,
            annotations=annotations,
            modifiers=modifiers
        )
    
    def _find_class(self, tree: CompilationUnit, class_name: str) -> Optional[ClassDeclaration]:
        """Find a class by name in the AST."""
        for type_decl in tree.types:
            if isinstance(type_decl, ClassDeclaration) and type_decl.name == class_name:
                return type_decl
        
        # Also check nested classes
        for type_decl in tree.types:
            if isinstance(type_decl, ClassDeclaration):
                for member in type_decl.body:
                    if isinstance(member, ClassDeclaration) and member.name == class_name:
                        return member
        
        return None
    
    def _find_method(self, class_node: ClassDeclaration, method_name: str) -> Optional[MethodDeclaration]:
        """Find a method by name in a class."""
        for member in class_node.body:
            if isinstance(member, MethodDeclaration) and member.name == method_name:
                return member
        return None
    
    def _get_available_classes(self, tree: CompilationUnit) -> List[str]:
        """Get list of available class names in the file."""
        classes = []
        for type_decl in tree.types:
            if isinstance(type_decl, ClassDeclaration):
                classes.append(type_decl.name)
                # Add nested classes
                for member in type_decl.body:
                    if isinstance(member, ClassDeclaration):
                        classes.append(f"{type_decl.name}.{member.name}")
        return classes
    
    def _get_available_methods(self, class_node: ClassDeclaration) -> List[str]:
        """Get list of available method names in a class."""
        methods = []
        for member in class_node.body:
            if isinstance(member, MethodDeclaration):
                methods.append(member.name)
        return methods
    
    def _get_method_signature(self, method: MethodDeclaration) -> str:
        """Get the full method signature."""
        modifiers = ' '.join(method.modifiers) if method.modifiers else ''
        return_type = str(method.return_type) if method.return_type else 'void'
        params = ', '.join(
            f"{param.type} {param.name}"
            for param in method.parameters
        ) if method.parameters else ''
        
        return f"{modifiers} {return_type} {method.name}({params})"
    
    def _get_return_type(self, method: MethodDeclaration) -> str:
        """Get the return type as a string."""
        if method.return_type:
            return str(method.return_type)
        return "void"
    
    def _get_parameters(self, method: MethodDeclaration) -> List[Dict[str, str]]:
        """Get method parameters as a list of dictionaries."""
        parameters = []
        if method.parameters:
            for param in method.parameters:
                parameters.append({
                    'name': param.name,
                    'type': str(param.type),
                    'varargs': str(param.varargs) if hasattr(param, 'varargs') else 'False'
                })
        return parameters
    
    def _get_method_body(self, method: MethodDeclaration, source_code: str) -> str:
        """Extract the method body from source code."""
        if not method.position:
            return "Method body not available"
        
        # Split source code into lines
        lines = source_code.split('\n')
        start_line = method.position.line - 1
        
        # Find the opening brace on or after the method declaration line
        method_line = lines[start_line]
        brace_pos = method_line.find('{')
        
        # If not found on the same line, check subsequent lines
        search_line = start_line
        while brace_pos == -1 and search_line < len(lines):
            brace_pos = lines[search_line].find('{')
            if brace_pos == -1:
                search_line += 1
        
        if brace_pos == -1:
            return "Method body not available"
        
        # Start from the position after the opening brace
        brace_count = 1
        line_idx = search_line
        char_idx = brace_pos + 1
        
        # Track the start position of the method body
        body_start_line = line_idx
        body_start_char = char_idx
        
        # Parse character by character to find the matching closing brace
        while brace_count > 0 and line_idx < len(lines):
            line = lines[line_idx]
            while char_idx < len(line) and brace_count > 0:
                if line[char_idx] == '{':
                    brace_count += 1
                elif line[char_idx] == '}':
                    brace_count -= 1
                if brace_count > 0:  # Only advance if we haven't found the closing brace
                    char_idx += 1
            
            # If we haven't found the matching brace, move to the next line
            if brace_count > 0:
                line_idx += 1
                char_idx = 0
        
        # If we found the matching closing brace
        if brace_count == 0:
            # Extract the method body
            if body_start_line == line_idx:
                # Same line
                body = lines[body_start_line][body_start_char:char_idx]
            else:
                # Multiple lines
                body_lines = []
                body_lines.append(lines[body_start_line][body_start_char:])
                for i in range(body_start_line + 1, line_idx):
                    body_lines.append(lines[i])
                body_lines.append(lines[line_idx][:char_idx])
                body = '\n'.join(body_lines)
            
            return body.strip()
        
        return "Method body extraction failed"
    
    def _get_imports(self, tree: CompilationUnit) -> List[str]:
        """Get all import statements."""
        imports = []
        if tree.imports:
            for imp in tree.imports:
                if imp.static:
                    imports.append(f"static {imp.path}")
                else:
                    imports.append(str(imp.path))
        return imports
    
    def _get_class_fields(self, class_node: ClassDeclaration) -> List[Dict[str, str]]:
        """Get class fields/members."""
        fields = []
        for member in class_node.body:
            if hasattr(member, 'type') and hasattr(member, 'name'):
                fields.append({
                    'name': member.name,
                    'type': str(member.type),
                    'modifiers': list(member.modifiers) if hasattr(member, 'modifiers') else []
                })
        return fields
    
    def _get_annotations(self, method: MethodDeclaration) -> List[str]:
        """Get method annotations."""
        annotations = []
        if method.annotations:
            for ann in method.annotations:
                annotations.append(str(ann.name))
        return annotations
    
    def _get_modifiers(self, method: MethodDeclaration) -> List[str]:
        """Get method modifiers."""
        return list(method.modifiers) if method.modifiers else []


def extract_java_signature(method: MethodDeclaration) -> str:
    """
    Utility function to extract method signature.
    
    Args:
        method: javalang MethodDeclaration node
        
    Returns:
        String representation of method signature
    """
    extractor = JavaCodeExtractor()
    return extractor._get_method_signature(method)