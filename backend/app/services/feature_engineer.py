"""
Proper feature engineering for LSTM forecasting.
Uses weather data and time-based features.
"""

import numpy as np
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class ProperFeatureEngineer:
    """Engineer features for LSTM time series prediction."""
    
    # Features that LSTM will use
    FEATURE_NAMES = [
        'temperature',
        'humidity',
        'wind_x',  # wind component (east-west)
        'wind_y',  # wind component (north-south)
        'hour_sin', 'hour_cos',  # cyclical hour encoding
        'day_of_week',
        'pressure',
        'visibility_scaled'
    ]
    
    @staticmethod
    def engineer_features_24h(
        weather_forecast: List[Dict],
        base_time: datetime = None
    ) -> np.ndarray:
        """
        Engineer features for 24-hour forecast window.
        
        Args:
            weather_forecast: List of 24 hourly weather dicts with:
                - temperature: °C
                - humidity: %
                - wind_speed: m/s
                - wind_direction: degrees (0-360)
                - pressure: hPa
                - visibility_m: meters
                - timestamp (optional)
            base_time: Reference time (default: now)
            
        Returns:
            Array of shape (24, num_features) normalized to [0, 1]
        """
        if base_time is None:
            base_time = datetime.now()
        
        try:
            features = []
            
            for hour_idx, weather in enumerate(weather_forecast[:24]):
                # Calculate timestamp for this hour
                if 'timestamp' in weather and weather['timestamp']:
                    try:
                        hour_time = datetime.fromisoformat(str(weather['timestamp']))
                    except:
                        hour_time = base_time + timedelta(hours=hour_idx)
                else:
                    hour_time = base_time + timedelta(hours=hour_idx)
                
                # Extract weather variables
                temp = float(weather.get('temperature', 25.0))
                humidity = float(weather.get('humidity', 50))
                wind_speed = float(weather.get('wind_speed', 2.0))
                wind_dir = float(weather.get('wind_direction', 180))
                pressure = float(weather.get('pressure', 1013))
                visibility = float(weather.get('visibility_m', 10000))
                
                # Convert wind direction to components (U and V)
                wind_rad = math.radians(wind_dir)
                wind_x = wind_speed * math.cos(wind_rad)
                wind_y = wind_speed * math.sin(wind_rad)
                
                # Cyclical encoding of hour (0-23)
                hour_val = float(hour_time.hour)
                hour_sin = math.sin(2 * math.pi * hour_val / 24)
                hour_cos = math.cos(2 * math.pi * hour_val / 24)
                
                # Day of week (0-6)
                day_of_week = float(hour_time.weekday())
                
                # Normalize visibility (scale to 0-1)
                visibility_scaled = min(visibility / 10000.0, 1.0)
                
                # Build feature vector
                feature_vector = [
                    temp,                  # Raw temperature
                    humidity,             # Raw humidity
                    wind_x,               # Wind X component
                    wind_y,               # Wind Y component
                    hour_sin,             # Hour sine
                    hour_cos,             # Hour cosine
                    day_of_week,          # Day of week
                    pressure,             # Raw pressure
                    visibility_scaled,    # Scaled visibility
                ]
                
                features.append(feature_vector)
            
            features_array = np.array(features, dtype=np.float32)
            
            # Normalize features to [0, 1] using min-max scaling
            features_normalized = ProperFeatureEngineer._normalize_features(features_array)
            
            logger.info(f"✅ Engineered {features_normalized.shape[0]} hours × {features_normalized.shape[1]} features")
            
            return features_normalized
        
        except Exception as e:
            logger.error(f"Feature engineering error: {e}")
            # Return default features
            return np.ones((24, len(ProperFeatureEngineer.FEATURE_NAMES)), dtype=np.float32) * 0.5
    
    @staticmethod
    def _normalize_features(features: np.ndarray) -> np.ndarray:
        """
        Normalize features to [0, 1] using min-max scaling.
        
        Args:
            features: Array of shape (24, num_features)
            
        Returns:
            Normalized array of same shape
        """
        try:
            # Define reasonable bounds for each feature
            feature_bounds = {
                0: (-20, 50),      # temperature
                1: (0, 100),       # humidity
                2: (-10, 10),      # wind_x
                3: (-10, 10),      # wind_y
                4: (-1, 1),        # hour_sin
                5: (-1, 1),        # hour_cos
                6: (0, 6),         # day_of_week
                7: (950, 1050),    # pressure
                8: (0, 1),         # visibility_scaled
            }
            
            normalized = np.copy(features)
            
            for col_idx in range(features.shape[1]):
                if col_idx in feature_bounds:
                    min_val, max_val = feature_bounds[col_idx]
                else:
                    min_val = features[:, col_idx].min()
                    max_val = features[:, col_idx].max()
                
                # Avoid division by zero
                if max_val == min_val:
                    normalized[:, col_idx] = 0.5
                else:
                    normalized[:, col_idx] = (features[:, col_idx] - min_val) / (max_val - min_val)
                    # Clip to [0, 1]
                    normalized[:, col_idx] = np.clip(normalized[:, col_idx], 0, 1)
            
            return normalized
        
        except Exception as e:
            logger.error(f"Normalization error: {e}")
            return features
    
    @staticmethod
    def add_aqi_feature(
        aqi_values: List[float],
        features: np.ndarray
    ) -> np.ndarray:
        """
        Add normalized AQI as first feature.
        
        Args:
            aqi_values: 24 hourly AQI values
            features: (24, num_features) array
            
        Returns:
            (24, num_features+1) array with AQI prepended
        """
        try:
            # Normalize AQI to [0, 1]
            aqi_array = np.array(aqi_values, dtype=np.float32).reshape(-1, 1)
            
            # Use AQI 0-500 as bounds
            aqi_normalized = np.clip(aqi_array / 500.0, 0, 1)
            
            # Concatenate AQI as first feature
            combined = np.hstack([aqi_normalized, features])
            
            logger.info(f"✅ Added AQI feature: AQI range {aqi_array.min():.1f} - {aqi_array.max():.1f}")
            
            return combined
        
        except Exception as e:
            logger.error(f"Error adding AQI feature: {e}")
            return features
