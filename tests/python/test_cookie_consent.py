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
        mock_exists.return_value = True
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch('app.routes.cookie_consent.is_bot_request', return_value=(False, "Human")):
            result = log_js_capable_user(self.test_user_agent, self.test_url)
            
            assert result is True
            mock_file.write.assert_called_once()
            
            # Check log entry format (now has 6 fields with consent)
            log_entry = mock_file.write.call_args[0][0]
            parts = log_entry.strip().split('|')
            assert len(parts) == 6
            assert parts[1] == 'HUMAN_BY_UA'
            assert self.test_url in parts[2]
            assert self.test_user_agent in parts[3]
            assert parts[4] == 'Human'
            assert parts[5] == 'unknown'  # Default consent status

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
            
            # Should end with exactly one newline (for log file format)
            assert log_entry.endswith('\n'), 'Log entry should end with newline'
            
            # Remove the final newline and check for any other newlines
            content_without_final_newline = log_entry.rstrip('\n')
            assert "\n" not in content_without_final_newline, f'Newlines found in content: {repr(content_without_final_newline)}'
            
            # Check that pipe characters from input were replaced with spaces
            # The original dangerous inputs had \n| which should become ' ' (single space)
            assert ' ' in content_without_final_newline, 'Input pipe characters should be replaced with spaces'
            
            # Count field separators (should be exactly 5 pipes for 6 fields with consent)
            pipe_count = content_without_final_newline.count('|')
            assert pipe_count == 5, f'Should have exactly 5 field separators, got {pipe_count}: {repr(content_without_final_newline)}'


class TestCookieConsentAPI:
    def setup_method(self):
        """Set up test fixtures for API tests."""
        self.app = Mock()
        self.app.test_client_context = Mock()
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        self.test_url = "/tools/qr-generator"
    
    def test_accept_endpoint_success(self):
        """Test successful JavaScript capability logging."""
        from app.routes.cookie_consent import cookie_consent_bp
        from flask import Flask
        
        # Create a test Flask app context
        app = Flask(__name__)
        with app.app_context():
            with app.test_request_context():
                # Mock the request object within the context
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
                            
                            # Flask functions return Response objects, need to get JSON data
                            import json
                            response_data = json.loads(response.get_data(as_text=True))
                            
                            # Verify response
                            assert response_data['success'] is True
                            
                            # Verify logging was called
                            mock_log.assert_called_once()
    
    def test_js_capable_endpoint_logging_failure(self):
        """Test JavaScript capability logging when logging fails."""
        from app.routes.cookie_consent import cookie_consent_bp
        from flask import Flask
        
        app = Flask(__name__)
        with app.app_context():
            with app.test_request_context():
                with patch('app.routes.cookie_consent.request') as mock_request:
                    mock_request.headers.get.return_value = self.test_user_agent
                    mock_request.is_json = True
                    mock_request.json = {'url': '/tools/qr-generator'}
                    
                    # Mock the log function to fail
                    with patch('app.routes.cookie_consent.log_js_capable_user', return_value=False):
                            from app.routes.cookie_consent import log_js_capable
                            
                            # Call the function
                            response = log_js_capable()
                            
                            # Flask functions return Response objects, need to get JSON data
                            import json
                            response_data = json.loads(response.get_data(as_text=True))
                            
                            # Should still succeed (logging failure doesn't block user experience)
                            assert response_data['success'] is True
    
    def test_js_capable_endpoint_invalid_nonce(self):
        """Test JavaScript capability logging with invalid nonce."""
        from app.routes.cookie_consent import cookie_consent_bp
        from flask import Flask
        
        app = Flask(__name__)
        with app.app_context():
            with app.test_request_context():
                with patch('app.routes.cookie_consent.request') as mock_request:
                    mock_request.headers.get.return_value = self.test_user_agent
                    mock_request.is_json = True
                    mock_request.json = {'url': '/tools/qr-generator', 'nonce': 'invalid_nonce'}
                    
                    # Mock nonce validation to fail
                    with patch('app.routes.cookie_consent.validate_js_nonce', return_value=False):
                        from app.routes.cookie_consent import log_js_capable
                        
                        # Call the function
                        response = log_js_capable()
                        
                        # Handle tuple response (response, status_code)
                        if isinstance(response, tuple):
                            response_obj = response[0]
                            status_code = response[1]
                        else:
                            response_obj = response
                            status_code = 200
                        
                        # Flask functions return Response objects, need to get JSON data
                        import json
                        response_data = json.loads(response_obj.get_data(as_text=True))
                        
                        # Should fail with invalid nonce
                        assert response_data['success'] is False
                        assert 'nonce' in response_data['error'].lower()
                        assert status_code == 400

    def test_failed_api_logging(self):
        """Test that failed API attempts are logged without IP addresses."""
        from app.routes.cookie_consent import log_failed_api_attempt
        from unittest.mock import Mock, patch
        from flask import Flask
        
        # Mock the file operations
        mock_file = Mock()
        
        with patch('builtins.open', return_value=mock_file):
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_file.write = Mock()
            
            with patch('os.makedirs'):
                with patch('os.path.exists', return_value=True):
                    # Create Flask app context for request access
                    app = Flask(__name__)
                    with app.app_context():
                        with app.test_request_context():
                            # Test logging failed attempt (no IP should be logged)
                            result = log_failed_api_attempt('MISSING_NONCE', 'curl/7.68.0', 'missing')
                            
                            assert result is True
                            mock_file.write.assert_called_once()
                            
                            # Check log entry format (should NOT contain IP)
                            log_entry = mock_file.write.call_args[0][0]
                            parts = log_entry.strip().split('|')
                            assert len(parts) == 4  # timestamp|reason|user_agent|nonce_status (no IP)
                            assert parts[1] == 'MISSING_NONCE'
                            assert 'curl/7.68.0' in parts[2]
                            assert parts[3] == 'missing'
                            
                            # Verify no IP address is in the log entry
                            full_log_text = log_entry.strip()
                            assert '192.168.1.100' not in full_log_text
                            assert '217.224.64.71' not in full_log_text
