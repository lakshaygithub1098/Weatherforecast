from datetime import datetime
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class PredictionCache:
    """Simple in-memory cache for predictions."""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time to live for cache entries (default 5 minutes)
        """
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_key(self, latitude: float, longitude: float) -> str:
        """Generate cache key from coordinates."""
        return f"{latitude:.2f}_{longitude:.2f}"
    
    def get(self, latitude: float, longitude: float) -> Optional[dict]:
        """Get cached prediction if valid."""
        key = self.get_key(latitude, longitude)
        
        if key in self.cache:
            entry = self.cache[key]
            age = (datetime.utcnow() - entry['timestamp']).total_seconds()
            
            if age < self.ttl:
                logger.info(f"Cache hit for {key} (age: {age:.1f}s)")
                return entry['data']
            else:
                del self.cache[key]
                logger.info(f"Cache expired for {key}")
        
        return None
    
    def set(self, latitude: float, longitude: float, data: dict) -> None:
        """Store prediction in cache."""
        key = self.get_key(latitude, longitude)
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
        logger.info(f"Cached prediction for {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")


class ForecastCache:
    """Simple in-memory cache for 24-hour forecasts."""
    
    def __init__(self, ttl_seconds: int = 600):
        """
        Initialize forecast cache.
        
        Args:
            ttl_seconds: Time to live for cache entries (default 10 minutes)
        """
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_key(self, station: str) -> str:
        """Generate cache key from station name."""
        return f"forecast_{station.lower().strip()}"
    
    def get(self, station: str) -> Optional[dict]:
        """Get cached forecast if valid."""
        key = self.get_key(station)
        
        if key in self.cache:
            entry = self.cache[key]
            age = (datetime.utcnow() - entry['timestamp']).total_seconds()
            
            if age < self.ttl:
                logger.info(f"Forecast cache hit for {station} (age: {age:.1f}s, TTL: {self.ttl}s)")
                return entry['data']
            else:
                del self.cache[key]
                logger.info(f"Forecast cache expired for {station}")
        
        return None
    
    def set(self, station: str, data: dict) -> None:
        """Store forecast in cache."""
        key = self.get_key(station)
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
        logger.info(f"Cached forecast for {station}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Forecast cache cleared")


# Global cache instances
prediction_cache = PredictionCache(ttl_seconds=300)
forecast_cache = ForecastCache(ttl_seconds=600)  # 10 minutes for forecasts
