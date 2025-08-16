"""
Tests for SimplePNGGenerator class.
"""

import pytest
import tempfile
import os
from PIL import Image
from java_mermaid.core.simple_png_generator import SimplePNGGenerator


class TestSimplePNGGenerator:
    """Test cases for SimplePNGGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = SimplePNGGenerator(output_dir=self.temp_dir, verbose=False)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_png_simple_flowchart(self):
        """Test generating PNG from simple flowchart."""
        mermaid_code = '''
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
'''
        
        filepath = self.generator.generate_png(
            mermaid_code=mermaid_code,
            class_name='TestClass',
            method_name='testMethod'
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith('TestClass_testMethod.png')
        
        # Verify it's a valid image
        img = Image.open(filepath)
        assert img.format == 'PNG'
        assert img.size[0] == 1200  # Default width
        assert img.size[1] == 800   # Default height
    
    def test_generate_png_custom_dimensions(self):
        """Test generating PNG with custom dimensions."""
        mermaid_code = '''
flowchart TD
    A[Start] --> B[End]
'''
        
        filepath = self.generator.generate_png(
            mermaid_code=mermaid_code,
            class_name='TestClass',
            method_name='testMethod',
            width=600,
            height=400
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        
        img = Image.open(filepath)
        assert img.size[0] == 600
        assert img.size[1] == 400
    
    def test_generate_png_empty_mermaid(self):
        """Test generating PNG with empty Mermaid code."""
        filepath = self.generator.generate_png(
            mermaid_code='',
            class_name='TestClass',
            method_name='testMethod'
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
    
    def test_generate_png_long_method_name(self):
        """Test handling long method names."""
        long_name = 'a' * 100
        filepath = self.generator.generate_png(
            mermaid_code='flowchart TD\nA[Start] --> B[End]',
            class_name='TestClass',
            method_name=long_name
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        # Should be truncated due to filename length
        assert len(os.path.basename(filepath)) < 200
    
    def test_parse_mermaid_flowchart(self):
        """Test parsing Mermaid flowchart into nodes and edges."""
        mermaid_code = '''
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
'''
        
        nodes, edges = self.generator._parse_mermaid_flowchart(mermaid_code)
        
        assert len(nodes) >= 4  # Should find start, decision, process, end nodes
        assert len(edges) >= 3  # Should find connections
        
        # Check for specific node types
        node_labels = [node['label'] for node in nodes]
        assert 'Start' in node_labels
        assert 'Decision' in node_labels
        assert 'Process' in node_labels
        assert 'End' in node_labels
    
    def test_parse_mermaid_node(self):
        """Test parsing individual nodes."""
        # Test process node
        node = self.generator._parse_node('A[Process Node]')
        assert node is not None
        assert node['id'] == 'A'
        assert node['label'] == 'Process Node'
        assert node['type'] == 'process'
        
        # Test decision node
        node = self.generator._parse_node('B{Decision Node}')
        assert node is not None
        assert node['id'] == 'B'
        assert node['label'] == 'Decision Node'
        assert node['type'] == 'decision'
        
        # Test start/end node
        node = self.generator._parse_node('C((Start/End))')
        assert node is not None
        assert node['id'] == 'C'
        assert node['label'] == 'Start/End'
        assert node['type'] == 'start_end'
        
        # Test invalid node
        node = self.generator._parse_node('Invalid syntax')
        assert node is None or node['type'] == 'process'  # Fallback behavior
    
    def test_parse_mermaid_edge(self):
        """Test parsing edges."""
        # Test simple edge
        edge = self.generator._parse_edge('A --> B')
        assert edge is not None
        assert edge['source'] == 'A'
        assert edge['target'] == 'B'
        assert edge['label'] == ''
        
        # Test labeled edge
        edge = self.generator._parse_edge('A -->|Yes| B')
        assert edge is not None
        assert edge['source'] == 'A'
        assert edge['target'] == 'B'
        assert edge['label'] == 'Yes'
        
        # Test invalid edge
        edge = self.generator._parse_edge('Invalid syntax')
        assert edge is None
    
    def test_create_text_png_fallback(self):
        """Test text-based PNG fallback."""
        mermaid_code = '''
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
'''
        
        filepath = tempfile.mktemp(suffix='.png', dir=self.temp_dir)
        
        result = self.generator._create_text_png(
            mermaid_code=mermaid_code,
            class_name='TestClass',
            method_name='testMethod',
            filepath=filepath
        )
        
        assert result == filepath
        assert os.path.exists(filepath)
        
        # Verify it's a valid image
        img = Image.open(filepath)
        assert img.format == 'PNG'
    
    def test_break_text(self):
        """Test text breaking utility."""
        text = "This is a very long line that should be broken into multiple lines"
        broken = self.generator._break_text(text, 20)
        
        assert len(broken) > 1
        assert all(len(line) <= 20 for line in broken)
        assert ''.join(broken) == text.replace('\n', '')
    
    def test_empty_mermaid_input(self):
        """Test handling of completely empty Mermaid input."""
        filepath = self.generator.generate_png(
            mermaid_code='',
            class_name='TestClass',
            method_name='emptyMethod'
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
    
    def test_mermaid_with_comments(self):
        """Test Mermaid code with comments."""
        mermaid_code = '''
%% This is a comment
flowchart TD
    A[Start] --> B[End] %% Another comment
'''
        
        filepath = self.generator.generate_png(
            mermaid_code=mermaid_code,
            class_name='TestClass',
            method_name='withComments'
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)