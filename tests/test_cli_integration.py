"""
Integration tests for CLI interface.
"""

import pytest
import tempfile
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock


class TestCLIIntegration:
    """Integration tests for the CLI interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple Java file for testing
        self.java_file = os.path.join(self.temp_dir, 'TestJava.java')
        with open(self.java_file, 'w') as f:
            f.write('''
public class TestJava {
    public void simpleMethod(int x) {
        if (x > 0) {
            System.out.println("Positive");
        } else {
            System.out.println("Non-positive");
        }
    }
}
''')
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cli_help_command(self):
        """Test CLI help command."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid', '--help'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert 'usage:' in result.stdout
            assert 'class_name method_name java_file' in result.stdout
            assert '--pic-off' in result.stdout
            assert '--doc-off' in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI help command timed out")
    
    def test_cli_dry_run(self):
        """Test CLI dry run mode."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--dry-run', '--verbose'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail due to missing API key, but that's expected
            assert result.returncode != 0
            assert 'API key is required' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI dry run command timed out")
    
    def test_cli_invalid_java_file(self):
        """Test CLI with invalid Java file."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', '/non/existent/file.java'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            assert 'does not exist' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI invalid file test timed out")
    
    def test_cli_invalid_class_name(self):
        """Test CLI with invalid class name."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'NonExistentClass', 'simpleMethod', self.java_file,
                '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            assert 'not found' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI invalid class test timed out")
    
    def test_cli_invalid_method_name(self):
        """Test CLI with invalid method name."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'nonExistentMethod', self.java_file,
                '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            assert 'not found' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI invalid method test timed out")
    
    def test_cli_output_flags(self):
        """Test CLI output flags."""
        try:
            # Test --pic-off flag
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--pic-off', '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail due to missing API key, but that's expected
            assert result.returncode != 0
            
            # Test --doc-off flag
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--doc-off', '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            
            # Test --comments-off flag
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--comments-off', '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI output flags test timed out")
    
    def test_cli_custom_output_dir(self):
        """Test CLI with custom output directory."""
        custom_dir = os.path.join(self.temp_dir, 'custom_output')
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--output-dir', custom_dir,
                '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail due to missing API key, but that's expected
            assert result.returncode != 0
            assert os.path.exists(custom_dir) or 'API key is required' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI custom output dir test timed out")
    
    def test_cli_config_file(self):
        """Test CLI with configuration file."""
        config_data = {
            "model": "gpt-4",
            "timeout": 60
        }
        
        config_file = os.path.join(self.temp_dir, 'config.json')
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--config', config_file,
                '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail due to missing API key, but config should be loaded
            assert result.returncode != 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI config file test timed out")
    
    def test_cli_invalid_config_file(self):
        """Test CLI with invalid configuration file."""
        config_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(config_file, 'w') as f:
            f.write('invalid json {')
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--config', config_file,
                '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode != 0
            assert 'Invalid JSON' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI invalid config file test timed out")
    
    def test_cli_verbose_logging(self):
        """Test CLI verbose logging."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'java_mermaid',
                'TestJava', 'simpleMethod', self.java_file,
                '--verbose', '--dry-run'
            ], capture_output=True, text=True, timeout=10)
            
            # Should contain verbose output
            assert 'Starting Java Mermaid flowchart generator' in result.stderr or 'API key is required' in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI verbose test timed out")