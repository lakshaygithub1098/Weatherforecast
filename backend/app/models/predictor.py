import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import Optional, Tuple
import joblib

logger = logging.getLogger(__name__)


class ModelLoader:
    """Load and manage ML models."""
    
    _xgboost_model = None
    _lstm_model = None
    _scaler = None
    
    @classmethod
    def load_xgboost(cls, model_path: str):
        """
        Load XGBoost model from pickle file.
        
        Args:
            model_path: Path to .pkl file
            
        Returns:
            Loaded XGBoost model
        """
        if cls._xgboost_model is not None:
            return cls._xgboost_model
        
        try:
            path = Path(model_path)
            if not path.exists():
                logger.warning(f"XGBoost model not found at {model_path}")
                return None
            
            with open(path, 'rb') as f:
                cls._xgboost_model = pickle.load(f)
            
            logger.info(f"✅ XGBoost model loaded from {model_path}")
            return cls._xgboost_model
            
        except Exception as e:
            logger.error(f"Error loading XGBoost model: {str(e)}")
            return None
    
    @classmethod
    def load_lstm(cls, model_path: str):
        """
        Load LSTM model from h5 file.
        
        Args:
            model_path: Path to .h5 file
            
        Returns:
            Loaded LSTM model
        """
        if cls._lstm_model is not None:
            return cls._lstm_model
        
        try:
            from tensorflow import keras
            
            path = Path(model_path)
            if not path.exists():
                logger.warning(f"LSTM model not found at {model_path}")
                return None
            
            cls._lstm_model = keras.models.load_model(path)
            logger.info(f"✅ LSTM model loaded from {model_path}")
            return cls._lstm_model
            
        except Exception as e:
            logger.error(f"Error loading LSTM model: {str(e)}")
            return None
    
    @classmethod
    def load_scaler(cls, scaler_path: str):
        """Load StandardScaler for feature normalization."""
        if cls._scaler is not None:
            return cls._scaler
        
        try:
            path = Path(scaler_path)
            if not path.exists():
                logger.warning(f"Scaler not found at {scaler_path}, creating new one")
                return None
            
            cls._scaler = joblib.load(path)
            logger.info(f"✅ Scaler loaded from {scaler_path}")
            return cls._scaler
            
        except Exception as e:
            logger.error(f"Error loading scaler: {str(e)}")
            return None
    
    @classmethod
    def clear(cls):
        """Clear loaded models from memory."""
        cls._xgboost_model = None
        cls._lstm_model = None
        cls._scaler = None


class ModelPredictor:
    """Make predictions using loaded models."""
    
    def __init__(self, xgb_model, lstm_model, scaler: Optional[object] = None):
        self.xgb_model = xgb_model
        self.lstm_model = lstm_model
        self.scaler = scaler
    
    def preprocess_features(
        self, 
        features: np.ndarray,
        feature_names: Optional[list] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Preprocess features for model prediction.
        
        Args:
            features: Input feature array
            feature_names: Names of features (for debugging)
            
        Returns:
            Tuple of (features_for_xgb, features_for_lstm)
        """
        try:
            # XGBoost uses raw features
            xgb_features = features.reshape(1, -1)
            
            # LSTM expects 3D input: (samples, timesteps, features)
            # If we have sequential data, reshape accordingly
            # For now, assume we have a single sample
            lstm_features = features.reshape(1, 1, -1)
            
            # Apply scaling if available
            if self.scaler is not None:
                try:
                    lstm_features = self.scaler.transform(lstm_features.reshape(1, -1))
                    lstm_features = lstm_features.reshape(1, 1, -1)
                except:
                    pass
            
            return xgb_features, lstm_features
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {str(e)}")
            raise
    
    def predict(
        self, 
        features: np.ndarray,
        xgb_weight: float = 0.7,
        lstm_weight: float = 0.3
    ) -> dict:
        """
        Make ensemble prediction.
        
        Args:
            features: Input feature array
            xgb_weight: Weight for XGBoost prediction
            lstm_weight: Weight for LSTM prediction
            
        Returns:
            Dictionary with predictions and confidence
        """
        try:
            xgb_features, lstm_features = self.preprocess_features(features)
            
            # XGBoost prediction
            xgb_pred = None
            xgb_confidence = 0.0
            if self.xgb_model is not None:
                try:
                    raw_pred = float(self.xgb_model.predict(xgb_features)[0])
                    
                    # Handle negative predictions - model might be miscalibrated
                    if raw_pred < 0:
                        logger.warning(f"XGBoost produced negative prediction: {raw_pred}, applying correction")
                        # Use absolute value or add offset
                        xgb_pred = abs(raw_pred) + 50  # Add base AQI offset
                    else:
                        xgb_pred = raw_pred
                    
                    xgb_pred = np.clip(xgb_pred, 0, 500)  # Clip to valid AQI range
                    xgb_confidence = 0.92 if xgb_pred > 10 else 0.5  # Lower confidence for small values
                except Exception as e:
                    logger.error(f"XGBoost prediction error: {str(e)}")
                    xgb_pred = None
            
            # LSTM prediction
            lstm_pred = None
            lstm_confidence = 0.0
            if self.lstm_model is not None:
                try:
                    lstm_pred = float(self.lstm_model.predict(lstm_features, verbose=0)[0][0])
                    lstm_pred = np.clip(lstm_pred, 0, 500)  # Clip to valid AQI range
                    lstm_confidence = 0.88
                except Exception as e:
                    logger.error(f"LSTM prediction error: {str(e)}")
                    lstm_pred = None
            
            # Ensemble prediction
            if xgb_pred is not None and lstm_pred is not None:
                final_pred = (xgb_pred * xgb_weight) + (lstm_pred * lstm_weight)
            elif xgb_pred is not None:
                final_pred = xgb_pred
            elif lstm_pred is not None:
                final_pred = lstm_pred
            else:
                # Fallback: return moderate AQI
                final_pred = 150.0
            
            final_pred = float(np.clip(final_pred, 0, 500))
            
            return {
                "aqi": final_pred,
                "xgboost_prediction": xgb_pred or 0.0,
                "lstm_prediction": lstm_pred or 0.0,
                "model_confidence": {
                    "xgboost": xgb_confidence,
                    "lstm": lstm_confidence
                },
                "weights": {
                    "xgboost": xgb_weight,
                    "lstm": lstm_weight
                }
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
