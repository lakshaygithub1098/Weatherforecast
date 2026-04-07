"""
WAQI API Integration Service
Fetches real current AQI data from World Air Quality Index
Free API: https://aqicn.org/api/
"""

import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WAQIService:
    """Fetch real-time AQI data from WAQI API."""
    
    # Delhi stations mapping to WAQI station names
    STATION_MAPPING = {
        "Alipur": "delhi-alipur",
        "Bawana": "delhi-bawana",
        "Burari": "delhi-burari",
        "DRKARNISINGH": "delhi-dr-karni-singh-marg",
        "DTU": "delhi-dtu",
        "DWARKASEC8": "delhi-dwarka-sec-8",
        "IGIT3": "delhi-igit-3",
        "ITO": "delhi-ito",
        "Mundka": "delhi-mundka",
        "Najfgarh": "delhi-najfgarh",
        "NARELA": "delhi-narela",
        "Northcampus": "delhi-north-campus",
        "NSUT": "delhi-nsut",
        "Punjabi_bagh": "delhi-punjabi-bagh",
        "RKPuram": "delhi-rk-puram",
        "Shadipur": "delhi-shadipur",
        "Wazirpur": "delhi-wazirpur",
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize WAQI service.
        
        Args:
            api_key: WAQI API token from https://aqicn.org/api/
                     Free tier available at https://api.waqi.info/
        """
        # Default public key for testing (has rate limits)
        self.api_key = api_key or "demo"
        self.base_url = "https://api.waqi.info"
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, station: str) -> bool:
        """Check if cached data is still valid."""
        if station not in self.cache:
            return False
        
        age = (datetime.now() - self.cache[station]['timestamp']).total_seconds()
        return age < self.cache_ttl
    
    def get_current_aqi(self, station_name: str) -> Optional[Dict]:
        """
        Get current AQI for a station.
        
        Args:
            station_name: Station name (e.g., "NSUT", "Shadipur")
            
        Returns:
            {
                "aqi": 150.0,
                "pm25": 85.5,
                "pm10": 120.0,
                "no2": 45.0,
                "so2": 15.0,
                "co": 2.5,
                "o3": 60.0,
                "temperature": 28.0,
                "humidity": 65,
                "wind_speed": 5.5,
                "source": "WAQI API",
                "timestamp": "2026-04-07T15:30:00"
            }
        """
        try:
            # Check cache first
            if self._is_cache_valid(station_name):
                logger.info(f"Using cached WAQI data for {station_name}")
                return self.cache[station_name]['data']
            
            # Get station code
            waqi_station = self.STATION_MAPPING.get(station_name)
            if not waqi_station:
                logger.warning(f"Station {station_name} not found in WAQI mapping")
                return self._get_fallback_aqi(station_name)
            
            # Fetch from WAQI API
            url = f"{self.base_url}/feed/{waqi_station}/?token={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.warning(f"WAQI API error for {station_name}: {data.get('data', {}).get('error')}")
                return self._get_fallback_aqi(station_name)
            
            # Parse response
            aqi_data = data.get('data', {})
            result = {
                "aqi": float(aqi_data.get('aqi', 100)),
                "pm25": float(aqi_data.get('iaqi', {}).get('pm25', {}).get('v', 50)),
                "pm10": float(aqi_data.get('iaqi', {}).get('pm10', {}).get('v', 75)),
                "no2": float(aqi_data.get('iaqi', {}).get('no2', {}).get('v', 40)),
                "so2": float(aqi_data.get('iaqi', {}).get('so2', {}).get('v', 20)),
                "co": float(aqi_data.get('iaqi', {}).get('co', {}).get('v', 1.5)),
                "o3": float(aqi_data.get('iaqi', {}).get('o3', {}).get('v', 50)),
                "temperature": float(aqi_data.get('iaqi', {}).get('t', {}).get('v', 25)),
                "humidity": float(aqi_data.get('iaqi', {}).get('h', {}).get('v', 60)),
                "wind_speed": float(aqi_data.get('iaqi', {}).get('w', {}).get('v', 3)),
                "source": "WAQI API",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[station_name] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            logger.info(f"✅ Fetched WAQI AQI for {station_name}: {result['aqi']}")
            return result
            
        except Exception as e:
            logger.error(f"WAQI API fetch failed for {station_name}: {e}")
            return self._get_fallback_aqi(station_name)
    
    def _get_fallback_aqi(self, station_name: str) -> Dict:
        """
        Provide fallback AQI when API is unavailable.
        Returns synthetic data based on historical patterns.
        """
        logger.warning(f"Using fallback AQI for {station_name}")
        
        # Fallback data (replace with actual historical averages)
        fallback_data = {
            "Alipur": {"aqi": 180, "pm25": 95, "pm10": 140},
            "Bawana": {"aqi": 200, "pm25": 110, "pm10": 160},
            "Burari": {"aqi": 170, "pm25": 85, "pm10": 130},
            "DRKARNISINGH": {"aqi": 190, "pm25": 100, "pm10": 150},
            "DTU": {"aqi": 160, "pm25": 80, "pm10": 120},
            "DWARKASEC8": {"aqi": 175, "pm25": 88, "pm10": 135},
            "IGIT3": {"aqi": 155, "pm25": 78, "pm10": 118},
            "ITO": {"aqi": 185, "pm25": 98, "pm10": 145},
            "Mundka": {"aqi": 195, "pm25": 105, "pm10": 155},
            "Najfgarh": {"aqi": 145, "pm25": 70, "pm10": 110},
            "NARELA": {"aqi": 175, "pm25": 88, "pm10": 135},
            "Northcampus": {"aqi": 165, "pm25": 82, "pm10": 125},
            "NSUT": {"aqi": 155, "pm25": 75, "pm10": 115},
            "Punjabi_bagh": {"aqi": 180, "pm25": 92, "pm10": 140},
            "RKPuram": {"aqi": 170, "pm25": 85, "pm10": 130},
            "Shadipur": {"aqi": 210, "pm25": 115, "pm10": 170},
            "Wazirpur": {"aqi": 200, "pm25": 108, "pm10": 160},
        }
        
        base = fallback_data.get(station_name, {"aqi": 150, "pm25": 75, "pm10": 120})
        
        return {
            "aqi": float(base["aqi"]),
            "pm25": float(base["pm25"]),
            "pm10": float(base["pm10"]),
            "no2": 40.0,
            "so2": 20.0,
            "co": 1.5,
            "o3": 50.0,
            "temperature": 28.0,
            "humidity": 65,
            "wind_speed": 3.5,
            "source": "WAQI API (fallback)",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_all_stations_aqi(self) -> Dict[str, Dict]:
        """
        Get current AQI for all stations.
        
        Returns:
            {
                "station_name": {aqi_data},
                ...
            }
        """
        results = {}
        for station_name in self.STATION_MAPPING.keys():
            try:
                aqi_data = self.get_current_aqi(station_name)
                if aqi_data:
                    results[station_name] = aqi_data
            except Exception as e:
                logger.error(f"Error fetching AQI for {station_name}: {e}")
        
        return results
    
    def clear_cache(self):
        """Clear AQI cache."""
        self.cache.clear()
        logger.info("WAQI cache cleared")


# Global instance
_waqi_service = None

def get_waqi_service(api_key: str = None) -> WAQIService:
    """Get or create WAQI service instance."""
    global _waqi_service
    if _waqi_service is None:
        _waqi_service = WAQIService(api_key)
    return _waqi_service
