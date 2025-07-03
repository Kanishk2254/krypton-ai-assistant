"""
Configuration manager for Krypton voice assistant
Handles all configuration files and settings
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self.config_files = {
            "settings": "settings.json",
            "commands": "commands_config.json",
            "tray": "tray_icon_config.json",
            "security": "security.json"
        }
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files"""
        for name, filename in self.config_files.items():
            self.configs[name] = self._load_config(filename)
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load a single configuration file"""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
            else:
                # Create default config if doesn't exist
                default_config = self._get_default_config(filename)
                self._save_config(filename, default_config)
                return default_config
        except Exception as e:
            print(f"[Config] Error loading {filename}: {e}")
            return {}
    
    def _save_config(self, filename: str, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            # Create backup
            if os.path.exists(filename):
                backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(filename, backup_name)
            
            with open(filename, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[Config] Error saving {filename}: {e}")
    
    def _get_default_config(self, filename: str) -> Dict[str, Any]:
        """Get default configuration for a file"""
        defaults = {
            "settings.json": {
                "assistant_name": "KRYPTON",
                "user_name": "User",
                "voice_mode": True,
                "debug_mode": False,
                "log_commands": True,
                "default_browser": "chrome",
                "theme": "dark",
                "confirm_sound": "confirm.wav",
                "error_sound": "error.wav",
                "trigger_phrases": ["hey krypton", "wake up", "krypton"],
                "tray_icon": "pfp.jpg",
                "nlp_enabled": True,
                "session_timeout": 300
            },
            "commands_config.json": {},
            "tray_icon_config.json": {
                "default_icon": "Images/KRYPTON.png",
                "voice_on_icon": "Images/voice_on.png",
                "voice_off_icon": "Images/voice_off.png"
            },
            "security.json": {
                "pin_required": True,
                "encryption_enabled": True,
                "log_retention_days": 30
            }
        }
        return defaults.get(filename, {})
    
    def get(self, config_name: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        config = self.configs.get(config_name, {})
        if key is None:
            return config
        return config.get(key, default)
    
    def set(self, config_name: str, key: str, value: Any):
        """Set configuration value"""
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        self.configs[config_name][key] = value
        filename = self.config_files.get(config_name)
        if filename:
            self._save_config(filename, self.configs[config_name])
    
    def update_config(self, config_name: str, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        self.configs[config_name].update(updates)
        filename = self.config_files.get(config_name)
        if filename:
            self._save_config(filename, self.configs[config_name])
    
    def reload_config(self, config_name: str):
        """Reload configuration from file"""
        filename = self.config_files.get(config_name)
        if filename:
            self.configs[config_name] = self._load_config(filename)
    
    def validate_config(self, config_name: str) -> bool:
        """Validate configuration structure"""
        config = self.configs.get(config_name, {})
        
        if config_name == "settings":
            required_keys = ["assistant_name", "user_name", "voice_mode"]
            return all(key in config for key in required_keys)
        
        return True  # Basic validation passed
    
    def export_config(self, export_path: str):
        """Export all configurations to a single file"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "configs": self.configs
            }
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception as e:
            print(f"[Config] Export failed: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configurations from exported file"""
        try:
            with open(import_path, "r") as f:
                data = json.load(f)
            
            imported_configs = data.get("configs", {})
            for config_name, config_data in imported_configs.items():
                if config_name in self.config_files:
                    self.configs[config_name] = config_data
                    filename = self.config_files[config_name]
                    self._save_config(filename, config_data)
            
            return True
        except Exception as e:
            print(f"[Config] Import failed: {e}")
            return False

# Global instance
config_manager = ConfigManager()
