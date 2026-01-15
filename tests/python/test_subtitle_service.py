"""
Tests for Subtitle Service
Run with: pytest tests/python/test_subtitle_service.py -v
"""

import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.subtitle_service import (
    get_supported_formats,
    get_format_from_filename,
    is_valid_format,
    load_subtitle_string,
    convert_subtitle_to_string,
    convert_string_to_string,
)


class TestGetSupportedFormats:
    def test_returns_dict(self):
        formats = get_supported_formats()
        assert isinstance(formats, dict)
    
    def test_contains_common_formats(self):
        formats = get_supported_formats()
        assert 'srt' in formats
        assert 'ass' in formats
        assert 'vtt' in formats
    
    def test_returns_copy(self):
        formats1 = get_supported_formats()
        formats2 = get_supported_formats()
        formats1['test'] = 'test'
        assert 'test' not in formats2


class TestGetFormatFromFilename:
    def test_srt_extension(self):
        assert get_format_from_filename('movie.srt') == 'srt'
    
    def test_ass_extension(self):
        assert get_format_from_filename('movie.ass') == 'ass'
    
    def test_vtt_extension(self):
        assert get_format_from_filename('movie.vtt') == 'vtt'
    
    def test_uppercase_extension(self):
        assert get_format_from_filename('movie.SRT') == 'srt'
    
    def test_unknown_extension(self):
        assert get_format_from_filename('movie.xyz') is None
    
    def test_no_extension(self):
        assert get_format_from_filename('movie') is None


class TestIsValidFormat:
    def test_valid_formats(self):
        assert is_valid_format('srt') is True
        assert is_valid_format('ass') is True
        assert is_valid_format('vtt') is True
        assert is_valid_format('ssa') is True
    
    def test_invalid_format(self):
        assert is_valid_format('invalid') is False
        assert is_valid_format('') is False
    
    def test_case_insensitive(self):
        assert is_valid_format('SRT') is True
        assert is_valid_format('Srt') is True


class TestLoadSubtitleString:
    def test_load_srt_content(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!

2
00:00:05,000 --> 00:00:08,000
This is a test.
"""
        subs = load_subtitle_string(srt_content, 'srt')
        assert len(subs) == 2
        assert 'Hello' in subs[0].text
        assert 'test' in subs[1].text
    
    def test_empty_content_returns_empty(self):
        # pysubs2 is lenient with invalid content, returns empty subtitles
        subs = load_subtitle_string('', 'srt')
        assert len(subs) == 0


class TestConvertSubtitleToString:
    def test_convert_to_srt(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!
"""
        subs = load_subtitle_string(srt_content, 'srt')
        result = convert_subtitle_to_string(subs, 'srt')
        assert 'Hello' in result
        assert '-->' in result
    
    def test_convert_to_vtt(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!
"""
        subs = load_subtitle_string(srt_content, 'srt')
        result = convert_subtitle_to_string(subs, 'vtt')
        assert 'WEBVTT' in result
        assert 'Hello' in result
    
    def test_invalid_format_raises(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello!
"""
        subs = load_subtitle_string(srt_content, 'srt')
        with pytest.raises(ValueError):
            convert_subtitle_to_string(subs, 'invalid_format')


class TestConvertStringToString:
    def test_srt_to_vtt(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!
"""
        result = convert_string_to_string(srt_content, 'vtt', 'srt')
        assert 'WEBVTT' in result
        assert 'Hello' in result
    
    def test_srt_to_ass(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, world!
"""
        result = convert_string_to_string(srt_content, 'ass', 'srt')
        assert '[Script Info]' in result
        assert 'Hello' in result
