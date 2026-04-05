"""
Feature preprocessing for 24-hour AQI forecasting.
Constructs feature arrays for each hour of the forecast period.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ForecastPreprocessor:
    """Prepare features for 24-hour AQI forecasting."""
    
    # Feature names must match training order exactly (27 features)
    FEATURE_COLUMNS = [
        'upwind_aqi',
        'upwind_aqi_lag1', 'upwind_aqi_lag2', 'upwind_aqi_lag3', 'upwind_aqi_lag24',
        'wind_speed_ms', 'wind_x', 'wind_y',
        'temp_c', 'humidity_pct', 'rain_mm', 'visibility_m', 'pressure_hpa',
        'temp_sq', 'humidity_sq',
        'hour', 'day', 'month', 'hour_sq',
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
        'wind_humidity_inter', 'temp_humidity_inter', 'wind_temp_inter',
        'visibility_scaled', 'upwind_wind_inter'
    ]
    
    @staticmethod
    def prepare_forecast_features(
        last_24_hours_aqi: List[float],
        forecast_weather: List[Dict],
        current_timestamp: datetime,
        other_stations_aqi: Optional[Dict[str, float]] = None,
        scaler=None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Prepare 24-hour forecast features.
        
        Args:
            last_24_hours_aqi: List of last 24 hourly AQI values
            forecast_weather: List of 24 forecast dicts with weather data
            current_timestamp: Current datetime
            other_stations_aqi: Dict with other station AQI values
            scaler: Fitted StandardScaler (optional, for normalization)
            
        Returns:
            Tuple of (feature_array shape (24, num_features), metadata)
        """
        try:
            if len(last_24_hours_aqi) < 24:
                # Pad with repeated values if less than 24 hours
                last_24_hours_aqi = list(last_24_hours_aqi) + [last_24_hours_aqi[-1]] * (24 - len(last_24_hours_aqi))
            else:
                last_24_hours_aqi = list(last_24_hours_aqi[-24:])
            
            if len(forecast_weather) < 24:
                # Repeat last weather if needed
                forecast_weather = list(forecast_weather) + [forecast_weather[-1]] * (24 - len(forecast_weather))
            else:
                forecast_weather = list(forecast_weather[:24])
            
            features_list = []
            metadata_list = []
            
            # Initialize lags with last known values
            aqi_lag1 = last_24_hours_aqi[-1]
            aqi_lag2 = last_24_hours_aqi[-2] if len(last_24_hours_aqi) > 1 else last_24_hours_aqi[-1]
            aqi_lag3 = last_24_hours_aqi[-3] if len(last_24_hours_aqi) > 2 else last_24_hours_aqi[-1]
            aqi_lag24 = last_24_hours_aqi[0] if len(last_24_hours_aqi) >= 24 else last_24_hours_aqi[-1]
            
            # Extract other station AQIs (upwind stations)
            upwind_aqi = other_stations_aqi.get('station1', 100.0) if other_stations_aqi else 100.0
            
            for hour_idx in range(24):
                timestamp = current_timestamp + timedelta(hours=hour_idx)
                weather = forecast_weather[hour_idx]
                
                # Extract weather components
                temp = weather.get('temperature', 25.0)
                humidity = weather.get('humidity', 50)
                wind_speed = weather.get('wind_speed', 2.0)
                wind_dir = weather.get('wind_direction', 180)
                pressure = weather.get('pressure', 1013)
                visibility = weather.get('visibility_m', 10000)
                precip = weather.get('precipitation', 0.0)
                
                # Convert wind direction to components
                angle_rad = np.deg2rad(wind_dir)
                wind_x = wind_speed * np.cos(angle_rad)
                wind_y = wind_speed * np.sin(angle_rad)
                
                # Time features
                hour = float(timestamp.hour)
                day = float(timestamp.day)
                month = float(timestamp.month)
                
                # Cyclical time encoding
                hour_sin = np.sin(2 * np.pi * hour / 24)
                hour_cos = np.cos(2 * np.pi * hour / 24)
                day_sin = np.sin(2 * np.pi * day / 31)
                day_cos = np.cos(2 * np.pi * day / 31)
                
                # Polynomial features
                temp_sq = temp ** 2
                humidity_sq = humidity ** 2
                hour_sq = hour ** 2
                
                # Interaction features
                wind_humidity_inter = wind_speed * humidity / 100
                temp_humidity_inter = temp * humidity / 100
                wind_temp_inter = wind_speed * temp / 25
                
                # Derived features
                visibility_scaled = visibility / 1000.0 * 10
                upwind_wind_inter = upwind_aqi * wind_speed / 5.0
                
                # Build feature vector - 27 features to match XGBoost training
                # Must match order exactly with features.py construct_feature_vector
                features = np.array([
                    upwind_aqi,  # 1
                    aqi_lag1,  # 2
                    aqi_lag2,  # 3
                    aqi_lag3,  # 4
                    aqi_lag24,  # 5
                    wind_speed,  # 6
                    wind_x,  # 7
                    wind_y,  # 8
                    temp,  # 9
                    humidity,  # 10
                    precip,  # 11 (rain_mm)
                    visibility / 1000.0,  # 12 (in km)
                    pressure,  # 13
                    temp_sq,  # 14
                    humidity_sq,  # 15
                    hour,  # 16
                    day,  # 17
                    month,  # 18
                    hour_sq,  # 19
                    hour_sin,  # 20
                    hour_cos,  # 21
                    day_sin,  # 22
                    day_cos,  # 23
                    wind_humidity_inter,  # 24
                    temp_humidity_inter,  # 25
                    wind_temp_inter,  # 26
                    visibility_scaled,  # 27
                ], dtype=np.float32)
                
                features_list.append(features)
                metadata_list.append({
                    "hour": int(hour),
                    "timestamp": timestamp.isoformat(),
                    "temperature": round(temp, 1),
                    "humidity": humidity,
                    "wind_speed": round(wind_speed, 2),
                })
                
                # Update lags for next iteration (aqi_lag1 will be updated with prediction)
                aqi_lag24 = aqi_lag3
                aqi_lag3 = aqi_lag2
                aqi_lag2 = aqi_lag1
            
            # Convert to numpy array shape (24, 27 features)
            features_array = np.array(features_list, dtype=np.float32)
            
            # Ensure we have exactly 27 features
            if features_array.shape[1] != 27:
                logger.warning(f"Feature shape is {features_array.shape[1]}, expected 27")
                if features_array.shape[1] < 27:
                    # Pad with zeros
                    pad_width = ((0, 0), (0, 27 - features_array.shape[1]))
                    features_array = np.pad(features_array, pad_width, mode='constant')
                else:
                    # Truncate
                    features_array = features_array[:, :27]
            
            # Apply scaler if available
            if scaler is not None:
                try:
                    features_array = scaler.transform(features_array).astype(np.float32)
                    logger.debug("Applied scaler to forecast features")
                except Exception as e:
                    logger.warning(f"Could not apply scaler: {e}")
            
            logger.info(f"✅ Prepared forecast features: shape {features_array.shape}")
            return features_array, metadata_list
            
        except Exception as e:
            logger.error(f"Error preparing forecast features: {e}")
            # Return dummy features
            return np.ones((24, 28), dtype=np.float32), []
    
    @staticmethod
    def get_last_24_hours_aqi(station_name: str, csv_path: Optional[str] = None) -> List[float]:
        """
        Extract last 24 hours of AQI data for a station from CSV.
        
        Args:
            station_name: Name of the station
            csv_path: Path to data CSV
            
        Returns:
            List of 24 hourly AQI values (most recent last)
        """
        try:
            if csv_path is None:
                # Use default path
                from pathlib import Path
                csv_path = Path(__file__).parent.parent.parent.parent / "data" / "Processed" / "DELHI_MASTER_AQI_WEATHER_2025.csv"
            
            df = pd.read_csv(csv_path)
            
            # Filter for station
            station_data = df[df['station'] == station_name]
            
            if len(station_data) == 0:
                logger.warning(f"No data found for station {station_name}")
                return [100.0] * 24
            
            # Sort by datetime and get last 24 records
            station_data = station_data.sort_values('datetime')
            last_24 = station_data.tail(24)
            
            aqi_values = last_24['aqi'].values.tolist()
            
            # Ensure we have 24 values
            if len(aqi_values) < 24:
                aqi_values = [aqi_values[0]] * (24 - len(aqi_values)) + aqi_values
            
            return aqi_values[-24:]  # Return last 24
            
        except Exception as e:
            logger.error(f"Error getting last 24h AQI for {station_name}: {e}")
            return [100.0] * 24
