# Data Sources for AQI Predictions

## Current AQI Prediction (Real-time)
Frontend calls: `predictionsAPI.predict(latitude, longitude, station_name)`

Backend endpoint: `POST /predict`
Location: [backend/app/main.py](main.py#L127)

Data flow:
1. **Real-time Weather Data** ← Google Places API (or fallback weather service)
   - Source: `_weather_service.get_weather(lat, lon)`
   - Location: [backend/app/utils/weather.py](utils/weather.py)
   - Fetches: Temperature, Humidity, Wind Speed, Pressure, Visibility, etc.

2. **ML Model** ← XGBoost model
   - Source: [models/xgboost_aqi_model.pkl](../models/xgboost_aqi_model.pkl)
   - Input: Weather features + Location (lat/lon)
   - Output: Current AQI prediction

3. **Result Display**
   - Shows: "Current AQI: XXX" (real-time calculation based on weather)
   - Updated: Every time you refresh/click predict
   - Data freshness: Real-time weather only

---

## 24-Hour Forecast Data
Frontend calls: `/forecast?station={name}`

Backend endpoint: `GET /forecast`
Location: [backend/app/main.py](main.py#L255)

Data flow:
1. **Historical AQI Data** ← CSV file
   - Source: [data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv](../data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv)
   - Reads: Last 24 hours of hourly AQI readings for the selected station
   - Used for: Baseline calculation + lag features
   - Updates: When new sensor data added to CSV (hourly?)

2. **Weather Forecast (24h)** ← Open-Meteo API
   - Source: WeatherForecastService.get_24hour_forecast()
   - Location: [backend/app/utils/weather_forecast.py](utils/weather_forecast.py)
   - Fetches: Hourly forecast for next 24 hours (temp, humidity, wind, rain, etc.)

3. **ML Model** ← XGBoost model
   - Same as above: [models/xgboost_aqi_model.pkl](../models/xgboost_aqi_model.pkl)
   - Input: 24 hourly feature arrays (historical AQI + weather forecast)
   - Output: 24 hourly AQI predictions

4. **Caching**
   - Cached for 10 minutes to prevent recalculation
   - Cache key: Station name
   - Location: [backend/app/utils/cache.py](utils/cache.py)

---

## Summary Table

| What | Source | Freshness | Used For |
|------|--------|-----------|----------|
| **Current AQI Prediction** | Real-time weather API | Every refresh | "Current Air Quality" display |
| **Historical 24h AQI** | CSV file | Hourly when data updates | Forecast baseline + trends |
| **24h Weather Forecast** | Open-Meteo API | Every API call | Weather input for forecast model |
| **ML Predictions** | XGBoost model | Calculated on demand | AQI values (current + forecast) |

---

## Key Data File Locations

- **Current Weather**: Google API / Weather Service
- **Forecast Weather**: Free Open-Meteo API (https://open-meteo.com)
- **Historical AQI**: `data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv`
- **ML Models**: `models/xgboost_aqi_model.pkl`
- **Forecast Cache**: In-memory (10 min TTL)
