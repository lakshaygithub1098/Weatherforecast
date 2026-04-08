"""
Real AQI data service - fetches actual historical AQI from CSV database.
"""

import pandas as pd
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RealAQIDataService:
    """Fetch real historical AQI data from CSV."""
    
    _instance = None
    _csv_path = None
    _df = None
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize AQI data service.
        
        Args:
            csv_path: Path to CSV file with AQI data
        """
        if csv_path:
            RealAQIDataService._csv_path = csv_path
            RealAQIDataService._df = None
        
        self._load_data()
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = RealAQIDataService()
        return cls._instance
    
    @staticmethod
    def set_csv_path(csv_path: str):
        """Set CSV path (call before initialization)."""
        RealAQIDataService._csv_path = csv_path
        RealAQIDataService._df = None
    
    def _load_data(self):
        """Load CSV data into memory."""
        if RealAQIDataService._df is not None:
            return  # Already loaded
        
        csv_path = RealAQIDataService._csv_path
        if not csv_path:
            # Auto-detect common paths
            project_root = Path(__file__).parent.parent.parent.parent
            possible_paths = [
                project_root / "data" / "Processed" / "DELHI_MASTER_AQI_WEATHER_2025.csv",
                project_root / "data" / "DELHI_MASTER_AQI_WEATHER_2025.csv",
                Path("data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv"),
                Path("data/DELHI_MASTER_AQI_WEATHER_2025.csv"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    csv_path = str(path)
                    break
        
        if not csv_path or not Path(csv_path).exists():
            logger.warning(f"CSV file not found at {csv_path}")
            return
        
        try:
            df = pd.read_csv(csv_path)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime')
            RealAQIDataService._df = df
            logger.info(f"✅ Loaded {len(df)} rows from {csv_path}")
            logger.info(f"   Stations: {df['station'].nunique()}, Date range: {df['datetime'].min()} to {df['datetime'].max()}")
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
    
    def get_last_24_hours_aqi(self, station_name: str) -> List[float]:
        """
        Get last 24 hours of actual AQI data for a station.
        
        Args:
            station_name: Station name (e.g., "ITO", "Alipur")
            
        Returns:
            List of 24 hourly AQI values (chronological order)
        """
        if RealAQIDataService._df is None or RealAQIDataService._df.empty:
            logger.warning(f"No CSV data available for {station_name}")
            return [100.0] * 24  # Fallback
        
        try:
            df = RealAQIDataService._df
            
            # Filter for station
            station_df = df[df['station'] == station_name].copy()
            if station_df.empty:
                logger.warning(f"Station {station_name} not found in CSV")
                return [100.0] * 24
            
            # Get last 24 records
            last_24 = station_df.tail(24).sort_values('datetime')
            
            # Extract AQI values
            aqi_values = last_24['aqi'].values.tolist()
            
            # Ensure we have 24 values
            if len(aqi_values) < 24:
                # Pad with last value
                last_val = aqi_values[-1] if aqi_values else 100.0
                aqi_values = aqi_values + [last_val] * (24 - len(aqi_values))
            
            logger.info(f"✅ Got {len(aqi_values)} hours of real AQI for {station_name}")
            logger.info(f"   Range: {min(aqi_values):.1f} - {max(aqi_values):.1f}")
            
            return aqi_values
        
        except Exception as e:
            logger.error(f"Error fetching AQI for {station_name}: {e}")
            return [100.0] * 24
    
    def get_current_aqi(self, station_name: str) -> float:
        """
        Get most recent AQI observation for a station.
        
        Args:
            station_name: Station name
            
        Returns:
            Latest AQI value or 100.0 as default
        """
        if RealAQIDataService._df is None or RealAQIDataService._df.empty:
            return 100.0
        
        try:
            df = RealAQIDataService._df
            station_df = df[df['station'] == station_name].sort_values('datetime')
            
            if station_df.empty:
                return 100.0
            
            current_aqi = float(station_df.tail(1)['aqi'].values[0])
            return current_aqi
        
        except Exception as e:
            logger.error(f"Error getting current AQI for {station_name}: {e}")
            return 100.0
    
    def get_time_series(
        self, 
        station_name: str, 
        hours: int = 24
    ) -> tuple:
        """
        Get time series data for a station.
        
        Args:
            station_name: Station name
            hours: Number of hours to retrieve
            
        Returns:
            Tuple of (timestamps, aqi_values)
        """
        if RealAQIDataService._df is None or RealAQIDataService._df.empty:
            return [], []
        
        try:
            df = RealAQIDataService._df
            station_df = df[df['station'] == station_name].tail(hours).sort_values('datetime')
            
            timestamps = station_df['datetime'].tolist()
            aqi_values = station_df['aqi'].values.tolist()
            
            return timestamps, aqi_values
        
        except Exception as e:
            logger.error(f"Error getting time series for {station_name}: {e}")
            return [], []
