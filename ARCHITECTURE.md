# AQI Prediction System - Project Guidelines

## 🏗️ Architecture Overview

### Backend Architecture
```
app/main.py (FastAPI)
    ├── Startup Events
    │   ├── Load XGBoost Model
    │   ├── Load LSTM Model
    │   └── Initialize Weather Service
    ├── Endpoints
    │   ├── /predict (POST) - Main prediction
    │   ├── /stations (GET) - Get stations
    │   ├── /health (GET) - Health check
    │   └── /models/info (GET) - Model info
    └── Shutdown Events
        └── Cleanup & Cache Clear

Model Pipeline:
Features → Preprocessing → Predictions → Ensemble → Response
```

### Frontend Architecture
```
App.jsx (Main Component)
    ├── Header (Status, Refresh)
    ├── Statistics (Avg, Max, Min AQI)
    └── Main Grid
        ├── AQIMap
        │   ├── Leaflet Layer
        │   ├── Station Markers
        │   └── Wind Arrows
        └── Sidebar
            ├── StationSearch
            └── AQIDetailCard
```

## 🔄 Data Flow

### Prediction Flow
```
1. User clicks marker or searches station
2. Frontend calls POST /predict with lat/lon
3. Backend receives request
4. Weather API fetch (async)
5. Feature extraction:
   - Weather features
   - Time features (hour, day, month)
   - Wind components (cos/sin)
   - AQI lag features (simulated)
6. Feature preprocessing
7. Dual prediction:
   - XGBoost: Raw features
   - LSTM: Normalized features (3D)
8. Ensemble: 0.7*XGB + 0.3*LSTM
9. Feature importance calculation
10. JSON response with metadata
11. Frontend displays in detail card
```

### Caching Flow
```
Request → Check Cache (5-min TTL)
    ├─ Cache Hit → Return cached data
    └─ Cache Miss → Make prediction → Cache → Return
```

## 🎨 Design Patterns

### Backend
- **Service Pattern**: WeatherService for API calls
- **Factory Pattern**: ModelLoader for model management
- **Adapter Pattern**: WeatherServiceSync as async wrapper
- **Singleton**: Global prediction_cache and _model_predictor
- **Configuration**: Pydantic BaseSettings for env management

### Frontend
- **Component Pattern**: Reusable React components
- **Custom Hooks**: usePredictionStore for state
- **Service Pattern**: predictionsAPI for backend calls
- **Utility Functions**: getAQICategory, formatWindDirection, etc.
- **Container/Presenter**: Smart components manage data, dumb components render

## 🧪 Testing Guidelines

### Backend Testing
```python
# Test endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 28.55, "longitude": 77.23}'

# Run diagnostics
python backend/debug_utils.py

# Check health
curl http://localhost:8000/health
```

### Frontend Testing
```bash
# Check console for errors
# Open http://localhost:5173 in browser
# Test map interactions
# Verify all stations load
# Check network tab for API calls
```

## 📝 Code Style

### Backend
- Use type hints everywhere
- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions
- Use logging instead of print()

### Frontend
- Use functional components with hooks
- JSDoc comments for components
- Destructure props
- Use constant values at top of file
- Follow React naming conventions (PascalCase for components)

## 🚀 Deployment Steps

### Manual Deployment
1. SSH into server
2. Clone repository
3. Set up backend venv and install dependencies
4. Set up frontend node_modules
5. Configure .env files with production values
6. Run with systemd or supervisor
7. Set up Nginx reverse proxy

### Docker Deployment
```bash
docker-compose up -d
docker logs -f <container_id>
```

### Environment-Specific Configuration
- Development: `DEBUG=True`, `CORS_ORIGINS=["*"]`
- Production: `DEBUG=False`, specific CORS origins, use `.env.prod`

## 🔐 Security Checklist

- [ ] API keys stored in .env (never in code)
- [ ] CORS properly configured (not wildcard in production)
- [ ] Input validation on all endpoints
- [ ] Rate limiting considered
- [ ] Error messages don't expose internals
- [ ] Frontend components sanitize data
- [ ] Dependencies kept up to date

## 📊 Performance Optimization

### Backend
- ✅ Prediction caching (5-min TTL)
- ✅ Async weather API calls
- ✅ Model loading on startup
- 🔄 Consider connection pooling for multiple requests
- 🔄 Add database caching for historical data

### Frontend
- ✅ React.memo for expensive components
- ✅ useCallback for functions
- ✅ Lazy loading for map tiles
- 🔄 Service Worker for offline support
- 🔄 Progressive image loading

## 🐛 Debugging Guide

### Backend Issues
1. Check logs in console
2. Use debug_utils.py for diagnostics
3. Add print statements or logging
4. Test endpoints with curl
5. Check .env configuration

### Frontend Issues
1. Open browser DevTools (F12)
2. Check Console for JS errors
3. Check Network tab for API calls
4. Check React DevTools (if installed)
5. Verify API response format

## 📚 Adding New Features

### Add New Prediction Factor
1. Modify `FeatureExtractor.construct_feature_vector()`
2. Update feature schema in debug_utils.py
3. Retrain models with new features
4. Update frontend to display factor

### Add New Endpoint
1. Create function in app/main.py
2. Add @app.route decorator
3. Document in README.md
4. Update frontend API client

### Add New Frontend Component
1. Create .jsx file in src/components/
2. Export as named export
3. Import in App.jsx or parent component
4. Add Tailwind classes for styling

## 🔗 Integration Points

### External APIs
- OpenWeatherMap: Weather data
- Future: Additional weather sources, pollution data APIs

### Database (Future)
- Store prediction history
- Cache long-term data
- User preferences

### Monitoring (Future)
- Prometheus metrics
- Grafana dashboards
- Error tracking (Sentry)

## 📞 Support & Troubleshooting

For common issues, see [README.md](../README.md) Troubleshooting section.

For development questions: Check comments in code, docstrings, and run debug_utils.py.
