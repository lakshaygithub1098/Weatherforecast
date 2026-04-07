"""
Debug script to test forecast endpoint for different stations.
"""
import sys
import json
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.utils.weather_forecast import WeatherForecastService
from app.utils.preprocessing_forecast import ForecastPreprocessor

# Station coordinates
stations = {
    "NSUT": {"lat": 28.686, "lon": 77.209},
    "Shadipur": {"lat": 28.651, "lon": 77.146},
    "DTU": {"lat": 28.750049, "lon": 77.111261},
}

print("=" * 80)
print("Testing Weather Forecast for Different Stations")
print("=" * 80)

# Test 1: Compare weather forecasts
print("\n1. WEATHER FORECAST COMPARISON:")
print("-" * 80)

weather_data = {}
for station_name, coords in stations.items():
    try:
        forecast = WeatherForecastService.get_24hour_forecast(coords["lat"], coords["lon"])
        weather_data[station_name] = forecast
        print(f"\n{station_name} ({coords['lat']}, {coords['lon']})")
        print(f"  Hours 0-3 temps: {[f['temperature'] for f in forecast[:4]]}")
        print(f"  Hours 0-3 wind_speed: {[f['wind_speed'] for f in forecast[:4]]}")
        print(f"  Hours 0-3 humidity: {[f['humidity'] for f in forecast[:4]]}")
    except Exception as e:
        print(f"\nError fetching weather for {station_name}: {e}")

# Test 2: Compare historical AQI
print("\n\n2. HISTORICAL AQI COMPARISON (Last 24 hours):")
print("-" * 80)

aqi_data = {}
for station_name in stations.keys():
    try:
        last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station_name)
        aqi_data[station_name] = last_24_aqi
        print(f"\n{station_name}")
        print(f"  First 4 hours: {last_24_aqi[:4]}")
        print(f"  Last 4 hours: {last_24_aqi[-4:]}")
        print(f"  Min: {min(last_24_aqi):.1f}, Max: {max(last_24_aqi):.1f}, Mean: {sum(last_24_aqi)/len(last_24_aqi):.1f}")
    except Exception as e:
        print(f"\nError getting AQI for {station_name}: {e}")

# Test 3: Compare feature preparation (if models loaded)
print("\n\n3. FEATURE ARRAY COMPARISON (First 5 features, Hour 0):")
print("-" * 80)

from app.utils.forecast_model_service import create_forecast_service
from datetime import datetime

try:
    forecast_service = create_forecast_service(
        xgb_path="backend/models/xgboost_model.pkl",
        lstm_path=None
    )
    
    for station_name in stations.keys():
        if station_name in aqi_data and station_name in weather_data:
            try:
                features_array, metadata = ForecastPreprocessor.prepare_forecast_features(
                    last_24_hours_aqi=aqi_data[station_name],
                    forecast_weather=weather_data[station_name],
                    current_timestamp=datetime.now(),
                    other_stations_aqi={"station1": 100.0},
                    scaler=forecast_service.scaler
                )
                print(f"\n{station_name} - First hour features (first 10):")
                print(f"  {features_array[0][:10]}")
            except Exception as e:
                print(f"\nError preparing features for {station_name}: {e}")
except Exception as e:
    print(f"\nError loading forecast service: {e}")

print("\n" + "=" * 80)
print("END OF DEBUG")
print("=" * 80)
