"""
Tests for OutputManager class.
"""

import pytest
from java_mermaid.core.output_manager import OutputManager


class TestOutputManager:
    """Test cases for OutputManager."""
    
    def test_default_configuration(self):
        """Test default configuration."""
        manager = OutputManager()
        
        assert manager.should_generate_png() is True
        assert manager.should_generate_comments() is True
        assert manager.should_generate_javadoc() is True
    
    def test_png_disabled(self):
        """Test PNG generation disabled."""
        manager = OutputManager(generate_png=False)
        
        assert manager.should_generate_png() is False
        assert manager.should_generate_comments() is True
        assert manager.should_generate_javadoc() is True
    
    def test_comments_disabled(self):
        """Test comment generation disabled."""
        manager = OutputManager(generate_comments=False)
        
        assert manager.should_generate_png() is True
        assert manager.should_generate_comments() is False
        assert manager.should_generate_javadoc() is False
    
    def test_javadoc_disabled(self):
        """Test JavaDoc generation disabled."""
        manager = OutputManager(generate_javadoc=False)
        
        assert manager.should_generate_png() is True
        assert manager.should_generate_comments() is True
        assert manager.should_generate_javadoc() is False
    
    def test_all_disabled(self):
        """Test all generation disabled."""
        manager = OutputManager(
            generate_png=False,
            generate_comments=False,
            generate_javadoc=False
        )
        
        assert manager.should_generate_png() is False
        assert manager.should_generate_comments() is False
        assert manager.should_generate_javadoc() is False
    
    def test_apply_output_config(self):
        """Test applying output configuration from flags."""
        manager = OutputManager()
        
        flags = {
            'pic_off': True,
            'comments_off': False,
            'doc_off': True
        }
        
        manager.apply_output_config(flags)
        
        assert manager.should_generate_png() is False
        assert manager.should_generate_comments() is True
        assert manager.should_generate_javadoc() is False
    
    def test_apply_output_config_partial(self):
        """Test applying partial output configuration."""
        manager = OutputManager()
        
        flags = {
            'pic_off': True
        }
        
        manager.apply_output_config(flags)
        
        assert manager.should_generate_png() is False
        assert manager.should_generate_comments() is True
        assert manager.should_generate_javadoc() is True
    
    def test_get_output_summary(self):
        """Test getting output summary."""
        manager = OutputManager(
            generate_png=False,
            generate_comments=True,
            generate_javadoc=False
        )
        
        summary = manager.get_output_summary()
        
        assert summary['png_generation'] is False
        assert summary['comment_generation'] is True
        assert summary['javadoc_generation'] is False
    
    def test_string_representation(self):
        """Test string representation."""
        manager = OutputManager(
            generate_png=False,
            generate_comments=True,
            generate_javadoc=False
        )
        
        str_repr = str(manager)
        
        assert 'OutputManager' in str_repr
        assert 'PNG=False' in str_repr
        assert 'Comments=True' in str_repr
        assert 'JavaDoc=False' in str_repr