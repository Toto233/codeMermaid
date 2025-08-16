"""
Flowchart Generator - Main orchestrator for the Java Mermaid flowchart generation process.
"""

import os
import sys
from typing import Dict, Any, Optional

from java_mermaid.extractors.java_code_extractor import JavaCodeExtractor
from java_mermaid.clients.llm_client import LLMClient
from java_mermaid.core.output_manager import OutputManager
from java_mermaid.core.file_writer import FileWriter
from java_mermaid.utils.logger import get_logger
from java_mermaid.utils.exceptions import (
    JavaParsingError, LLMError, OutputError, 
    ValidationError, MethodNotFoundError, ClassNotFoundError,
    MermaidSyntaxError
)


class FlowchartGenerator:
    """
    Orchestrates the complete flowchart generation workflow.
    
    Coordinates Java parsing, LLM analysis, and conditional output generation
    based on CLI flags and configuration.
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_endpoint: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        output_dir: str = ".",
        generate_png: bool = True,
        generate_comments: bool = True,
        generate_javadoc: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the FlowchartGenerator with configuration.
        
        Args:
            api_key: OpenAI API key or compatible API key
            api_endpoint: LLM API endpoint URL
            model: LLM model name
            output_dir: Directory for output files
            generate_png: Whether to generate PNG images
            generate_comments: Whether to generate any comments
            generate_javadoc: Whether to generate JavaDoc comments
            verbose: Enable verbose logging
        """
        self.logger = get_logger(verbose=verbose)
        
        # Initialize components
        self.java_extractor = JavaCodeExtractor()
        self.llm_client = LLMClient(
            api_key=api_key,
            api_endpoint=api_endpoint,
            model=model,
            verbose=verbose
        )
        self.output_manager = OutputManager(
            generate_png=generate_png,
            generate_comments=generate_comments,
            generate_javadoc=generate_javadoc
        )
        self.file_writer = FileWriter(
            output_dir=output_dir,
            verbose=verbose
        )
        
        self.logger.info("FlowchartGenerator initialized successfully")
    
    def generate(self, java_file: str, class_name: str, method_name: str) -> None:
        """
        Generate a flowchart for the specified Java method.
        
        Args:
            java_file: Path to the Java source file
            class_name: Name of the Java class
            method_name: Name of the Java method
            
        Raises:
            ValidationError: If input validation fails
            JavaParsingError: If Java parsing fails
            LLMError: If LLM API call fails
            OutputError: If output generation fails
        """
        try:
            self.logger.info(f"Starting flowchart generation for {class_name}.{method_name}")
            
            # Validate inputs
            self._validate_inputs(java_file, class_name, method_name)
            
            # Step 1: Extract Java method context
            self.logger.debug("Extracting Java method context...")
            try:
                method_context = self.java_extractor.extract_method_context(
                    filepath=java_file,
                    class_name=class_name,
                    method_name=method_name
                )
            except FileNotFoundError as e:
                raise ValidationError(str(e))
            except Exception as e:
                raise JavaParsingError(f"Failed to parse Java file: {str(e)}")
            
            # Step 2: Generate Mermaid diagram via LLM
            self.logger.debug("Generating Mermaid diagram via LLM...")
            try:
                mermaid_code = self.llm_client.generate_flowchart(method_context)
            except Exception as e:
                raise LLMError(f"LLM generation failed: {str(e)}")
            
            if not mermaid_code:
                raise LLMError("Failed to generate Mermaid code from LLM")
            
            # Step 3: Validate Mermaid syntax
            if not self.llm_client.validate_mermaid_syntax(mermaid_code):
                self.logger.warning("LLM generated invalid Mermaid syntax, attempting correction...")
                mermaid_code = self._correct_mermaid_syntax(mermaid_code)
                if not self.llm_client.validate_mermaid_syntax(mermaid_code):
                    raise MermaidSyntaxError("Generated Mermaid code has invalid syntax")
            
            # Step 4: Generate outputs based on flags
            self.logger.debug("Generating outputs based on configuration...")
            self.logger.debug(f"  should_generate_png: {self.output_manager.should_generate_png()}")
            self.logger.debug(f"  should_generate_comments: {self.output_manager.should_generate_comments()}")
            self.logger.debug(f"  should_generate_javadoc: {self.output_manager.should_generate_javadoc()}")
            
            try:
                if self.output_manager.should_generate_png():
                    png_path = self.file_writer.write_png(
                        mermaid_code=mermaid_code,
                        class_name=class_name,
                        method_name=method_name
                    )
                    if png_path:
                        self.logger.info(f"Successfully generated PNG: {png_path}")
                    else:
                        self.logger.info("PNG generation skipped - no high-quality rendering method available")
                
                # Only generate comments if comments are enabled
                # When --doc-off is used, this should be False
                if self.output_manager.should_generate_comments():
                    self.logger.debug("Calling write_comments with generate_javadoc=" + 
                                    str(self.output_manager.should_generate_javadoc()))
                    self.file_writer.write_comments(
                        mermaid_code=mermaid_code,
                        java_file=java_file,
                        class_name=class_name,
                        method_name=method_name,
                        generate_javadoc=self.output_manager.should_generate_javadoc()
                    )
                else:
                    self.logger.debug("Skipping comment generation (comments disabled)")
            except Exception as e:
                raise OutputError(f"Failed to generate outputs: {str(e)}")
            
            self.logger.info(f"Successfully generated flowchart for {class_name}.{method_name}")
            
        except (ValidationError, JavaParsingError, LLMError, OutputError, MermaidSyntaxError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            self.logger.error(f"Unexpected error during flowchart generation: {str(e)}")
            raise JavaParsingError(f"Unexpected error: {str(e)}")
    
    def _validate_inputs(self, java_file: str, class_name: str, method_name: str) -> None:
        """
        Validate input parameters.
        
        Args:
            java_file: Path to Java file
            class_name: Name of Java class
            method_name: Name of Java method
            
        Raises:
            ValidationError: If validation fails
        """
        if not java_file:
            raise ValidationError("Java file path cannot be empty")
        
        if not class_name:
            raise ValidationError("Class name cannot be empty")
        
        if not method_name:
            raise ValidationError("Method name cannot be empty")
        
        if not os.path.exists(java_file):
            raise ValidationError(f"Java file does not exist: {java_file}")
        
        if not java_file.endswith('.java'):
            raise ValidationError(f"File must have .java extension: {java_file}")
        
        if not os.path.isfile(java_file):
            raise ValidationError(f"Path is not a file: {java_file}")
    
    def _correct_mermaid_syntax(self, mermaid_code: str) -> str:
        """
        Attempt to correct common Mermaid syntax issues.
        
        Args:
            mermaid_code: The potentially invalid Mermaid code
            
        Returns:
            Corrected Mermaid code
        """
        import re
        
        # Basic corrections for common LLM issues
        corrections = [
            (r'\bflowchart\s+TD\b', 'flowchart TD'),
            (r'\bend\b', 'End'),
            (r'\bstart\b', 'Start'),
            (r'\n\s*\n', '\n'),
            (r'\s+$', ''),
            (r'^\s+', ''),
        ]
        
        corrected = mermaid_code
        for pattern, replacement in corrections:
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        return corrected.strip()