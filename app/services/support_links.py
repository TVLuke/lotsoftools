import json
import os


def _get_localized_text(text_map, lang, fallback):
    if not isinstance(text_map, dict):
        return fallback
    if isinstance(lang, str) and lang in text_map and text_map.get(lang):
        return text_map.get(lang)
    if 'en' in text_map and text_map.get('en'):
        return text_map.get('en')
    return fallback


def support_placement_enabled(link, placement):
    if not isinstance(link, dict):
        return False

    placements = link.get('placements')
    if not isinstance(placements, dict):
        return False

    p = placements.get(placement)
    if isinstance(p, bool):
        return p
    if isinstance(p, dict):
        enabled = p.get('enabled')
        return bool(enabled)
    return False


def support_link_text(link, placement, lang):
    if not isinstance(link, dict):
        return ''

    url = link.get('url') if isinstance(link.get('url'), str) else ''

    # New format: placements.<placement>.text
    placements = link.get('placements')
    if isinstance(placements, dict):
        p = placements.get(placement)
        if isinstance(p, dict):
            placement_text = p.get('text')
            t = _get_localized_text(placement_text, lang, None)
            if t:
                return t

    # Backward-compatibility: top-level text
    return _get_localized_text(link.get('text'), lang, url)


def load_support_links():
    import base64
    # Try environment variable first (for Docker deployments)
    # Supports both raw JSON and base64-encoded JSON
    env_config = os.environ.get('SUPPORT_CONFIG')
    if env_config:
        try:
            # Try base64 decode first
            decoded = base64.b64decode(env_config).decode('utf-8')
            data = json.loads(decoded)
        except Exception:
            try:
                # Fall back to raw JSON
                data = json.loads(env_config)
            except Exception:
                data = None
    else:
        # Fall back to config file
        config_path = os.path.join('app', 'config', 'support_config.json')
        if not os.path.exists(config_path):
            return []

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = f.read().strip()
                if not raw:
                    return []
                data = json.loads(raw)
        except Exception:
            return []
    
    if data is None:
        return []

    links = data.get('links') if isinstance(data, dict) else None
    if not isinstance(links, list):
        return []

    cleaned = []
    for item in links:
        if not isinstance(item, dict):
            continue

        url = item.get('url')
        link_type = item.get('type')
        text = item.get('text')
        placements = item.get('placements')

        if not isinstance(url, str) or not url:
            continue
        if not isinstance(link_type, str) or not link_type:
            continue
        if not isinstance(text, dict):
            text = {}
        if not isinstance(placements, dict):
            placements = {}

        # Normalize placements:
        # - old format: {"footer": true, "menu": false}
        # - new format: {"footer": {"enabled": true, "text": {...}}, "menu": {"enabled": true, "text": {...}}}
        normalized_placements = {}
        for key, value in placements.items():
            if isinstance(value, bool):
                normalized_placements[key] = {'enabled': value}
            elif isinstance(value, dict):
                enabled = bool(value.get('enabled'))
                placement_text = value.get('text') if isinstance(value.get('text'), dict) else None
                normalized_placements[key] = {'enabled': enabled}
                if placement_text is not None:
                    normalized_placements[key]['text'] = placement_text

        placements = normalized_placements

        cleaned.append({
            'url': url,
            'type': link_type,
            'text': text,
            'placements': placements,
        })

    return cleaned


def support_icon_class(link_type):
    icon_map = {
        'ko-fi': 'fas fa-coffee',
        'kofi': 'fas fa-coffee',
    }
    return icon_map.get(link_type, 'fas fa-heart')
