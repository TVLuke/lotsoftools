"""
Tests for bot detection functionality
Run with: pytest tests/python/test_bot_detection.py -v
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.bot_detection import is_bot_request


# Bot detection test cases organized by category
BOT_DETECTION_TEST_CASES = {
    "old_browsers": [
        {
            "name": "Windows NT 6.1 (old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "Windows NT 6.1 (old Windows)"
        },
        {
            "name": "Chrome 83 (old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "Chrome 83 (old Chrome)"
        },
        {
            "name": "Chrome 144 (current)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": False,
            "expected_reason": "Human"
        },
        {
            "name": "Firefox 77 (old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "Firefox 77 (old Firefox)"
        },
        {
            "name": "Firefox 109 (current)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": False,
            "expected_reason": "Human"
        },
        {
            "name": "Edge 12.246 (very old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "Edge 12.246 (old browser)"
        },
        {
            "name": "Opera 7.50 (Windows XP)",
            "headers": {
                "User-Agent": "Opera/7.50 (Windows XP; U)",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "Windows XP/2000 (very old OS)"
        }
    ],
    "mobile_os": [
        {
            "name": "iOS 13.2.3 (old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "ios 13.2.3 (old iOS)"
        },
        {
            "name": "iOS 16.0 (current)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": False,
            "expected_reason": "Human"
        },
        {
            "name": "Android 6.0 (old)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": False,
            "expected_reason": "Human"
        },
        {
            "name": "Android 13 (current)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": False,
            "expected_reason": "Human"
        }
    ],
    "suspicious_patterns": [
        {
            "name": "No User-Agent",
            "headers": {
                "User-Agent": "",
                "Referer": "",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "No User-Agent header"
        },
        {
            "name": "lotsof.tools subdomain referer",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "https://m.lotsof.tools/",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "lotsof.tools subdomain referer (bot)"
        },
        {
            "name": "IP address referer",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "http://152.53.202.205:80/",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "IP address referer (bot)"
        },
        {
            "name": "No cookies or Accept-Language",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "",
                "Accept-Language": ""
            },
            "cookies": {},
            "expected_bot": True,
            "expected_reason": "No cookies or Accept-Language"
        },
        {
            "name": "No Accept-Language header",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "",
                "Accept-Language": ""
            },
            "cookies": {"session": "test"},
            "expected_bot": True,
            "expected_reason": "No Accept-Language header"
        }
    ],
    "legitimate_users": [
        {
            "name": "Modern Chrome with cookies",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Referer": "https://google.com/",
                "Accept-Language": "en-US,en;q=0.9,de;q=0.8"
            },
            "cookies": {"session": "test", "preferences": "dark"},
            "expected_bot": False,
            "expected_reason": "Human"
        },
        {
            "name": "Modern Firefox with cookies",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
                "Referer": "https://duckduckgo.com/",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.8"
            },
            "cookies": {"session_id": "abc123"},
            "expected_bot": False,
            "expected_reason": "Human"
        }
    ]
}


class TestBotDetection:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock Flask request context
        self.mock_request = Mock()
    
    @pytest.mark.parametrize("test_case", BOT_DETECTION_TEST_CASES["old_browsers"], ids=lambda x: x.get("name", "unnamed"))
    def test_old_browsers(self, test_case):
        """Test old browser versions."""
        self._run_test_case(test_case)
    
    @pytest.mark.parametrize("test_case", BOT_DETECTION_TEST_CASES["mobile_os"], ids=lambda x: x.get("name", "unnamed"))
    def test_mobile_os(self, test_case):
        """Test mobile operating systems."""
        self._run_test_case(test_case)
    
    @pytest.mark.parametrize("test_case", BOT_DETECTION_TEST_CASES["suspicious_patterns"], ids=lambda x: x.get("name", "unnamed"))
    def test_suspicious_patterns(self, test_case):
        """Test suspicious patterns."""
        self._run_test_case(test_case)
    
    @pytest.mark.parametrize("test_case", BOT_DETECTION_TEST_CASES["legitimate_users"], ids=lambda x: x.get("name", "unnamed"))
    def test_legitimate_users(self, test_case):
        """Test legitimate users."""
        self._run_test_case(test_case)
    
    def _run_test_case(self, test_case):
        """Helper method to run a single test case."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr('app.services.bot_detection.request', self.mock_request)
            
            # Set up headers
            def mock_headers(key, default=''):
                return test_case.get('headers', {}).get(key, default)
            
            self.mock_request.headers.get.side_effect = mock_headers
            self.mock_request.cookies = test_case.get('cookies', {})
            
            is_bot, reason = is_bot_request()
            
            assert is_bot == test_case['expected_bot'], f"Expected bot={test_case['expected_bot']}, got bot={is_bot}"
            assert reason == test_case['expected_reason'], f"Expected reason='{test_case['expected_reason']}', got reason='{reason}'"
        
    
