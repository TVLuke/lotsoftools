"""
Sound service - downloads and manages sound files for tools.
"""
import os
import requests
from pathlib import Path


class SoundService:
    _instance = None
    _data_dir = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def init(cls, data_dir):
        """Initialize the service and download sound files if needed."""
        instance = cls.get_instance()
        
        if cls._initialized:
            return instance
        
        instance._data_dir = data_dir
        sounds_dir = os.path.join(data_dir, 'sounds')
        os.makedirs(sounds_dir, exist_ok=True)
        
        # Download fire.mp3 if it doesn't exist
        fire_mp3_path = os.path.join(sounds_dir, 'fire.mp3')
        if not os.path.exists(fire_mp3_path):
            print("Downloading fireplace sound...")
            try:
                response = requests.get('https://tvluke.de/sounds/fire.mp3', timeout=30)
                response.raise_for_status()
                
                with open(fire_mp3_path, 'wb') as f:
                    f.write(response.content)
                
                file_size_mb = os.path.getsize(fire_mp3_path) / (1024 * 1024)
                print(f"✓ Downloaded fire.mp3 ({file_size_mb:.1f} MB)")
                
            except requests.RequestException as e:
                print(f"✗ Failed to download fire.mp3: {e}")
        else:
            file_size_mb = os.path.getsize(fire_mp3_path) / (1024 * 1024)
            print(f"✓ Fire.mp3 already exists ({file_size_mb:.1f} MB)")
        
        cls._initialized = True
        return instance
    
    @classmethod
    def get_sound_path(cls, sound_name):
        """Get the path to a sound file."""
        if not cls._initialized:
            return None
        
        sounds_dir = os.path.join(cls._data_dir, 'sounds')
        sound_path = os.path.join(sounds_dir, sound_name)
        
        if os.path.exists(sound_path):
            return sound_path
        return None
