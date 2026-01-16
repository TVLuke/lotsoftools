import json
import re
import os
from flask import session, request
from app.models.link import Link
from app import db

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright'
]

def _load_bot_patterns():
    """Load regex patterns from well-known-bots.json"""
    global _bot_regex_patterns
    if _bot_regex_patterns:
        return
    
    json_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'well-known-bots-main', 'well-known-bots.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            bots = json.load(f)
            for bot in bots:
                patterns = bot.get('pattern', {}).get('accepted', [])
                for pattern in patterns:
                    try:
                        _bot_regex_patterns.append(re.compile(pattern, re.IGNORECASE))
                    except re.error:
                        pass
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def is_bot_request():
    """Check if the current request is from a bot/crawler based on User-Agent."""
    _load_bot_patterns()
    
    user_agent = request.headers.get('User-Agent', '')
    user_agent_lower = user_agent.lower()
    
    # No User-Agent is suspicious
    if not user_agent:
        return True
    
    # Check against simple patterns (fast)
    for pattern in _bot_simple_patterns:
        if pattern in user_agent_lower:
            return True
    
    # Check against regex patterns from well-known-bots.json
    for regex in _bot_regex_patterns:
        if regex.search(user_agent):
            return True
    
    return False

def get_all_links():
    return Link.query.all()

def get_link_by_url(url):
    return Link.query.filter_by(url=url).first()

def increment_click_count(url):
    """Increment the click count for a link by its URL. Separates bot vs human clicks."""
    link = get_link_by_url(url)
    if link:
        if is_bot_request():
            link.bot_click_count = (link.bot_click_count or 0) + 1
        else:
            link.click_count = (link.click_count or 0) + 1
        db.session.commit()
        return True
    return False

def get_links_stats():
    """Get all links with stats, ordered by click count descending."""
    links = Link.query.order_by(Link.click_count.desc()).all()
    return [{'name': link.name, 'url': link.url, 'click_count': link.click_count or 0, 'bot_click_count': link.bot_click_count or 0} for link in links]

def get_links_by_category(lang=None):
    if lang is None:
        lang = session.get('lang', 'en')
    
    links = get_all_links()
    categories = {}
    
    for link in links:
        link_dict = link.to_dict(lang)
        for tag in link.tags:
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(link_dict)
    
    sorted_categories = dict(sorted(categories.items()))
    
    for category in sorted_categories:
        sorted_categories[category].sort(key=lambda x: x.get('name', '').lower())
    
    return sorted_categories
