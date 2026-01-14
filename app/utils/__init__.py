import json
import os
from functools import wraps
from flask import abort

# Cache for tool config
_tool_config_cache = None

def load_tool_config(force_reload=False):
    """Load tool configuration from config file (cached)"""
    global _tool_config_cache
    if _tool_config_cache is not None and not force_reload:
        return _tool_config_cache
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'tool_config.json')
    if not os.path.exists(config_path):
        _tool_config_cache = {}
        return _tool_config_cache
    
    try:
        with open(config_path, 'r') as f:
            _tool_config_cache = json.load(f)
            return _tool_config_cache
    except Exception:
        _tool_config_cache = {}
        return _tool_config_cache

def is_tool_active(tool_name, tool_config=None):
    """Check if a tool is active in the config (default: False if not in config)"""
    if tool_config is None:
        tool_config = load_tool_config()
    if tool_name not in tool_config:
        return False
    return tool_config[tool_name].get('active', False)

def require_tool_active(tool_name):
    """Decorator to check if a tool is active before serving its route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_tool_active(tool_name):
                abort(404)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_db():
    """Lazy import of db to avoid circular imports"""
    from app import db
    return db

def get_link_model():
    """Lazy import of Link model to avoid circular imports"""
    from app.models.link import Link
    return Link

def register_tool_from_json(json_path):
    if not os.path.exists(json_path):
        return
    
    with open(json_path, 'r') as f:
        tool_data = json.load(f)
    
    route = tool_data.get('route')
    if not route:
        return
    
    try:
        db = get_db()
        Link = get_link_model()
        existing_link = Link.query.filter_by(url=route).first()
        
        if existing_link:
            existing_link.name = tool_data.get('name', {})
            existing_link.img = tool_data.get('img', '')
            existing_link.description = tool_data.get('description', {})
            existing_link.tags = tool_data.get('tags', [])
            existing_link.new_window = tool_data.get('new_window', False)
            existing_link.frontend_only = tool_data.get('frontend_only', False)
            existing_link.uses_external_service = tool_data.get('uses_external_service', False)
        else:
            new_link = Link(
                url=route,
                img=tool_data.get('img', ''),
                new_window=tool_data.get('new_window', False),
                frontend_only=tool_data.get('frontend_only', False),
                uses_external_service=tool_data.get('uses_external_service', False)
            )
            new_link.name = tool_data.get('name', {})
            new_link.description = tool_data.get('description', {})
            new_link.tags = tool_data.get('tags', [])
            db.session.add(new_link)
        
        db.session.commit()
    except Exception:
        pass

def get_tool_name_from_filename(filename):
    """Extract tool name from filename (e.g., 'qr_generator_tool.json' -> 'qr_generator')"""
    if filename.endswith('_tool.json'):
        return filename[:-10]  # Remove '_tool.json'
    return None

def remove_tool_from_db(route):
    """Remove a tool from the database by its route"""
    try:
        db = get_db()
        Link = get_link_model()
        existing_link = Link.query.filter_by(url=route).first()
        if existing_link:
            db.session.delete(existing_link)
            db.session.commit()
            print(f"Removed inactive tool: {route}")
    except Exception as e:
        print(f"Error removing tool {route}: {e}")

def init_tools():
    """Initialize tools based on tool_config.json - register active, remove inactive"""
    tools_dir = os.path.join('app', 'routes', 'tools')
    if not os.path.exists(tools_dir):
        return
    
    tool_config = load_tool_config(force_reload=True)
    
    for filename in os.listdir(tools_dir):
        if filename.endswith('_tool.json'):
            tool_name = get_tool_name_from_filename(filename)
            if not tool_name:
                continue
            
            json_path = os.path.join(tools_dir, filename)
            
            # Load tool data to get route
            try:
                with open(json_path, 'r') as f:
                    tool_data = json.load(f)
                route = tool_data.get('route')
            except Exception:
                continue
            
            # Check if tool is active
            if is_tool_active(tool_name, tool_config):
                register_tool_from_json(json_path)
            else:
                # Remove inactive tool from database
                if route:
                    remove_tool_from_db(route)
