import json
import re
import os
from datetime import datetime
from flask import session, request
from app.models.link import Link
from app import db

# Server start time for stats display
_server_start_time = datetime.now()

def get_server_start_time():
    """Get the server start time."""
    return _server_start_time

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright', 'claudebot', 'req/',
    'python-requests/'
]

# In-memory tracking of user agents and their click counts
_user_agent_counts = {}  # {user_agent: {'count': N, 'is_bot': bool}}

def get_user_agent_stats():
    """Get user agent statistics sorted by count descending."""
    return sorted(_user_agent_counts.items(), key=lambda x: x[1]['count'], reverse=True)

def get_bot_user_agents():
    """Get only bot user agents sorted by count descending."""
    bots = [(ua, data) for ua, data in _user_agent_counts.items() if data['is_bot']]
    return sorted(bots, key=lambda x: x[1]['count'], reverse=True)

def get_human_user_agents():
    """Get only human user agents sorted by count descending."""
    humans = [(ua, data) for ua, data in _user_agent_counts.items() if not data['is_bot']]
    return sorted(humans, key=lambda x: x[1]['count'], reverse=True)

def track_user_agent(user_agent, is_bot):
    """Track user agent and increment its count."""
    if user_agent in _user_agent_counts:
        _user_agent_counts[user_agent]['count'] += 1
    else:
        _user_agent_counts[user_agent] = {'count': 1, 'is_bot': is_bot}

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
        user_agent = request.headers.get('User-Agent', '')
        is_bot = is_bot_request()
        track_user_agent(user_agent, is_bot)
        if is_bot:
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


def get_related_tools(current_url, limit=4, lang=None):
    """Get related tools based on shared tags, excluding current tool."""
    if lang is None:
        lang = session.get('lang', 'en')
    
    current_link = get_link_by_url(current_url)
    if not current_link or not current_link.tags:
        return []
    
    current_tags = set(current_link.tags)
    all_links = get_all_links()
    
    # Score links by number of shared tags
    scored_links = []
    for link in all_links:
        if link.url == current_url:
            continue
        shared_tags = len(current_tags & set(link.tags))
        if shared_tags > 0:
            scored_links.append((shared_tags, link))
    
    # Sort by score (descending), then by name
    scored_links.sort(key=lambda x: (-x[0], x[1].get_name(lang).lower()))
    
    # Return top N as dicts
    return [link.to_dict(lang) for _, link in scored_links[:limit]]
