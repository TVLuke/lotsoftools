from flask import session
from app.models.link import Link
from app import db

def get_all_links():
    return Link.query.all()

def get_link_by_url(url):
    return Link.query.filter_by(url=url).first()

def increment_click_count(url):
    """Increment the click count for a link by its URL"""
    link = get_link_by_url(url)
    if link:
        link.click_count = (link.click_count or 0) + 1
        db.session.commit()
        return True
    return False

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
