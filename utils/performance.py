"""
Performance monitoring and optimization utilities for Krypton
"""

import time
import psutil
import threading
from functools import wraps
from typing import Dict, Any, Callable
from collections import defaultdict

class PerformanceMonitor:
    """Monitor system and application performance"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(list)
        self.function_timings: Dict[str, list] = defaultdict(list)
        self.start_time = time.time()
        
    def time_function(self, func: Callable):
        """Decorator to time function execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                self.function_timings[func.__name__].append(duration)
                
                # Keep only last 100 timings to prevent memory bloat
                if len(self.function_timings[func.__name__]) > 100:
                    self.function_timings[func.__name__] = self.function_timings[func.__name__][-100:]
        
        return wrapper
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_function_stats(self, func_name: str) -> Dict[str, float]:
        """Get statistics for a specific function"""
        timings = self.function_timings.get(func_name, [])
        if not timings:
            return {}
        
        return {
            "calls": len(timings),
            "avg_time": sum(timings) / len(timings),
            "min_time": min(timings),
            "max_time": max(timings),
            "total_time": sum(timings)
        }
    
    def log_performance(self, interval: int = 60):
        """Log performance metrics at regular intervals"""
        while True:
            stats = self.get_system_stats()
            self.metrics["system_stats"].append({
                "timestamp": time.time(),
                **stats
            })
            
            # Keep only last 100 entries
            if len(self.metrics["system_stats"]) > 100:
                self.metrics["system_stats"] = self.metrics["system_stats"][-100:]
            
            time.sleep(interval)

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Start performance logging in background
perf_thread = threading.Thread(target=perf_monitor.log_performance, daemon=True)
perf_thread.start()

# Decorator for easy use
def monitor_performance(func):
    """Convenience decorator for performance monitoring"""
    return perf_monitor.time_function(func)
