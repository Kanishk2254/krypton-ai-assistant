"""
Base plugin class for Krypton voice assistant
Provides standardized interface for plugin development
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class KryptonPlugin(ABC):
    """Base class for all Krypton plugins"""
    
    def __init__(self, speak_func, settings: Dict[str, Any]):
        self.speak = speak_func
        self.settings = settings
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "A Krypton plugin"
        
    @abstractmethod
    def execute(self, input_text: str, **kwargs) -> bool:
        """
        Execute the plugin's main functionality
        
        Args:
            input_text: Raw user input
            **kwargs: Additional context
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        pass
    
    @abstractmethod
    def get_commands(self) -> List[str]:
        """Return list of commands this plugin handles"""
        pass
    
    def get_help(self) -> str:
        """Return help text for this plugin"""
        return f"{self.name}: {self.description}"
    
    def validate_input(self, input_text: str) -> bool:
        """Validate input before processing"""
        return bool(input_text and input_text.strip())
    
    def save_data(self, data: Dict[str, Any], filename: str) -> bool:
        """Save plugin data to JSON file"""
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            filepath = os.path.join(data_dir, f"{self.name}_{filename}")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to save data: {e}")
            return False
    
    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load plugin data from JSON file"""
        try:
            filepath = os.path.join("data", f"{self.name}_{filename}")
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"[{self.name}] Failed to load data: {e}")
            return {}

# Example implementation
class WeatherPlugin(KryptonPlugin):
    """Example weather plugin implementation"""
    
    def __init__(self, speak_func, settings):
        super().__init__(speak_func, settings)
        self.description = "Provides weather information"
        self.api_key = settings.get("weather_api_key", "")
    
    def execute(self, input_text: str, **kwargs) -> bool:
        if any(cmd in input_text.lower() for cmd in self.get_commands()):
            # Weather implementation would go here
            self.speak("Weather plugin executed!")
            return True
        return False
    
    def get_commands(self) -> List[str]:
        return ["weather", "forecast", "temperature"]
