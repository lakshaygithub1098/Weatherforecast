# 🌍 Delhi AQI Predictor - Full Stack Air Quality Prediction System

A **production-ready, full-stack machine learning system** that predicts Air Quality Index (AQI) for Delhi using real-time weather data and advanced ensemble models. Features an interactive React dashboard with Leaflet maps, FastAPI backend, and comprehensive ML pipeline.

## ✨ Key Features

- 🤖 **Ensemble ML Models**: XGBoost (70%) + LSTM (30%) for robust predictions
- 🗺️ **Interactive Map**: Real-time Leaflet map with AQI station visualization
- 🌡️ **Weather Integration**: Live OpenWeatherMap API for current conditions
- ⚡ **Fast API**: RESTful FastAPI backend with Swagger documentation
- 🎨 **Modern UI**: React 18 with Tailwind CSS and smooth animations
- 🐳 **Docker Ready**: Complete Docker and Docker Compose support
- 📊 **Detailed Analytics**: Feature importance and confidence scores
- ✅ **Production Tested**: Error handling, caching, and comprehensive validation

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (Port 5173)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Interactive Leaflet Map | Station Details Card  │  │
│  │  Real-time AQI Visualization & Weather Data     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /predict  /stations  /health  /models/info     │  │
│  │  Prediction Cache | Weather Service              │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ML Ensemble Pipeline                            │  │
│  │  XGBoost Model (70%) + LSTM Model (30%)          │  │
│  │  Feature Engineering | Preprocessing            │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
  OpenWeatherMap API        Pre-trained Models
  (Real-time Weather)       (XGBoost + LSTM)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenWeatherMap API Key (free at https://openweathermap.org/api)

### 1. Automated Setup

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Key
1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Create/edit `backend/.env`:
```env
WEATHER_API_KEY=your_api_key_here
WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

### 3. Start Backend (Terminal 1)
```bash
cd backend
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate.bat  # Windows

# Run server
python -m uvicorn app.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
# Dashboard available at http://localhost:5173
```

### 5. Open Dashboard
Navigate to **http://localhost:5173** in your browser

## 📖 How to Use

1. **View Stations**: Interactive map shows all AQI monitoring stations
2. **Click Markers**: Get detailed predictions and weather data for any station
3. **Search Stations**: Use search box to find specific stations
4. **Analyze Predictions**: View model predictions, confidence scores, and feature importance
5. **Weather Info**: See real-time temperature, humidity, wind speed, and direction

## 🔌 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Get All Stations
```bash
curl http://localhost:8000/stations
```

### Get AQI Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.55,
    "longitude": 77.23,
    "station_name": "ITO"
  }'
```

### API Documentation
Interactive Swagger UI available at: **http://localhost:8000/docs**

## 📂 Project Structure

```
Delhi_AQI_Predictor/
│
├── 🔙 backend/                 FastAPI application
│   ├── app/
│   │   ├── main.py             Main API endpoints
│   │   ├── config.py           Configuration & settings
│   │   ├── schemas.py          Request/response schemas
│   │   ├── models/
│   │   │   └── predictor.py    ML prediction logic
│   │   └── utils/
│   │       ├── weather.py      Weather API integration
│   │       ├── features.py     Feature engineering
│   │       └── cache.py        Prediction caching
│   ├── run.py                  Server entry point
│   ├── requirements.txt        Python dependencies
│   └── Dockerfile              Docker image config
│
├── 🎨 frontend/                React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── AQIMap.jsx       Interactive Leaflet map
│   │   │   ├── AQIDetailCard.jsx Station details view
│   │   │   ├── LoadingAndStates.jsx Loading/error states
│   │   │   ├── UI.jsx           Header/footer/layout
│   │   │   └── DataViz.jsx      Charts & visualizations
│   │   ├── services/api.js      API client
│   │   ├── store/               State management (Zustand)
│   │   ├── App.jsx              Main component
│   │   └── main.jsx             Entry point
│   ├── package.json             NPM dependencies
│   ├── vite.config.js           Build configuration
│   └── Dockerfile               Docker image config
│
├── 🤖 models/
│   ├── xgboost_aqi_model.pkl    Trained XGBoost model
│   └── lstm_aqi_model.h5        Trained LSTM model
│
├── 📊 data/
│   └── Processed/
│       └── DELHI_MASTER_AQI_WEATHER_2025.csv
│
├── 📚 notebooks/
│   ├── LSTM.ipynb               LSTM model training
│   ├── Multi_modal.ipynb        Multi-modal ensemble approach
│   └── train_baseline.ipynb     Baseline model training
│
├── 📖 Documentation
│   ├── README.md                This file
│   ├── QUICKSTART.md            2-minute setup guide
│   ├── ARCHITECTURE.md          Technical design & patterns
│   ├── DEPLOYMENT.md            Production deployment guide
│   ├── SYSTEM_OVERVIEW.md       Detailed system description
│   └── INDEX.md                 Project index
│
├── 🐳 Infrastructure
│   ├── docker-compose.yml       Multi-container orchestration
│   ├── setup.sh                 Linux/Mac setup script
│   ├── setup.bat                Windows setup script
│   └── .env.example             Environment template
│
└── Other Files
    ├── FILE_LIST.md             Complete file listing
    └── .gitignore               Git ignore rules
```

## 🛠️ Development

### Backend Technologies
```
FastAPI         Web framework
Uvicorn         ASGI server
XGBoost         Gradient boosting ML model
TensorFlow      LSTM neural network
Pandas/NumPy    Data processing
Scikit-learn    Feature preprocessing
OpenWeatherMap  Weather data API
```

### Frontend Technologies
```
React 18        UI library
Leaflet.js      Map visualization
Tailwind CSS    Styling framework
Framer Motion   Animations
Zustand         State management
Axios           HTTP client
Vite            Build tool
```

## 📈 Model Details

### Ensemble Approach
- **XGBoost** (70% weight): Fast, interpretable predictions on raw features
- **LSTM** (30% weight): Neural network for temporal patterns
- **Ensemble Output** = 0.7 × XGBoost + 0.3 × LSTM

### Feature Set
- Weather features: Temperature, Humidity, Pressure, Wind Speed/Direction
- Time features: Hour of day, Day of week, Month
- Engineered features: Wind components (cos/sin), Feature interactions
- Includes feature importance scoring for explainability

## 🐳 Docker Deployment

### Local Docker Compose
```bash
docker-compose up --build
```
Services start automatically:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### Production Docker Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Nginx reverse proxy setup
- SSL/TLS configuration
- Systemd service management
- Environment optimization

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Models not found" | Ensure model files exist in `models/` folder. Check paths in `backend/.env` |
| "API connection refused" | Verify backend is running on port 8000. Check firewall settings |
| "CORS error" | Update `backend/.env` - `CORS_ORIGINS` must include frontend URL |
| "Weather API error" | Verify API key is correct and not rate-limited (60 calls/min free tier) |
| "Port already in use" | Change port in `.env` or terminal flags: `--port 8001` |

## 📊 Performance

- **Prediction Latency**: ~50-100ms (cached: <5ms)
- **Map Load Time**: <2 seconds
- **API Response Time**: <500ms
- **Refresh Rate**: Configurable (default: every 5 minutes)

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - 2-minute setup guide
- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** - Detailed system architecture
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Design patterns and technical guidelines
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[INDEX.md](./INDEX.md)** - Complete project index with file descriptions

## 🔄 Data Flow

```
User Action (Click/Search)
    ↓
POST /predict (lat, lon, station_name)
    ↓
Check Cache (5 min TTL)
    ├─ HIT → Return cached prediction
    └─ MISS → Fetch weather data from OpenWeatherMap
              ↓
              Extract & Engineer Features
              ↓
              Run XGBoost Prediction
              Run LSTM Prediction
              ↓
              Ensemble: 0.7×XGB + 0.3×LSTM
              ↓
              Calculate Feature Importance
              ↓
              Cache Result
              ↓
              Return JSON Response
    ↓
Frontend Displays:
  - AQI Category with Color
  - Individual Model Predictions
  - Confidence Scores
  - Feature Importance Chart
  - Weather Information
```

## 🤝 Contributing

### Backend Changes
1. Modify `backend/app/` files
2. Restart server: `python -m uvicorn app.main:app --reload`
3. Test with: `curl http://localhost:8000/health`

### Frontend Changes
1. Modify `frontend/src/` files
2. Vite hot reload automatically applies changes
3. Check browser console for errors

### Adding New Models
1. Train and save model to `models/` folder
2. Update `backend/app/models/predictor.py`
3. Modify ensemble weights if needed
4. Test predictions end-to-end

## 📞 Support

For issues, questions, or contributions:
1. Check [troubleshooting](#-troubleshooting) section
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
3. Check API docs at http://localhost:8000/docs
4. Review notebook examples in `notebooks/` folder

## 📄 License

This project is provided as-is for educational and research purposes.

## 🎓 Credits

Built using:
- **FastAPI** - Modern web framework
- **React** - UI library
- **XGBoost** - Gradient boosting library
- **TensorFlow/Keras** - Deep learning framework
- **Leaflet.js** - Map visualization
- **OpenWeatherMap** - Weather data API

---

**Last Updated**: April 5, 2026
**Status**: Production Ready ✅
