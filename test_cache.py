"""
Test the forecast caching implementation.
"""
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.utils.cache import ForecastCache

print("=" * 80)
print("Testing Forecast Cache Implementation")
print("=" * 80)

# Create cache with short TTL for testing (5 seconds)
cache = ForecastCache(ttl_seconds=5)

# Test data
station = "Shadipur"
forecast_data = {
    "station": station,
    "forecast": [
        {"hour": 0, "aqi": 327.5},
        {"hour": 1, "aqi": 327.2},
    ]
}

print(f"\n1. Initial cache (empty):")
result = cache.get(station)
print(f"   Result: {result}")

print(f"\n2. Storing forecast in cache...")
cache.set(station, forecast_data)

print(f"\n3. Retrieving immediately (should hit cache):")
result = cache.get(station)
print(f"   Result: {result['forecast'][0] if result else None}")

print(f"\n4. Retrieving after 2 seconds (should still hit cache):")
time.sleep(2)
result = cache.get(station)
print(f"   Result: {result['forecast'][0] if result else None}")

print(f"\n5. Waiting for cache to expire (6 seconds total)...")
time.sleep(4)
result = cache.get(station)
print(f"   Result: {result}")

print(f"\n✅ Cache test complete!")
print("=" * 80)
print("\nSummary:")
print("- Forecast is cached for 10 minutes in production")
print("- Multiple rapid refreshes will return the same cached forecast")
print("- After 10 minutes, a fresh forecast will be recalculated")
print("- This prevents the AQI predictions from fluctuating with each refresh")
