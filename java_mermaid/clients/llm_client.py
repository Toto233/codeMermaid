"""
LLM Client for OpenAI-compatible API integration.

Handles communication with LLM APIs for generating Mermaid flowcharts
from Java method context.
"""

import json
import time
import requests
from typing import Dict, Any, Optional
from java_mermaid.extractors.java_code_extractor import JavaCodeContext
from java_mermaid.core.prompt_manager import PromptManager


class LLMClient:
    """
    Client for interacting with OpenAI-compatible LLM APIs.
    
    Handles API calls, retries, rate limiting, and Mermaid syntax validation.
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_endpoint: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        timeout: int = 30,
        max_retries: int = 3,
        verbose: bool = False
    ):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for authentication
            api_endpoint: API endpoint URL
            model: LLM model name
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.verbose = verbose
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        
        # Ensure API key is provided
        if not self.api_key:
            raise ValueError(
                "API key is required. Set OPENAI_API_KEY environment variable "
                "or provide api_key parameter."
            )
    
    def generate_flowchart(self, code_context: JavaCodeContext) -> str:
        """
        Generate Mermaid flowchart from Java method context.
        
        Args:
            code_context: Java method context information
            
        Returns:
            Mermaid flowchart code as string
            
        Raises:
            Exception: If API call fails after all retries
        """
        # Prepare the prompt
        prompt = self._build_prompt(code_context)
        
        # Make API call with retries
        return self._make_api_call(prompt)
    
    def validate_mermaid_syntax(self, mermaid_code: str) -> bool:
        """
        Validate Mermaid syntax.
        
        Args:
            mermaid_code: Mermaid diagram code to validate
            
        Returns:
            True if syntax appears valid, False otherwise
        """
        if not mermaid_code:
            return False
        
        # Basic syntax validation
        lines = mermaid_code.strip().split('\n')
        
        # Check for required flowchart declaration
        has_flowchart = any(
            line.strip().lower().startswith('flowchart') or 
            line.strip().lower().startswith('graph') 
            for line in lines
        )
        
        if not has_flowchart:
            return False
        
        # Check for node definitions (should have arrows or connections)
        has_connections = any(
            '-->' in line or '---' in line or '---|' in line
            for line in lines
        )
        
        return True
    
    def _build_prompt(self, code_context: JavaCodeContext) -> str:
        """Build the prompt for LLM from Java method context."""
        context_dict = code_context.to_dict()
        
        # Format parameters as readable string
        parameters_str = '\n'.join(
            f"- {p['type']} {p['name']}" 
            for p in context_dict['parameters']
        ) if context_dict['parameters'] else "None"
        
        # Format imports as readable string
        imports_str = '\n'.join(
            f"- {imp}" 
            for imp in context_dict['imports']
        ) if context_dict['imports'] else "None"
        
        # Format class fields as readable string
        fields_str = '\n'.join(
            f"- {f['type']} {f['name']} ({', '.join(f['modifiers'])}"
            for f in context_dict['class_fields']
        ) if context_dict['class_fields'] else "None"
        
        # Format annotations
        annotations_str = ', '.join(context_dict['annotations']) if context_dict['annotations'] else "None"
        
        # Format modifiers
        modifiers_str = ', '.join(context_dict['modifiers']) if context_dict['modifiers'] else "None"
        
        # Get prompt template from prompt manager
        prompt_template = self.prompt_manager.get_java_method_prompt()
        
        return prompt_template.format(
            class_name=context_dict['class_name'],
            method_name=context_dict['method_name'],
            method_signature=context_dict['method_signature'],
            return_type=context_dict['return_type'],
            parameters=parameters_str,
            annotations=annotations_str,
            modifiers=modifiers_str,
            imports=imports_str,
            class_fields=fields_str,
            method_body=context_dict['method_body']
        )
    
    def _make_api_call(self, prompt: str) -> str:
        """
        Make API call to LLM with retry logic.
        
        Args:
            prompt: The prompt to send to LLM
            
        Returns:
            Generated Mermaid code
            
        Raises:
            Exception: If all retries fail
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert Java programmer who generates accurate Mermaid flowcharts from Java method code. Always return valid Mermaid flowchart syntax only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 2000
        }
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if self.verbose:
                    print(f"Making API call attempt {attempt + 1}/{self.max_retries + 1}")
                
                # Handle different API endpoint formats
                endpoint_url = f"{self.api_endpoint}/chat/completions"
                if not self.api_endpoint.endswith('/v1'):
                    endpoint_url = f"{self.api_endpoint}/v1/chat/completions"
                
                response = requests.post(
                    endpoint_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    mermaid_code = result['choices'][0]['message']['content'].strip()
                    
                    # Clean up the response
                    mermaid_code = self._clean_mermaid_code(mermaid_code)
                    
                    if self.verbose:
                        print(f"Successfully generated Mermaid code ({len(mermaid_code)} chars)")
                    
                    return mermaid_code
                
                elif response.status_code == 429:
                    # Rate limit hit, wait and retry
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        if self.verbose:
                            print(f"Rate limited, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after all retries")
                
                elif response.status_code == 401:
                    raise Exception("Invalid API key")
                
                else:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    if attempt < self.max_retries:
                        if self.verbose:
                            print(f"API error: {error_msg}, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(error_msg)
                        
            except requests.exceptions.Timeout:
                last_exception = Exception("API request timeout")
                if attempt < self.max_retries:
                    if self.verbose:
                        print("Request timeout, retrying...")
                    time.sleep(1)
                    continue
            
            except requests.exceptions.RequestException as e:
                last_exception = Exception(f"Network error: {str(e)}")
                if attempt < self.max_retries:
                    if self.verbose:
                        print(f"Network error: {e}, retrying...")
                    time.sleep(1)
                    continue
        
        # All retries failed
        raise last_exception or Exception("All API call attempts failed")
    
    def _clean_mermaid_code(self, mermaid_code: str) -> str:
        """
        Clean up the Mermaid code from LLM response.
        
        Args:
            mermaid_code: Raw Mermaid code from LLM
            
        Returns:
            Cleaned Mermaid code
        """
        # Remove common markdown formatting
        lines = mermaid_code.split('\n')
        
        # Remove ```mermaid or ``` blocks
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        
        # Clean up each line
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('```'):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def handle_api_errors(self, error: Exception) -> str:
        """
        Handle API errors and return user-friendly messages.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        error_msg = str(error).lower()
        
        if "invalid api key" in error_msg:
            return "Invalid API key. Please check your OpenAI API key."
        elif "rate limit" in error_msg:
            return "Rate limit exceeded. Please try again later."
        elif "timeout" in error_msg:
            return "API request timed out. Please check your internet connection."
        elif "network" in error_msg:
            return "Network error. Please check your internet connection."
        else:
            return f"API error: {str(error)}"


# Test the client if run directly
if __name__ == "__main__":
    import os
    
    # Test with mock context
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = LLMClient(api_key=api_key, verbose=True)
        
        # Mock context
        mock_context = JavaCodeContext(
            class_name="TestClass",
            method_name="testMethod",
            method_signature="public void testMethod(int x)",
            return_type="void",
            parameters=[{"name": "x", "type": "int"}],
            method_body='if (x > 0) { return; } else { System.out.println("test"); }',
            imports=["java.util.*"],
            class_fields=[{"name": "value", "type": "int", "modifiers": ["private"]}],
            annotations=["@Override"],
            modifiers=["public"]
        )
        
        try:
            mermaid = client.generate_flowchart(mock_context)
            print("Generated Mermaid:")
            print(mermaid)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Set OPENAI_API_KEY environment variable to test")