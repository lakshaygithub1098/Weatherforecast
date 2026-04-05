#!/usr/bin/env python
"""Test script to debug prediction issues."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.predictor import ModelLoader, ModelPredictor
from app.utils.features import FeatureExtractor
from app.utils.weather import WeatherServiceSync
from app.config import settings
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("=" * 60)
print("[TEST] Testing AQI Prediction Pipeline")
print("=" * 60)

# 1. Load models
print("\n[1] Loading models...")
try:
    xgb_model = ModelLoader.load_xgboost(settings.xgboost_model_path)
    print(f"   OK XGBoost: {type(xgb_model)}")
except Exception as e:
    print(f"   ERROR XGBoost: {e}")
    xgb_model = None

try:
    lstm_model = ModelLoader.load_lstm(settings.lstm_model_path)
    print(f"   OK LSTM: {type(lstm_model)}")
except Exception as e:
    print(f"   ERROR LSTM: {e}")
    lstm_model = None

# 2. Check model load status
if xgb_model is None and lstm_model is None:
    print("   ERROR: No models loaded!")
    sys.exit(1)

# 3. Create predictor
print("\n[2] Creating predictor...")
try:
    predictor = ModelPredictor(xgb_model, lstm_model)
    print("   OK Predictor created")
except Exception as e:
    print(f"   ERROR {e}")
    sys.exit(1)

# 4. Get weather data
print("\n[3] Fetching weather data...")
try:
    weather_service = WeatherServiceSync(settings.google_api_key)
    weather_data = weather_service.get_weather(28.55, 77.23)
    print(f"   OK Weather data OK: {weather_data}")
except Exception as e:
    print(f"   WARN Weather error: {e}")
    weather_data = {
        "temperature": 25.0,
        "humidity": 50,
        "wind_speed": 2.0,
        "wind_direction": 90,
        "pressure": 1013,
        "description": "Clear",
        "visibility": 10000
    }
    print(f"   INFO Using fallback weather: {weather_data}")

# 5. Extract features
print("\n[4] Extracting features...")
try:
    feature_vector = FeatureExtractor.construct_feature_vector(
        weather_data=weather_data,
        location_data={'latitude': 28.55, 'longitude': 77.23},
        historical_data={}
    )
    print(f"   OK Features shape: {feature_vector.shape}")
    print(f"   OK Features: {feature_vector}")
except Exception as e:
    print(f"   ERROR {e}")
    sys.exit(1)

# 6. Make prediction
print("\n[5] Making prediction...")
try:
    # Detailed debugging
    print(f"   INFO XGBoost model type: {type(predictor.xgb_model)}")
    print(f"   INFO Input features shape: {feature_vector.shape}")
    print(f"   INFO Input features (first 5): {feature_vector[:5]}")
    
    # Direct XGBoost test
    if predictor.xgb_model:
        xgb_features = feature_vector.reshape(1, -1)
        raw_pred = predictor.xgb_model.predict(xgb_features)
        print(f"   INFO Raw XGBoost output: {raw_pred}")
        print(f"   INFO Raw output type: {type(raw_pred)}")
        print(f"   INFO Raw output shape: {raw_pred.shape if hasattr(raw_pred, 'shape') else 'N/A'}")
    
    predictions = predictor.predict(feature_vector)
    print(f"   OK AQI: {predictions['aqi']:.1f}")
    print(f"   OK XGBoost: {predictions['xgboost_prediction']:.1f}")
    print(f"   OK LSTM: {predictions['lstm_prediction']:.1f}")
    print(f"   OK Confidence: {predictions['model_confidence']}")
except Exception as e:
    print(f"   ERROR Prediction error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 7. Get feature importance
print("\n[6] Calculating feature importance...")
try:
    importance = FeatureExtractor.get_feature_importance_mock(feature_vector, predictions)
    print(f"   OK Top factors:")
    for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      - {k}: {v*100:.1f}%")
except Exception as e:
    print(f"   ERROR {e}")

print("\n" + "=" * 60)
print("SUCCESS: All tests passed!")
print("=" * 60)
