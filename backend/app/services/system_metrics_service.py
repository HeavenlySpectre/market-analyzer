import time
import logging
from datetime import datetime
from collections import deque
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemMetricsTracker:
    """Tracks system health metrics in memory."""
    
    def __init__(self):
        self.start_time = time.time()
        self.response_times = deque(maxlen=100)  # Keep last 100 requests
        self.api_call_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.downtime_seconds = 0  # Track any known downtime
        
        logger.info("[METRICS] System metrics tracker initialized")
    
    def record_api_call(self):
        """Record an API call."""
        self.api_call_count += 1
    
    def record_response_time(self, response_time: float):
        """Record a response time in seconds."""
        self.response_times.append(response_time)
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage."""
        current_time = time.time()
        total_uptime = current_time - self.start_time
        expected_uptime = total_uptime + self.downtime_seconds
        
        if expected_uptime == 0:
            return 100.0
        
        uptime_percentage = (total_uptime / expected_uptime) * 100
        return min(100.0, uptime_percentage)
    
    def get_avg_response_time(self) -> float:
        """Get average response time in seconds."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage."""
        total_cache_operations = self.cache_hits + self.cache_misses
        if total_cache_operations == 0:
            return 0.0
        return (self.cache_hits / total_cache_operations) * 100
    
    def get_api_call_count(self) -> int:
        """Get total API calls count."""
        return self.api_call_count
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics."""
        return {
            "uptime_percentage": round(self.get_uptime_percentage(), 1),
            "avg_response_time": round(self.get_avg_response_time(), 2),
            "cache_hit_rate": round(self.get_cache_hit_rate(), 1),
            "api_calls": self.get_api_call_count(),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "total_requests": len(self.response_times)
        }
    
    def add_mock_data(self):
        """Add some mock data for demonstration."""
        # Simulate some API calls and response times
        import random
        
        for _ in range(50):
            self.record_api_call()
            self.record_response_time(random.uniform(0.5, 4.0))
            
            # Simulate cache operations
            if random.random() < 0.8:  # 80% cache hit rate
                self.record_cache_hit()
            else:
                self.record_cache_miss()
        
        logger.info("[METRICS] Mock data added for demonstration")

# Global instance
system_metrics = SystemMetricsTracker()

# Add some initial mock data
system_metrics.add_mock_data()
