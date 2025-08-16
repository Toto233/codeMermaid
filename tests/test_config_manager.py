"""
Tests for ConfigManager class.
"""

import pytest
import tempfile
import os
import json
from java_mermaid.utils.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def test_default_configuration(self):
        """Test default configuration."""
        config = ConfigManager()
        
        assert config.get('api_endpoint') == 'https://api.openai.com/v1'
        assert config.get('model') == 'gpt-3.5-turbo'
        assert config.get('timeout') == 30
        assert config.get('max_retries') == 3
        assert config.get('output_dir') == '.'
        assert config.get('generate_png') is True
        assert config.get('generate_comments') is True
        assert config.get('generate_javadoc') is True
    
    def test_load_from_environment_variables(self):
        """Test loading configuration from environment variables."""
        os.environ['JAVA_MERMAID_API_KEY'] = 'test_key'
        os.environ['JAVA_MERMAID_MODEL'] = 'gpt-4'
        os.environ['JAVA_MERMAID_TIMEOUT'] = '60'
        os.environ['JAVA_MERMAID_OUTPUT_DIR'] = '/tmp/test'
        os.environ['JAVA_MERMAID_GENERATE_PNG'] = 'false'
        
        try:
            config = ConfigManager()
            
            assert config.get('api_key') == 'test_key'
            assert config.get('model') == 'gpt-4'
            assert config.get('timeout') == 60
            assert config.get('output_dir') == '/tmp/test'
            assert config.get('generate_png') is False
            
        finally:
            # Clean up environment variables
            del os.environ['JAVA_MERMAID_API_KEY']
            del os.environ['JAVA_MERMAID_MODEL']
            del os.environ['JAVA_MERMAID_TIMEOUT']
            del os.environ['JAVA_MERMAID_OUTPUT_DIR']
            del os.environ['JAVA_MERMAID_GENERATE_PNG']
    
    def test_load_from_openai_env_var(self):
        """Test loading API key from OpenAI environment variable."""
        os.environ['OPENAI_API_KEY'] = 'openai_test_key'
        
        try:
            config = ConfigManager()
            
            assert config.get('api_key') == 'openai_test_key'
            
        finally:
            del os.environ['OPENAI_API_KEY']
    
    def test_load_from_file(self):
        """Test loading configuration from JSON file."""
        config_data = {
            'api_key': 'file_test_key',
            'model': 'gpt-4-turbo',
            'timeout': 45,
            'output_dir': '/custom/dir',
            'generate_png': False,
            'generate_comments': True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            
            try:
                config = ConfigManager(f.name)
                
                assert config.get('api_key') == 'file_test_key'
                assert config.get('model') == 'gpt-4-turbo'
                assert config.get('timeout') == 45
                assert config.get('output_dir') == '/custom/dir'
                assert config.get('generate_png') is False
                assert config.get('generate_comments') is True
                
            finally:
                os.unlink(f.name)
    
    def test_invalid_json_file(self):
        """Test handling of invalid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json {')
            f.flush()
            
            try:
                with pytest.raises(ValueError) as exc_info:
                    ConfigManager(f.name)
                
                assert 'Invalid JSON' in str(exc_info.value)
                
            finally:
                os.unlink(f.name)
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ConfigManager('/non/existent/file.json')
        
        assert 'Configuration file not found' in str(exc_info.value)
    
    def test_get_llm_config(self):
        """Test getting LLM-specific configuration."""
        config = ConfigManager()
        config.set('api_key', 'test_key')
        config.set('model', 'gpt-4')
        config.set('timeout', 60)
        config.set('max_retries', 5)
        
        llm_config = config.get_llm_config()
        
        assert llm_config['api_key'] == 'test_key'
        assert llm_config['model'] == 'gpt-4'
        assert llm_config['timeout'] == 60
        assert llm_config['max_retries'] == 5
    
    def test_get_output_config(self):
        """Test getting output-specific configuration."""
        config = ConfigManager()
        config.set('output_dir', '/test/dir')
        config.set('generate_png', False)
        config.set('generate_comments', True)
        config.set('theme', 'dark')
        config.set('width', 800)
        config.set('height', 600)
        
        output_config = config.get_output_config()
        
        assert output_config['output_dir'] == '/test/dir'
        assert output_config['generate_png'] is False
        assert output_config['generate_comments'] is True
        assert output_config['theme'] == 'dark'
        assert output_config['width'] == 800
        assert output_config['height'] == 600
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        # Valid configuration
        config = ConfigManager()
        config.set('api_key', 'test_key')
        assert config.validate() is True
        
        # Missing API key
        config.set('api_key', None)
        assert config.validate() is False
        
        config.set('api_key', '')
        assert config.validate() is False
        
        # Invalid numeric values
        config.set('api_key', 'test_key')
        config.set('timeout', -1)
        assert config.validate() is False
        
        config.set('timeout', 'invalid')
        assert config.validate() is False
    
    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = ConfigManager()
        config.set('api_key', 'save_test_key')
        config.set('model', 'gpt-4-mini')
        config.set('timeout', 90)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            
            try:
                config.save_to_file(temp_file)
                
                # Load and verify
                with open(temp_file, 'r') as saved_file:
                    saved_config = json.load(saved_file)
                
                assert saved_config['api_key'] == 'save_test_key'
                assert saved_config['model'] == 'gpt-4-mini'
                assert saved_config['timeout'] == 90
                
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_dict_like_access(self):
        """Test dictionary-like access to configuration."""
        config = ConfigManager()
        config.set('test_key', 'test_value')
        
        assert config['test_key'] == 'test_value'
        assert 'test_key' in config
        assert 'non_existent_key' not in config
    
    def test_string_representation(self):
        """Test string representation."""
        config = ConfigManager()
        config.set('api_key', 'test_key')
        
        str_repr = str(config)
        
        assert '"api_key": "test_key"' in str_repr
        assert '"model": "gpt-3.5-turbo"' in str_repr