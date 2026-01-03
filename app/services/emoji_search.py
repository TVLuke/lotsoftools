import re
import random
from typing import Any

import emoji


SUPPORTED_LANGS: list[str] = [
    'en',
    'de',
    'es',
    'pt',
    'it',
    'fr',
    'fa',
    'id',
    'zh',
    'ja',
    'ko',
    'ru',
    'ar',
    'tr',
]


def _safe_load_languages() -> None:
    for lang in SUPPORTED_LANGS:
        if lang == 'en':
            continue
        try:
            emoji.config.load_language(lang)
        except Exception:
            pass


_safe_load_languages()


_EMOJI_KEYS: list[str] = list(emoji.EMOJI_DATA.keys())


_U_PLUS_RE = re.compile(r"U\+([0-9A-Fa-f]{4,6})")


def _to_codepoints(s: str) -> list[str]:
    return [f"U+{ord(ch):04X}" for ch in s]


def _normalize_query(q: str) -> str:
    return q.strip().lower()


def _strip_colons(s: str) -> str:
    s = s.strip()
    if s.startswith(':') and s.endswith(':') and len(s) >= 2:
        return s[1:-1]
    return s


_NON_ALNUM_RE = re.compile(r"[^0-9a-z]+")


def _slugify(s: str) -> str:
    s = _normalize_query(s)
    s = _strip_colons(s)
    s = _NON_ALNUM_RE.sub('_', s)
    s = re.sub(r"_+", "_", s).strip('_')
    return s


def _parse_u_plus_query(q: str) -> str | None:
    matches = _U_PLUS_RE.findall(q)
    if not matches:
        return None
    try:
        chars = ''.join(chr(int(h, 16)) for h in matches)
        return chars
    except Exception:
        return None


def _emoji_from_query(q: str) -> str | None:
    q = q.strip()

    u_plus = _parse_u_plus_query(q)
    if u_plus and u_plus in emoji.EMOJI_DATA:
        return u_plus

    if q in emoji.EMOJI_DATA:
        return q

    tokens = list(emoji.analyze(q))
    for t in tokens:
        if hasattr(t, 'value') and getattr(t.value, 'emoji', None):
            candidate = t.value.emoji
            if candidate in emoji.EMOJI_DATA:
                return candidate

    if emoji.is_emoji(q) and q in emoji.EMOJI_DATA:
        return q

    return None


def _names_for_emoji(e: str) -> dict[str, str]:
    data = emoji.EMOJI_DATA.get(e, {})
    out: dict[str, str] = {}
    for lang in SUPPORTED_LANGS:
        val = data.get(lang)
        if isinstance(val, str) and val:
            out[lang] = val
    return out


def _aliases_for_emoji(e: str) -> list[str]:
    data = emoji.EMOJI_DATA.get(e, {})
    aliases = data.get('alias')
    if isinstance(aliases, list):
        return [a for a in aliases if isinstance(a, str) and a]
    return []


def _search_text_for_emoji(e: str, lang: str | None) -> list[str]:
    names = _names_for_emoji(e)
    aliases = _aliases_for_emoji(e)

    if lang and lang != 'all':
        parts: list[str] = []
        if lang in names:
            parts.append(names[lang])
        if lang == 'en':
            parts.extend(aliases)
        return parts

    return list(names.values()) + aliases


def search_emojis(
    query: str,
    lang: str = 'all',
    limit: int = 200,
    offset: int = 0,
) -> dict[str, Any]:
    lang = (lang or 'all').strip().lower()
    if lang not in SUPPORTED_LANGS and lang != 'all':
        lang = 'all'

    limit = max(1, min(int(limit or 200), 500))
    offset = max(0, int(offset or 0))

    q = query or ''
    qn = _normalize_query(q)

    if not qn:
        sample_size = max(1, min(limit, len(_EMOJI_KEYS)))
        picked = random.sample(_EMOJI_KEYS, k=sample_size)
        items: list[dict[str, Any]] = []
        for e in picked:
            data = emoji.EMOJI_DATA.get(e, {})
            items.append({
                'emoji': e,
                'names': _names_for_emoji(e),
                'aliases': _aliases_for_emoji(e),
                'codepoints': _to_codepoints(e),
                'status': data.get('status'),
                'version': data.get('E'),
            })

        return {
            'query': '',
            'lang': lang,
            'offset': 0,
            'limit': sample_size,
            'total': sample_size,
            'items': items,
            'random': True,
        }

    exact: list[dict[str, Any]] = []
    matches: list[tuple[int, str]] = []

    if qn:
        e = _emoji_from_query(q)
        if e:
            names = _names_for_emoji(e)
            exact.append({
                'emoji': e,
                'names': names,
                'aliases': _aliases_for_emoji(e),
                'codepoints': _to_codepoints(e),
                'status': emoji.EMOJI_DATA.get(e, {}).get('status'),
                'version': emoji.EMOJI_DATA.get(e, {}).get('E'),
            })

    if qn:
        qn_no_colons = _strip_colons(qn)
        q_slug = _slugify(qn_no_colons)
        q_tokens = [t for t in q_slug.split('_') if t]
        for e in _EMOJI_KEYS:
            if exact and e == exact[0]['emoji']:
                continue

            codepoints = _to_codepoints(e)
            if any(cp.lower() == qn for cp in codepoints):
                matches.append((0, e))
                continue

            if qn.startswith('u+'):
                if any(cp.lower() == qn for cp in codepoints):
                    matches.append((0, e))
                    continue

            texts = _search_text_for_emoji(e, lang)
            best_rank: int | None = None
            for t in texts:
                tn = _normalize_query(t)
                if not tn:
                    continue

                tn_stripped = _strip_colons(tn)
                tn_slug = _slugify(tn_stripped)

                if tn_slug == q_slug:
                    best_rank = 0
                    break

                if q_slug and tn_slug.startswith(q_slug):
                    best_rank = min(best_rank, 1) if best_rank is not None else 1
                elif q_slug and q_slug in tn_slug:
                    best_rank = min(best_rank, 2) if best_rank is not None else 2
                elif q_tokens and all(tok in tn_slug for tok in q_tokens):
                    best_rank = min(best_rank, 3) if best_rank is not None else 3

            if best_rank is not None:
                matches.append((best_rank, e))

    matches.sort(key=lambda x: (x[0], x[1]))

    total = len(exact) + len(matches)
    page_emojis = [e for _, e in matches][offset:offset + limit]

    items: list[dict[str, Any]] = []
    items.extend(exact)

    for e in page_emojis:
        data = emoji.EMOJI_DATA.get(e, {})
        items.append({
            'emoji': e,
            'names': _names_for_emoji(e),
            'aliases': _aliases_for_emoji(e),
            'codepoints': _to_codepoints(e),
            'status': data.get('status'),
            'version': data.get('E'),
        })

    return {
        'query': query,
        'lang': lang,
        'offset': offset,
        'limit': limit,
        'total': total,
        'items': items,
    }
