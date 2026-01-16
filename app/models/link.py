import json
from app import db

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(2000), nullable=False)
    img = db.Column(db.String(128), nullable=False)
    _description = db.Column(db.Text, default='{}')
    _tags = db.Column(db.Text, default='[]')
    new_window = db.Column(db.Boolean, default=True)
    frontend_only = db.Column(db.Boolean, default=False)
    uses_external_service = db.Column(db.Boolean, default=False)
    click_count = db.Column(db.Integer, default=0)
    bot_click_count = db.Column(db.Integer, default=0)
    
    @property
    def name(self):
        try:
            return json.loads(self._name)
        except (TypeError, json.JSONDecodeError):
            return {}
    
    @name.setter
    def name(self, value):
        if isinstance(value, dict):
            self._name = json.dumps(value)
        else:
            self._name = json.dumps({})
    
    @property
    def description(self):
        try:
            return json.loads(self._description)
        except (TypeError, json.JSONDecodeError):
            return {}
    
    @description.setter
    def description(self, value):
        if isinstance(value, dict):
            self._description = json.dumps(value)
        else:
            self._description = json.dumps({})
    
    @property
    def tags(self):
        try:
            return json.loads(self._tags)
        except (TypeError, json.JSONDecodeError):
            return []
    
    @tags.setter
    def tags(self, value):
        if isinstance(value, list):
            self._tags = json.dumps(value)
        else:
            self._tags = '[]'
    
    def get_name(self, lang='en'):
        return self.name.get(lang, self.name.get('en', ''))
    
    def get_description(self, lang='en'):
        return self.description.get(lang, self.description.get('en', ''))
    
    def to_dict(self, lang='en'):
        return {
            'id': self.id,
            'name': self.get_name(lang),
            'url': self.url,
            'img': self.img,
            'description': self.get_description(lang),
            'tags': self.tags,
            'new_window': self.new_window,
            'frontend_only': self.frontend_only,
            'uses_external_service': self.uses_external_service,
            'click_count': self.click_count
        }
    
    @classmethod
    def from_dict(cls, data):
        link = cls(
            name=data.get('name'),
            url=data.get('url'),
            img=data.get('img'),
            description=data.get('description', ''),
            new_window=data.get('new_window', True)
        )
        link.tags = data.get('tags', [])
        return link
