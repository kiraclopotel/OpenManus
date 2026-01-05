"""
settings_manager.py - Persistent settings for OpenManus UI
Place in: C:\Users\tialc\Documents\GitHub\OpenManus\
"""

import json
import os
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "config" / "ui_settings.json"

DEFAULT_SETTINGS = {
    "model": {
        "name": "qwen2.5:7b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "temperature": 0.0,
        "max_tokens": 4096
    },
    "agent": {
        "max_steps": 20,
        "timeout": 300
    },
    "ui": {
        "theme": "dark",
        "show_cot": True,
        "show_tokens": True,
        "auto_scroll": True,
        "font_size": 14
    },
    "tools": {
        "python_execute": True,
        "browser": True,
        "search": True,
        "file_operations": True
    }
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()
    
    def load(self):
        """Load settings from file."""
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r') as f:
                    saved = json.load(f)
                    self._deep_update(self.settings, saved)
        except Exception as e:
            print(f"Settings load error: {e}")
    
    def save(self):
        """Save settings to file."""
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Settings save error: {e}")
    
    def get(self, path: str, default=None):
        """Get setting by dot-path: 'model.temperature'"""
        keys = path.split('.')
        val = self.settings
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
    
    def set(self, path: str, value):
        """Set setting by dot-path."""
        keys = path.split('.')
        d = self.settings
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save()
    
    def _deep_update(self, base: dict, updates: dict):
        """Recursively update dict."""
        for k, v in updates.items():
            if isinstance(v, dict) and k in base:
                self._deep_update(base[k], v)
            else:
                base[k] = v
    
    def to_dict(self):
        return self.settings.copy()

# Global instance
settings = SettingsManager()