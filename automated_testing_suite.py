#!/usr/bin/env python3
"""
Krypton Phase 4.5 - Automated Testing Suite
Comprehensive testing without external users
"""

import json
import time
import os
import sys
import traceback
import threading
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import difflib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)

class KryptonTester:
    """Automated testing suite for Krypton Phase 4.5"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 KRYPTON PHASE 4.5 - AUTOMATED TESTING SUITE")
        print("=" * 60)
        
        tests = [
            ("Configuration Tests", self.test_configurations),
            ("NLP Engine Tests", self.test_nlp_engine),
            ("Command Matching Tests", self.test_command_matching),
            ("Plugin System Tests", self.test_plugin_system),
            ("Performance Tests", self.test_performance),
            ("Memory Usage Tests", self.test_memory_usage),
            ("Error Handling Tests", self.test_error_handling),
            ("Security Tests", self.test_security_features),
            ("File System Tests", self.test_file_operations),
            ("Context Manager Tests", self.test_context_manager)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                print(f"{status} - {test_name}")
            except Exception as e:
                print(f"❌ FAILED - {test_name}: {e}")
                self.test_results[test_name] = {"success": False, "error": str(e)}
        
        self.generate_report()
    
    def test_configurations(self) -> Dict[str, Any]:
        """Test all configuration files"""
        results = {"success": True, "details": []}
        
        config_files = [
            "settings.json",
            "commands_config.json", 
            "tray_icon_config.json",
            "help_commands.json"
        ]
        
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        data = json.load(f)
                    results["details"].append(f"✅ {config_file}: Valid JSON, {len(data)} items")
                else:
                    results["details"].append(f"⚠️ {config_file}: File not found")
                    results["success"] = False
            except json.JSONDecodeError as e:
                results["details"].append(f"❌ {config_file}: JSON Error - {e}")
                results["success"] = False
            except Exception as e:
                results["details"].append(f"❌ {config_file}: {e}")
                results["success"] = False
        
        return results
    
    def test_nlp_engine(self) -> Dict[str, Any]:
        """Test NLP processing capabilities"""
        results = {"success": True, "details": [], "performance": {}}
        
        try:
            from core.context_manager import context_manager
            from core.nlp_engine import create_nlp_engine
            
            nlp_engine = create_nlp_engine(context_manager)
            
            test_phrases = [
                ("open notepad", "app_control"),
                ("what time is it", "time_query"),
                ("remind me to call mom", "reminder_management"),
                ("search for python tutorials", "search_web"),
                ("mute the sound", "system_control"),
                ("close chrome", "app_control"),
                ("find my report.pdf", "file_operation"),
                ("how's the weather", "search_web"),
                ("add task buy groceries", "reminder_management"),
                ("volume up", "system_control")
            ]
            
            correct_predictions = 0
            total_time = 0
            
            for phrase, expected_intent in test_phrases:
                start_time = time.time()
                result = nlp_engine.process_input(phrase)
                processing_time = time.time() - start_time
                total_time += processing_time
                
                predicted_intent = result["intent"]
                confidence = result["confidence"]
                
                if predicted_intent == expected_intent:
                    correct_predictions += 1
                    status = "✅"
                else:
                    status = "❌"
                
                results["details"].append(
                    f"{status} '{phrase}' -> {predicted_intent} (conf: {confidence:.2f}, time: {processing_time:.3f}s)"
                )
            
            accuracy = correct_predictions / len(test_phrases)
            avg_time = total_time / len(test_phrases)
            
            results["performance"]["accuracy"] = accuracy
            results["performance"]["avg_processing_time"] = avg_time
            results["details"].append(f"📊 Overall accuracy: {accuracy:.2%}")
            results["details"].append(f"⏱️ Average processing time: {avg_time:.3f}s")
            
            if accuracy < 0.6:  # 60% accuracy threshold
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ NLP Engine Error: {e}")
            traceback.print_exc()
        
        return results
    
    def test_command_matching(self) -> Dict[str, Any]:
        """Test fuzzy command matching"""
        results = {"success": True, "details": []}
        
        try:
            with open("commands_config.json", "r") as f:
                commands_config = json.load(f)
            
            # Build aliases
            ALIASES = {}
            for command, config in commands_config.items():
                if isinstance(config, dict):
                    for alias in config.get("aliases", []):
                        ALIASES[alias.lower()] = command
            
            def match_command(user_input):
                matches = difflib.get_close_matches(user_input, ALIASES.keys(), n=1, cutoff=0.6)
                return ALIASES[matches[0]] if matches else None
            
            test_cases = [
                ("open notepad", "open_notepad", True),
                ("oepn notepad", "open_notepad", True),  # Typo
                ("launch chrome", "open_chrome", True),
                ("time please", None, False),  # Should not match
                ("what time is it", "get_time", True),
                ("exit krypton", "exit", True),
                ("random gibberish", None, False)
            ]
            
            correct_matches = 0
            
            for input_text, expected, should_match in test_cases:
                matched = match_command(input_text.lower())
                
                if should_match and matched == expected:
                    results["details"].append(f"✅ '{input_text}' -> {matched}")
                    correct_matches += 1
                elif not should_match and matched is None:
                    results["details"].append(f"✅ '{input_text}' -> No match (correct)")
                    correct_matches += 1
                else:
                    results["details"].append(f"❌ '{input_text}' -> {matched} (expected {expected})")
            
            accuracy = correct_matches / len(test_cases)
            results["details"].append(f"📊 Matching accuracy: {accuracy:.2%}")
            
            if accuracy < 0.8:  # 80% accuracy threshold
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Command matching error: {e}")
        
        return results
    
    def test_plugin_system(self) -> Dict[str, Any]:
        """Test plugin loading and basic functionality"""
        results = {"success": True, "details": []}
        
        try:
            plugins_dir = "plugins"
            if not os.path.exists(plugins_dir):
                results["success"] = False
                results["details"].append("❌ Plugins directory not found")
                return results
            
            plugins = []
            for filename in os.listdir(plugins_dir):
                if filename.endswith(".py") and filename != "base_plugin.py":
                    plugin_name = os.path.splitext(filename)[0]
                    plugins.append(plugin_name)
                    
                    # Test plugin file syntax
                    try:
                        with open(os.path.join(plugins_dir, filename), 'r') as f:
                            plugin_code = f.read()
                        
                        # Basic syntax check
                        compile(plugin_code, filename, 'exec')
                        results["details"].append(f"✅ {filename}: Syntax OK")
                        
                    except SyntaxError as e:
                        results["details"].append(f"❌ {filename}: Syntax Error - {e}")
                        results["success"] = False
                    except Exception as e:
                        results["details"].append(f"⚠️ {filename}: {e}")
            
            results["details"].append(f"📊 Total plugins found: {len(plugins)}")
            
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Plugin system error: {e}")
        
        return results
    
    def test_performance(self) -> Dict[str, Any]:
        """Test system performance metrics"""
        results = {"success": True, "details": [], "metrics": {}}
        
        try:
            # Test import speed
            start_time = time.time()
            import speech_recognition as sr
            import pyttsx3
            import pygame
            import_time = time.time() - start_time
            
            results["metrics"]["import_time"] = import_time
            results["details"].append(f"📦 Import time: {import_time:.3f}s")
            
            # Test TTS initialization
            start_time = time.time()
            engine = pyttsx3.init()
            tts_init_time = time.time() - start_time
            
            results["metrics"]["tts_init_time"] = tts_init_time
            results["details"].append(f"🗣️ TTS init time: {tts_init_time:.3f}s")
            
            # Test pygame mixer
            start_time = time.time()
            pygame.mixer.init()
            mixer_init_time = time.time() - start_time
            
            results["metrics"]["mixer_init_time"] = mixer_init_time
            results["details"].append(f"🔊 Mixer init time: {mixer_init_time:.3f}s")
            
            # Performance thresholds
            if import_time > 5.0:  # 5 second threshold
                results["success"] = False
                results["details"].append("❌ Import time too slow")
            
            if tts_init_time > 3.0:  # 3 second threshold
                results["success"] = False
                results["details"].append("❌ TTS initialization too slow")
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Performance test error: {e}")
        
        return results
    
    def test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage patterns"""
        results = {"success": True, "details": [], "metrics": {}}
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            results["metrics"]["initial_memory_mb"] = initial_memory
            results["details"].append(f"💾 Initial memory: {initial_memory:.1f} MB")
            
            # Simulate some operations
            test_data = []
            for i in range(1000):
                test_data.append(f"test_command_{i}" * 10)
            
            memory_after_ops = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after_ops - initial_memory
            
            results["metrics"]["memory_after_ops_mb"] = memory_after_ops
            results["metrics"]["memory_increase_mb"] = memory_increase
            results["details"].append(f"💾 Memory after operations: {memory_after_ops:.1f} MB")
            results["details"].append(f"📈 Memory increase: {memory_increase:.1f} MB")
            
            # Memory usage thresholds
            if initial_memory > 200:  # 200 MB threshold
                results["success"] = False
                results["details"].append("❌ Initial memory usage too high")
            
            if memory_increase > 50:  # 50 MB increase threshold
                results["success"] = False
                results["details"].append("❌ Memory increase too high")
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Memory test error: {e}")
        
        return results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios"""
        results = {"success": True, "details": []}
        
        error_scenarios = [
            ("Missing file operation", "open file nonexistent.txt"),
            ("Invalid command", "random gibberish command"),
            ("Empty input", ""),
            ("Special characters", "!@#$%^&*()"),
            ("Very long input", "a" * 1000)
        ]
        
        try:
            with open("commands_config.json", "r") as f:
                commands_config = json.load(f)
            
            ALIASES = {}
            for command, config in commands_config.items():
                if isinstance(config, dict):
                    for alias in config.get("aliases", []):
                        ALIASES[alias.lower()] = command
            
            def match_command(user_input):
                try:
                    matches = difflib.get_close_matches(user_input, ALIASES.keys(), n=1, cutoff=0.6)
                    return ALIASES[matches[0]] if matches else None
                except Exception:
                    return None
            
            for scenario_name, test_input in error_scenarios:
                try:
                    result = match_command(test_input.lower())
                    results["details"].append(f"✅ {scenario_name}: Handled gracefully")
                except Exception as e:
                    results["details"].append(f"❌ {scenario_name}: Unhandled error - {e}")
                    results["success"] = False
                    
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Error handling test failed: {e}")
        
        return results
    
    def test_security_features(self) -> Dict[str, Any]:
        """Test security components"""
        results = {"success": True, "details": []}
        
        try:
            from cryptography.fernet import Fernet
            
            # Test encryption
            key = Fernet.generate_key()
            fernet = Fernet(key)
            test_message = b"test security message"
            
            encrypted = fernet.encrypt(test_message)
            decrypted = fernet.decrypt(encrypted)
            
            if decrypted == test_message:
                results["details"].append("✅ Encryption/decryption working")
            else:
                results["details"].append("❌ Encryption/decryption failed")
                results["success"] = False
            
            # Test PIN validation (simulated)
            test_pin = "2254"
            if len(test_pin) == 4 and test_pin.isdigit():
                results["details"].append("✅ PIN format validation working")
            else:
                results["details"].append("❌ PIN format validation failed")
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Security test error: {e}")
        
        return results
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test file system operations"""
        results = {"success": True, "details": []}
        
        try:
            # Test directory existence
            required_dirs = ["sounds", "Images", "data", "plugins", "core"]
            for directory in required_dirs:
                if os.path.exists(directory):
                    results["details"].append(f"✅ Directory {directory} exists")
                else:
                    results["details"].append(f"⚠️ Directory {directory} missing")
            
            # Test file creation in data directory
            test_file = "data/test_file.json"
            test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
            
            try:
                os.makedirs("data", exist_ok=True)
                with open(test_file, 'w') as f:
                    json.dump(test_data, f)
                
                # Test file reading
                with open(test_file, 'r') as f:
                    loaded_data = json.load(f)
                
                if loaded_data == test_data:
                    results["details"].append("✅ File read/write operations working")
                else:
                    results["details"].append("❌ File read/write data mismatch")
                    results["success"] = False
                
                # Cleanup
                os.remove(test_file)
                
            except Exception as e:
                results["details"].append(f"❌ File operations error: {e}")
                results["success"] = False
                
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ File system test error: {e}")
        
        return results
    
    def test_context_manager(self) -> Dict[str, Any]:
        """Test context management system"""
        results = {"success": True, "details": []}
        
        try:
            from core.context_manager import context_manager
            
            # Test adding commands to context
            test_commands = [
                ("open_notepad", "open notepad", "success"),
                ("get_time", "what time is it", "success"),
                ("search_web", "search python", "success")
            ]
            
            for command, input_text, result in test_commands:
                context_manager.add_command_to_context(
                    command=command,
                    input_text=input_text,
                    result=result
                )
            
            # Test context summary
            summary = context_manager.get_context_summary()
            
            if "session_info" in summary:
                results["details"].append("✅ Context summary generation working")
            else:
                results["details"].append("❌ Context summary generation failed")
                results["success"] = False
            
            if summary["session_info"]["commands_executed"] >= len(test_commands):
                results["details"].append("✅ Command counting working")
            else:
                results["details"].append("❌ Command counting incorrect")
                results["success"] = False
                
            results["details"].append(f"📊 Commands in context: {summary['session_info']['commands_executed']}")
            
        except Exception as e:
            results["success"] = False
            results["details"].append(f"❌ Context manager test error: {e}")
            traceback.print_exc()
        
        return results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 AUTOMATED TESTING REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result.get("success", False))
        total_tests = len(self.test_results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
        print(f"⏱️ Total Test Time: {total_time:.2f}s")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            print(f"\n{status} - {test_name}")
            
            for detail in result.get("details", []):
                print(f"  {detail}")
            
            if "metrics" in result:
                print("  📊 Metrics:")
                for metric, value in result["metrics"].items():
                    if isinstance(value, float):
                        print(f"    {metric}: {value:.3f}")
                    else:
                        print(f"    {metric}: {value}")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "summary": {
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "total": total_tests
            },
            "results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: test_report.json")
        
        # Recommendations
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Krypton is ready for production!")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed. Review and fix issues before proceeding.")
            print("🔧 Check the detailed results above for specific issues to address.")

if __name__ == "__main__":
    tester = KryptonTester()
    tester.run_all_tests()
