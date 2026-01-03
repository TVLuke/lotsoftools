import json
import os
from app import db
from app.models.link import Link

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

def init_tools():
    tools_dir = os.path.join('app', 'routes', 'tools')
    if not os.path.exists(tools_dir):
        return
    
    for filename in os.listdir(tools_dir):
        if filename.endswith('_tool.json'):
            json_path = os.path.join(tools_dir, filename)
            register_tool_from_json(json_path)
