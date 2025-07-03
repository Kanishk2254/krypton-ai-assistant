"""
Smart Context Memory System for Krypton
Tracks conversation context, user patterns, and intelligent references
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import re

class ContextManager:
    """Manages conversation context and user interaction patterns"""
    
    def __init__(self, max_context_items=50):
        self.max_context_items = max_context_items
        self.context_file = "data/context_memory.json"
        self.patterns_file = "data/user_patterns.json"
        
        # Context storage
        self.conversation_history: deque = deque(maxlen=max_context_items)
        self.entity_memory: Dict[str, Any] = {}  # Remember entities (files, apps, etc.)
        self.command_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.user_preferences: Dict[str, Any] = {}
        
        # Session context
        self.current_session = {
            "start_time": datetime.now(),
            "commands_count": 0,
            "last_command": None,
            "active_references": {}  # "the file", "that reminder", etc.
        }
        
        self._load_persistent_context()
    
    def add_command_to_context(self, command: str, input_text: str, result: str = None, entities: Dict = None):
        """Add a command to conversation context"""
        context_item = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "input_text": input_text,
            "result": result,
            "entities": entities or {},
            "session_id": self._get_session_id()
        }
        
        self.conversation_history.append(context_item)
        self.current_session["commands_count"] += 1
        self.current_session["last_command"] = context_item
        
        # Update command patterns for predictive intelligence
        self.command_patterns[command].append(datetime.now())
        
        # Extract and remember entities
        self._extract_and_remember_entities(input_text, entities)
        
        # Auto-save every 5 commands
        if self.current_session["commands_count"] % 5 == 0:
            self._save_persistent_context()
    
    def _extract_and_remember_entities(self, input_text: str, entities: Dict = None):
        """Extract and remember important entities from user input"""
        
        # File references
        file_patterns = [
            r"(?:file|document|pdf|txt)\s+['\"]([^'\"]+)['\"]",
            r"([A-Za-z0-9_\-\.]+\.(py|txt|pdf|docx?|xlsx?|jpg|png))",
            r"(?:open|find|edit)\s+([A-Za-z0-9_\-\.]+)"
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, input_text, re.IGNORECASE)
            for match in matches:
                filename = match if isinstance(match, str) else match[0]
                self.entity_memory[f"file_{filename}"] = {
                    "type": "file",
                    "name": filename,
                    "last_mentioned": datetime.now().isoformat(),
                    "context": input_text[:100]  # Store context snippet
                }
        
        # App references
        app_patterns = [
            r"(?:open|start|launch)\s+([A-Za-z0-9\s]+?)(?:\s|$)",
            r"(notepad|chrome|spotify|discord|vs\s*code)"
        ]
        
        for pattern in app_patterns:
            matches = re.findall(pattern, input_text, re.IGNORECASE)
            for match in matches:
                app_name = match.strip()
                if len(app_name) > 2:  # Avoid single letters
                    self.entity_memory[f"app_{app_name}"] = {
                        "type": "app",
                        "name": app_name,
                        "last_mentioned": datetime.now().isoformat(),
                        "context": input_text[:100]
                    }
        
        # Time/date references
        time_patterns = [
            r"(\d{1,2}:\d{2}(?:\s*[ap]m)?)",
            r"(today|tomorrow|yesterday|next week|this weekend)",
            r"(in\s+\d+\s+(?:minutes?|hours?|days?))"
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, input_text, re.IGNORECASE)
            for match in matches:
                self.entity_memory[f"time_{match}"] = {
                    "type": "time",
                    "value": match,
                    "last_mentioned": datetime.now().isoformat(),
                    "context": input_text[:100]
                }
    
    def resolve_reference(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Resolve pronouns and references like 'it', 'that', 'the file'"""
        
        # Common reference patterns
        references = {
            r"(?:it|that|this)": "last_entity",
            r"(?:the\s+file|that\s+file)": "last_file",
            r"(?:the\s+app|that\s+app)": "last_app",
            r"(?:the\s+reminder|that\s+reminder)": "last_reminder",
            r"(?:the\s+meeting|that\s+meeting)": "last_meeting"
        }
        
        for pattern, ref_type in references.items():
            if re.search(pattern, input_text, re.IGNORECASE):
                return self._get_last_entity_by_type(ref_type)
        
        return None
    
    def _get_last_entity_by_type(self, ref_type: str) -> Optional[Dict[str, Any]]:
        """Get the most recent entity of a specific type"""
        
        if ref_type == "last_entity":
            # Return the most recent entity mentioned
            recent_entities = sorted(
                self.entity_memory.items(),
                key=lambda x: x[1]["last_mentioned"],
                reverse=True
            )
            return recent_entities[0][1] if recent_entities else None
        
        elif ref_type == "last_file":
            file_entities = {k: v for k, v in self.entity_memory.items() if v["type"] == "file"}
            if file_entities:
                recent_file = max(file_entities.items(), key=lambda x: x[1]["last_mentioned"])
                return recent_file[1]
        
        elif ref_type == "last_app":
            app_entities = {k: v for k, v in self.entity_memory.items() if v["type"] == "app"}
            if app_entities:
                recent_app = max(app_entities.items(), key=lambda x: x[1]["last_mentioned"])
                return recent_app[1]
        
        return None
    
    def get_command_suggestions(self, time_of_day: str = None) -> List[str]:
        """Suggest commands based on usage patterns"""
        current_hour = datetime.now().hour
        
        # Analyze command patterns by time
        suggestions = []
        
        for command, timestamps in self.command_patterns.items():
            # Filter to same time of day (within 2 hours)
            same_time_commands = [
                ts for ts in timestamps 
                if abs(ts.hour - current_hour) <= 2
            ]
            
            if len(same_time_commands) >= 2:  # Used at least twice at this time
                suggestions.append(command)
        
        return suggestions[:5]  # Top 5 suggestions
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context for debugging/display"""
        recent_commands = list(self.conversation_history)[-5:]  # Last 5 commands
        
        return {
            "session_info": {
                "duration_minutes": (datetime.now() - self.current_session["start_time"]).total_seconds() / 60,
                "commands_executed": self.current_session["commands_count"],
                "last_command": self.current_session["last_command"]["command"] if self.current_session["last_command"] else None
            },
            "recent_commands": [cmd["command"] for cmd in recent_commands],
            "remembered_entities": len(self.entity_memory),
            "top_commands": self._get_top_commands(),
            "suggestions": self.get_command_suggestions()
        }
    
    def _get_top_commands(self) -> List[str]:
        """Get most frequently used commands"""
        command_counts = defaultdict(int)
        for item in self.conversation_history:
            command_counts[item["command"]] += 1
        
        return sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _get_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{self.current_session['start_time'].strftime('%Y%m%d_%H%M%S')}"
    
    def _load_persistent_context(self):
        """Load context from persistent storage"""
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            if os.path.exists(self.context_file):
                with open(self.context_file, "r") as f:
                    data = json.load(f)
                    
                # Load entity memory (only recent ones)
                cutoff_date = datetime.now() - timedelta(days=7)
                for key, entity in data.get("entity_memory", {}).items():
                    entity_date = datetime.fromisoformat(entity["last_mentioned"])
                    if entity_date > cutoff_date:
                        self.entity_memory[key] = entity
            
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, "r") as f:
                    data = json.load(f)
                    self.user_preferences = data.get("preferences", {})
                    
                    # Load command patterns (last 30 days)
                    cutoff_date = datetime.now() - timedelta(days=30)
                    for command, timestamps in data.get("command_patterns", {}).items():
                        recent_timestamps = [
                            datetime.fromisoformat(ts) for ts in timestamps
                            if datetime.fromisoformat(ts) > cutoff_date
                        ]
                        if recent_timestamps:
                            self.command_patterns[command] = recent_timestamps
                            
        except Exception as e:
            print(f"[Context] Error loading persistent context: {e}")
    
    def _save_persistent_context(self):
        """Save context to persistent storage"""
        try:
            os.makedirs("data", exist_ok=True)
            
            # Save entity memory and recent context
            context_data = {
                "entity_memory": self.entity_memory,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.context_file, "w") as f:
                json.dump(context_data, f, indent=2)
            
            # Save patterns and preferences
            patterns_data = {
                "command_patterns": {
                    cmd: [ts.isoformat() for ts in timestamps]
                    for cmd, timestamps in self.command_patterns.items()
                },
                "preferences": self.user_preferences,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.patterns_file, "w") as f:
                json.dump(patterns_data, f, indent=2)
                
        except Exception as e:
            print(f"[Context] Error saving persistent context: {e}")
    
    def cleanup_old_data(self):
        """Clean up old context data to prevent memory bloat"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Remove old entities
        self.entity_memory = {
            key: entity for key, entity in self.entity_memory.items()
            if datetime.fromisoformat(entity["last_mentioned"]) > cutoff_date
        }
        
        # Remove old command patterns
        for command in list(self.command_patterns.keys()):
            self.command_patterns[command] = [
                ts for ts in self.command_patterns[command]
                if ts > cutoff_date
            ]
            
            # Remove commands with no recent usage
            if not self.command_patterns[command]:
                del self.command_patterns[command]

# Global context manager instance
context_manager = ContextManager()
