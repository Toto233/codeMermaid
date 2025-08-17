"""
File Writer for handling PNG generation and JavaDoc comment operations.

Manages file system operations including PNG image generation from Mermaid diagrams
and insertion of JavaDoc comments into Java source files.
"""

import os
import re
import tempfile
from typing import Optional
from java_mermaid.utils.logger import get_logger
from java_mermaid.core.mermaid_cli_png_generator import MermaidPNGGenerator


class FileWriter:
    """
    Handles file operations for PNG generation and JavaDoc comment insertion.
    
    Provides methods to write PNG images from Mermaid diagrams and insert
    JavaDoc comments into Java source files while preserving existing content.
    """
    
    def __init__(self, output_dir: str = ".", verbose: bool = False):
        """
        Initialize the file writer.
        
        Args:
            output_dir: Directory for output files
            verbose: Enable verbose logging
        """
        self.output_dir = output_dir
        self.logger = get_logger(verbose=verbose)
        self.png_generator = MermaidPNGGenerator(output_dir, verbose)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def write_png(
        self,
        mermaid_code: str,
        class_name: str,
        method_name: str,
        theme: str = "default",
        width: int = 1200,
        height: int = 800
    ) -> Optional[str]:
        """
        Generate PNG image from Mermaid diagram using mermaid-cli.
        
        Args:
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
            theme: Mermaid theme (default, forest, dark, neutral)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Path to the generated PNG file, or None if PNG generation was skipped
            
        Raises:
            RuntimeError: If PNG generation fails
        """
        filename = f"{class_name}_{method_name}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Handle long filenames
        if len(filename) > 200:
            import hashlib
            hash_suffix = hashlib.md5(f"{class_name}_{method_name}".encode()).hexdigest()[:8]
            filename = f"{class_name[:50]}_{method_name[:50]}_{hash_suffix}.png"
            filepath = os.path.join(self.output_dir, filename)
        
        try:
            png_path = self.png_generator.generate_png(
                mermaid_code=mermaid_code,
                class_name=class_name,
                method_name=method_name,
                width=width,
                height=height
            )
            if png_path:
                return png_path
            else:
                # PNG generation was skipped
                return None
        except Exception as e:
            raise RuntimeError(f"PNG generation failed: {str(e)}")
    
    def write_comments(
        self,
        mermaid_code: str,
        java_file: str,
        class_name: str,
        method_name: str,
        generate_javadoc: bool = True
    ) -> str:
        """
        Insert Mermaid diagram as comments into Java source file.
        
        Args:
            mermaid_code: Mermaid diagram code
            java_file: Path to Java source file
            class_name: Name of the Java class
            method_name: Name of the Java method
            generate_javadoc: Whether to use JavaDoc format
            
        Returns:
            Path to the modified Java file
            
        Raises:
            FileNotFoundError: If Java file doesn't exist
            RuntimeError: If file modification fails
        """
        self.logger.debug(f"write_comments called with generate_javadoc={generate_javadoc}")
        
        if not os.path.exists(java_file):
            raise FileNotFoundError(f"Java file not found: {java_file}")
        
        # Save clean mermaid code to a separate file
        self._save_clean_mermaid_code(mermaid_code, class_name, method_name)
        
        # Read the original file
        with open(java_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the method and insert comments
        new_content = self._insert_mermaid_comments(
            content,
            mermaid_code,
            class_name,
            method_name,
            generate_javadoc
        )
        
        # Write back to file
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.logger.info(f"Successfully updated Java file: {java_file}")
        return java_file
    
    def _save_clean_mermaid_code(self, mermaid_code: str, class_name: str, method_name: str) -> None:
        """
        Save clean Mermaid code to a separate .mmd file for easy copy/paste.
        
        Args:
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
        """
        try:
            # Create .mmd file path
            mmd_filename = f"{class_name}_{method_name}.mmd"
            mmd_filepath = os.path.join(self.output_dir, mmd_filename)
            
            # Write clean mermaid code
            with open(mmd_filepath, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            self.logger.info(f"Saved clean Mermaid code to: {mmd_filepath}")
        except Exception as e:
            self.logger.warning(f"Failed to save clean Mermaid code: {str(e)}")
    
    def _insert_mermaid_comments(
        self,
        content: str,
        mermaid_code: str,
        class_name: str,
        method_name: str,
        generate_javadoc: bool
    ) -> str:
        """
        Insert Mermaid comments before the specified method.
        
        Args:
            content: Java source file content
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
            generate_javadoc: Whether to use JavaDoc format
            
        Returns:
            Modified content with inserted comments
        """
        lines = content.split('\n')
        
        # Find the method declaration
        method_pattern = re.compile(
            rf'^(\s*)(?:public|private|protected|static|final|synchronized|abstract|native|strictfp|\s)*\s+(?:\w+|<[^>]*>\s*)\s+{method_name}\s*\('
        )
        
        method_line_idx = -1
        for i, line in enumerate(lines):
            if method_pattern.search(line):
                method_line_idx = i
                break
        
        if method_line_idx == -1:
            raise RuntimeError(f"Method {method_name} not found in file")
        
        # Find the indentation level
        method_line = lines[method_line_idx]
        indentation = len(method_line) - len(method_line.lstrip())
        indent_str = ' ' * indentation
        
        # Prepare the comment block
        if generate_javadoc:
            comment_block = self._create_javadoc_comment(mermaid_code, indent_str)
        else:
            comment_block = self._create_block_comment(mermaid_code, indent_str)
        
        # Find the insertion point and check for existing Mermaid comments
        insert_idx = method_line_idx
        remove_start_idx = -1
        remove_end_idx = -1
        
        # Look for existing Mermaid comments before the method
        # Search backwards from the method line
        for i in range(method_line_idx - 1, -1, -1):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # If we find a non-comment line, stop searching
            if not line.strip().startswith('//') and not line.strip().startswith('/*') and not line.strip().startswith('*') and not line.strip().startswith('*/'):
                insert_idx = i + 1
                break
            
            # Look for existing Mermaid comment start (@mermaid tag or Method flowchart)
            if '@mermaid' in line or 'Method flowchart visualization' in line:
                remove_start_idx = i
                # Find the end of the existing comment block
                for j in range(i, method_line_idx):
                    if lines[j].strip() == '*/':
                        remove_end_idx = j
                        break
                # If we found a start but not an end, that's an error - let's be safe and not remove anything
                if remove_end_idx == -1:
                    remove_start_idx = -1
                break
        
        # Remove existing Mermaid comment if found
        if remove_start_idx != -1 and remove_end_idx != -1:
            # Replace the existing comment with the new one
            new_lines = lines[:remove_start_idx] + comment_block + lines[remove_end_idx + 1:]
        else:
            # Insert the comment block before the method
            # Find the first non-comment line before the method
            insert_idx = method_line_idx
            for i in range(method_line_idx - 1, -1, -1):
                line = lines[i]
                # Skip empty lines
                if not line.strip():
                    continue
                # If we find a non-comment line, this is our insertion point
                if not line.strip().startswith('//') and not line.strip().startswith('/*') and not line.strip().startswith('*') and not line.strip().startswith('*/'):
                    insert_idx = i + 1
                    break
                # If we find the start of a comment block, continue searching
                if line.strip().startswith('/*'):
                    continue
            
            # Insert the comment block
            new_lines = lines[:insert_idx] + comment_block + lines[insert_idx:]
        
        return '\n'.join(new_lines)
    
    def _create_javadoc_comment(self, mermaid_code: str, indent_str: str) -> list:
        """Create JavaDoc-style comment with Mermaid diagram."""
        lines = [
            f"{indent_str}/**",
            f"{indent_str} * Method flowchart visualization.",
            f"{indent_str} *",
            f"{indent_str} * @mermaid",
            f"{indent_str} * ```mermaid",
        ]
        
        # Add Mermaid code with proper indentation
        for mermaid_line in mermaid_code.split('\n'):
            lines.append(f"{indent_str} * {mermaid_line}")
        
        lines.extend([
            f"{indent_str} * ```",
            f"{indent_str} *",
            f"{indent_str} * To extract clean Mermaid code:",
            f"{indent_str} * 1. Copy lines between the ```mermaid and ``` markers",
            f"{indent_str} * 2. Remove the leading asterisks and spaces",
            f"{indent_str} * OR",
            f"{indent_str} * 1. Use the generated .mmd file in the output directory",
            f"{indent_str} */"
        ])
        
        return lines
    
    def _create_clean_javadoc_comment(self, mermaid_code: str, indent_str: str) -> list:
        """Create JavaDoc-style comment with clean Mermaid diagram for easy copy/paste."""
        lines = [
            f"{indent_str}/**",
            f"{indent_str} * Method flowchart visualization.",
            f"{indent_str} *",
            f"{indent_str} * To use this diagram:",
            f"{indent_str} * 1. Copy the Mermaid code between the markers",
            f"{indent_str} * 2. Paste into any Mermaid-compatible tool",
            f"{indent_str} *",
            f"{indent_str} * BEGIN MERMAID DIAGRAM -----",
            f"{indent_str} * ```mermaid",
        ]
        
        # Add clean Mermaid code (without extra asterisks)
        for mermaid_line in mermaid_code.split('\n'):
            lines.append(f"{indent_str} * {mermaid_line}")
        
        lines.extend([
            f"{indent_str} * ```",
            f"{indent_str} * END MERMAID DIAGRAM -------",
            f"{indent_str} */"
        ])
        
        return lines
    
    def _create_block_comment(self, mermaid_code: str, indent_str: str) -> list:
        """Create regular block comment with Mermaid diagram."""
        lines = [
            f"{indent_str}/*",
            f"{indent_str} * Method flowchart:",
            f"{indent_str} *",
        ]
        
        # Add Mermaid code with proper indentation
        for mermaid_line in mermaid_code.split('\n'):
            lines.append(f"{indent_str} * {mermaid_line}")
        
        lines.append(f"{indent_str} */")
        
        return lines
    
    def _create_clean_block_comment(self, mermaid_code: str, indent_str: str) -> list:
        """Create regular block comment with clean Mermaid diagram for easy copy/paste."""
        lines = [
            f"{indent_str}/*",
            f"{indent_str} * Method flowchart:",
            f"{indent_str} *",
            f"{indent_str} * To use this diagram:",
            f"{indent_str} * 1. Copy the Mermaid code between the markers",
            f"{indent_str} * 2. Paste into any Mermaid-compatible tool",
            f"{indent_str} *",
            f"{indent_str} * BEGIN MERMAID DIAGRAM -----",
            f"{indent_str} * ```mermaid",
        ]
        
        # Add clean Mermaid code (without extra asterisks that interfere with copying)
        for mermaid_line in mermaid_code.split('\n'):
            lines.append(f"{indent_str} * {mermaid_line}")
        
        lines.extend([
            f"{indent_str} * ```",
            f"{indent_str} * END MERMAID DIAGRAM -------",
            f"{indent_str} */"
        ])
        
        return lines
    
    def cleanup_on_error(self) -> None:
        """
        Clean up temporary files on error.
        
        This method can be called to clean up any temporary files
        that might have been created during the process.
        """
        # Currently no persistent temporary files to clean up
        # This method is reserved for future use
        pass
    
    def get_output_dir(self) -> str:
        """Get the current output directory."""
        return self.output_dir