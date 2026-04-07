"""
Deep dive: What actually changes between rapid API calls?
"""
import sys
import statistics
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.utils.weather_forecast import WeatherForecastService
from app.utils.preprocessing_forecast import ForecastPreprocessor
from app.utils.forecast_model_service import create_forecast_service

station_name = "Shadipur"
coords = {"lat": 28.651, "lon": 77.146}

print("=" * 80)
print("Deep Analysis: What Changes Between Rapid Refreshes?")
print("=" * 80)

forecast_service = create_forecast_service()

print("\n[Analysis] Comparing 5 rapid calls within the same minute:\n")

results = []

for call_num in range(5):
    # Get historical AQI
    last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station_name)
    baseline = statistics.mean(last_24_aqi)
    
    # Get weather
    weather = WeatherForecastService.get_24hour_forecast(coords["lat"], coords["lon"])
    
    # Extract key weather values
    weather_values = {
        "temp": weather[0]['temperature'],
        "humidity": weather[0]['humidity'],
        "wind_speed": weather[0]['wind_speed'],
        "wind_dir": weather[0]['wind_direction'],
        "precip": weather[0]['precipitation'],
    }
    
    # Build feature array
    current_time = datetime.now()
    features_array, _ = ForecastPreprocessor.prepare_forecast_features(
        last_24_hours_aqi=last_24_aqi,
        forecast_weather=weather,
        current_timestamp=current_time,
        other_stations_aqi={"station1": baseline, "station2": 100.0},
        scaler=forecast_service.scaler
    )
    
    # Get prediction
    raw_preds = forecast_service.forecast_24hours(
        features_array=features_array,
        initial_aqi=last_24_aqi[-1]
    )
    
    baseline_trend = 1.0 + (baseline - 100.0) / 200.0
    adjusted = [max(0, min(500, p * baseline_trend)) for p in raw_preds]
    
    # Store results
    results.append({
        "call": call_num + 1,
        "baseline": baseline,
        "weather": weather_values,
        "raw_pred": raw_preds[0],
        "adjusted_pred": adjusted[0],
        "time": current_time.strftime('%H:%M:%S.%f')[:-3],
        "hour_feature": features_array[0, 15],
        "last_aqi_val": last_24_aqi[-1]
    })

# Print results
print("Call | Time        | Baseline | Weather(T°/H%/W) | Last AQI | Raw Pred | Adj Pred")
print("-" * 90)

for r in results:
    w = r["weather"]
    print(f"{r['call']}    | {r['time']} | {r['baseline']:7.1f} | "
          f"{w['temp']:4.1f}/{w['humidity']:3.0f}/{w['wind_speed']:3.1f}  | "
          f"{r['last_aqi_val']:7.1f} | {r['raw_pred']:7.1f} | {r['adjusted_pred']:7.1f}")

# Analysis
print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

baselines = [r['baseline'] for r in results]
temps = [r['weather']['temp'] for r in results]
adjusted_preds = [r['adjusted_pred'] for r in results]

print(f"\n✓ Baseline values:    {[f'{b:.1f}' for b in baselines]}")
print(f"  All same? {len(set([f'{b:.0f}' for b in baselines])) == 1}")

print(f"\n✓ Weather temps:      {[f'{t:.1f}' for t in temps]}")
print(f"  All same? {len(set([f'{t:.1f}' for t in temps])) == 1}")
print(f"  Range: {min(temps):.1f} to {max(temps):.1f}C (variation: {max(temps)-min(temps):.2f}C)")

print(f"\n✓ Adjusted predictions: {[f'{p:.1f}' for p in adjusted_preds]}")
print(f"  All same? {len(set([f'{p:.1f}' for p in adjusted_preds])) == 1}")
print(f"  Range: {min(adjusted_preds):.1f} to {max(adjusted_preds):.1f} (variation: {max(adjusted_preds)-min(adjusted_preds):.2f})")

if len(set([f'{p:.0f}' for p in adjusted_preds])) == 1:
    print("\n[OK] Predictions ARE identical - caching is just for efficiency!")
else:
    print(f"\n[ISSUE] Weather API returns DIFFERENT values each call!")
    print(f"        This causes prediction variation: +/- {(max(adjusted_preds)-min(adjusted_preds))/2:.1f} AQI")
    print(f"        Weather changes by up to {max(temps)-min(temps):.2f}C between calls")

print("\n" + "=" * 80)
