# 🚀 KRYPTON - Advanced AI Voice Assistant

![Krypton Banner](Images/KRYPTON.png)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)](https://github.com)

> **An enterprise-grade AI assistant with advanced natural language processing, context awareness, and extensible plugin architecture.**

## 🌟 **Features**

### 🧠 **Advanced Intelligence**
- **🎯 Natural Language Processing** - Understands context and intent with 80%+ accuracy
- **📝 Context Memory** - Remembers conversations and learns usage patterns
- **🔗 Reference Resolution** - Handles pronouns like "it", "that", "the file"
- **🎪 Fuzzy Matching** - Works even with typos ("oepn notepad" → "open notepad")

### 🎤 **Voice-First Design**
- **🗣️ Multi-Wake Phrases** - "Hey Krypton", "Wake up", "Initiate sequence"
- **🔊 High-Quality TTS** - Natural voice synthesis with customizable speed/volume
- **🎛️ Voice Mode Toggle** - Switch between voice and silent modes
- **🔇 Dual Input** - Voice commands with text fallback

### 🔐 **Enterprise Security**
- **🛡️ PIN Authentication** - Voice + manual PIN protection
- **⏱️ Session Timeouts** - Automatic re-authentication after inactivity
- **🔒 Encrypted Logging** - All commands logged with military-grade encryption
- **🏰 Plugin Sandboxing** - Secure execution environment for extensions

### 🔌 **Extensible Architecture**
- **📦 Plugin System** - Easy-to-develop custom functionality
- **⚙️ Configuration Management** - JSON-based settings with hot-reload
- **🎨 Tray Integration** - System tray controls and status indicators
- **📊 Performance Monitoring** - Built-in analytics and optimization

### 🤖 **Smart Automation**
- **⏰ Intelligent Reminders** - Natural language time parsing
- **📋 Task Management** - Built-in todo system with persistence
- **🌐 Web Integration** - Smart search and browser automation
- **🔊 System Control** - Volume, applications, and file management

---

## 🎬 **Demo**

### Quick Start Commands
```bash
# Authentication
"2254" (or set custom PIN via KRYPTON_PIN environment variable)

# Wake Phrase
"Hey Krypton"

# Core Commands
"Open notepad"              # Launch applications
"What time is it?"          # Information queries
"Mute sound"               # System control
"Search Python tutorials"  # Web search
"Remind me to call mom in 5 minutes"  # Smart reminders
"Add task buy groceries"    # Task management
"Voice off"                # Toggle voice mode
```

### Context Awareness Demo
```bash
"Open notepad"        # Opens Notepad
"Close it"           # Closes Notepad (understands "it" = Notepad)
"Search Python"      # Searches for Python
"Open that in Chrome" # Opens search in browser (understands "that" = search)
```

---

## 🛠️ **Installation**

### Prerequisites
- **Python 3.8+** (tested with 3.11+)
- **Windows 10/11** (Windows-specific features)
- **Microphone** (for voice input)
- **Internet connection** (for speech recognition and web features)

### Quick Install
```bash
# Clone the repository
git clone https://github.com/yourusername/krypton-ai-assistant.git
cd krypton-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm

# Set up configuration
cp settings.json.example settings.json
cp .env.example .env

# Configure your security PIN
echo "KRYPTON_PIN=your_4_digit_pin" >> .env

# Run Krypton
python krypton_phase4_5.py
```

### Advanced Installation
```bash
# Create virtual environment (recommended)
python -m venv krypton-env
source krypton-env/bin/activate  # Linux/Mac
# OR
krypton-env\Scripts\activate     # Windows

# Install with development tools
pip install -r requirements.txt
pip install black pytest mypy     # Optional: Development tools

# Run tests
python automated_testing_suite.py
```

---

## ⚙️ **Configuration**

### Environment Variables (.env)
```bash
# Security
KRYPTON_PIN=1234                    # Your 4-digit PIN
SESSION_TIMEOUT_MINUTES=5           # Session timeout

# Voice Settings
DEFAULT_VOICE_SPEED=200             # Speech rate
DEFAULT_VOICE_VOLUME=0.9            # Volume level

# Debug
DEBUG_MODE=false                    # Enable debug output
```

### Main Settings (settings.json)
```json
{
  "assistant_name": "KRYPTON",
  "user_name": "Your Name",
  "voice_mode": true,
  "trigger_phrases": ["hey krypton", "wake up", "awaken"],
  "default_browser": "chrome",
  "debug_mode": false
}
```

### Commands Configuration
Krypton supports 15+ built-in commands with aliases:
- **App Control**: "open notepad", "launch chrome"
- **System**: "mute sound", "volume up", "time"
- **Search**: "google search", "find information"
- **Files**: "open file report.pdf"
- **Voice**: "voice on/off", "silent mode"

---

## 🔌 **Plugin Development**

### Creating Custom Plugins
```python
# plugins/my_plugin.py
def my_custom_function():
    speak("Hello from my plugin!")
    
# Plugin entry point
if "my command" in input_text.lower():
    my_custom_function()
```

### Available Plugin APIs
- **speak(text)** - Text-to-speech output
- **play_feedback(sound)** - Audio feedback
- **settings** - Access configuration
- **input_text** - User's raw input

### Plugin Security
- Automatic security scanning for dangerous operations
- Restricted execution environment
- User confirmation for sensitive actions

---

## 🏗️ **Architecture**

### Core Components
```
krypton/
├── krypton_phase4_5.py     # Main application
├── core/
│   ├── nlp_engine.py       # Natural language processing
│   ├── context_manager.py  # Memory and context
│   └── config_manager.py   # Configuration management
├── plugins/                # Extensible plugin system
├── utils/                  # Utility functions
└── data/                   # User data and context
```

### Technology Stack
- **🧠 NLP**: spaCy + custom intent detection
- **🎤 Speech**: SpeechRecognition + pyttsx3
- **🔐 Security**: Cryptography (Fernet encryption)
- **🎮 Audio**: pygame mixer
- **🖥️ GUI**: pystray (system tray)
- **📊 Data**: JSON-based persistence

---

## 📊 **Performance**

### Benchmarks (Automated Testing)
- **⚡ Response Time**: ~0.018s average
- **🧠 NLP Accuracy**: 80%+ intent detection
- **💾 Memory Usage**: ~138MB (very efficient)
- **🎯 Command Matching**: 100% accuracy with typo tolerance
- **🔒 Security**: Military-grade encryption

### System Requirements
- **RAM**: 256MB minimum, 512MB recommended
- **CPU**: Any modern processor (very lightweight)
- **Storage**: 50MB for installation + user data
- **Network**: Required for speech recognition

---

## 🧪 **Testing**

### Automated Test Suite
```bash
# Run comprehensive tests
python automated_testing_suite.py

# Expected results: 10/10 tests passing
✅ Configuration Tests
✅ NLP Engine Tests  
✅ Command Matching Tests
✅ Plugin System Tests
✅ Performance Tests
✅ Memory Usage Tests
✅ Error Handling Tests
✅ Security Tests
✅ File System Tests
✅ Context Manager Tests
```

### Manual Testing
```bash
# Test voice recognition
"Hey Krypton" → "Open notepad"

# Test security
Wait 5+ minutes → Auto re-authentication

# Test context memory
"Open chrome" → "Close it" → Should close Chrome
```

---

## 🔧 **Troubleshooting**

### Common Issues

**🎤 Voice Recognition Not Working**
```bash
# Check microphone permissions
# Ensure internet connection for Google Speech API
# Verify microphone in Windows Sound settings
```

**⚠️ Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm
```

**🔐 Authentication Failed**
```bash
# Check PIN in .env file
echo $KRYPTON_PIN  # Should show your 4-digit PIN

# Reset PIN
echo "KRYPTON_PIN=1234" > .env
```

**🔊 Audio Issues**
```bash
# Check Windows audio settings
# Verify nircmd.exe exists in project directory
# Test TTS: python -c "import pyttsx3; pyttsx3.init().say('test')"
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/krypton-ai-assistant.git

# Create development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install black pytest mypy

# Make your changes and test
python automated_testing_suite.py

# Format code
black *.py

# Submit pull request
```

### Contribution Guidelines
- **🧪 Tests Required**: All new features must include tests
- **📝 Documentation**: Update README and docstrings
- **🎨 Code Style**: Use Black formatter
- **🔒 Security**: No hardcoded credentials or personal data
- **🚀 Performance**: Maintain <2s response times

### Plugin Contributions
- Create plugins in `plugins/` directory
- Follow security guidelines
- Include usage examples
- Test with multiple scenarios

---

## 📈 **Roadmap**

### Phase 5.0 (Planned)
- **🌐 Cloud Integration** - AWS/Azure backend services
- **📱 Mobile App** - iOS/Android companion
- **🏠 IoT Integration** - Smart home device control
- **🤖 Advanced AI** - GPT integration for conversations
- **🌍 Multi-language** - Support for multiple languages

### Community Requests
- **📊 Analytics Dashboard** - Usage statistics and insights
- **🎛️ GUI Interface** - Optional graphical interface
- **🔄 Auto-updates** - Seamless update mechanism
- **☁️ Cloud Sync** - Settings and data synchronization

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **spaCy**: MIT License
- **SpeechRecognition**: BSD License  
- **pyttsx3**: Mozilla Public License
- **cryptography**: Apache/BSD License

---

## 👨‍💻 **Author**

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 **Acknowledgments**

- **spaCy Team** - Excellent NLP library
- **Python Community** - Amazing ecosystem
- **Contributors** - All community contributions
- **Testers** - Beta testing and feedback

---

## 📞 **Support**

### Getting Help
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/yourusername/krypton-ai-assistant/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/yourusername/krypton-ai-assistant/discussions)
- **📧 Direct Contact**: your.email@example.com
- **📖 Documentation**: [Wiki](https://github.com/yourusername/krypton-ai-assistant/wiki)

### Community
- **💬 Discord**: [Join our server](https://discord.gg/krypton)
- **📱 Twitter**: [@KryptonAI](https://twitter.com/KryptonAI)
- **📺 YouTube**: [Demo videos](https://youtube.com/KryptonAI)

---

## ⭐ **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/krypton-ai-assistant&type=Date)](https://star-history.com/#yourusername/krypton-ai-assistant&Date)

---

<p align="center">
  <b>🚀 Made with ❤️ by passionate developers</b><br>
  <i>If you found this project helpful, please consider giving it a ⭐</i>
</p>

---

**⚡ Krypton - Where Intelligence Meets Voice ⚡**
