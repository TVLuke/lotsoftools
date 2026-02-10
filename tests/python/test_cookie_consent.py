"""
Tests for cookie consent functionality
Run with: pytest tests/python/test_cookie_consent.py -v
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.routes.cookie_consent import log_js_capable_user


class TestCookieConsent:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_request = Mock()
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        self.test_url = "/tools/qr-generator"
    
    @patch('app.routes.cookie_consent.open', create=True)
    @patch('app.routes.cookie_consent.os.makedirs')
    @patch('app.routes.cookie_consent.os.path.exists')
    def test_log_js_capable_user_success(self, mock_exists, mock_makedirs, mock_open):
        """Test successful logging of JavaScript-capable user."""
        # Setup mocks
        mock_exists.return_value = True
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock bot detection to return human
        with patch('app.routes.cookie_consent.is_bot_request', return_value=(False, "Human")):
            result = log_js_capable_user(self.test_user_agent, self.test_url)
            
            # Verify success
            assert result is True
            
            # Verify file was written
            mock_file.write.assert_called_once()
            
            # Check log entry format
            log_entry = mock_file.write.call_args[0][0]
            assert "HUMAN_BY_UA" in log_entry
            assert self.test_user_agent in log_entry
            assert self.test_url in log_entry
    
    @patch('app.routes.cookie_consent.open', create=True)
    @patch('app.routes.cookie_consent.os.makedirs')
    @patch('app.routes.cookie_consent.os.path.exists')
    def test_log_js_capable_user_bot(self, mock_exists, mock_makedirs, mock_open):
        """Test logging of user detected as bot by UA analysis."""
        # Setup mocks
        mock_exists.return_value = True
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock bot detection to return bot
        with patch('app.routes.cookie_consent.is_bot_request', return_value=(True, "Chrome 83 (old Chrome)")):
            result = log_js_capable_user(self.test_user_agent, self.test_url)
            
            # Verify success (we still log JS-capable bots)
            assert result is True
            
            # Check log entry format
            log_entry = mock_file.write.call_args[0][0]
            assert "BOT" in log_entry
            assert "old Chrome" in log_entry
    
    def test_log_js_capable_user_exception(self):
        """Test handling of exceptions during logging."""
        # Mock is_bot_request to raise an exception
        with patch('app.routes.cookie_consent.is_bot_request', side_effect=Exception("Test error")):
            result = log_js_capable_user(self.test_user_agent, self.test_url)
            
            # Should return False but not raise exception
            assert result is False
    
    @patch('app.routes.cookie_consent.open', create=True)
    @patch('app.routes.cookie_consent.os.makedirs')
    @patch('app.routes.cookie_consent.os.path.exists')
    def test_log_entry_sanitization(self, mock_exists, mock_makedirs, mock_open):
        """Test that log entries are properly sanitized."""
        # Setup mocks
        mock_exists.return_value = True
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test with problematic characters
        dangerous_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n|Chrome/130.0.0.0 Safari/537.36"
        dangerous_url = "/tools/qr-generator\n|malicious"
        
        with patch('app.routes.cookie_consent.is_bot_request', return_value=(False, "Human")):
            log_js_capable_user(dangerous_ua, dangerous_url)
            
            # Check log entry format
            log_entry = mock_file.write.call_args[0][0]
            
            # Newlines should be replaced with spaces
            assert "\n" not in log_entry
            assert " " in log_entry
            
            # Pipe characters should be replaced with spaces
            assert "|" not in log_entry


class TestCookieConsentAPI:
    def setup_method(self):
        """Set up test fixtures for API tests."""
        self.app = Mock()
        self.app.test_client_context = Mock()
    
    def test_accept_endpoint_success(self):
        """Test successful JavaScript capability logging."""
        from app.routes.cookie_consent import cookie_consent_bp
        
        # Create a test Flask app context
        with patch('app.routes.cookie_consent.request') as mock_request:
            mock_request.headers.get.return_value = self.test_user_agent
            mock_request.is_json = True
            mock_request.json = {'url': '/tools/qr-generator'}
            mock_request.referrer = 'https://lotsof.tools/tools/qr-generator'
            
            # Mock the log function
            with patch('app.routes.cookie_consent.log_js_capable_user', return_value=True) as mock_log:
                # Import and test the function directly
                from app.routes.cookie_consent import log_js_capable
                
                # Call the function
                response = log_js_capable()
                
                # Verify response
                response_data = response[0] if isinstance(response, tuple) else response
                assert response_data['success'] is True
                
                # Verify logging was called
                mock_log.assert_called_once()
    
    def test_js_capable_endpoint_logging_failure(self):
        """Test JavaScript capability logging when logging fails."""
        from app.routes.cookie_consent import cookie_consent_bp
        
        with patch('app.routes.cookie_consent.request') as mock_request:
            mock_request.headers.get.return_value = self.test_user_agent
            mock_request.is_json = True
            mock_request.json = {'url': '/tools/qr-generator'}
            
            # Mock the log function to fail
            with patch('app.routes.cookie_consent.log_js_capable_user', return_value=False):
                from app.routes.cookie_consent import log_js_capable
                
                # Call the function
                response = log_js_capable()
                
                # Should still succeed (logging failure doesn't block user experience)
                response_data = response[0] if isinstance(response, tuple) else response
                assert response_data['success'] is True
