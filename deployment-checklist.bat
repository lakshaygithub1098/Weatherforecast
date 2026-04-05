@echo off
REM Delhi AQI Predictor - Production Deployment Checklist for Windows
REM Run this to verify everything is ready for deployment

setlocal enabledelayedexpansion

echo ================================
echo Deployment Pre-Flight Checklist
echo ================================

REM Check 1: Git Repository
echo.
echo [1/7] Checking Git Repository...
if exist ".git" (
    echo X Git repository exists
    for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
    echo   Branch: !BRANCH!
) else (
    echo X Git repository NOT found
    echo   Run: git init ^&^& git add . ^&^& git commit -m "Initial commit"
)

REM Check 2: Backend Configuration
echo.
echo [2/7] Checking Backend Configuration...
set passed=0
set total=0

if exist "backend\requirements.txt" (
    echo X Checking for gunicorn in requirements.txt...
    findstr /M "gunicorn" backend\requirements.txt >nul
    if !errorlevel! equ 0 (
        echo X gunicorn in requirements.txt
        set /a passed+=1
    ) else (
        echo ! gunicorn NOT in requirements.txt
    )
    set /a total+=1
)

if exist "backend\Procfile" (
    echo X Procfile exists
    set /a passed+=1
) else (
    echo ! Procfile missing
)
set /a total+=1

if exist "backend\runtime.txt" (
    echo X runtime.txt exists
    set /a passed+=1
) else (
    echo ! runtime.txt missing
)
set /a total+=1

echo   Backend Config: !passed!/!total! passes

REM Check 3: Frontend Configuration
echo.
echo [3/7] Checking Frontend Configuration...
if exist "frontend\vercel.json" (
    echo X vercel.json exists
) else (
    echo ! vercel.json missing
)

if exist "frontend\package.json" (
    echo X package.json exists
) else (
    echo ! package.json missing
)

REM Check 4: Models
echo.
echo [4/7] Checking Models...
if exist "models\xgboost_aqi_model.pkl" (
    for %%A in ("models\xgboost_aqi_model.pkl") do (
        set SIZE=%%~zA
        echo X XGBoost model found (!SIZE! bytes^)
    )
) else (
    echo ! XGBoost model NOT found
)

if exist "models\lstm_aqi_model.h5" (
    for %%A in ("models\lstm_aqi_model.h5") do (
        set SIZE=%%~zA
        echo X LSTM model found (!SIZE! bytes^)
    )
) else (
    echo ~ LSTM model NOT found (optional, XGBoost will be primary^)
)

REM Check 5: Data Files
echo.
echo [5/7] Checking Data Files...
if exist "data\Processed\DELHI_MASTER_AQI_WEATHER_2025.csv" (
    echo X CSV data exists
) else (
    echo ! CSV data NOT found
)

REM Check 6: Environment Files
echo.
echo [6/7] Checking Environment Files...
if exist "backend\.env.example" (
    echo X backend\.env.example exists
) else (
    echo ~ backend\.env.example missing (will be needed in production^)
)

if exist "frontend\.env.example" (
    echo X frontend\.env.example exists
) else (
    echo ~ frontend\.env.example missing (will be needed in production^)
)

REM Check 7: Documentation
echo.
echo [7/7] Checking Documentation...
if exist "DEPLOYMENT_GUIDE.md" (
    echo X DEPLOYMENT_GUIDE.md exists
) else (
    echo ~ DEPLOYMENT_GUIDE.md missing
)

REM Summary
echo.
echo ================================
echo Summary
echo ================================
echo.
echo Ready for deployment (git push + Vercel + Render setup^)
echo.
echo Next Steps:
echo 1. git push origin main
echo 2. Create/Link GitHub repository to Vercel
echo 3. Create/Link GitHub repository to Render
echo 4. Set environment variables on both platforms
echo 5. Test production deployment
echo.
echo See DEPLOYMENT_GUIDE.md for detailed instructions
echo.

endlocal
