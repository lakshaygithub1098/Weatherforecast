"""
LSTM-based 24-hour AQI forecasting service.
Implements proper sequence-to-sequence forecasting with rolling windows.
"""

import numpy as np
import logging
from typing import List, Tuple, Optional
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LSTMForecastService:
    """LSTM-based time series forecasting for AQI."""
    
    def __init__(self, lstm_model_path: str, scaler=None):
        """
        Initialize LSTM service.
        
        Args:
            lstm_model_path: Path to LSTM model file
            scaler: Optional sklearn scaler for normalization
        """
        self.lstm_model = None
        self.scaler = scaler
        self.lstm_model_path = lstm_model_path
        self._load_model()
    
    def _load_model(self):
        """Load LSTM model from disk."""
        if not Path(self.lstm_model_path).exists():
            logger.warning(f"LSTM model not found at {self.lstm_model_path}")
            return
        
        try:
            from tensorflow import keras
            self.lstm_model = keras.models.load_model(self.lstm_model_path)
            logger.info("✅ LSTM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
    
    def is_available(self) -> bool:
        """Check if LSTM model is loaded."""
        return self.lstm_model is not None
    
    def forecast_24hours(
        self,
        past_24_aqi: List[float],
        features_24h: np.ndarray,
        initial_aqi: float = 100.0
    ) -> Tuple[List[float], List[datetime], str]:
        """
        Generate 24-hour AQI forecast using LSTM.
        
        Args:
            past_24_aqi: Last 24 hours of actual AQI values
            features_24h: Shape (24, num_features) with weather features
            initial_aqi: Current/baseline AQI value
            
        Returns:
            Tuple of (forecast_aqi_list, timestamps, status_message)
        """
        if not self.is_available():
            logger.error("LSTM model not available")
            return self._fallback_forecast(initial_aqi)
        
        try:
            # Ensure we have 24 values
            if len(past_24_aqi) < 24:
                past_24_aqi = list(past_24_aqi) + [initial_aqi] * (24 - len(past_24_aqi))
            else:
                past_24_aqi = list(past_24_aqi[-24:])
            
            # Prepare input sequence: use past 24 hours as context
            # Shape should be (1, 24, num_features)
            input_sequence = self._prepare_sequence(past_24_aqi, features_24h)
            
            if input_sequence is None:
                return self._fallback_forecast(initial_aqi)
            
            # Generate predictions with rolling window
            predictions = self._generate_with_rolling_window(
                input_sequence, 
                past_24_aqi, 
                features_24h
            )
            
            # Generate timestamps for next 24 hours
            now = datetime.now()
            timestamps = [now + timedelta(hours=i) for i in range(1, 25)]
            
            logger.info(f"✅ LSTM forecast generated: min={min(predictions):.1f}, max={max(predictions):.1f}, std={np.std(predictions):.1f}")
            
            return predictions, timestamps, "success"
            
        except Exception as e:
            logger.error(f"LSTM forecast error: {e}", exc_info=True)
            return self._fallback_forecast(initial_aqi)
    
    def _prepare_sequence(
        self, 
        past_aqi: List[float], 
        features: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Prepare input sequence for LSTM.
        
        Args:
            past_aqi: 24-hour AQI history
            features: (24, num_features) weather features
            
        Returns:
            Array of shape (1, 24, num_features) or None
        """
        try:
            # Combine AQI history with weather features
            past_aqi_array = np.array(past_aqi).reshape(-1, 1)  # (24, 1)
            
            # Concatenate AQI with weather features
            combined = np.hstack([past_aqi_array, features])  # (24, 1+num_features)
            
            # Normalize if scaler is available
            if self.scaler:
                combined = self.scaler.transform(combined)
            
            # Reshape for LSTM: (1, sequence_length, num_features)
            sequence = combined.reshape(1, combined.shape[0], combined.shape[1])
            
            return sequence
        except Exception as e:
            logger.error(f"Sequence preparation error: {e}")
            return None
    
    def _generate_with_rolling_window(
        self,
        initial_sequence: np.ndarray,
        past_aqi: List[float],
        features_24h: np.ndarray
    ) -> List[float]:
        """
        Generate 24-hour forecast using rolling window approach.
        
        Each prediction is inserted into the sequence for the next prediction.
        
        Args:
            initial_sequence: Shape (1, 24, num_features)
            past_aqi: Past AQI values
            features_24h: Weather features for next 24 hours
            
        Returns:
            List of 24 predicted AQI values
        """
        predictions = []
        current_sequence = initial_sequence.copy()
        current_aqi_window = list(past_aqi[-24:])
        
        for hour_idx in range(24):
            try:
                # Predict next AQI
                pred = self.lstm_model.predict(current_sequence, verbose=0)
                
                # Extract AQI from prediction
                if pred.ndim == 3:
                    # If output is (1, 1, 1) or similar
                    aqi_pred = float(pred[0, -1, 0])
                elif pred.ndim == 2:
                    # If output is (1, 1)
                    aqi_pred = float(pred[0, 0])
                else:
                    aqi_pred = float(pred[0])
                
                # Clip to reasonable range
                aqi_pred = max(0, min(500, aqi_pred))
                predictions.append(aqi_pred)
                
                # Roll window: remove first hour, add prediction
                current_aqi_window = current_aqi_window[1:] + [aqi_pred]
                
                # Update sequence with new prediction
                new_aqi_array = np.array(current_aqi_window).reshape(-1, 1)
                new_sequence = np.hstack([new_aqi_array, features_24h])
                
                if self.scaler:
                    new_sequence = self.scaler.transform(new_sequence)
                
                current_sequence = new_sequence.reshape(1, 24, -1)
                
            except Exception as e:
                logger.warning(f"Prediction for hour {hour_idx} failed: {e}")
                # Use mean of recent predictions
                predictions.append(np.mean(predictions[-3:]) if predictions else 100.0)
        
        return predictions
    
    def _fallback_forecast(
        self, 
        initial_aqi: float
    ) -> Tuple[List[float], List[datetime], str]:
        """
        Generate fallback forecast when LSTM is unavailable.
        Uses simple trend continuation.
        
        Args:
            initial_aqi: Current AQI value
            
        Returns:
            Tuple of (forecast_list, timestamps, status_message)
        """
        # Simple decay towards average
        forecast = []
        current_aqi = initial_aqi
        avg_aqi = 100.0
        
        for i in range(24):
            # Gradual reversion to mean with small noise
            trend = 0.95 * current_aqi + 0.05 * avg_aqi
            noise = np.random.normal(0, 2)
            current_aqi = max(0, min(500, trend + noise))
            forecast.append(current_aqi)
        
        now = datetime.now()
        timestamps = [now + timedelta(hours=i) for i in range(1, 25)]
        
        logger.warning("⚠️ Using fallback forecast (LSTM unavailable)")
        return forecast, timestamps, "fallback"
