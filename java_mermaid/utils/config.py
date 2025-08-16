"""
Configuration management for Java Mermaid flowchart generator.

Handles loading and managing configuration from files and environment variables.
"""

import os
import json
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages configuration for the Java Mermaid flowchart generator.
    
    Supports configuration from environment variables, configuration files,
    and command-line arguments.
    """
    
    DEFAULT_CONFIG = {
        'api_endpoint': 'https://api.openai.com/v1',
        'model': 'gpt-3.5-turbo',
        'timeout': 30,
        'max_retries': 3,
        'output_dir': '.',
        'generate_png': True,
        'generate_comments': True,
        'generate_javadoc': True,
        'theme': 'default',
        'width': 1200,
        'height': 800,
        'verbose': False,
        'dry_run': False
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from config file if provided
        if config_file:
            self._load_from_file(config_file)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'JAVA_MERMAID_API_KEY': 'api_key',
            'JAVA_MERMAID_API_ENDPOINT': 'api_endpoint',
            'JAVA_MERMAID_MODEL': 'model',
            'JAVA_MERMAID_TIMEOUT': 'timeout',
            'JAVA_MERMAID_MAX_RETRIES': 'max_retries',
            'JAVA_MERMAID_OUTPUT_DIR': 'output_dir',
            'JAVA_MERMAID_THEME': 'theme',
            'JAVA_MERMAID_WIDTH': 'width',
            'JAVA_MERMAID_HEIGHT': 'height',
            'OPENAI_API_KEY': 'api_key'  # Also support standard OpenAI env var
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['timeout', 'max_retries', 'width', 'height']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif config_key in ['generate_png', 'generate_comments', 'generate_javadoc', 'verbose', 'dry_run']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self.config[config_key] = value
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with existing config
            self.config.update(file_config)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        self.config.update(updates)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration."""
        return {
            'api_key': self.get('api_key'),
            'api_endpoint': self.get('api_endpoint'),
            'model': self.get('model'),
            'timeout': self.get('timeout'),
            'max_retries': self.get('max_retries')
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration."""
        return {
            'output_dir': self.get('output_dir'),
            'generate_png': self.get('generate_png'),
            'generate_comments': self.get('generate_comments'),
            'generate_javadoc': self.get('generate_javadoc'),
            'theme': self.get('theme'),
            'width': self.get('width'),
            'height': self.get('height')
        }
    
    def save_to_file(self, config_file: str) -> None:
        """
        Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        required_keys = ['api_key']
        
        for key in required_keys:
            if not self.get(key):
                return False
        
        # Validate numeric values
        numeric_keys = ['timeout', 'max_retries', 'width', 'height']
        for key in numeric_keys:
            value = self.get(key)
            if not isinstance(value, int) or value <= 0:
                return False
        
        return True
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to configuration."""
        return self.config[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration contains key."""
        return key in self.config
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config, indent=2)