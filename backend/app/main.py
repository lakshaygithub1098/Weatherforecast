"""
AQI Prediction API - FastAPI Application
Combines XGBoost and LSTM models with real-time weather data
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import statistics
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import os

from app.config import settings
from app.schemas import PredictionInput, PredictionOutput, ErrorResponse
from app.models.predictor import ModelLoader, ModelPredictor
from app.utils.weather import WeatherServiceSync
from app.utils.features import FeatureExtractor
from app.utils.cache import prediction_cache, forecast_cache
from app.utils.weather_forecast import WeatherForecastService
from app.utils.preprocessing_forecast import ForecastPreprocessor
from app.utils.forecast_model_service import create_forecast_service
from app.utils.waqi_service import get_waqi_service
from app.utils.wind_influence import WindInfluenceCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AQI Prediction API",
    description="Real-time AQI prediction using ensemble ML models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"]
)

# Global model instances
_model_predictor: Optional[ModelPredictor] = None
_weather_service: Optional[WeatherServiceSync] = None
_forecast_service = None
_waqi_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup."""
    global _model_predictor, _weather_service, _forecast_service, _waqi_service
    
    logger.info("🚀 Starting AQI Prediction API...")
    
    try:
        # Load models
        logger.info("Loading ML models...")
        xgb_model = ModelLoader.load_xgboost(settings.xgboost_model_path)
        lstm_model = ModelLoader.load_lstm(settings.lstm_model_path)
        
        # Check if at least one model is loaded
        if xgb_model is None and lstm_model is None:
            logger.error("❌ No models loaded! At least XGBoost or LSTM must be available.")
            raise Exception("No ML models available")
        
        # Create predictor (LSTM can be None)
        _model_predictor = ModelPredictor(xgb_model, lstm_model)
        if xgb_model:
            logger.info("✅ XGBoost model loaded successfully")
        if lstm_model:
            logger.info("✅ LSTM model loaded successfully")
        else:
            logger.warning("⚠️  LSTM model not available - using XGBoost only")
        
        # Initialize weather service
        logger.info("Initializing weather service...")
        _weather_service = WeatherServiceSync(settings.google_api_key)
        logger.info("✅ Weather service initialized")
        
        # Initialize forecast service
        logger.info("Initializing forecast service...")
        _forecast_service = create_forecast_service(
            xgb_path=settings.xgboost_model_path,
            lstm_path=settings.lstm_model_path
        )
        logger.info("✅ Forecast service initialized")
        
        # Initialize WAQI service for live AQI
        logger.info("Initializing WAQI service...")
        _waqi_service = get_waqi_service(api_key=settings.waqi_api_key if hasattr(settings, 'waqi_api_key') else None)
        logger.info("✅ WAQI service initialized")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        if settings.debug:
            raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down AQI Prediction API...")
    ModelLoader.clear()
    prediction_cache.clear()
    forecast_cache.clear()


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": _model_predictor is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post(
    "/predict",
    response_model=PredictionOutput,
    responses={
        200: {"description": "Successful prediction"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    tags=["Prediction"]
)
async def predict_aqi(
    request: PredictionInput,
    background_tasks: BackgroundTasks
) -> PredictionOutput:
    """
    Predict AQI for given location.
    
    Fetches weather data, preprocesses features, and combines XGBoost and LSTM predictions.
    
    Args:
        request: Location data (latitude, longitude)
        
    Returns:
        AQI prediction with contributing factors and model details
        
    Raises:
        HTTPException: If models not loaded or prediction fails
    """
    
    # Check cache first
    cached_result = prediction_cache.get(request.latitude, request.longitude)
    if cached_result:
        return cached_result
    
    try:
        logger.info(f"📍 Predicting AQI for {request.latitude}, {request.longitude}")
        
        # Validate models are loaded
        if _model_predictor is None:
            logger.error("Models not loaded")
            raise HTTPException(
                status_code=503,
                detail="ML models not loaded. Please check server logs.",
                headers={"X-Error-Code": "MODELS_NOT_LOADED"}
            )
        
        if _model_predictor.xgb_model is None and _model_predictor.lstm_model is None:
            logger.error("No ML models available")
            raise HTTPException(
                status_code=503,
                detail="No ML models available.",
                headers={"X-Error-Code": "NO_MODELS"}
            )
        
        # Fetch weather data
        weather_data = _weather_service.get_weather(
            request.latitude,
            request.longitude
        ) if _weather_service else None
        
        if weather_data is None:
            weather_data = {
                "temperature": 25.0,
                "humidity": 50,
                "wind_speed": 0.0,
                "wind_direction": 0,
                "pressure": 1013,
                "description": "Data unavailable",
                "visibility": 10000
            }
        
        # Extract features
        feature_vector = FeatureExtractor.construct_feature_vector(
            weather_data=weather_data,
            location_data={
                'latitude': request.latitude,
                'longitude': request.longitude
            },
            historical_data={}
        )
        
        # Make prediction
        predictions = _model_predictor.predict(feature_vector)
        
        # Get feature importance
        contributing_factors = FeatureExtractor.get_feature_importance_mock(
            feature_vector,
            predictions
        )
        
        # Get time features for response
        time_feat = FeatureExtractor.extract_time_features(
            request.latitude,
            request.longitude
        )
        
        # Build response
        response = PredictionOutput(
            aqi=predictions['aqi'],
            xgboost_prediction=predictions['xgboost_prediction'],
            lstm_prediction=predictions['lstm_prediction'],
            station_name=request.station_name or f"Station_{request.latitude:.2f}_{request.longitude:.2f}",
            latitude=request.latitude,
            longitude=request.longitude,
            weather={
                "temperature": weather_data.get('temperature', 25.0),
                "humidity": weather_data.get('humidity', 50),
                "wind_speed": weather_data.get('wind_speed', 0.0),
                "wind_direction": int(weather_data.get('wind_direction', 0)),
                "pressure": weather_data.get('pressure', 1013),
                "description": weather_data.get('description', 'Clear')
            },
            contributing_factors=contributing_factors,
            model_confidence=predictions['model_confidence'],
            timestamp=time_feat['timestamp']
        )
        
        # Cache the result
        prediction_cache.set(request.latitude, request.longitude, response.model_dump())
        
        logger.info(f"✅ Prediction complete: AQI={predictions['aqi']:.1f}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
            headers={"X-Error-Code": "PREDICTION_FAILED"}
        )


@app.get(
    "/forecast",
    tags=["Forecasting"]
)
async def forecast_24hours(
    station: str = Query(..., description="Station name")
):
    """
    Get 24-hour AQI forecast for a station.
    
    Args:
        station: Station name (e.g., "ITO", "Alipur")
        
    Returns:
        24-hour hourly AQI forecast
    """
    try:
        logger.info(f"📊 Forecasting 24h AQI for station: {station}")
        
        # Check forecast cache first to avoid recalculating too frequently
        cached_forecast = forecast_cache.get(station)
        if cached_forecast:
            logger.info(f"✅ Returning cached forecast for {station}")
            return cached_forecast
        
        if _forecast_service is None:
            raise HTTPException(
                status_code=503,
                detail="Forecast service not initialized"
            )
        
        # Get station coordinates
        stations_list = [
            {"name": "Alipur", "latitude": 28.7986, "longitude": 77.1331},
            {"name": "Bawana", "latitude": 28.623, "longitude": 77.21},
            {"name": "Burari", "latitude": 28.7167, "longitude": 77.2},
            {"name": "DRKARNISINGH", "latitude": 28.498571, "longitude": 77.26484},
            {"name": "DTU", "latitude": 28.750049, "longitude": 77.111261},
            {"name": "DWARKASEC8", "latitude": 28.571027, "longitude": 77.0719},
            {"name": "IGIT3", "latitude": 28.562776, "longitude": 77.118005},
            {"name": "ITO", "latitude": 28.6286, "longitude": 77.241},
            {"name": "Mundka", "latitude": 28.68, "longitude": 77.08},
            {"name": "Najfgarh", "latitude": 28.570173, "longitude": 76.933762},
            {"name": "NARELA", "latitude": 28.822836, "longitude": 77.101981},
            {"name": "Northcampus", "latitude": 28.686, "longitude": 77.209},
            {"name": "NSUT", "latitude": 28.686, "longitude": 77.209},
            {"name": "Punjabi_bagh", "latitude": 28.674045, "longitude": 77.131023},
            {"name": "RKPuram", "latitude": 28.563262, "longitude": 77.186937},
            {"name": "Shadipur", "latitude": 28.651, "longitude": 77.146},
            {"name": "Wazirpur", "latitude": 28.699793, "longitude": 77.165453},
        ]
        
        station_data = next((s for s in stations_list if s["name"] == station), None)
        if not station_data:
            raise HTTPException(
                status_code=404,
                detail=f"Station '{station}' not found"
            )
        
        lat, lon = station_data["latitude"], station_data["longitude"]
        
        # Get 24-hour weather forecast
        logger.info(f"Fetching weather forecast for {lat}, {lon}...")
        weather_forecast = WeatherForecastService.get_24hour_forecast(lat, lon)
        
        # Get last 24 hours of AQI data
        logger.info(f"Fetching historical AQI for {station}...")
        last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station)
        
        # Prepare features
        logger.info("Preparing forecast features...")
        from datetime import datetime
        import statistics
        
        # Calculate station baseline AQI (mean of last 24 hours)
        # This makes the 'upwind_aqi' feature station-specific
        station_baseline_aqi = statistics.mean(last_24_aqi) if last_24_aqi else 100.0
        
        features_array, metadata = ForecastPreprocessor.prepare_forecast_features(
            last_24_hours_aqi=last_24_aqi,
            forecast_weather=weather_forecast,
            current_timestamp=datetime.now(),
            other_stations_aqi={"station1": station_baseline_aqi, "station2": 100.0},
            scaler=_forecast_service.scaler
        )
        
        # Generate predictions
        logger.info("Generating 24-hour forecast...")
        aqi_predictions = _forecast_service.forecast_24hours(
            features_array=features_array,
            initial_aqi=last_24_aqi[-1] if last_24_aqi else 100.0
        )
        
        # Apply station-specific baseline adjustment
        # The model was trained on normalized features, so we apply a correction
        # based on the station's historical AQI characteristics
        current_aqi = last_24_aqi[-1] if last_24_aqi else 100.0
        min_aqi = min(last_24_aqi) if last_24_aqi else current_aqi
        max_aqi = max(last_24_aqi) if last_24_aqi else current_aqi
        aqi_range = max_aqi - min_aqi if max_aqi > min_aqi else 50
        
        # Adjust predictions to respect station characteristics
        baseline_trend = 1.0 + (station_baseline_aqi - 100.0) / 200.0  # Normalize baseline effect
        adjusted_predictions = [
            max(0, min(500, pred * baseline_trend))
            for pred in aqi_predictions
        ]
        aqi_predictions = adjusted_predictions
        
        # Build forecast response
        forecast_data = []
        for i, aqi_val in enumerate(aqi_predictions):
            timestamp = datetime.now() + timedelta(hours=i)
            forecast_data.append({
                "hour": i,
                "timestamp": timestamp.isoformat(),
                "aqi": aqi_val,
                "aqi_level": _get_aqi_level(aqi_val),
                "temperature": metadata[i].get("temperature", 25.0) if i < len(metadata) else 25.0,
                "humidity": metadata[i].get("humidity", 50) if i < len(metadata) else 50,
            })
        
        logger.info(f"✅ Generated forecast: {[f['aqi'] for f in forecast_data[:3]]}... (first 3 hours)")
        
        response_data = {
            "station": station,
            "latitude": lat,
            "longitude": lon,
            "forecast_generated_at": datetime.utcnow().isoformat(),
            "forecast": forecast_data
        }
        
        # Cache the forecast for 10 minutes to avoid recalculating frequently
        forecast_cache.set(station, response_data)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Forecast error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Forecast generation failed: {str(e)}"
        )


def _get_aqi_level(aqi: float) -> str:
    """Get AQI level category."""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Fair"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


@app.get(
    "/live-aqi",
    tags=["Live Data"]
)
async def get_live_aqi(station: str = Query(..., description="Station name")):
    """
    Get current live AQI for a station from WAQI API.
    This is REAL-TIME data, not ML predictions.
    
    Args:
        station: Station name (e.g., "NSUT", "Shadipur")
        
    Returns:
        Current AQI data with PM2.5, PM10, temperature, humidity, wind
    """
    try:
        if _waqi_service is None:
            raise HTTPException(
                status_code=503,
                detail="WAQI service not initialized"
            )
        
        aqi_data = _waqi_service.get_current_aqi(station)
        if not aqi_data:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch AQI for station {station}"
            )
        
        return {
            "station": station,
            "aqi_data": aqi_data,
            "aqi_level": _get_aqi_level(aqi_data["aqi"]),
            "fetched_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching live AQI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch live AQI: {str(e)}"
        )


@app.get(
    "/all-live-aqi",
    tags=["Live Data"]
)
async def get_all_live_aqi():
    """
    Get current live AQI for ALL stations.
    
    Returns:
        Dictionary of station names to AQI data
    """
    try:
        if _waqi_service is None:
            raise HTTPException(status_code=503, detail="WAQI service not initialized")
        
        all_aqi = _waqi_service.get_all_stations_aqi()
        
        # Add AQI levels and return
        result = {}
        for station, aqi_data in all_aqi.items():
            result[station] = {
                "aqi_data": aqi_data,
                "aqi_level": _get_aqi_level(aqi_data["aqi"])
            }
        
        return {
            "stations": result,
            "fetched_at": datetime.utcnow().isoformat(),
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error fetching all live AQI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live AQI data: {str(e)}")


@app.get(
    "/debug",
    tags=["Debug"]
)
async def debug_forecast(station: str = Query(..., description="Station name")):
    """
    Debug endpoint to verify forecast pipeline end-to-end.
    Shows all intermediate data for verification.
    
    Args:
        station: Station name
        
    Returns:
        Complete forecast pipeline data
    """
    try:
        logger.info(f"DEBUG: Starting pipeline debug for {station}")
        
        # Station coordinates
        stations_list = [
            {"name": "Alipur", "latitude": 28.7986, "longitude": 77.1331},
            {"name": "Bawana", "latitude": 28.623, "longitude": 77.21},
            {"name": "Burari", "latitude": 28.7167, "longitude": 77.2},
            {"name": "DRKARNISINGH", "latitude": 28.498571, "longitude": 77.26484},
            {"name": "DTU", "latitude": 28.750049, "longitude": 77.111261},
            {"name": "DWARKASEC8", "latitude": 28.571027, "longitude": 77.0719},
            {"name": "IGIT3", "latitude": 28.562776, "longitude": 77.118005},
            {"name": "ITO", "latitude": 28.6286, "longitude": 77.241},
            {"name": "Mundka", "latitude": 28.68, "longitude": 77.08},
            {"name": "Najfgarh", "latitude": 28.570173, "longitude": 76.933762},
            {"name": "NARELA", "latitude": 28.822836, "longitude": 77.101981},
            {"name": "Northcampus", "latitude": 28.686, "longitude": 77.209},
            {"name": "NSUT", "latitude": 28.686, "longitude": 77.209},
            {"name": "Punjabi_bagh", "latitude": 28.674045, "longitude": 77.131023},
            {"name": "RKPuram", "latitude": 28.563262, "longitude": 77.186937},
            {"name": "Shadipur", "latitude": 28.651, "longitude": 77.146},
            {"name": "Wazirpur", "latitude": 28.699793, "longitude": 77.165453},
        ]
        
        station_data = next((s for s in stations_list if s["name"] == station), None)
        if not station_data:
            raise HTTPException(status_code=404, detail=f"Station {station} not found")
        
        lat, lon = station_data["latitude"], station_data["longitude"]
        
        # 1. Get past 24 hours AQI from CSV
        logger.info("DEBUG: Fetching historical AQI...")
        last_24_aqi = ForecastPreprocessor.get_last_24_hours_aqi(station)
        baseline_aqi = sum(last_24_aqi) / len(last_24_aqi) if last_24_aqi else 100.0
        
        # 2. Get weather forecast
        logger.info("DEBUG: Fetching weather forecast...")
        weather_forecast = WeatherForecastService.get_24hour_forecast(lat, lon)
        
        # 3. Get live AQI for wind influence
        logger.info("DEBUG: Fetching live AQI for wind influence...")
        live_aqi = _waqi_service.get_current_aqi(station) if _waqi_service else {}
        wind_direction = live_aqi.get("wind_speed", 3.0)  # placeholder
        
        # 4. Calculate upwind stations
        logger.info("DEBUG: Calculating upwind stations...")
        upwind_stations = WindInfluenceCalculator.get_upwind_stations(
            station, wind_direction, top_n=3
        )
        upwind_names = [s["station"] for s in upwind_stations]
        
        # 5. Prepare features
        logger.info("DEBUG: Preparing forecast features...")
        import statistics
        features_array, metadata = ForecastPreprocessor.prepare_forecast_features(
            last_24_hours_aqi=last_24_aqi,
            forecast_weather=weather_forecast,
            current_timestamp=datetime.now(),
            other_stations_aqi={"station1": baseline_aqi, "station2": 100.0},
            scaler=_forecast_service.scaler if _forecast_service else None
        )
        
        # 6. Generate forecast
        logger.info("DEBUG: Generating forecast...")
        aqi_predictions = _forecast_service.forecast_24hours(
            features_array=features_array,
            initial_aqi=last_24_aqi[-1] if last_24_aqi else 100.0
        ) if _forecast_service else [100.0] * 24
        
        # 7. Apply adjustments
        baseline_trend = 1.0 + (baseline_aqi - 100.0) / 200.0
        adjusted = [max(0, min(500, p * baseline_trend)) for p in aqi_predictions]
        
        # Build response
        return {
            "station": station,
            "coordinates": {"latitude": lat, "longitude": lon},
            "data_source": "live_csv+openmeteo_forecast",
            "past_24h_aqi": {
                "values": last_24_aqi[-24:],
                "mean": baseline_aqi,
                "min": min(last_24_aqi),
                "max": max(last_24_aqi)
            },
            "weather_forecast_used": {
                "hour_0": {
                    "temperature": weather_forecast[0]["temperature"],
                    "humidity": weather_forecast[0]["humidity"],
                    "wind_speed": weather_forecast[0]["wind_speed"],
                    "wind_direction": weather_forecast[0]["wind_direction"]
                },
                "first_3_temps": [w["temperature"] for w in weather_forecast[:3]],
                "first_3_winds": [w["wind_speed"] for w in weather_forecast[:3]]
            },
            "features_array": {
                "shape": f"{features_array.shape[0]} x {features_array.shape[1]}",
                "first_hour_first_10_features": features_array[0, :10].tolist()
            },
            "model_used": "xgboost (24h forecast)",
            "raw_forecast": aqi_predictions[:6],
            "adjusted_forecast": [round(x, 1) for x in adjusted[:6]],
            "baseline_trend_factor": baseline_trend,
            "upwind_influence": {
                "wind_direction_from": wind_direction,
                "nearby_stations": upwind_names,
                "detailed": [
                    {
                        "station": s["station"],
                        "distance_km": round(s["distance"], 1),
                        "bearing": round(s["bearing"], 0),
                        "influence_score": round(s["influence_score"], 2)
                    }
                    for s in upwind_stations
                ]
            },
            "verification": {
                "past_24h_data_loaded": len(last_24_aqi) == 24,
                "weather_forecast_24h": len(weather_forecast) == 24,
                "features_shape_correct": features_array.shape == (24, 27),
                "prediction_values_valid": all(0 <= p <= 500 for p in adjusted),
                "upwind_calculation_done": len(upwind_names) > 0
            },
            "debug_timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Debug failed: {str(e)}"
        )



@app.get(
    "/stations",
    tags=["Data"]
)
async def get_stations():
    """
    Get list of monitoring stations in Delhi.
    
    Returns:
        List of stations with coordinates
    """
    # All Delhi AQI monitoring stations from the dataset
    stations = [
        {"name": "Alipur", "latitude": 28.7986, "longitude": 77.1331, "region": "North Delhi"},
        {"name": "Bawana", "latitude": 28.623, "longitude": 77.21, "region": "North Delhi"},
        {"name": "Burari", "latitude": 28.7167, "longitude": 77.2, "region": "North Delhi"},
        {"name": "DRKARNISINGH", "latitude": 28.498571, "longitude": 77.26484, "region": "South Delhi"},
        {"name": "DTU", "latitude": 28.750049, "longitude": 77.111261, "region": "West Delhi"},
        {"name": "DWARKASEC8", "latitude": 28.571027, "longitude": 77.0719, "region": "West Delhi"},
        {"name": "IGIT3", "latitude": 28.562776, "longitude": 77.118005, "region": "South Delhi"},
        {"name": "ITO", "latitude": 28.6286, "longitude": 77.241, "region": "Central Delhi"},
        {"name": "Mundka", "latitude": 28.68, "longitude": 77.08, "region": "West Delhi"},
        {"name": "Najfgarh", "latitude": 28.570173, "longitude": 76.933762, "region": "South Delhi"},
        {"name": "NARELA", "latitude": 28.822836, "longitude": 77.101981, "region": "North Delhi"},
        {"name": "Northcampus", "latitude": 28.686, "longitude": 77.209, "region": "Central Delhi"},
        {"name": "NSUT", "latitude": 28.686, "longitude": 77.209, "region": "Central Delhi"},
        {"name": "Punjabi_bagh", "latitude": 28.674045, "longitude": 77.131023, "region": "West Delhi"},
        {"name": "RKPuram", "latitude": 28.563262, "longitude": 77.186937, "region": "South Delhi"},
        {"name": "Shadipur", "latitude": 28.651, "longitude": 77.146, "region": "Central Delhi"},
        {"name": "Wazirpur", "latitude": 28.699793, "longitude": 77.165453, "region": "North Delhi"},
    ]
    return {"stations": stations, "count": len(stations)}


@app.get("/models/info", tags=["System"])
async def get_model_info():
    """Get information about loaded models."""
    return {
        "models": {
            "xgboost": {
                "status": "loaded" if _model_predictor and _model_predictor.xgb_model else "not_loaded",
                "path": settings.xgboost_model_path,
                "weight": 0.7
            },
            "lstm": {
                "status": "loaded" if _model_predictor and _model_predictor.lstm_model else "not_loaded",
                "path": settings.lstm_model_path,
                "weight": 0.3
            }
        },
        "ensemble_weights": {
            "xgboost": 0.7,
            "lstm": 0.3
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/cache/stats", tags=["System"])
async def get_cache_stats():
    """Get cache statistics."""
    return {
        "cached_entries": len(prediction_cache.cache),
        "ttl_seconds": prediction_cache.ttl,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/cache/clear", tags=["System"])
async def clear_cache():
    """Clear prediction cache."""
    prediction_cache.clear()
    return {"message": "Cache cleared successfully"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AQI Prediction API",
        "version": "1.0.0",
        "description": "Real-time Air Quality Index prediction using ensemble ML models",
        "endpoints": {
            "predict": "/predict (POST)",
            "stations": "/stations (GET)",
            "health": "/health (GET)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1
    )
