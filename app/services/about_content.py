import os


def load_about_content(lang='en'):
    """
    Load about content HTML for the given language.
    Looks for about_content.{lang}.html in app/config/
    Falls back to English if the requested language is not found.
    Returns empty string if no content file exists.
    """
    config_dir = os.path.join('app', 'config')
    
    # Try requested language first
    content_file = os.path.join(config_dir, f'about_content.{lang}.html')
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            pass
    
    # Fall back to English
    if lang != 'en':
        content_file = os.path.join(config_dir, 'about_content.en.html')
        if os.path.exists(content_file):
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
    
    return ''
