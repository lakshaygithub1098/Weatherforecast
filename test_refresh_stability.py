"""
Debug script to check what changes between forecast API calls.
"""
import sys
import statistics
from pathlib import Path
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.utils.weather_forecast import WeatherForecastService
from app.utils.preprocessing_forecast import ForecastPreprocessor
from app.utils.forecast_model_service import create_forecast_service

# Station
station_name = "Shadipur"
coords = {"lat": 28.651, "lon": 77.146}

print("=" * 80)
print(f"Testing {station_name} - Multiple Calls (Simulating Refresh)")
print("=" * 80)

forecast_service = create_forecast_service()

results = []

for call_num in range(3):
    print(f"\n\n{'='*80}")
    print(f"CALL #{call_num + 1} at {datetime.now().strftime('%H:%M:%S')}")
    print('='*80)
    
    # Get historical AQI
    last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station_name)
    station_baseline = statistics.mean(last_24_aqi)
    
    print(f"Historical AQI: {last_24_aqi[-5:]} (last 5 hours)")
    print(f"Baseline: {station_baseline:.1f}")
    
    # Get weather forecast
    weather_forecast = WeatherForecastService.get_24hour_forecast(coords["lat"], coords["lon"])
    print(f"Weather Hour 0: Temp={weather_forecast[0]['temperature']}°C, Wind={weather_forecast[0]['wind_speed']}m/s")
    
    # Current time affects the hour feature!
    current_time = datetime.now()
    print(f"Request Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Hour={current_time.hour})")
    
    # Prepare features
    features_array, metadata = ForecastPreprocessor.prepare_forecast_features(
        last_24_hours_aqi=last_24_aqi,
        forecast_weather=weather_forecast,
        current_timestamp=current_time,
        other_stations_aqi={"station1": station_baseline, "station2": 100.0},
        scaler=forecast_service.scaler
    )
    
    print(f"Feature Hour: {features_array[0, 15]}")  # Hour is feature 16 (index 15)
    
    # Generate forecast
    aqi_predictions = forecast_service.forecast_24hours(
        features_array=features_array,
        initial_aqi=last_24_aqi[-1]
    )
    
    baseline_trend = 1.0 + (station_baseline - 100.0) / 200.0
    adjusted_predictions = [
        max(0, min(500, pred * baseline_trend))
        for pred in aqi_predictions
    ]
    
    current_prediction = adjusted_predictions[0]
    print(f"\n✅ PREDICTION: {current_prediction:.1f}")
    print(f"   First 3 hours: {[f'{p:.1f}' for p in adjusted_predictions[:3]]}")
    
    results.append({
        "call": call_num + 1,
        "time": current_time.strftime('%H:%M:%S'),
        "hour": current_time.hour,
        "baseline": station_baseline,
        "prediction": current_prediction,
        "weather_temp": weather_forecast[0]['temperature']
    })
    
    if call_num < 2:
        print("\nWaiting 2 seconds before next call...")
        time.sleep(2)

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY - Why Did Predictions Change?")
print('='*80)

for r in results:
    print(f"Call {r['call']} ({r['time']}): Prediction={r['prediction']:.1f}, Baseline={r['baseline']:.1f}, Weather_Temp={r['weather_temp']:.1f}")

# Check if baseline changed
baselines = [r['baseline'] for r in results]
if len(set([f"{b:.0f}" for b in baselines])) > 1:
    print("\n⚠️  BASELINE (station AQI mean) CHANGED between calls!")
    print("    Reason: CSV data was updated with new hourly readings")
else:
    print("\n✅ Baseline stayed the same")

# Check if weather changed
weathers = [r['weather_temp'] for r in results]
if len(set([f"{w:.1f}" for w in weathers])) > 1:
    print("\n⚠️  WEATHER changed between calls!")
    print("    Reason: OpenMeteo API returns slightly different forecast")
else:
    print("\n✅ Weather stayed the same")

# Check if hour changed
hours = [r['hour'] for r in results]
if len(set(hours)) > 1:
    print("\n⚠️  HOUR feature changed between calls!")
    print("    Reason: Requests span across hour boundary or hour is changing")
else:
    print("\n✅ Hour stayed the same")

print("\n" + "=" * 80)
