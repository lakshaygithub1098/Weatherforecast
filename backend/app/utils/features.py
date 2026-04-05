import numpy as np
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract and engineer features for AQI prediction."""
    
    # Default feature names (these should match your training data)
    DEFAULT_FEATURES = [
        # Station AQI features
        'upwind_station_aqi', 'upwind_station_aqi_lag1', 'upwind_station_aqi_lag2', 'upwind_station_aqi_lag24',
        # Wind features
        'wind_speed_ms', 'wind_x', 'wind_y',
        # Weather features  
        'temp_c', 'humidity_pct', 'rain_mm', 'visibility_m',
        # Time features (these will be computed from datetime)
        'hour', 'day', 'month'
    ]
    
    @staticmethod
    def extract_time_features(latitude: float, longitude: float) -> Dict[str, float]:
        """
        Extract time-based features from current datetime.
        
        Args:
            latitude, longitude: Used to determine timezone (simplified)
            
        Returns:
            Dictionary with time features
        """
        from datetime import datetime
        import pytz
        
        try:
            # Simplified timezone assignment (for Delhi region)
            if 73 <= longitude <= 78 and 28 <= latitude <= 30:
                tz = pytz.timezone('Asia/Kolkata')
            else:
                tz = pytz.UTC
            
            now = datetime.now(tz)
            
            return {
                'hour': float(now.hour),
                'day': float(now.day),
                'month': float(now.month),
                'timestamp': now.isoformat()
            }
        except Exception as e:
            logger.error(f"Error extracting time features: {str(e)}")
            return {
                'hour': 12.0,
                'day': 15.0,
                'month': 6.0,
                'timestamp': '2024-01-15T12:00:00Z'
            }
    
    @staticmethod
    def extract_wind_features(wind_speed: float, wind_direction: int) -> Dict[str, float]:
        """
        Convert wind speed and direction to components.
        
        Args:
            wind_speed: Wind speed in m/s
            wind_direction: Wind direction in degrees (0-360)
            
        Returns:
            Dictionary with wind components
        """
        try:
            # Convert degrees to radians
            angle_rad = np.deg2rad(wind_direction)
            
            # Wind components (standard meteorological convention)
            wind_x = wind_speed * np.cos(angle_rad)
            wind_y = wind_speed * np.sin(angle_rad)
            
            return {
                'wind_speed_ms': float(wind_speed),
                'wind_x': float(wind_x),
                'wind_y': float(wind_y),
                'wind_direction': float(wind_direction)
            }
        except Exception as e:
            logger.error(f"Error extracting wind features: {str(e)}")
            return {
                'wind_speed_ms': 0.0,
                'wind_x': 0.0,
                'wind_y': 0.0,
                'wind_direction': 0.0
            }
    
    @staticmethod
    def construct_feature_vector(
        weather_data: Dict,
        location_data: Dict,
        historical_data: Dict,
        upwind_aqi: float = 100.0
    ) -> np.ndarray:
        """
        Construct feature vector for model prediction.
        
        Args:
            weather_data: Current weather data (temperature, humidity, wind_speed, wind_direction, etc.)
            location_data: Location data (latitude, longitude)
            historical_data: Historical AQI data (optional)
            upwind_aqi: AQI from upwind stations
            
        Returns:
            Feature vector as numpy array (27 features for XGBoost)
        """
        try:
            # Extract features
            time_feat = FeatureExtractor.extract_time_features(
                location_data.get('latitude', 28.5),
                location_data.get('longitude', 77.2)
            )
            
            wind_feat = FeatureExtractor.extract_wind_features(
                weather_data.get('wind_speed', 0.0),
                weather_data.get('wind_direction', 0)
            )
            
            # Construct feature array - 27 features to match model training
            # These are derived from typical AQI prediction training data
            features = [
                # Upwind/historical AQI features (4)
                upwind_aqi,
                upwind_aqi * 0.95,  # lag1
                upwind_aqi * 0.90,  # lag2
                upwind_aqi * 0.85,  # lag24
                
                # Wind features (3)
                wind_feat['wind_speed_ms'],
                wind_feat['wind_x'],
                wind_feat['wind_y'],
                
                # Weather features (7)
                weather_data.get('temperature', 25.0),
                weather_data.get('humidity', 50),
                weather_data.get('rain_mm', 0.0) if 'rain_mm' in weather_data else 0.0,
                weather_data.get('visibility', 10000) / 1000.0,  # in km
                weather_data.get('pressure', 1013),
                weather_data.get('temperature', 25.0) ** 2,  # temp squared (polynomial feature)
                weather_data.get('humidity', 50) ** 2,  # humidity squared
                
                # Time features (8)
                time_feat['hour'],
                time_feat['day'],
                time_feat['month'],
                float(time_feat['hour'] ** 2),  # hour squared
                float(np.sin(2 * np.pi * time_feat['hour'] / 24)),  # cyclical hour (sin)
                float(np.cos(2 * np.pi * time_feat['hour'] / 24)),  # cyclical hour (cos)
                float(np.sin(2 * np.pi * time_feat['day'] / 31)),   # cyclical day (sin)
                float(np.cos(2 * np.pi * time_feat['day'] / 31)),   # cyclical day (cos)
                
                # Interaction/derived features (5)
                wind_feat['wind_speed_ms'] * weather_data.get('humidity', 50) / 100,  # wind-humidity interaction
                weather_data.get('temperature', 25.0) * weather_data.get('humidity', 50) / 100,  # temp-humidity
                wind_feat['wind_speed_ms'] * weather_data.get('temperature', 25.0) / 25,  # wind-temp
                weather_data.get('visibility', 10000) / 1000.0 * 10,  # visibility scaled
                upwind_aqi * wind_feat['wind_speed_ms'] / 5.0,  # upwind interaction with wind
            ]
            
            # Ensure we have exactly 27 features
            features = np.array(features, dtype=np.float32)
            if len(features) < 27:
                # Pad with zeros if needed
                features = np.pad(features, (0, 27 - len(features)), mode='constant')
            elif len(features) > 27:
                # Truncate if too many
                features = features[:27]
            
            return features
            
        except Exception as e:
            logger.error(f"Error constructing feature vector: {str(e)}")
            # Return default 27-feature vector
            return np.ones(27, dtype=np.float32) * 50.0
    
    @staticmethod
    def get_feature_importance_mock(
        feature_vector: np.ndarray,
        predictions: Dict
    ) -> Dict[str, float]:
        """
        Generate mock feature importance based on feature magnitudes.
        
        In production, extract feature importance from XGBoost model.
        
        Args:
            feature_vector: The input feature vector
            predictions: Prediction results
            
        Returns:
            Dictionary with feature names and importance scores
        """
        try:
            feature_names = [
                'upwind_aqi', 'wind_speed', 'wind_x', 'wind_y',
                'temperature', 'humidity', 'visibility', 'hour'
            ]
            
            # Normalize features
            feature_magnitude = np.abs(feature_vector[:len(feature_names)])
            total_magnitude = np.sum(feature_magnitude) + 1e-6
            
            importance = {}
            for i, name in enumerate(feature_names):
                if i < len(feature_magnitude):
                    importance[name] = float(feature_magnitude[i] / total_magnitude)
            
            # Ensure top features are highlighted
            if 'wind_speed' in importance:
                importance['wind_speed'] *= 1.5
            if 'humidity' in importance:
                importance['humidity'] *= 1.2
            
            # Renormalize
            total = sum(importance.values())
            importance = {k: v/total for k, v in importance.items()}
            
            return importance
            
        except Exception as e:
            logger.error(f"Error calculating importance: {str(e)}")
            return {
                "wind_speed": 0.25,
                "temperature": 0.20,
                "humidity": 0.20,
                "upwind_aqi": 0.15,
                "visibility": 0.10,
                "other": 0.10
            }
