"""
Logging utilities for the Java Mermaid flowchart generator.

Provides consistent logging across the application with configurable verbosity.
"""

import logging
import sys
from typing import Optional


def setup_logger(verbose: bool = False, name: str = "java_mermaid") -> logging.Logger:
    """
    Set up and configure the logger.
    
    Args:
        verbose: Enable verbose logging (DEBUG level)
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level based on verbose flag
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "java_mermaid", verbose: bool = False) -> logging.Logger:
    """
    Get the existing logger instance or create a new one.
    
    Args:
        name: Logger name
        verbose: Enable verbose logging
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(verbose=verbose, name=name)
    return logger


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for terminal output.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_colored_logger(verbose: bool = False, name: str = "java_mermaid") -> logging.Logger:
    """
    Set up logger with colored output.
    
    Args:
        verbose: Enable verbose logging
        name: Logger name
        
    Returns:
        Logger with colored output
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create colored formatter
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger