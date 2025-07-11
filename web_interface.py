#!/usr/bin/env python3
"""
Krypton JARVIS-like Web Interface
A Flask-based web application providing a futuristic UI for controlling Krypton AI Assistant
"""

from flask import Flask, render_template, request, jsonify, Response
import json
import threading
import time
import subprocess
import sys
import os
import signal
from datetime import datetime
import psutil

# Import Krypton components
try:
    # Import core functions from Krypton
    import krypton_phase4_5 as krypton
    KRYPTON_AVAILABLE = True
    print("✓ Krypton modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Krypton modules not available: {e}")
    print("Running in demo mode.")
    KRYPTON_AVAILABLE = False
    
# Load Krypton configurations if available
if KRYPTON_AVAILABLE:
    try:
        with open('settings.json', 'r') as f:
            krypton_settings = json.load(f)
        with open('commands_config.json', 'r') as f:
            krypton_commands = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load Krypton configs: {e}")
        krypton_settings = {}
        krypton_commands = {}
else:
    krypton_settings = {}
    krypton_commands = {}

app = Flask(__name__)
app.secret_key = 'krypton_jarvis_interface_2024'

# Global state
krypton_status = {
    'active': False,
    'listening': False,
    'last_command': '',
    'last_response': '',
    'session_start': None,
    'commands_processed': 0,
    'voice_mode': True
}

# System monitoring
def get_system_stats():
    """Get current system statistics"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'processes': len(psutil.pids()),
            'uptime': time.time() - psutil.boot_time()
        }
    except:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'processes': 0,
            'uptime': 0
        }

@app.route('/')
def index():
    """Main interface page"""
    return render_template('index.html', 
                         krypton_status=krypton_status,
                         system_stats=get_system_stats())

@app.route('/api/status')
def api_status():
    """Get current Krypton status"""
    stats = get_system_stats()
    return jsonify({
        'krypton': krypton_status,
        'system': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start Krypton AI Assistant"""
    try:
        if not krypton_status['active']:
            krypton_status['active'] = True
            krypton_status['session_start'] = datetime.now().isoformat()
            krypton_status['commands_processed'] = 0
            
            if KRYPTON_AVAILABLE:
                # Start Krypton in background thread
                threading.Thread(target=krypton_background_task, daemon=True).start()
            
            return jsonify({
                'success': True, 
                'message': 'Krypton AI Assistant activated',
                'status': krypton_status
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Krypton is already active'
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Failed to start Krypton: {str(e)}'
        })

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop Krypton AI Assistant"""
    try:
        krypton_status['active'] = False
        krypton_status['listening'] = False
        return jsonify({
            'success': True, 
            'message': 'Krypton AI Assistant deactivated',
            'status': krypton_status
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Failed to stop Krypton: {str(e)}'
        })

@app.route('/api/command', methods=['POST'])
def api_command():
    """Send text command to Krypton"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({
                'success': False, 
                'message': 'No command provided'
            })
        
        # Process command
        krypton_status['last_command'] = command
        krypton_status['commands_processed'] += 1
        
        if KRYPTON_AVAILABLE:
            # Process with actual Krypton
            response = process_command_safely(command)
        else:
            # Demo response
            response = f"Demo mode: Received command '{command}'"
        
        krypton_status['last_response'] = response
        
        return jsonify({
            'success': True,
            'command': command,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Command processing failed: {str(e)}'
        })

@app.route('/api/voice/start', methods=['POST'])
def api_voice_start():
    """Start voice listening mode"""
    try:
        if not krypton_status['active']:
            return jsonify({
                'success': False, 
                'message': 'Krypton must be active to use voice mode'
            })
        
        krypton_status['listening'] = True
        
        # Start voice listening in background
        threading.Thread(target=voice_listening_task, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Voice listening activated',
            'status': krypton_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Voice activation failed: {str(e)}'
        })

@app.route('/api/voice/stop', methods=['POST'])
def api_voice_stop():
    """Stop voice listening mode"""
    try:
        krypton_status['listening'] = False
        return jsonify({
            'success': True,
            'message': 'Voice listening deactivated',
            'status': krypton_status
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Voice deactivation failed: {str(e)}'
        })

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or update Krypton settings"""
    if request.method == 'GET':
        if KRYPTON_AVAILABLE:
            return jsonify(krypton_settings)
        else:
            return jsonify({'demo_mode': True})
    
    elif request.method == 'POST':
        try:
            new_settings = request.get_json()
            if KRYPTON_AVAILABLE:
                # Update actual settings
                krypton_settings.update(new_settings)
                with open('settings.json', 'w') as f:
                    json.dump(krypton_settings, f, indent=2)
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Settings update failed: {str(e)}'
            })

@app.route('/api/commands')
def api_commands():
    """Get available commands"""
    if KRYPTON_AVAILABLE:
        return jsonify(krypton_commands)
    else:
        return jsonify({
            'demo_commands': ['time', 'weather', 'help', 'status']
        })

def process_command_safely(command):
    """Safely process a command with Krypton"""
    try:
        if KRYPTON_AVAILABLE:
            # Import and use actual Krypton functions
            from krypton_phase4_5 import (
                ALIASES, commands_config, execute_command, 
                match_command, nlp_engine, debug_log,
                play_feedback, CONFIRM_SOUND, ERROR_SOUND
            )
            
            # Multi-tier command recognition (same as main Krypton)
            command_key = None
            
            # Tier 1: Direct exact matches
            if command in ALIASES:
                command_key = ALIASES[command]
                debug_log(f"Web Interface - Exact match: {command_key}")
            
            # Tier 2: Fuzzy matching
            if not command_key:
                command_key = match_command(command)
                if command_key:
                    debug_log(f"Web Interface - Fuzzy match: {command_key}")
            
            # Tier 3: Simple keyword detection
            if not command_key:
                simple_keywords = {
                    "notepad": "open_notepad",
                    "chrome": "open_chrome", 
                    "time": "get_time",
                    "help": "help",
                    "weather": "weather_report",
                    "search": "search_web",
                    "volume up": "increase_volume",
                    "volume down": "decrease_volume",
                    "mute": "mute_sound",
                    "unmute": "unmute_sound"
                }
                for keyword, cmd in simple_keywords.items():
                    if keyword in command.lower():
                        command_key = cmd
                        debug_log(f"Web Interface - Keyword match: {command_key}")
                        break
            
            # Tier 4: NLP processing
            if not command_key:
                nlp_result = nlp_engine.process_input(command)
                if nlp_result["intent"] != "unknown" and nlp_result["confidence"] > 0.1:
                    command_key = nlp_result["intent"]
                    debug_log(f"Web Interface - NLP match: {command_key}")
            
            if command_key:
                try:
                    # Execute the command using Krypton's actual function
                    execute_command(command_key, command)
                    return f"✅ Command executed successfully: {command}"
                except Exception as e:
                    return f"❌ Error executing command: {str(e)}"
            else:
                return f"❓ Command not recognized: {command}. Try 'help' for available commands."
        else:
            return f"Demo mode: Received command '{command}'"
    except Exception as e:
        return f"Error processing command: {str(e)}"

def voice_listening_task():
    """Background task for voice listening"""
    while krypton_status['listening'] and krypton_status['active']:
        try:
            if KRYPTON_AVAILABLE:
                from krypton_phase4_5 import listen_command
                command = listen_command()
                if command:
                    krypton_status['last_command'] = command
                    response = process_command_safely(command)
                    krypton_status['last_response'] = response
                    krypton_status['commands_processed'] += 1
            time.sleep(0.1)
        except Exception as e:
            print(f"Voice listening error: {e}")
            break

def krypton_background_task():
    """Background task for Krypton operations"""
    while krypton_status['active']:
        try:
            # Keep Krypton running and responsive
            time.sleep(1)
        except Exception as e:
            print(f"Krypton background error: {e}")
            break

if __name__ == '__main__':
    print("🚀 Starting Krypton JARVIS Interface...")
    print("🌐 Access the interface at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        app.run(
            host='0.0.0.0',  # Allow access from other devices on network
            port=5000,
            debug=False,  # Set to True for development
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Krypton JARVIS Interface...")
        sys.exit(0)
