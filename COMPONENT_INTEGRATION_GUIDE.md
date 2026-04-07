# Component Integration Guide

This guide shows how to integrate the new frontend components into your existing Delhi AQI Predictor application.

## New Components Created

### 1. **LiveAQIDisplay** (`frontend/src/components/LiveAQIDisplay.jsx`)
- **Purpose**: Display real-time AQI data from WAQI API
- **Shows**: Current AQI, pollutants (PM2.5, PM10, NO2), weather, wind data
- **Auto-refresh**: Every 5 minutes
- **Usage Context**: Add to station detail card to show current conditions

### 2. **ForecastConfidenceBands** (`frontend/src/components/ForecastConfidenceBands.jsx`)
- **Purpose**: Display 24-hour forecast with uncertainty bands
- **Shows**: Confidence intervals (±RMSE of 18 AQI), statistics (min/max/avg)
- **Usage Context**: Replace existing forecast chart to show model uncertainty
- **Requires**: Recharts library (already installed)

### 3. **WindVisualization** (`frontend/src/components/WindVisualization.jsx`)
- **Purpose**: Draw wind direction arrows between stations on map
- **Shows**: Wind speed (arrow thickness), pollution flow, upwind influence
- **Usage Context**: Integrate into AQIMap component to visualize pollution transport

### 4. **StationComparisonPanel** (`frontend/src/components/StationComparisonPanel.jsx`)
- **Purpose**: Show all stations ranked by current AQI
- **Shows**: Ranking, current AQI, PM2.5, upwind influences
- **Usage Context**: Add as sidebar panel or modal
- **Requires**: Connection to `/all-live-aqi` and `/debug` endpoints

---

## Integration Steps

### Step 1: Update AQIDetailCard.jsx

Add LiveAQIDisplay to show real current AQI above the forecast:

```jsx
import { LiveAQIDisplay } from './LiveAQIDisplay'

export const AQIDetailCard = ({ prediction, station }) => {
  // ... existing code ...
  
  return (
    <motion.div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* ... existing header and content ... */}
      
      {/* ADD THIS: Live AQI Display from WAQI API */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="font-semibold text-gray-800 mb-3">Current Conditions (Live)</h3>
        <LiveAQIDisplay station={station?.name} />
      </div>
      
      {/* ... existing forecast and other sections ... */}
    </motion.div>
  )
}
```

**Location**: After header section, before existing AQI display

---

### Step 2: Replace Forecast Chart with Confidence Bands

Replace existing forecast visualization:

```jsx
import { ForecastConfidenceBands } from './ForecastConfidenceBands'

// In AQIDetailCard or wherever forecast is displayed:
{prediction.forecast_24h && (
  <div className="border-t border-gray-200 pt-4">
    <ForecastConfidenceBands 
      forecast={prediction.forecast_24h} 
      rmse={18}
      title={`${station?.name} 24-Hour Forecast`}
    />
  </div>
)}
```

**Forecast Data Format Expected**:
```javascript
forecast_24h: [
  { hour: 'Now', aqi: 127, upwind_influence: 0.5 },
  { hour: '+1h', aqi: 131, upwind_influence: 0.6 },
  // ... 22 more hours
]
```

---

### Step 3: Add Wind Visualization to Map

Integrate wind arrows into existing AQIMap component:

```jsx
import WindVisualization from './WindVisualization'
import { useRef } from 'react'

export const AQIMap = ({ stations, predictions, selectedStation, onStationSelect, showWindArrows }) => {
  const mapRef = useRef(null)
  const [map, setMap] = useState(null)
  
  // ... existing map setup ...
  
  useEffect(() => {
    if (map && showWindArrows && selectedStation) {
      // Get wind data from predictions
      const windData = predictions[selectedStation?.name]?.weather || {}
      
      <WindVisualization 
        map={map}
        stations={stations}
        stationAQI={predictions}
        windData={windData}
      />
    }
  }, [map, selectedStation, predictions, showWindArrows])
  
  // ... rest of component ...
}
```

**Note**: Wind arrows will draw automatically when a station is selected

---

### Step 4: Add Station Comparison Panel

Add as right sidebar or modal in App.jsx:

```jsx
import { StationComparisonPanel } from './components/StationComparisonPanel'

// In App.jsx, within the main grid layout:
<div className="lg:col-span-1">
  <motion.div
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: 0.4 }}
    className="bg-white rounded-lg shadow-lg p-4"
  >
    <StationComparisonPanel
      selectedStation={selectedStation?.name}
      stationList={stations}
      apiBaseUrl="http://localhost:8000" // Update with your API URL
    />
  </motion.div>
</div>
```

**Alternative**: Use as a modal/overlay that appears on button click

---

## Backend Endpoint Requirements

Ensure your backend provides these endpoints (already implemented):

### 1. `/live-aqi?station=STATIONNAME`
**Response**:
```json
{
  "station": "NSUT",
  "aqi": 127,
  "pm25": 45.2,
  "pm10": 78.5,
  "no2": 23.4,
  "so2": 12.1,
  "temperature": 22.5,
  "humidity": 65,
  "wind_speed": 3.2,
  "wind_direction": 180,
  "update_time": "2024-04-07T14:30:00Z"
}
```

### 2. `/all-live-aqi`
**Response**:
```json
{
  "stations": [
    {
      "name": "NSUT",
      "aqi": 127,
      "pm25": 45.2,
      "...": "..."
    },
    // ... 16 more stations
  ],
  "update_time": "2024-04-07T14:30:00Z"
}
```

### 3. `/debug?station=STATIONNAME`
**Response**:
```json
{
  "station": "NSUT",
  "past_24h_aqi": [125.3, 128.1, ...],
  "weather_forecast_used": {"temp": 22, "wind": 180},
  "features_shape": "24 x 27",
  "model_used": "xgboost (24h forecast)",
  "raw_forecast": [125, 130, ...],
  "upwind_influence": [
    {"name": "Shadipur", "influence_score": 0.65},
    {"name": "DTU", "influence_score": 0.45}
  ],
  "verification": {
    "historical_data_loaded": true,
    "weather_forecast_available": true,
    "features_correct_shape": true,
    "model_found": true,
    "predictions_valid": true
  }
}
```

---

## Environment Configuration

Update API URLs in your frontend services:

**`frontend/src/services/api.js`** (or similar):
```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000'

export const predictionsAPI = {
  // ... existing endpoints ...
  
  // Add these new endpoints:
  getLiveAQI: (station) => 
    axios.get(`${API_BASE_URL}/live-aqi?station=${station}`),
  
  getAllLiveAQI: () => 
    axios.get(`${API_BASE_URL}/all-live-aqi`),
  
  getDebugInfo: (station) => 
    axios.get(`${API_BASE_URL}/debug?station=${station}`)
}
```

---

## Testing Checklist

- [ ] Backend `/live-aqi` endpoint returns real WAQI data
- [ ] Backend `/all-live-aqi` returns data for all stations
- [ ] Backend `/debug` endpoint shows full pipeline
- [ ] LiveAQIDisplay renders without errors
- [ ] ForecastConfidenceBands displays forecast with bands
- [ ] WindVisualization draws arrows on map when station selected
- [ ] StationComparisonPanel loads and displays rankings
- [ ] All components auto-refresh at correct intervals
- [ ] Error handling works when API is down

---

## Deployment Notes

### Production API URL
Update `VITE_API_URL` environment variable:

```bash
# Frontend deployment (Vercel)
VITE_API_URL=https://your-deployed-backend.com
```

### WAQI API Key
Update in backend configuration:

```bash
# Backend environment variable
WAQI_API_KEY=your_production_api_key_here
```

Get free tier key at: https://aqicn.org/api/

---

## Component Dependencies

**Required Libraries** (already in package.json):
- `react` - UI framework
- `axios` - HTTP requests
- `recharts` - Charts for ForecastConfidenceBands
- `leaflet` - Mapping (for WindVisualization)
- `framer-motion` - Animations (optional, for polish)

**Installation** (if missing):
```bash
npm install axios recharts leaflet framer-motion
```

---

## Troubleshooting

### LiveAQIDisplay shows "Connection error"
- [ ] Backend is running
- [ ] `/live-aqi` endpoint accessible
- [ ] WAQI API key is valid (check backend logs)
- [ ] Station name matches exactly

### ForecastConfidenceBands shows empty chart
- [ ] Forecast data has correct format (hour, aqi fields)
- [ ] Data is array with at least 1 item
- [ ] AQI values are numbers, not strings

### WindVisualization doesn't draw arrows
- [ ] Map object properly initialized
- [ ] selectedStation is not null
- [ ] stations array has latitude/longitude
- [ ] Check browser console for errors

### StationComparisonPanel shows "Failed to load"
- [ ] `/all-live-aqi` endpoint accessible
- [ ] Backend is responding
- [ ] Check browser console for CORS errors

---

## Next Steps

1. **Test components locally** with `npm run dev`
2. **Verify backend endpoints** using `/debug` for each station
3. **Integrate components** one by one into existing pages
4. **Deploy to production** and monitor API calls
5. **Monitor WAQI API rate limits** (free tier: 1000/day)

---

Generated: April 7, 2024
Last Updated: Development
Status: Ready for Integration
