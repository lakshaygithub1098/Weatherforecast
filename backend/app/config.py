from pydantic_settings import BaseSettings
from typing import List
import json
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Google API
    google_api_key: str = "your_google_api_key_here"
    
    # Model paths - use absolute paths
    _models_dir = Path(__file__).parent.parent.parent / "models"
    xgboost_model_path: str = str(_models_dir / "xgboost_aqi_model.pkl")
    lstm_model_path: str = str(_models_dir / "lstm_aqi_model.h5")
    
    # Server config
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "https://delhi-aqi-frontend.vercel.app", "https://delhi-aqi-predictor.vercel.app", "https://delhi-aqi-frontend-og8k3sxf5-lakshaypal20232704-6255s-projects.vercel.app"]'
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string."""
        try:
            return json.loads(self.cors_origins)
        except:
            return ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]


settings = Settings()
