"""
Test script to verify the station-specific forecast fix.
"""
import sys
import statistics
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.utils.weather_forecast import WeatherForecastService
from app.utils.preprocessing_forecast import ForecastPreprocessor
from app.utils.forecast_model_service import create_forecast_service

# Station coordinates
stations = {
    "NSUT": {"lat": 28.686, "lon": 77.209},
    "Shadipur": {"lat": 28.651, "lon": 77.146},
    "DTU": {"lat": 28.750049, "lon": 77.111261},
}

print("=" * 80)
print("Testing Station-Specific Forecast Fix")
print("=" * 80)

# Load forecast service
try:
    forecast_service = create_forecast_service()
    print("✅ Forecast service loaded\n")
except Exception as e:
    print(f"⚠️  Could not load forecast service: {e}\n")
    forecast_service = None

results = {}

for station_name, coords in stations.items():
    try:
        print(f"\n{'='*80}")
        print(f"Station: {station_name} ({coords['lat']}, {coords['lon']})")
        print('='*80)
        
        # Get historical AQI
        last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station_name)
        station_baseline = statistics.mean(last_24_aqi)
        print(f"Historical AQI (last 24h): Min={min(last_24_aqi):.1f}, Max={max(last_24_aqi):.1f}, Mean={station_baseline:.1f}")
        
        # Get weather forecast
        weather_forecast = WeatherForecastService.get_24hour_forecast(coords["lat"], coords["lon"])
        print(f"Weather forecast obtained (24 hours)")
        
        # Prepare features WITH station-specific baseline
        print(f"\nPreparing features with station baseline AQI = {station_baseline:.1f}...")
        features_array, metadata = ForecastPreprocessor.prepare_forecast_features(
            last_24_hours_aqi=last_24_aqi,
            forecast_weather=weather_forecast,
            current_timestamp=datetime.now(),
            other_stations_aqi={"station1": station_baseline, "station2": 100.0},  # <-- STATION-SPECIFIC!
            scaler=forecast_service.scaler if forecast_service else None
        )
        
        print(f"Features array shape: {features_array.shape}")
        print(f"First 5 features (hour 0): {features_array[0][:5]}")
        
        # Generate forecast if service available
        if forecast_service:
            aqi_predictions = forecast_service.forecast_24hours(
                features_array=features_array,
                initial_aqi=last_24_aqi[-1]
            )
            
            # Apply baseline adjustment (same as main.py)
            baseline_trend = 1.0 + (station_baseline - 100.0) / 200.0
            adjusted_predictions = [
                max(0, min(500, pred * baseline_trend))
                for pred in aqi_predictions
            ]
            
            results[station_name] = {
                "baseline": station_baseline,
                "predictions": adjusted_predictions[:6],
                "trend": baseline_trend
            }
            
            print(f"\n✅ Forecast Generated:")
            print(f"   Baseline Trend Factor: {baseline_trend:.3f}")
            print(f"   First 6 hours: {[f'{p:.1f}' for p in adjusted_predictions[:6]]}")

    except Exception as e:
        print(f"❌ Error for {station_name}: {e}")

# Summary
print(f"\n\n{'='*80}")
print("COMPARISON SUMMARY")
print('='*80)

if len(results) >= 2:
    stations_list = list(results.items())
    for i, (station1, data1) in enumerate(stations_list):
        for station2, data2 in stations_list[i+1:]:
            pred_diff = abs(sum(data1["predictions"]) - sum(data2["predictions"])) / max(1, len(data1["predictions"]))
            print(f"\n{station1} vs {station2}:")
            print(f"  Baseline: {data1['baseline']:.1f} vs {data2['baseline']:.1f}")  
            print(f"  Trend Factor: {data1['trend']:.3f} vs {data2['trend']:.3f}")
            print(f"  Avg Prediction Difference: {pred_diff:.1f}")
            if pred_diff > 5:
                print(f"  ✅ Forecasts ARE DIFFERENT (good!)")
            else:
                print(f"  ⚠️  Forecasts still similar")

print("\n" + "=" * 80)
