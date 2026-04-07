# Quick Start Guide - Local Testing

**Time Required**: 15-20 minutes  
**Prerequisites**: Python 3.10+, Node.js 18+, Git

---

## 1. Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source AQI_env/bin/activate  # On Windows: AQI_env\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt

# Start FastAPI server
python run.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**✅ Backend Ready**: http://localhost:8000/docs (Swagger UI)

---

## 2. Test Backend Endpoints

### Test 1: Check Live AQI for Single Station

```bash
# In new terminal window
curl "http://localhost:8000/live-aqi?station=NSUT"
```

**Expected Response**:
```json
{
  "station": "NSUT",
  "aqi": 127,
  "pm25": 45.2,
  "temperature": 22.5,
  "humidity": 65,
  "wind_speed": 3.2,
  "wind_direction": 180,
  "update_time": "2024-04-07T14:30:00Z"
}
```

### Test 2: Get All Stations Live AQI

```bash
curl "http://localhost:8000/all-live-aqi"
```

**Expected**: Array of 17 stations with live AQI

### Test 3: Debug Pipeline for Station

```bash
curl "http://localhost:8000/debug?station=NSUT"
```

**Expected**: Comprehensive pipeline info with verification checklist

**Key Check**: All items in `verification` section should be `true`

---

## 3. Start Frontend Server

```bash
# In new terminal window, navigate to frontend
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

**✅ Frontend Ready**: http://localhost:5173

---

## 4. Test Frontend Components

### 4.1 Open in Browser

Navigate to: **http://localhost:5173**

You should see the Delhi AQI Predictor interface with:
- Map view with station markers
- Station search dropdown
- Stats cards (Average AQI, Highest, Lowest, Stations)

### 4.2 Click on a Station

Click any station marker on map:
- Should show popup
- Detail card appears on right sidebar
- Check browser console (F12) for errors

### 4.3 Check Network Requests

**Open Browser DevTools**: Press `F12`

Go to **Network** tab and look for:
- `live-aqi?station=...` requests (should return JSON)
- `all-live-aqi` requests (should return array)
- Check response should be 200 OK

---

## 5. Component Integration Testing

### Test LiveAQIDisplay

**File to Modify**: `frontend/src/components/AQIDetailCard.jsx`

**Add this import** at top:
```jsx
import { LiveAQIDisplay } from './LiveAQIDisplay'
```

**Add this JSX** in the component (after the header):
```jsx
{/* Live AQI Display */}
<div className="border-t border-gray-200 pt-4">
  <h3 className="font-semibold text-gray-800 mb-3">Current Conditions (Live)</h3>
  <LiveAQIDisplay station={station?.name} />
</div>
```

**Expected**: New "Current Conditions (Live)" section with real AQI data

### Test StationComparisonPanel

**File to Modify**: `frontend/src/App.jsx`

**Add this import** at top:
```jsx
import { StationComparisonPanel } from './components/StationComparisonPanel'
```

**Find** the sidebar section (around line 200) and add after detail card:

```jsx
{/* Station Comparison Panel */}
<div className="mt-6 bg-white rounded-lg shadow-lg p-4">
  <StationComparisonPanel
    selectedStation={selectedStation?.name}
    stationList={stations}
    apiBaseUrl="http://localhost:8000"
  />
</div>
```

**Expected**: New ranked list showing all stations

---

## 6. Verify Data Flow

### Check 1: Backend is Serving Data

```bash
# Terminal 1: Check if backend running
curl -s http://localhost:8000/health | head -20
```

Should show status information.

### Check 2: Frontend Connecting to Backend

**DevTools → Network tab**:
- Select station from dropdown
- Look for API calls to `localhost:8000`
- Should see 200 responses

### Check 3: Components Rendering

**DevTools → Elements tab**:
- Find `<div class="LiveAQIDisplay">`
- Should contain pollutant data (PM2.5, PM10, NO2)

### Check 4: No Errors

**DevTools → Console tab**:
- Should be clean (no red error messages)
- Yellow warnings only (if any)

---

## 7. Performance Check

### Forecast Stability Test

1. **Select a station** (e.g., NSUT)
2. **Click Refresh** button multiple times
3. **Check**: Forecast should NOT change within 10 minutes (it's cached)

**Expected Behavior**:
```
Call 1: 245.4 AQI (forecast)
Call 2: 245.4 AQI (from cache)
Call 3: 245.4 AQI (from cache)
After 10 min: May update
```

### Live Data Still Updates

1. **Check**: `/live-aqi` endpoint should show current real data
2. **Check**: Live AQI display should update every 5 minutes
3. **Note**: This is from WAQI API, so may only update hourly

---

## 8. Debugging Tips

### If Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.10+

# Check port is free
netstat -an | grep 8000  # Should be empty

# Try explicit port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### If Frontend Won't Load

```bash
# Clear cache
rm -rf node_modules/.vite

# Reinstall
npm install

# Start fresh
npm run dev
```

### If API Requests Fail

**Check CORS headers**:
```bash
curl -i http://localhost:8000/live-aqi?station=NSUT
```

Look for:
```
Access-Control-Allow-Origin: *
```

### If Components Show Errors

1. **Check Import Path**: Should be `./components/ComponentName`
2. **Check Station Name**: Must match exactly (case-sensitive)
3. **Check Component Props**: See COMPONENT_INTEGRATION_GUIDE.md

---

## 9. What to Look For

### ✅ Success Indicators

- [x] Backend starts without errors
- [x] `/debug` endpoint returned verification checklist with all TRUE
- [x] Browser loads at http://localhost:5173
- [x] Station selection triggers API calls
- [x] DevTools Network shows 200 responses
- [x] New components appear after integration
- [x] Console has no error messages

### ❌ Problems to Fix

- [ ] Backend won't start → Check Python version, port, dependencies
- [ ] API returns 404 → Verify endpoint path, check server logs
- [ ] Components not rendering → Check imports, file paths, prop names
- [ ] CORS errors → Backend not allowing frontend origin
- [ ] Console errors → Read error message, check component code

---

## 10. Next Steps

Once local testing is complete:

1. **Verify all 4 problems are fixed** ✅
   - [ ] Each station has unique forecast
   - [ ] Forecasts stable within 10 minutes
   - [ ] Live AQI from WAQI (not ML)
   - [ ] `/debug` shows full pipeline

2. **Verify all 5 improvements are working** ✅
   - [ ] Wind visualization (if on map)
   - [ ] AQI color coding
   - [ ] Forecast confidence bands
   - [ ] Station comparison panel
   - [ ] Time calculations correct

3. **Ready for deployment** ✅
   - [ ] Follow COMPONENT_INTEGRATION_GUIDE.md
   - [ ] All tests passing
   - [ ] No console errors
   - [ ] Performance acceptable

---

## 11. Useful Commands

```bash
# Backend
cd backend
source AQI_env/bin/activate
python run.py

# Frontend (new terminal)
cd frontend
npm run dev

# Test API endpoints (new terminal)
curl "http://localhost:8000/debug?station=NSUT" | python -m json.tool
curl "http://localhost:8000/all-live-aqi" | python -m json.tool

# Check if port is in use
lsof -i :8000  # For Unix/Mac
netstat -ano | findstr :8000  # For Windows

# Kill process on port
kill -9 <PID>  # For Unix/Mac
taskkill /PID <PID> /F  # For Windows
```

---

## 12. Support Resources

**Error with endpoint?**
- Check: `backend/app/main.py` to verify endpoint exists
- Run: `/debug` endpoint to verify data source
- Example: `curl http://localhost:8000/debug?station=NSUT`

**Component not showing?**
- Check: COMPONENT_INTEGRATION_GUIDE.md for exact code
- Verify: File imports and component props
- Debug: Browser DevTools → Elements tab → Search for component name

**WAQI data not appearing?**
- Check: Backend logs for WAQI API errors
- Verify: WAQI API key in backend config
- Test: `/live-aqi` endpoint directly
- Note: Free tier limited to 1000 calls/day

**Still stuck?**
- Check: IMPLEMENTATION_SUMMARY.md for context
- Review: Error messages in browser console and backend logs
- Verify: All backend endpoints return valid JSON
- Ensure: Node modules and Python packages installed

---

## Quick Checklist

```
🚀 LOCAL TESTING CHECKLIST

Backend Setup:
  [ ] Virtual environment activated
  [ ] Dependencies installed
  [ ] Run.py executed without errors
  [ ] http://localhost:8000/docs accessible

Backend Endpoints:
  [ ] /live-aqi?station=NSUT returns data
  [ ] /all-live-aqi returns 17 stations  
  [ ] /debug?station=NSUT verification all TRUE

Frontend Setup:
  [ ] npm dependencies installed
  [ ] npm run dev starts successfully
  [ ] http://localhost:5173 loads in browser

Frontend Components:
  [ ] Map displays with stations
  [ ] Station selection works
  [ ] No console errors

Component Integration:
  [ ] LiveAQIDisplay added to detail card
  [ ] StationComparisonPanel added to app
  [ ] ForecastConfidenceBands (optional)
  [ ] WindVisualization (optional)

Verification:
  [ ] Each station has unique forecast (±10-90 AQI diff)
  [ ] Forecasts stable within 10 min cache
  [ ] Live AQI displays real WAQI data
  [ ] /debug shows complete pipeline
```

---

**Status**: Ready to test locally  
**Estimated Duration**: 15-20 minutes  
**Next Document**: COMPONENT_INTEGRATION_GUIDE.md (after testing)

*Start with Step 1 above and progress through each section*
