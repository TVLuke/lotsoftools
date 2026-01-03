import json
import os
from app import db
from app.models.link import Link

def load_tool_config():
    """Load tool configuration from config file"""
    config_path = os.path.join('app', 'config', 'tool_config.json')
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def get_tool_name_from_filename(filename):
    """Extract tool name from filename (e.g., 'qr_generator_tool.json' -> 'qr_generator')"""
    if filename.endswith('_tool.json'):
        return filename[:-10]  # Remove '_tool.json'
    return None

def is_tool_active(tool_name, tool_config):
    """Check if a tool is active in the config (default: False if not in config)"""
    if tool_name not in tool_config:
        return False
    return tool_config[tool_name].get('active', False)

def register_tool_from_json(json_path):
    if not os.path.exists(json_path):
        return
    
    with open(json_path, 'r') as f:
        tool_data = json.load(f)
    
    route = tool_data.get('route')
    if not route:
        return
    
    try:
        existing_link = Link.query.filter_by(url=route).first()
        
        if existing_link:
            existing_link.name = tool_data.get('name', {})
            existing_link.img = tool_data.get('img', '')
            existing_link.description = tool_data.get('description', {})
            existing_link.tags = tool_data.get('tags', [])
            existing_link.new_window = tool_data.get('new_window', False)
            existing_link.frontend_only = tool_data.get('frontend_only', False)
        else:
            new_link = Link(
                url=route,
                img=tool_data.get('img', ''),
                new_window=tool_data.get('new_window', False),
                frontend_only=tool_data.get('frontend_only', False)
            )
            new_link.name = tool_data.get('name', {})
            new_link.description = tool_data.get('description', {})
            new_link.tags = tool_data.get('tags', [])
            db.session.add(new_link)
        
        db.session.commit()
    except Exception:
        pass

def remove_tool_from_db(route):
    """Remove a tool from the database by its route"""
    try:
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
    
    # Load tool configuration
    tool_config = load_tool_config()
    
    # Track all tool routes from JSON files
    tool_routes = {}
    
    # Process all tool JSON files
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
                if route:
                    tool_routes[tool_name] = route
            except Exception:
                continue
            
            # Check if tool is active
            if is_tool_active(tool_name, tool_config):
                # Register active tool
                register_tool_from_json(json_path)
            else:
                # Remove inactive tool from database
                if route:
                    remove_tool_from_db(route)
