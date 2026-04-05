"""
AQI Prediction System - Development Utilities
Helpful functions for development and testing
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelDebugger:
    """Debug utilities for ML models."""
    
    @staticmethod
    def check_model_file(path: str) -> bool:
        """Check if model file exists and is readable."""
        try:
            file_path = Path(path)
            if not file_path.exists():
                logger.error(f"Model file not found: {path}")
                return False
            
            file_size = file_path.stat().st_size
            logger.info(f"✅ Model file found: {path} ({file_size / 1024 / 1024:.2f} MB)")
            return True
        except Exception as e:
            logger.error(f"Error checking model: {str(e)}")
            return False
    
    @staticmethod
    def test_prediction(model, features):
        """Test if model can make a prediction."""
        try:
            import numpy as np
            features_array = np.array(features).reshape(1, -1)
            prediction = model.predict(features_array)
            logger.info(f"✅ Model prediction test passed: {prediction[0]:.2f}")
            return True
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}")
            return False


class APIDebugger:
    """Debug utilities for API testing."""
    
    @staticmethod
    def generate_test_request():
        """Generate a test prediction request."""
        return {
            "latitude": 28.5505,  # ITO, Delhi
            "longitude": 77.2303,
            "station_name": "ITO"
        }
    
    @staticmethod
    def print_api_info():
        """Print API endpoint information."""
        endpoints = {
            "POST /predict": "Get AQI prediction for a location",
            "GET /stations": "List all monitoring stations",
            "GET /health": "API health check",
            "GET /models/info": "Model information and weights",
            "GET /cache/stats": "Cache statistics",
            "POST /cache/clear": "Clear prediction cache",
            "GET /docs": "Interactive API documentation (Swagger)",
            "GET /redoc": "API documentation (ReDoc)",
        }
        
        print("\n" + "="*60)
        print("AQI Prediction API - Endpoints")
        print("="*60)
        
        for endpoint, description in endpoints.items():
            print(f"\n  {endpoint}")
            print(f"  └─ {description}")
        
        print("\n" + "="*60 + "\n")


class FeatureDebugger:
    """Debug utilities for feature engineering."""
    
    @staticmethod
    def print_feature_schema():
        """Print expected feature schema."""
        features = [
            "upwind_station_aqi",
            "upwind_station_aqi_lag1",
            "upwind_station_aqi_lag2",
            "upwind_station_aqi_lag24",
            "wind_speed_ms",
            "wind_x",
            "wind_y",
            "temp_c",
            "humidity_pct",
            "rain_mm",
            "visibility_m",
            "hour",
            "day",
            "month"
        ]
        
        print("\n" + "="*60)
        print("Expected Feature Schema")
        print("="*60)
        
        for i, feature in enumerate(features, 1):
            print(f"  {i:2d}. {feature}")
        
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def validate_feature_vector(features: List[float]) -> bool:
        """Validate if feature vector has correct shape."""
        expected_length = 14
        
        if len(features) != expected_length:
            logger.error(
                f"Feature vector length mismatch. Expected {expected_length}, got {len(features)}"
            )
            return False
        
        # Check for NaN or Inf
        import numpy as np
        features_array = np.array(features)
        
        if np.any(np.isnan(features_array)):
            logger.error("Feature vector contains NaN values")
            return False
        
        if np.any(np.isinf(features_array)):
            logger.error("Feature vector contains Inf values")
            return False
        
        logger.info("✅ Feature vector validation passed")
        return True


def run_diagnostics():
    """Run full system diagnostics."""
    print("\n" + "🔍" * 10 + " AQI System Diagnostics " + "🔍" * 10 + "\n")
    
    # Check Python version
    import sys
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}\n")
    
    # Check required packages
    packages = ['fastapi', 'uvicorn', 'xgboost', 'tensorflow', 'pandas', 'numpy']
    print("Installed Packages:")
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (NOT INSTALLED)")
    
    print("\n" + "="*60 + "\n")
    
    # Print API info
    APIDebugger.print_api_info()
    
    # Print feature schema
    FeatureDebugger.print_feature_schema()


if __name__ == "__main__":
    run_diagnostics()
