# Delhi AQI Prediction System - Complete Setup

## 🎯 What You've Got

A **production-ready, full-stack AQI prediction system** with:
- ✅ FastAPI backend with ML ensemble predictions
- ✅ React frontend with interactive Leaflet map
- ✅ Real-time weather integration
- ✅ XGBoost + LSTM ensemble models
- ✅ Comprehensive documentation
- ✅ Docker support
- ✅ Error handling & loading states
- ✅ Beautiful, modern UI

## 📂 Project Map

```
Delhi_AQI_Predictor/
│
├── 📄 Quick References
│   ├── README.md              👈 START HERE for full docs
│   ├── QUICKSTART.md          👈 2-minute setup guide
│   ├── ARCHITECTURE.md        Development patterns & structure
│   ├── DEPLOYMENT.md          Production deployment guide
│   └── INDEX.md               (this file)
│
├── 🔙 Backend (FastAPI)
│   ├── app/
│   │   ├── main.py                     Main FastAPI app
│   │   ├── config.py                   Settings management
│   │   ├── schemas.py                  Request/response models
│   │   ├── models/predictor.py         ML prediction logic
│   │   └── utils/
│   │       ├── weather.py              OpenWeatherMap API
│   │       ├── features.py             Feature engineering
│   │       ├── cache.py                Prediction cache
│   │       └── __init__.py
│   ├── run.py                          Entry point
│   ├── debug_utils.py                  Debug utilities
│   ├── requirements.txt                Python dependencies
│   ├── .env                            Environment variables
│   ├── .env.example                    Template
│   ├── Dockerfile                      Docker image
│   └── setup.py                        (optional)
│
├── 🎨 Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AQIMap.jsx                Leaflet map
│   │   │   ├── AQIDetailCard.jsx         Station details
│   │   │   ├── LoadingAndStates.jsx      Spinners & errors
│   │   │   ├── UI.jsx                    Header, footer, etc
│   │   │   └── DataViz.jsx               Charts & visualizations
│   │   ├── services/api.js               API client
│   │   ├── store/predictionStore.js      State management
│   │   ├── utils/aqi.js                  Utilities
│   │   ├── App.jsx                       Main component
│   │   ├── main.jsx                      Entry point
│   │   └── index.css                     Global styles
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── .env.example
│   ├── Dockerfile
│   └── .gitignore
│
├── 🤖 Models
│   ├── xgboost_aqi_model.pkl            Pre-trained XGBoost
│   └── lstm_aqi_model.h5                Pre-trained LSTM
│
├── 📊 Data
│   ├── Processed/
│   │   └── DELHI_MASTER_AQI_WEATHER_2025.csv
│   └── Raw/ (if needed)
│
├── 📚 Notebooks
│   ├── LSTM.ipynb
│   ├── Multi_modal.ipynb
│   └── train_baseline.ipynb
│
├── 🐳 Infrastructure
│   ├── docker-compose.yml               Multi-container setup
│   ├── setup.sh                         Linux/Mac setup
│   ├── setup.bat                        Windows setup
│   └── .gitignore                       Git ignore rules
│
└── 📖 Documentation
    ├── README.md                        Full documentation
    ├── QUICKSTART.md                    Quick start guide
    ├── ARCHITECTURE.md                  Technical design
    └── DEPLOYMENT.md                    Production guide
```

## ⚡ Quick Start (5 steps)

### 1️⃣ Get API Key
Visit https://openweathermap.org/api (free tier)

### 2️⃣ Setup
```bash
# Windows
setup.bat

# Mac/Linux
chmod +x setup.sh
./setup.sh
```

### 3️⃣ Configure
Edit `backend/.env`:
```env
WEATHER_API_KEY=your_key_here
```

### 4️⃣ Run Services
```bash
# Terminal 1
cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

### 5️⃣ Open Dashboard
🌐 http://localhost:5173

## 🎯 Key Features Implemented

### Backend
- ✅ POST `/predict` - ML ensemble predictions
- ✅ GET `/stations` - Station data
- ✅ GET `/health` - Health check
- ✅ GET `/docs` - Swagger UI
- ✅ Weather API integration
- ✅ Feature engineering
- ✅ Model caching
- ✅ Error handling

### Frontend
- ✅ Interactive Leaflet map
- ✅ Color-coded AQI markers
- ✅ Wind direction visualization
- ✅ Station search & filter
- ✅ Detailed prediction panel
- ✅ Real-time weather display
- ✅ Model confidence scores
- ✅ Modern, responsive design

### ML Models
- ✅ XGBoost (70% weight)
- ✅ LSTM (30% weight)
- ✅ Weighted ensemble
- ✅ Feature preprocessing
- ✅ Contributing factors analysis

## 📊 AQI Scale Reference

| AQI | Category | Color | Health | Emoji |
|-----|----------|-------|-----------|-------|
| 0-50 | Good | Green | ✅ Safe | 🟢 |
| 51-100 | Fair | Yellow | ⚠️ Caution | 🟡 |
| 101-200 | Moderate | Orange | ⚠️ Risky | 🟠 |
| 201-300 | Poor | Red | 🚫 Unsafe | 🔴 |
| 301-400 | Very Poor | Dark Red | 🚫 Hazardous | 🟣 |
| 401+ | Severe | Black | 🚫 Dangerous | ⬛ |

## 🌐 API Endpoints

### Prediction
```
POST /predict
Input:  { "latitude": 28.55, "longitude": 77.23, "station_name": "ITO" }
Output: { "aqi": 150.5, "xgboost_prediction": 152.0, "lstm_prediction": 145.0, ... }
```

### Data
```
GET /stations        - List monitoring stations
GET /models/info     - Model weights and status
GET /health          - API health check
GET /cache/stats     - Cache statistics
```

### Documentation
```
GET /docs           - Interactive Swagger UI
GET /redoc          - ReDoc documentation
```

## 📁 File Size Reference

```
Backend (~2-3 MB)
├── app/*.py              (~150 KB)
├── Python dependencies   (~2 GB when installed)
└── Models                (~500 MB - XGBoost + LSTM)

Frontend (~500 KB source)
├── src/*.jsx             (~100 KB)
├── node_modules          (~300 MB when installed)
└── build/dist            (~50 KB minified)
```

## 🔧 Configuration Files

### Backend `.env`
```env
WEATHER_API_KEY=your_openweathermap_key
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
XGBOOST_MODEL_PATH=../models/xgboost_aqi_model.pkl
LSTM_MODEL_PATH=../models/lstm_aqi_model.h5
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Deployment Options

| Option | Complexity | Cost | Scalability |
|--------|-----------|------|-------------|
| Local Dev | ⭐ | $0 | None |
| Docker | ⭐⭐ | $0+ | Good |
| VPS (Ubuntu) | ⭐⭐⭐ | $5-20 | Good |
| AWS/GCP/Azure | ⭐⭐⭐⭐ | $10-100 | Excellent |
| Kubernetes | ⭐⭐⭐⭐⭐ | $50+ | Enterprise |

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get stations
curl http://localhost:8000/stations

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 28.5505, "longitude": 77.2303, "station_name": "ITO"}'

# View API docs
curl http://localhost:8000/docs
```

## 🐛 Troubleshooting

### Models not loading?
```bash
# Check files exist
ls -la models/

# Check paths in .env
cat backend/.env | grep MODEL
```

### API connection error?
```bash
# Test backend is running
curl http://localhost:8000/health

# Check frontend .env
cat frontend/.env
```

### Port in use?
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

See [README.md](README.md#-troubleshooting) for full troubleshooting guide.

## 📚 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Leaflet.js](https://leafletjs.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [XGBoost Docs](https://xgboost.readthedocs.io/)
- [TensorFlow/Keras](https://www.tensorflow.org/guide/keras)

## 💡 Next Steps

1. ✅ Get it running locally (follow QUICKSTART.md)
2. 📊 Explore the notebooks to understand the models
3. 🔧 Customize the code for your needs
4. 🐳 Try Docker deployment
5. 🚀 Deploy to production (see DEPLOYMENT.md)

## 📞 Support

- **Documentation**: Read [README.md](README.md)
- **Quick Help**: See [QUICKSTART.md](QUICKSTART.md)
- **Technical Details**: Check [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment Help**: Refer to [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Check troubleshooting sections

## 🎓 File Descriptions

| File | Purpose | Language |
|------|---------|----------|
| `main.py` | FastAPI application | Python |
| `predictor.py` | ML model loading & prediction | Python |
| `weather.py` | Weather API integration | Python |
| `features.py` | Feature engineering | Python |
| `App.jsx` | Main React component | JavaScript |
| `AQIMap.jsx` | Leaflet map component | JavaScript |
| `api.js` | API client service | JavaScript |
| `aqi.js` | Utility functions | JavaScript |

## ✨ Architecture Highlights

### Backend
- **Async Weather API**: Non-blocking API calls
- **Model Singleton**: Load models once, reuse
- **Prediction Cache**: 5-minute TTL cache
- **Feature Pipeline**: Automatic feature extraction
- **Error Handling**: Comprehensive error responses

### Frontend
- **Component Composition**: Reusable components
- **State Management**: Zustand for global state
- **API Service**: Centralized API client
- **Error Boundaries**: Graceful error handling
- **Responsive Design**: Works on all devices

## 🎉 You're Ready!

Start with [QUICKSTART.md](QUICKSTART.md) to get up and running in 5 minutes!

---

Built with ❤️ | Questions? Read the docs or check troubleshooting!
