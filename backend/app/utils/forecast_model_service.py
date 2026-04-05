"""
Model service for 24-hour AQI forecasting.
Loads models and generates 24-hour predictions.
"""

import numpy as np
import logging
from typing import List, Optional, Tuple
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class ForecastModelService:
    """Manage models for 24-hour forecasting."""
    
    def __init__(self, xgb_model_path: str, lstm_model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        """
        Initialize model service.
        
        Args:
            xgb_model_path: Path to XGBoost model
            lstm_model_path: Path to LSTM model (optional)
            scaler_path: Path to feature scaler (optional)
        """
        self.xgb_model = None
        self.lstm_model = None
        self.scaler = None
        self.xgb_model_path = xgb_model_path
        self.lstm_model_path = lstm_model_path
        self.scaler_path = scaler_path
        
        self._load_models()
    
    def _load_models(self):
        """Load all available models."""
        # Load XGBoost
        if Path(self.xgb_model_path).exists():
            try:
                with open(self.xgb_model_path, 'rb') as f:
                    self.xgb_model = pickle.load(f)
                logger.info("✅ XGBoost model loaded for forecasting")
            except Exception as e:
                logger.error(f"Failed to load XGBoost: {e}")
        else:
            logger.warning(f"XGBoost model not found at {self.xgb_model_path}")
        
        # Load LSTM (optional)
        if self.lstm_model_path and Path(self.lstm_model_path).exists():
            try:
                from tensorflow import keras
                self.lstm_model = keras.models.load_model(self.lstm_model_path)
                logger.info("✅ LSTM model loaded for forecasting")
            except Exception as e:
                logger.warning(f"LSTM not available: {e}")
        
        # Load Scaler (optional)
        if self.scaler_path and Path(self.scaler_path).exists():
            try:
                import joblib
                self.scaler = joblib.load(self.scaler_path)
                logger.info("✅ Feature scaler loaded")
            except Exception as e:
                logger.warning(f"Scaler not available: {e}")
    
    def forecast_24hours(self, features_array: np.ndarray, initial_aqi: float = 100.0) -> List[float]:
        """
        Generate 24-hour AQI forecast using hybrid model.
        
        Args:
            features_array: Shape (24, num_features) - features for each hour
            initial_aqi: Initial AQI value for lag initialization
            
        Returns:
            List of 24 AQI predictions
        """
        predictions = []
        
        try:
            if self.xgb_model is None:
                logger.error("XGBoost model not loaded")
                return [initial_aqi] * 24
            
            # XGBoost predictions for each hour
            xgb_preds = []
            for hour_idx in range(24):
                try:
                    xgb_pred = float(self.xgb_model.predict(features_array[hour_idx:hour_idx+1])[0])
                    # Handle negative predictions
                    if xgb_pred < 0:
                        xgb_pred = abs(xgb_pred) + 50
                    xgb_preds.append(xgb_pred)
                except Exception as e:
                    logger.warning(f"XGBoost prediction failed for hour {hour_idx}: {e}")
                    xgb_preds.append(initial_aqi)
            
            # LSTM predictions (if available)
            lstm_preds = self._forecast_lstm(features_array) if self.lstm_model else None
            
            # Combine predictions (weighted ensemble)
            xgb_weight = 0.7
            lstm_weight = 0.3
            
            for hour_idx in range(24):
                xgb_val = xgb_preds[hour_idx]
                
                if lstm_preds:
                    lstm_val = lstm_preds[hour_idx]
                    final_pred = xgb_weight * xgb_val + lstm_weight * lstm_val
                else:
                    # XGBoost only
                    final_pred = xgb_val
                
                # Ensure reasonable AQI range (0-500)
                final_pred = max(0, min(500, float(final_pred)))
                predictions.append(round(final_pred, 1))
            
            logger.info(f"✅ Generated 24-hour forecast: {predictions[:3]}... (showing first 3)")
            return predictions
            
        except Exception as e:
            logger.error(f"Error in 24h forecasting: {e}")
            return [initial_aqi] * 24
    
    def _forecast_lstm(self, features_array: np.ndarray, initial_aqi: float = 100.0) -> Optional[List[float]]:
        """
        Generate LSTM predictions for 24 hours.
        
        Args:
            features_array: Shape (24, num_features)
            initial_aqi: Initial AQI value
            
        Returns:
            List of 24 predictions or None if LSTM unavailable
        """
        if self.lstm_model is None:
            return None
        
        try:
            # LSTM typically expects shape (batch_size, timesteps, features)
            # Use a sliding window approach or full 24-hour input
            
            # For simplicity, assume model can predict all 24 at once
            input_data = features_array.reshape(1, 24, -1)  # (1, 24, num_features)
            
            # Try prediction
            lstm_output = self.lstm_model.predict(input_data, verbose=0)
            
            if lstm_output.shape[-1] == 24:
                # Model returns all 24 predictions
                predictions = lstm_output[0].tolist()
            else:
                # Model returns 1 prediction, replicate for 24 hours
                single_pred = float(lstm_output[0, 0])
                predictions = [single_pred] * 24
            
            # Ensure valid range
            predictions = [max(0, min(500, float(p))) for p in predictions]
            
            logger.debug(f"LSTM predictions: {predictions[:3]}...")
            return predictions
            
        except Exception as e:
            logger.warning(f"LSTM prediction failed: {e}")
            return None


def create_forecast_service(
    xgb_path: str = None,
    lstm_path: str = None,
    scaler_path: str = None
) -> ForecastModelService:
    """
    Create and return a forecast model service instance.
    
    Args:
        xgb_path: XGBoost model path
        lstm_path: LSTM model path
        scaler_path: Scaler path
        
    Returns:
        ForecastModelService instance
    """
    if xgb_path is None:
        from app.config import settings
        xgb_path = settings.xgboost_model_path
    
    if lstm_path is None:
        from app.config import settings
        lstm_path = settings.lstm_model_path
    
    if scaler_path is None:
        scaler_path = str(Path(xgb_path).parent / "scaler.pkl")
    
    return ForecastModelService(
        xgb_model_path=xgb_path,
        lstm_model_path=lstm_path,
        scaler_path=scaler_path
    )
