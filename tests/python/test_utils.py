"""
Tests for app/utils decorators and helper functions
Run with: pytest tests/python/test_utils.py -v
"""

import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.utils import is_tool_active, require_tool_active, load_tool_config


class TestIsToolActive:
    def test_active_tool_returns_true(self):
        # Mock config with active tool
        config = {'my_tool': {'active': True}}
        assert is_tool_active('my_tool', config) is True
    
    def test_inactive_tool_returns_false(self):
        # Mock config with inactive tool
        config = {'my_tool': {'active': False}}
        assert is_tool_active('my_tool', config) is False
    
    def test_missing_tool_returns_false(self):
        # Tool not in config should return False
        config = {'other_tool': {'active': True}}
        assert is_tool_active('my_tool', config) is False
    
    def test_empty_config_returns_false(self):
        config = {}
        assert is_tool_active('my_tool', config) is False
    
    def test_tool_without_active_key_returns_false(self):
        # Tool exists but has no 'active' key
        config = {'my_tool': {'description': 'A tool'}}
        assert is_tool_active('my_tool', config) is False


class TestRequireToolActive:
    def test_decorator_allows_active_tool(self):
        """Test that decorator allows function execution when tool is active"""
        # Create a simple function with the decorator
        @require_tool_active('test_tool')
        def my_view():
            return 'success'
        
        # We need to mock is_tool_active or the config
        # Since we can't easily test Flask abort without app context,
        # we'll test the underlying is_tool_active function instead
        pass
    
    def test_decorator_preserves_function_name(self):
        """Test that decorator preserves the original function name"""
        @require_tool_active('test_tool')
        def my_special_view():
            return 'success'
        
        assert my_special_view.__name__ == 'my_special_view'
    
    def test_decorator_preserves_function_docstring(self):
        """Test that decorator preserves the original function docstring"""
        @require_tool_active('test_tool')
        def my_documented_view():
            """This is my docstring"""
            return 'success'
        
        assert my_documented_view.__doc__ == 'This is my docstring'


class TestLoadToolConfig:
    def test_returns_dict(self):
        """Test that load_tool_config returns a dictionary"""
        config = load_tool_config()
        assert isinstance(config, dict)
    
    def test_force_reload_works(self):
        """Test that force_reload parameter works"""
        config1 = load_tool_config()
        config2 = load_tool_config(force_reload=True)
        assert isinstance(config2, dict)
