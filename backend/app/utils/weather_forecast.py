"""
Weather forecast service for 24-hour predictions.
Fetches forecast data from weather APIs or generates synthetic forecasts.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class WeatherForecastService:
    """Fetch and process 24-hour weather forecasts."""
    
    @staticmethod
    def get_24hour_forecast(latitude: float, longitude: float, api_key: Optional[str] = None) -> List[Dict]:
        """
        Get 24-hour hourly weather forecast for given coordinates.
        
        Args:
            latitude: Station latitude
            longitude: Station longitude
            api_key: Optional API key for weather service (Open-Meteo, etc.)
            
        Returns:
            List of 24 hourly forecast dicts with keys:
            - timestamp: ISO format datetime
            - temperature: degrees Celsius
            - humidity: percentage (0-100)
            - wind_speed: meters per second
            - wind_direction: degrees (0-360)
            - precipitation: mm
            - cloud_cover: percentage (0-100)
        """
        try:
            # Try to fetch from Open-Meteo API (free, no key required)
            forecast = WeatherForecastService._fetch_open_meteo(latitude, longitude)
            if forecast:
                logger.info(f"✅ Fetched forecast from Open-Meteo for ({latitude}, {longitude})")
                return forecast
        except Exception as e:
            logger.warning(f"Failed to fetch from Open-Meteo: {e}")
        
        # Fallback to synthetic forecast
        logger.warning("Using synthetic weather forecast")
        return WeatherForecastService._generate_synthetic_forecast()
    
    @staticmethod
    def _fetch_open_meteo(latitude: float, longitude: float) -> Optional[List[Dict]]:
        """
        Fetch from Open-Meteo API (free, no authentication needed).
        
        Open-Meteo provides free weather data for research and education.
        """
        try:
            import requests
            
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation",
                "timezone": "Asia/Kolkata",
                "forecast_days": 1,  # Next 24 hours only
                "models": "best_match"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "hourly" not in data:
                return None
            
            hourly = data["hourly"]
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            humidity = hourly.get("relative_humidity_2m", [])
            wind_speed = hourly.get("wind_speed_10m", [])
            wind_dir = hourly.get("wind_direction_10m", [])
            precip = hourly.get("precipitation", [])
            
            forecast = []
            for i in range(min(24, len(times))):
                forecast.append({
                    "timestamp": times[i] if i < len(times) else "",
                    "temperature": float(temps[i]) if i < len(temps) else 25.0,
                    "humidity": int(humidity[i]) if i < len(humidity) else 50,
                    "wind_speed": float(wind_speed[i]) if i < len(wind_speed) else 2.0,
                    "wind_direction": int(wind_dir[i]) if i < len(wind_dir) else 180,
                    "precipitation": float(precip[i]) if i < len(precip) else 0.0,
                    "cloud_cover": 50,  # Not provided by Open-Meteo hourly
                })
            
            return forecast if len(forecast) == 24 else None
            
        except ImportError:
            logger.warning("requests library not available for weather API")
            return None
        except Exception as e:
            logger.error(f"Error fetching from Open-Meteo: {e}")
            return None
    
    @staticmethod
    def _generate_synthetic_forecast() -> List[Dict]:
        """
        Generate synthetic 24-hour weather forecast.
        Useful for testing and when no API is available.
        """
        forecast = []
        now = datetime.now()
        
        # Base values with realistic hourly variation
        base_temp = 28.0  # Delhi average
        base_humidity = 65
        base_wind = 3.0
        
        for hour in range(24):
            timestamp = now + timedelta(hours=hour)
            
            # Temperature typically lower at night, peaks in afternoon
            hour_angle = (hour % 24) * 15 - 90  # -90 to 270 degrees
            temp_variation = 8 * np.sin(np.deg2rad(hour_angle))
            temperature = base_temp + temp_variation + random.gauss(0, 1)
            
            # Humidity inversely correlated with temperature
            humidity = int(base_humidity - temp_variation * 2 + random.gauss(0, 5))
            humidity = max(30, min(95, humidity))
            
            # Wind speed with some randomness
            wind_speed = base_wind + random.gauss(0, 0.5)
            wind_speed = max(0.5, wind_speed)
            
            # Wind direction somewhat constant (seasonal patterns)
            base_wind_dir = 180 + random.randint(-30, 30)
            wind_direction = (base_wind_dir + random.randint(-20, 20)) % 360
            
            # Precipitation unlikely but possible
            precipitation = 0.0 if random.random() > 0.1 else random.uniform(0.1, 2.0)
            
            forecast.append({
                "timestamp": timestamp.isoformat(),
                "temperature": round(temperature, 1),
                "humidity": humidity,
                "wind_speed": round(wind_speed, 2),
                "wind_direction": int(wind_direction),
                "precipitation": round(precipitation, 2),
                "cloud_cover": int(50 + humidity / 2 + random.randint(-20, 20)),
            })
        
        return forecast


import numpy as np
