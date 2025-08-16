"""
Tests for JavaCodeExtractor class.
"""

import pytest
import tempfile
import os
from java_mermaid.extractors.java_code_extractor import JavaCodeExtractor, JavaCodeContext


class TestJavaCodeExtractor:
    """Test cases for JavaCodeExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = JavaCodeExtractor()
    
    def test_extract_method_context_simple_method(self):
        """Test extracting context from a simple method."""
        java_code = '''
public class TestClass {
    public int add(int a, int b) {
        return a + b;
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            context = self.extractor.extract_method_context(f.name, 'TestClass', 'add')
            
            assert context is not None
            assert context.class_name == 'TestClass'
            assert context.method_name == 'add'
            assert context.return_type == 'int'
            assert len(context.parameters) == 2
            assert context.parameters[0]['name'] == 'a'
            assert context.parameters[0]['type'] == 'int'
            assert 'return a + b;' in context.method_body
            
            os.unlink(f.name)
    
    def test_extract_method_context_with_modifiers(self):
        """Test extracting context from method with modifiers."""
        java_code = '''
public class TestClass {
    public static final synchronized String process(String input) {
        return input.toUpperCase();
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            context = self.extractor.extract_method_context(f.name, 'TestClass', 'process')
            
            assert context is not None
            assert 'public' in context.modifiers
            assert 'static' in context.modifiers
            assert 'final' in context.modifiers
            assert 'synchronized' in context.modifiers
            
            os.unlink(f.name)
    
    def test_extract_method_context_with_annotations(self):
        """Test extracting context from method with annotations."""
        java_code = '''
import java.lang.Override;

public class TestClass {
    @Override
    @Deprecated
    public String toString() {
        return "test";
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            context = self.extractor.extract_method_context(f.name, 'TestClass', 'toString')
            
            assert context is not None
            assert 'Override' in context.annotations
            assert 'Deprecated' in context.annotations
            
            os.unlink(f.name)
    
    def test_extract_method_context_with_complex_method(self):
        """Test extracting context from a complex method."""
        java_code = '''
import java.util.List;
import java.util.ArrayList;

public class TestClass {
    private List<String> items;
    
    public List<String> filterItems(String prefix) {
        List<String> result = new ArrayList<>();
        for (String item : items) {
            if (item.startsWith(prefix)) {
                result.add(item);
            }
        }
        return result;
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            context = self.extractor.extract_method_context(f.name, 'TestClass', 'filterItems')
            
            assert context is not None
            assert context.return_type == 'List<String>'
            assert len(context.parameters) == 1
            assert context.parameters[0]['type'] == 'String'
            assert 'java.util.List' in context.imports
            assert 'java.util.ArrayList' in context.imports
            assert len(context.class_fields) == 1
            assert context.class_fields[0]['name'] == 'items'
            assert 'List<String>' in context.class_fields[0]['type']
            
            os.unlink(f.name)
    
    def test_class_not_found(self):
        """Test error handling for non-existent class."""
        java_code = '''
public class TestClass {
    public void method() {}
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            with pytest.raises(ValueError) as exc_info:
                self.extractor.extract_method_context(f.name, 'NonExistentClass', 'method')
            
            assert 'NonExistentClass' in str(exc_info.value)
            
            os.unlink(f.name)
    
    def test_method_not_found(self):
        """Test error handling for non-existent method."""
        java_code = '''
public class TestClass {
    public void existingMethod() {}
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            with pytest.raises(ValueError) as exc_info:
                self.extractor.extract_method_context(f.name, 'TestClass', 'nonExistentMethod')
            
            assert 'nonExistentMethod' in str(exc_info.value)
            
            os.unlink(f.name)
    
    def test_invalid_java_syntax(self):
        """Test error handling for invalid Java syntax."""
        java_code = '''
public class TestClass {
    public void method() {
        invalid syntax here
    }
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            with pytest.raises(Exception):
                self.extractor.extract_method_context(f.name, 'TestClass', 'method')
            
            os.unlink(f.name)
    
    def test_nested_classes(self):
        """Test extracting from nested classes."""
        java_code = '''
public class OuterClass {
    public static class InnerClass {
        public void innerMethod() {
            System.out.println("inner");
        }
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(java_code)
            f.flush()
            
            context = self.extractor.extract_method_context(f.name, 'InnerClass', 'innerMethod')
            
            assert context is not None
            assert context.class_name == 'InnerClass'
            assert context.method_name == 'innerMethod'
            
            os.unlink(f.name)


class TestJavaCodeContext:
    """Test cases for JavaCodeContext."""
    
    def test_context_creation(self):
        """Test creating a JavaCodeContext instance."""
        context = JavaCodeContext(
            class_name='TestClass',
            method_name='testMethod',
            method_signature='public void testMethod(int x)',
            return_type='void',
            parameters=[{'name': 'x', 'type': 'int'}],
            method_body='System.out.println(x);',
            imports=['java.util.*'],
            class_fields=[{'name': 'counter', 'type': 'int', 'modifiers': ['private']}],
            annotations=['@Override'],
            modifiers=['public']
        )
        
        assert context.class_name == 'TestClass'
        assert context.method_name == 'testMethod'
        assert context.method_signature == 'public void testMethod(int x)'
        assert context.return_type == 'void'
        assert len(context.parameters) == 1
        assert context.parameters[0]['name'] == 'x'
        assert context.parameters[0]['type'] == 'int'
        assert context.method_body == 'System.out.println(x);'
        assert 'java.util.*' in context.imports
        assert len(context.class_fields) == 1
        assert context.class_fields[0]['name'] == 'counter'
        assert '@Override' in context.annotations
        assert 'public' in context.modifiers
    
    def test_context_to_dict(self):
        """Test converting context to dictionary."""
        context = JavaCodeContext(
            class_name='TestClass',
            method_name='testMethod',
            method_signature='public void testMethod(int x)',
            return_type='void',
            parameters=[{'name': 'x', 'type': 'int'}],
            method_body='System.out.println(x);',
            imports=['java.util.*'],
            class_fields=[{'name': 'counter', 'type': 'int', 'modifiers': ['private']}],
            annotations=['@Override'],
            modifiers=['public']
        )
        
        context_dict = context.to_dict()
        
        assert context_dict['class_name'] == 'TestClass'
        assert context_dict['method_name'] == 'testMethod'
        assert context_dict['method_signature'] == 'public void testMethod(int x)'
        assert context_dict['return_type'] == 'void'
        assert len(context_dict['parameters']) == 1
        assert context_dict['parameters'][0]['name'] == 'x'
        assert context_dict['parameters'][0]['type'] == 'int'
        assert context_dict['method_body'] == 'System.out.println(x);'
        assert 'java.util.*' in context_dict['imports']
        assert len(context_dict['class_fields']) == 1
        assert context_dict['class_fields'][0]['name'] == 'counter'
        assert '@Override' in context_dict['annotations']
        assert 'public' in context_dict['modifiers']
    
    def test_context_str(self):
        """Test string representation of context."""
        context = JavaCodeContext(
            class_name='TestClass',
            method_name='testMethod',
            method_signature='public void testMethod(int x)',
            return_type='void',
            parameters=[{'name': 'x', 'type': 'int'}],
            method_body='System.out.println(x);',
            imports=[],
            class_fields=[],
            annotations=[],
            modifiers=[]
        )
        
        assert str(context) == 'TestClass.testMethod()'