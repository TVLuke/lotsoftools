"""
Subtitle Converter Service
Provides functions to convert between subtitle formats using pysubs2.
"""

import pysubs2
import os

# Supported formats
FORMATS = {
    'srt': 'srt',
    'ass': 'ass',
    'ssa': 'ssa',
    'vtt': 'vtt',
    'ttml': 'ttml',
    'sami': 'sami',
    'tmp': 'tmp',
    'mpl2': 'mpl2',
    'microdvd': 'microdvd'
}


def get_supported_formats():
    """Return dictionary of supported formats."""
    return FORMATS.copy()


def get_format_from_filename(filename):
    """Extract format from filename extension.
    
    Args:
        filename: The filename to extract format from
        
    Returns:
        Format string if recognized, None otherwise
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else None
    return FORMATS.get(ext)


def is_valid_format(format_name):
    """Check if a format is supported.
    
    Args:
        format_name: Format string to check
        
    Returns:
        True if format is supported, False otherwise
    """
    return format_name.lower() in FORMATS


def load_subtitle_file(filepath):
    """Load a subtitle file using pysubs2.
    
    Args:
        filepath: Path to the subtitle file
        
    Returns:
        pysubs2.SSAFile object
        
    Raises:
        ValueError: If the file cannot be parsed
    """
    try:
        return pysubs2.load(filepath)
    except Exception as e:
        raise ValueError(f"Failed to parse subtitle file: {str(e)}")


def load_subtitle_string(content, format_hint=None):
    """Load subtitle content from a string.
    
    Args:
        content: Subtitle content as string
        format_hint: Optional format hint (e.g., 'srt', 'ass')
        
    Returns:
        pysubs2.SSAFile object
        
    Raises:
        ValueError: If the content cannot be parsed
    """
    try:
        return pysubs2.SSAFile.from_string(content, format_=format_hint)
    except Exception as e:
        raise ValueError(f"Failed to parse subtitle content: {str(e)}")


def save_subtitle_file(subs, filepath, format_name=None):
    """Save a subtitle file.
    
    Args:
        subs: pysubs2.SSAFile object
        filepath: Path to save to
        format_name: Optional format override (uses extension if not provided)
        
    Raises:
        ValueError: If the file cannot be saved
    """
    try:
        subs.save(filepath, format_=format_name)
    except Exception as e:
        raise ValueError(f"Failed to save subtitle file: {str(e)}")


def convert_subtitle_to_string(subs, format_name):
    """Convert subtitle to string in the specified format.
    
    Args:
        subs: pysubs2.SSAFile object
        format_name: Target format
        
    Returns:
        Subtitle content as string
        
    Raises:
        ValueError: If conversion fails
    """
    if not is_valid_format(format_name):
        raise ValueError(f"Invalid format: {format_name}")
    
    try:
        return subs.to_string(format_name)
    except Exception as e:
        raise ValueError(f"Failed to convert subtitle: {str(e)}")


def convert_subtitle_file(input_path, output_path, target_format=None):
    """Convert a subtitle file from one format to another.
    
    Args:
        input_path: Path to input subtitle file
        output_path: Path to save converted file
        target_format: Target format (uses output extension if not provided)
        
    Returns:
        True on success
        
    Raises:
        ValueError: If conversion fails
    """
    subs = load_subtitle_file(input_path)
    save_subtitle_file(subs, output_path, target_format)
    return True


def convert_string_to_string(content, target_format, source_format=None):
    """Convert subtitle content from one format to another.
    
    Args:
        content: Subtitle content as string
        target_format: Target format
        source_format: Optional source format hint
        
    Returns:
        Converted subtitle content as string
        
    Raises:
        ValueError: If conversion fails
    """
    subs = load_subtitle_string(content, source_format)
    return convert_subtitle_to_string(subs, target_format)
