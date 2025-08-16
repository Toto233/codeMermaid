"""
Prompt Manager for Java Mermaid Flowchart Generator.

Handles loading and managing prompt templates for LLM interactions.
"""

import os
from typing import Dict, Any


class PromptManager:
    """Manages prompt templates for the LLM client."""
    
    def __init__(self, prompts_dir: str = None):
        """
        Initialize the PromptManager.
        
        Args:
            prompts_dir: Directory containing prompt templates (default: bundled prompts)
        """
        if prompts_dir is None:
            # Use bundled prompts directory
            self.prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        else:
            self.prompts_dir = prompts_dir
            
        # Ensure prompts directory exists
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # Load default prompts
        self._load_default_prompts()
    
    def _load_default_prompts(self) -> None:
        """Load default prompt templates."""
        # Load Java method prompt
        java_prompt_path = os.path.join(self.prompts_dir, 'java_method.prompt')
        if os.path.exists(java_prompt_path):
            with open(java_prompt_path, 'r', encoding='utf-8') as f:
                self.java_method_prompt = f.read()
        else:
            # Use built-in default prompt
            self.java_method_prompt = self._get_default_java_method_prompt()
    
    def _get_default_java_method_prompt(self) -> str:
        """
        Get the default Java method prompt template.
        
        Returns:
            Default Java method prompt template
        """
        return """Analyze this Java method and generate a Mermaid flowchart.

Class: {class_name}
Method: {method_name}
Signature: {method_signature}
Return Type: {return_type}
Parameters: {parameters}
Annotations: {annotations}
Modifiers: {modifiers}

Imports:
{imports}

Class Fields:
{class_fields}

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
8. Stream operations (.map(), .filter(), .collect())
9. Lambda expressions
10. Generic type flows
11. Resource management (try-with-resources)
12. Synchronized blocks
13. Thread operations
14. I/O operations

Generate a flowchart TD diagram that shows all possible execution paths.
Use appropriate shapes:
- Rectangle [Process] for operations and return statements
- Diamond {{Decision}} for conditions
- Circle (Start/End) for start and end nodes
- Parallelogram [/Input/Output/] for I/O operations and return statements
- Subroutine [[Subroutine]] for method calls
- Database [(Database)] for persistence operations

Special formatting requirements:
- Use <br/> for line breaks in complex conditions instead of \n
- Use || instead of | for labeling decision branches (e.g., B -->||true|| C)
- For return statements, use parallelogram shape: [/"return value"/]
- For complex conditions, break them with <br/> for better readability
- Start node should be (Start) and end node should be (End)
- Use ||true|| and ||false|| for boolean conditions
- Use short, concise labels for nodes

Include Java-specific elements:
- Exception handling paths with different catch blocks
- Stream pipeline visualization
- Lambda expression flow
- Generic type parameter handling
- Resource cleanup in finally blocks
- Thread synchronization points

Example of expected output format:
flowchart TD
    A(Start) --> B{{username == null ||<br/>username.isEmpty()}}
    B -->||true|| C[/"return \\"Invalid username\\""/]
    B -->||false|| D{{password == null ||<br/>password.length() < 8}}
    C --> E(End)
    D -->||true|| F[/"return \\"Password too short\\""/]
    D -->||false|| G{{!password.matches<br/>(".*[A-Z].*")}}
    F --> E
    G -->||true|| H[/"return \\"Missing uppercase letter\\""/]
    G -->||false|| I[/"return \\"Valid user\\""/]
    H --> E
    I --> E

Keep the diagram readable and well-structured.
Return only valid Mermaid syntax, no explanations or markdown formatting."""

    def get_java_method_prompt(self) -> str:
        """
        Get the Java method prompt template.
        
        Returns:
            Java method prompt template
        """
        return self.java_method_prompt
    
    def load_prompt_from_file(self, filename: str) -> str:
        """
        Load a prompt template from a file.
        
        Args:
            filename: Name of the prompt file
            
        Returns:
            Prompt template content
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_prompt_to_file(self, filename: str, prompt_content: str) -> str:
        """
        Save a prompt template to a file.
        
        Args:
            filename: Name of the prompt file
            prompt_content: Prompt template content
            
        Returns:
            Path to the saved prompt file
        """
        prompt_path = os.path.join(self.prompts_dir, filename)
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        return prompt_path