#!/bin/bash

# Delhi AQI Predictor - Production Deployment Checklist
# Run this to verify everything is ready for deployment

echo "================================"
echo "Deployment Pre-Flight Checklist"
echo "================================"

# Check 1: Git Repository
echo ""
echo "[1/7] Checking Git Repository..."
if [ -d ".git" ]; then
    echo "✓ Git repository exists"
    echo "  Branch: $(git rev-parse --abbrev-ref HEAD)"
    echo "  Last commit: $(git log -1 --pretty=format:%s)"
else
    echo "✗ Git repository NOT found. Run: git init && git add . && git commit -m 'Initial commit'"
fi

# Check 2: Backend Configuration
echo ""
echo "[2/7] Checking Backend Configuration..."
checks_passed=0
checks_total=0

if [ -f "backend/requirements.txt" ]; then
    ((checks_total++))
    if grep -q "gunicorn" backend/requirements.txt; then
        echo "✓ gunicorn in requirements.txt"
        ((checks_passed++))
    else
        echo "✗ gunicorn NOT in requirements.txt"
    fi
fi

if [ -f "backend/Procfile" ]; then
    echo "✓ Procfile exists"
    ((checks_total++))
    ((checks_passed++))
else
    echo "✗ Procfile missing"
    ((checks_total++))
fi

if [ -f "backend/runtime.txt" ]; then
    echo "✓ runtime.txt exists"
    ((checks_total++))
    ((checks_passed++))
else
    echo "✗ runtime.txt missing"
    ((checks_total++))
fi

echo "  Backend Config: $checks_passed/$checks_total ✓"

# Check 3: Frontend Configuration
echo ""
echo "[3/7] Checking Frontend Configuration..."
if [ -f "frontend/vercel.json" ]; then
    echo "✓ vercel.json exists"
else
    echo "✗ vercel.json missing"
fi

if [ -f "frontend/package.json" ]; then
    echo "✓ package.json exists"
else
    echo "✗ package.json missing"
fi

# Check 4: Models
echo ""
echo "[4/7] Checking Models..."
if [ -f "models/xgboost_aqi_model.pkl" ]; then
    SIZE=$(du -h "models/xgboost_aqi_model.pkl" | cut -f1)
    echo "✓ XGBoost model found ($SIZE)"
else
    echo "✗ XGBoost model NOT found"
fi

if [ -f "models/lstm_aqi_model.h5" ]; then
    SIZE=$(du -h "models/lstm_aqi_model.h5" | cut -f1)
    echo "✓ LSTM model found ($SIZE)"
else
    echo "⚠ LSTM model NOT found (optional, XGBoost will be primary)"
fi

# Check 5: Data Files
echo ""
echo "[5/7] Checking Data Files..."
if [ -f "data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv" ]; then
    ROWS=$(wc -l < "data/Processed/DELHI_MASTER_AQI_WEATHER_2025.csv")
    echo "✓ CSV data exists ($ROWS rows)"
else
    echo "✗ CSV data NOT found"
fi

# Check 6: Environment Files
echo ""
echo "[6/7] Checking Environment Files..."
if [ -f "backend/.env.example" ]; then
    echo "✓ backend/.env.example exists"
else
    echo "⚠ backend/.env.example missing (will be needed in production)"
fi

if [ -f "frontend/.env.example" ]; then
    echo "✓ frontend/.env.example exists"
else
    echo "⚠ frontend/.env.example missing (will be needed in production)"
fi

# Check 7: Documentation
echo ""
echo "[7/7] Checking Documentation..."
if [ -f "DEPLOYMENT_GUIDE.md" ]; then
    echo "✓ DEPLOYMENT_GUIDE.md exists"
else
    echo "⚠ DEPLOYMENT_GUIDE.md missing"
fi

# Summary
echo ""
echo "================================"
echo "Summary"
echo "================================"
echo ""
echo "Ready for deployment (git push + Vercel + Render setup)"
echo ""
echo "Next Steps:"
echo "1. git push origin main"
echo "2. Create/Link GitHub repository to Vercel"
echo "3. Create/Link GitHub repository to Render"
echo "4. Set environment variables on both platforms"
echo "5. Test production deployment"
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions"
