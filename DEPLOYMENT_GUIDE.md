# Deployment Guide

This guide covers deploying the Delhi AQI Predictor to production using Vercel (frontend) and Render (backend).

## Prerequisites

- GitHub account and Git installed
- Vercel account (vercel.com)
- Render account (render.com) or Railway account (railway.app)
- Both repositories pushed to GitHub

## Local Testing Before Deployment

Before deploying, verify everything works locally:

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py
# Should start on http://localhost:8000

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
# Should start on http://localhost:5176
```

Test the application:
1. Open http://localhost:5176
2. Click on stations to see AQI predictions
3. Click "View 24h Forecast" to see 24-hour forecasts

## Step 1: Prepare Git Repository

```bash
# From project root
git init
git add .
git commit -m "Initial commit: AQI dashboard with 24-hour forecasting"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Delhi_AQI_Predictor.git
git push -u origin main
```

## Step 2: Deploy Frontend to Vercel

### Option A: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# In frontend directory
cd frontend
vercel
```

Follow the prompts:
- Link to existing project or create new
- Set root directory to `frontend`
- Build command: `npm run build` (should auto-detect)
- Output directory: `dist` (should auto-detect)
- Install dependencies: Yes

### Option B: Using Vercel Dashboard

1. Visit [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Set project name: `delhi-aqi-predictor`
5. Select root directory: `frontend`
6. Set environment variables:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```
   (Get this URL after deploying backend)
7. Click "Deploy"

### Vercel Deployment Details

- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**: 
  - `VITE_API_URL`: Your backend URL (set after Step 3)

**Frontend URL**: `https://delhi-aqi-predictor.vercel.app` (or your custom domain)

## Step 3: Deploy Backend to Render

### Prerequisites
- Backend requirements.txt is updated ✅ (includes gunicorn)
- Backend/Procfile exists ✅
- Backend/runtime.txt specifies Python 3.10.13 ✅

### Deployment Steps

1. Visit [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your project

5. Configure Web Service:
   - **Name**: `delhi-aqi-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: (leave empty - will auto-detect from Procfile)

6. Set Environment Variables:
   ```
   CORS_ORIGINS=["https://delhi-aqi-predictor.vercel.app","http://localhost:5173"]
   HOST=0.0.0.0
   PORT=8000
   DEBUG=False
   ```

7. Set Resource:
   - **Plan**: Free tier (recommended for testing)
   - Upgrade if needed for better performance

8. Click "Create Web Service"

### Handling Model Files

The models are large files that shouldn't be committed to Git. Choose one approach:

#### Option 1: Upload Models to Render After Deployment (Simplest)

1. After deployment, SSH into Render container
2. Upload models via Render dashboard file browser
3. Place in `/models/` directory

#### Option 2: Upload to AWS S3

1. Create S3 bucket with models
2. Add AWS credentials to Render environment
3. Modify `forecast_model_service.py` to download on startup

#### Option 3: Include Models in Docker (Recommended)

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
```

Then update Render to use Docker deployment.

### Backend URL
After deployment: `https://delhi-aqi-backend.onrender.com`

## Step 4: Update Frontend with Backend URL

After backend is deployed:

1. Go to Vercel project settings
2. Update environment variable:
   ```
   VITE_API_URL=https://delhi-aqi-backend.onrender.com
   ```
3. Redeploy frontend:
   ```bash
   cd frontend
   vercel --prod
   ```

## Step 5: Update CORS on Backend

Update backend environment variables with final frontend URL:

```
CORS_ORIGINS=["https://delhi-aqi-predictor.vercel.app","http://localhost:5173"]
```

Render will automatically restart with new variables.

## Step 6: Enable Custom Domain (Optional)

### Vercel Custom Domain
1. Vercel Dashboard → Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions

### Render Custom Domain
1. Render Dashboard → Environment → Custom Domain
2. Add your domain
3. Follow DNS configuration instructions

## Testing Production Deployment

1. Visit your Vercel frontend URL
2. Check browser console (F12) for any errors
3. Click stations on map
4. Verify AQI predictions load
5. Click "View 24h Forecast" button
6. Check that forecast appears

### Troubleshooting

**Issue: CORS Error**
- Check `CORS_ORIGINS` environment variable on Render
- Ensure frontend URL is included

**Issue: API Call Returns 404**
- Verify `VITE_API_URL` is correct in Vercel
- Check that backend is running on Render

**Issue: Models Not Found**
- Upload models to `/models` directory on Render
- Verify model paths in `backend/.env`

**Issue: Render Spins Down**
- Upgrade to paid plan for 24/7 uptime
- Or use Railway.app instead (auto-sleeps after 30 days of inactivity)

## Alternative Backend: Railway

1. Visit [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select repository
4. Railway auto-detects Procfile and Python
5. Set same environment variables from Render section
6. Deploy

Railway is similar to Render with slightly better free tier.

## Monitoring Production

### Vercel Monitoring
- Dashboard shows deployment history
- Real-time logs available
- Performance analytics included

### Render Monitoring
- Dashboard shows service status
- Logs available via dashboard or CLI
- Upgrade for monitoring metrics

## Continuous Deployment

Both Vercel and Render support automatic deployments on push:

1. **Vercel**: Automatically deploys on push to main branch
2. **Render**: Enable auto-deploy in settings

To deploy:
```bash
git add .
git commit -m "Update feature"
git push origin main
# Both platforms automatically redeploy
```

## Rollback

### Vercel
- Dashboard → Deployments → Select previous deployment → Promote

### Render
- Dashboard → Deployments → Redeploy previous version

## Environment Files Summary

### `frontend/.env.example`
```env
VITE_API_URL=http://localhost:8000
```

### `backend/.env.example`
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Quick Reference

| Component | Platform | URL | Tech |
|-----------|----------|-----|------|
| Frontend | Vercel | vercel.app | React 18, Vite, Tailwind |
| Backend | Render | onrender.com | FastAPI, Uvicorn |
| Database | CSV File | /data/Processed/ | pandas |
| Models | Local/S3 | /models/ | XGBoost, LSTM |
| Weather | Open-Meteo | api.open-meteo.com | Free (no key needed) |

## Support

For issues:
1. Check Vercel/Render logs
2. Review browser console (F12)
3. Check environment variables
4. Verify models are uploaded
5. Test local deployment first

