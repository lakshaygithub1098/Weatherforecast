# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- OpenWeatherMap API Key (free tier available)

## 1️⃣ Quick Setup (2 minutes)

### On Windows:
```bash
setup.bat
```

### On macOS/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

## 2️⃣ Configure API Key

1. Get free API key from https://openweathermap.org/api
2. Edit `backend/.env`:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```

## 3️⃣ Start Both Services

### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
python -m uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

## 4️⃣ Open Dashboard

🌐 http://localhost:5173

## 📊 Using the Dashboard

1. **View Stations**: See all AQI monitoring stations on the interactive map
2. **Click Markers**: Click any colored circle to see detailed information
3. **Search Stations**: Use the search box to filter stations
4. **View Predictions**: See XGBoost and LSTM predictions with confidence scores
5. **Check Weather**: View real-time weather data (wind, temperature, humidity)
6. **Analyze Factors**: See what factors most influence the AQI prediction

## 🔌 API Testing

```bash
# Check API health
curl http://localhost:8000/health

# Get all stations
curl http://localhost:8000/stations

# Get AQI prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 28.55, "longitude": 77.23, "station_name": "ITO"}'

# View API docs
# Open http://localhost:8000/docs in browser
```

## 🐛 Common Issues

**"Models not found"**
- Ensure model files exist in `models/` folder
- Check paths in `backend/.env`

**"API connection refused"**
- Make sure backend is running on port 8000
- Check firewall settings

**"CORS error"**
- Backend `.env` CORS_ORIGINS must include frontend URL
- Default includes `http://localhost:5173`

**"Weather API error"**
- Verify weather API key is correct
- Check rate limits (free tier has 60 calls/min limit)
- System will use mock data if API fails

## 📚 Next Steps

- Review [README.md](../README.md) for full documentation
- Check [API docs](http://localhost:8000/docs) for endpoint details
- Explore [ML models](../notebooks/) for training notebooks
- Deploy with Docker: `docker-compose up`

## ✨ Features Overview

```
┌─────────────────────────────────────┐
│     AQI Prediction Dashboard        │
├─────────────────────────────────────┤
│                                     │
│  📍 Interactive Map                 │
│  ├── Color-coded AQI markers       │
│  ├── Wind direction arrows         │
│  └── Station information popups    │
│                                     │
│  📊 Statistics Panel                │
│  ├── Average/Min/Max AQI           │
│  └── Station count                 │
│                                     │
│  🔍 Station Search & Filter         │
│  ├── Real-time search              │
│  └── Region filter                 │
│                                     │
│  📈 Detailed Predictions            │
│  ├── XGBoost prediction            │
│  ├── LSTM prediction               │
│  ├── Ensemble result               │
│  └── Confidence scores             │
│                                     │
│  🌤️  Weather Integration            │
│  ├── Temperature                   │
│  ├── Humidity                      │
│  ├── Wind speed & direction        │
│  └── Pressure                      │
│                                     │
└─────────────────────────────────────┘
```

---

Need help? Check the full [README.md](../README.md) or create an issue on GitHub!
