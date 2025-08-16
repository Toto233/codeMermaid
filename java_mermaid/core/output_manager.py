"""
Output Manager for controlling what gets generated based on CLI flags.

Handles conditional generation of PNG images, JavaDoc comments, and other outputs.
"""

from typing import Dict, Any


class OutputManager:
    """
    Manages output generation based on CLI flags and configuration.
    
    Provides methods to check whether specific outputs should be generated
    based on user preferences and CLI arguments.
    """
    
    def __init__(
        self,
        generate_png: bool = True,
        generate_comments: bool = True,
        generate_javadoc: bool = True
    ):
        """
        Initialize the output manager with generation flags.
        
        Args:
            generate_png: Whether to generate PNG images
            generate_comments: Whether to generate any comments
            generate_javadoc: Whether to generate JavaDoc comments specifically
        """
        self._generate_png = generate_png
        self._generate_comments = generate_comments
        self._generate_javadoc = generate_javadoc
    
    def should_generate_png(self) -> bool:
        """
        Check if PNG images should be generated.
        
        Returns:
            True if PNG generation is enabled
        """
        return self._generate_png
    
    def should_generate_comments(self) -> bool:
        """
        Check if any comments should be generated.
        
        Returns:
            True if comment generation is enabled
        """
        return self._generate_comments
    
    def should_generate_javadoc(self) -> bool:
        """
        Check if JavaDoc comments should be generated.
        
        Returns:
            True if JavaDoc generation is enabled
        """
        return self._generate_comments and self._generate_javadoc
    
    def apply_output_config(self, flags: Dict[str, Any]) -> None:
        """
        Apply output configuration from flags or configuration.
        
        Args:
            flags: Dictionary with output control flags
        """
        if 'pic_off' in flags:
            self._generate_png = not flags['pic_off']
        
        if 'comments_off' in flags:
            self._generate_comments = not flags['comments_off']
        
        if 'doc_off' in flags:
            self._generate_javadoc = not flags['doc_off']
    
    def get_output_summary(self) -> Dict[str, bool]:
        """
        Get a summary of what outputs will be generated.
        
        Returns:
            Dictionary with output generation status
        """
        return {
            'png_generation': self.should_generate_png(),
            'comment_generation': self.should_generate_comments(),
            'javadoc_generation': self.should_generate_javadoc()
        }
    
    def __str__(self) -> str:
        """String representation of output configuration."""
        summary = self.get_output_summary()
        return (
            f"OutputManager: PNG={summary['png_generation']}, "
            f"Comments={summary['comment_generation']}, "
            f"JavaDoc={summary['javadoc_generation']}"
        )