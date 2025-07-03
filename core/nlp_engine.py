"""
Enhanced NLP Engine for Krypton
Advanced natural language processing with context awareness
"""

import spacy
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

class EnhancedNLPEngine:
    """Advanced NLP processing with context awareness"""
    
    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        self.nlp = spacy.load("en_core_web_sm")
        
        # Intent patterns with confidence scoring
        self.intent_patterns = {
            "file_operation": {
                "patterns": [
                    r"(?:open|edit|find|search|locate|show me)\s+(?:the\s+)?(?:file|document|folder)",
                    r"(?:find|search for|locate)\s+(.+?)(?:\s+file|\s+document|$)",
                    r"where is (?:the\s+)?(.+?)(?:\s+file|$)",
                    r"show me (?:the\s+)?(.+?)(?:\s+file|$)"
                ],
                "entities": ["FILENAME", "FILEPATH", "EXTENSION"]
            },
            "app_control": {
                "patterns": [
                    r"(?:open|launch|start|run|close|exit|quit)\s+(.+?)(?:\s+app|\s+application|$)",
                    r"(?:switch to|go to)\s+(.+?)(?:\s+app|$)",
                    r"minimize|maximize|restore\s+(.+?)"
                ],
                "entities": ["APP_NAME"]
            },
            "time_query": {
                "patterns": [
                    r"(?:what time is it|current time|tell me the time)",
                    r"(?:what|how much) time (?:do|did) (?:i|we) have",
                    r"(?:when is|when's)\s+(.+?)"
                ],
                "entities": ["TIME", "DATE", "DURATION"]
            },
            "reminder_management": {
                "patterns": [
                    r"(?:remind me|set (?:a\s+)?reminder|don't forget)\s+to\s+(.+?)(?:\s+(?:at|in|on)\s+(.+?))?",
                    r"(?:remember|note)\s+(.+?)(?:\s+for\s+(.+?))?",
                    r"(?:schedule|plan)\s+(.+?)(?:\s+(?:at|for)\s+(.+?))?"
                ],
                "entities": ["TASK", "TIME", "DATE"]
            },
            "search_web": {
                "patterns": [
                    r"(?:search|google|look up|find online)\s+(?:for\s+)?(.+?)(?:\s+(?:on|in)\s+(.+?))?",
                    r"(?:what is|tell me about|information on)\s+(.+?)",
                    r"(?:how to|how do (?:i|you))\s+(.+?)"
                ],
                "entities": ["QUERY", "SEARCH_ENGINE"]
            },
            "system_control": {
                "patterns": [
                    r"(?:mute|unmute|silence|volume)\s*(?:up|down|to\s+(\d+))?",
                    r"(?:increase|decrease|raise|lower)\s+(?:the\s+)?volume",
                    r"(?:shut down|restart|sleep|hibernate)\s*(?:the\s+)?(?:computer|system)?"
                ],
                "entities": ["VOLUME_LEVEL", "SYSTEM_ACTION"]
            },
            "question_answering": {
                "patterns": [
                    r"(?:what|how|when|where|why|who)\s+.+\?",
                    r"(?:can you|could you|would you)\s+(?:tell me|explain|help)",
                    r"(?:i want to know|i need to know|tell me)\s+(?:about\s+)?(.+?)"
                ],
                "entities": ["TOPIC", "QUESTION_TYPE"]
            },
            "context_reference": {
                "patterns": [
                    r"(?:it|that|this|the (?:file|app|thing|one))",
                    r"(?:do that again|repeat|same as before)",
                    r"(?:what about|how about)\s+(?:it|that|this)"
                ],
                "entities": ["REFERENCE_TYPE"]
            }
        }
        
        # Sentiment analysis patterns
        self.sentiment_patterns = {
            "positive": ["good", "great", "excellent", "perfect", "awesome", "love", "like", "happy"],
            "negative": ["bad", "terrible", "awful", "hate", "dislike", "frustrated", "annoying", "slow"],
            "urgent": ["urgent", "immediately", "asap", "quickly", "fast", "hurry", "now", "emergency"]
        }
        
        # Time parsing patterns
        self.time_patterns = {
            "relative": {
                r"in (\d+) (second|seconds|minute|minutes|hour|hours|day|days)": "future_relative",
                r"(\d+) (second|seconds|minute|minutes|hour|hours|day|days) ago": "past_relative",
                r"(today|tomorrow|yesterday)": "day_relative",
                r"(this|next|last) (week|month|year)": "period_relative"
            },
            "absolute": {
                r"(\d{1,2}):(\d{2})(?:\s*(am|pm))?": "time_absolute",
                r"(\d{1,2})/(\d{1,2})/(\d{2,4})": "date_absolute",
                r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)": "day_absolute"
            }
        }
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Main NLP processing function"""
        
        # Basic preprocessing
        cleaned_input = self._preprocess_text(user_input)
        
        # Resolve context references first
        resolved_input = self._resolve_context_references(cleaned_input)
        
        # Extract entities using spaCy
        spacy_entities = self._extract_spacy_entities(resolved_input)
        
        # Detect intent
        intent_result = self._detect_intent(resolved_input)
        
        # Extract custom entities based on intent
        custom_entities = self._extract_custom_entities(resolved_input, intent_result["intent"])
        
        # Parse time expressions
        time_info = self._parse_time_expressions(resolved_input)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(resolved_input)
        
        # Combine all results
        result = {
            "original_input": user_input,
            "processed_input": resolved_input,
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "entities": {
                "spacy": spacy_entities,
                "custom": custom_entities,
                "time": time_info
            },
            "sentiment": sentiment,
            "context_resolved": resolved_input != cleaned_input,
            "suggestions": self._generate_suggestions(intent_result["intent"], custom_entities)
        }
        
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle contractions
        contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will", "'d": " would"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def _resolve_context_references(self, text: str) -> str:
        """Resolve pronouns and references using context"""
        if not self.context_manager:
            return text
        
        reference = self.context_manager.resolve_reference(text)
        if reference:
            # Replace pronouns with actual entity names
            replacements = {
                r"\bit\b": reference.get("name", ""),
                r"\bthat\b": reference.get("name", ""),
                r"\bthe file\b": reference.get("name", "") if reference.get("type") == "file" else "the file",
                r"\bthe app\b": reference.get("name", "") if reference.get("type") == "app" else "the app"
            }
            
            for pattern, replacement in replacements.items():
                if replacement:
                    text = re.sub(pattern, replacement, text)
        
        return text
    
    def _extract_spacy_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract entities using spaCy NER"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 0.8  # spaCy doesn't provide confidence, so we use default
            })
        
        return entities
    
    def _detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect user intent from text"""
        best_intent = None
        best_confidence = 0.0
        
        for intent, config in self.intent_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    confidence += 0.3  # Base confidence per pattern match
            
            # Boost confidence based on entity presence
            for entity_type in config.get("entities", []):
                if self._has_entity_type(text, entity_type):
                    confidence += 0.2
            
            # Normalize confidence
            if matches > 0:
                confidence = min(confidence / len(config["patterns"]), 1.0)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent
        
        return {
            "intent": best_intent or "unknown",
            "confidence": best_confidence
        }
    
    def _extract_custom_entities(self, text: str, intent: str) -> Dict[str, List[str]]:
        """Extract custom entities based on detected intent"""
        entities = defaultdict(list)
        
        if intent == "file_operation":
            # Extract file names and paths
            file_patterns = [
                r"([A-Za-z0-9_\-\.]+\.(py|txt|pdf|docx?|xlsx?|jpg|png|mp3|mp4))",
                r'"([^"]+)"',  # Quoted filenames
                r"'([^']+)'"   # Single-quoted filenames
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    filename = match if isinstance(match, str) else match[0]
                    entities["filename"].append(filename)
        
        elif intent == "app_control":
            # Extract application names
            app_pattern = r"(?:open|launch|start|run|close)\s+([A-Za-z0-9\s]+?)(?:\s|$)"
            matches = re.findall(app_pattern, text, re.IGNORECASE)
            for match in matches:
                entities["app_name"].append(match.strip())
        
        elif intent == "reminder_management":
            # Extract tasks and times
            reminder_patterns = [
                r"remind me to (.+?)(?:\s+(?:at|in|on)\s+(.+?))?$",
                r"don't forget to (.+?)(?:\s+(?:at|in|on)\s+(.+?))?$"
            ]
            
            for pattern in reminder_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities["task"].append(match.group(1).strip())
                    if match.group(2):
                        entities["time"].append(match.group(2).strip())
        
        elif intent == "search_web":
            # Extract search queries
            search_patterns = [
                r"(?:search|google|look up)\s+(?:for\s+)?(.+?)(?:\s+(?:on|in)\s+(.+?))?$",
                r"(?:what is|tell me about)\s+(.+?)$"
            ]
            
            for pattern in search_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities["query"].append(match.group(1).strip())
        
        return dict(entities)
    
    def _parse_time_expressions(self, text: str) -> Dict[str, Any]:
        """Parse time and date expressions"""
        time_info = {
            "relative_times": [],
            "absolute_times": [],
            "parsed_datetime": None
        }
        
        # Parse relative times
        for pattern, time_type in self.time_patterns["relative"].items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                time_info["relative_times"].append({
                    "match": match,
                    "type": time_type,
                    "text": ' '.join(match) if isinstance(match, tuple) else match
                })
        
        # Parse absolute times
        for pattern, time_type in self.time_patterns["absolute"].items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                time_info["absolute_times"].append({
                    "match": match,
                    "type": time_type,
                    "text": ' '.join(match) if isinstance(match, tuple) else match
                })
        
        # Try to convert to actual datetime if possible
        if time_info["relative_times"] or time_info["absolute_times"]:
            time_info["parsed_datetime"] = self._convert_to_datetime(time_info)
        
        return time_info
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional context"""
        sentiment_scores = {"positive": 0, "negative": 0, "urgent": 0}
        
        words = text.lower().split()
        
        for word in words:
            for sentiment_type, keywords in self.sentiment_patterns.items():
                if word in keywords:
                    sentiment_scores[sentiment_type] += 1
        
        # Determine overall sentiment
        total_sentiment_words = sum(sentiment_scores.values())
        if total_sentiment_words == 0:
            overall_sentiment = "neutral"
        else:
            dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            if sentiment_scores[dominant_sentiment] > 0:
                overall_sentiment = dominant_sentiment
            else:
                overall_sentiment = "neutral"
        
        return {
            "overall": overall_sentiment,
            "scores": sentiment_scores,
            "urgency_level": min(sentiment_scores["urgent"] * 0.3, 1.0)
        }
    
    def _has_entity_type(self, text: str, entity_type: str) -> bool:
        """Check if text contains entities of specific type"""
        patterns = {
            "FILENAME": r"[A-Za-z0-9_\-\.]+\.(py|txt|pdf|docx?|xlsx?|jpg|png)",
            "APP_NAME": r"(notepad|chrome|spotify|discord|code)",
            "TIME": r"\d{1,2}:\d{2}",
            "DATE": r"\d{1,2}/\d{1,2}/\d{2,4}",
            "VOLUME_LEVEL": r"\d{1,3}(?:%|percent)?",
        }
        
        pattern = patterns.get(entity_type)
        if pattern:
            return bool(re.search(pattern, text, re.IGNORECASE))
        return False
    
    def _convert_to_datetime(self, time_info: Dict[str, Any]) -> Optional[datetime]:
        """Convert parsed time information to datetime object"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated time parsing
        
        now = datetime.now()
        
        # Handle relative times
        for rel_time in time_info["relative_times"]:
            if rel_time["type"] == "future_relative":
                match = rel_time["match"]
                if isinstance(match, tuple) and len(match) >= 2:
                    amount = int(match[0])
                    unit = match[1]
                    
                    if "minute" in unit:
                        return now + timedelta(minutes=amount)
                    elif "hour" in unit:
                        return now + timedelta(hours=amount)
                    elif "day" in unit:
                        return now + timedelta(days=amount)
        
        return None
    
    def _generate_suggestions(self, intent: str, entities: Dict[str, List[str]]) -> List[str]:
        """Generate contextual suggestions based on intent and entities"""
        suggestions = []
        
        if intent == "file_operation" and not entities.get("filename"):
            suggestions.append("Try specifying a filename or file extension")
            
        elif intent == "app_control" and not entities.get("app_name"):
            suggestions.append("Try mentioning the specific application name")
            
        elif intent == "reminder_management":
            if not entities.get("task"):
                suggestions.append("Try specifying what you want to be reminded about")
            if not entities.get("time"):
                suggestions.append("Try adding when you want to be reminded")
                
        elif intent == "unknown":
            if self.context_manager:
                recent_commands = self.context_manager.get_command_suggestions()
                if recent_commands:
                    suggestions.extend([f"Try: {cmd}" for cmd in recent_commands[:3]])
        
        return suggestions

# Global NLP engine instance
def create_nlp_engine(context_manager=None):
    """Factory function to create NLP engine with context manager"""
    return EnhancedNLPEngine(context_manager)
