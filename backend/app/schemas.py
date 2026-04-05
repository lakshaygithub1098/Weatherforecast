from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class PredictionInput(BaseModel):
    """Input schema for AQI prediction."""
    latitude: float = Field(..., description="Station latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Station longitude", ge=-180, le=180)
    station_name: Optional[str] = Field(None, description="Station name (optional)")


class WeatherData(BaseModel):
    """Weather data from API."""
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    pressure: int
    description: str


class PredictionOutput(BaseModel):
    """Output schema for AQI prediction."""
    aqi: float = Field(..., description="Final predicted AQI (0-500)")
    xgboost_prediction: float = Field(..., description="XGBoost model prediction")
    lstm_prediction: float = Field(..., description="LSTM model prediction")
    
    station_name: Optional[str]
    latitude: float
    longitude: float
    
    weather: WeatherData
    
    contributing_factors: Dict[str, float] = Field(..., description="Feature importance")
    
    model_confidence: Dict[str, float] = Field(
        ..., 
        description="Confidence/reliability scores for each model"
    )
    
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "aqi": 150.5,
                "xgboost_prediction": 152.0,
                "lstm_prediction": 145.0,
                "station_name": "ITO",
                "latitude": 28.55,
                "longitude": 77.23,
                "weather": {
                    "temperature": 25.5,
                    "humidity": 65,
                    "wind_speed": 3.5,
                    "wind_direction": 180,
                    "pressure": 1013,
                    "description": "Scattered clouds"
                },
                "contributing_factors": {
                    "wind_speed": 0.15,
                    "humidity": 0.12,
                    "temperature": 0.08
                },
                "model_confidence": {
                    "xgboost": 0.92,
                    "lstm": 0.88
                },
                "timestamp": "2024-01-15T14:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: str
    timestamp: str
