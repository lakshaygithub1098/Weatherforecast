@echo off
REM Delhi AQI Prediction System - Setup Script for Windows

setlocal enabledelayedexpansion

echo 🚀 Setting up Delhi AQI Prediction System...

REM Backend Setup
echo.
echo 📦 Setting up Backend...
cd backend

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade pip
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt

REM Copy .env from example if it doesn't exist
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your OpenWeatherMap API key
)

cd ..

REM Frontend Setup
echo.
echo 📦 Setting up Frontend...
cd frontend

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    exit /b 1
)

REM Install npm dependencies
echo Installing Node dependencies...
call npm install

REM Copy .env from example if it doesn't exist
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
)

cd ..

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Edit backend\.env with your OpenWeatherMap API key
echo    2. Run the following commands in separate terminals:
echo.
echo    Terminal 1 (Backend):
echo      cd backend
echo      venv\Scripts\activate.bat
echo      python -m uvicorn app.main:app --reload
echo.
echo    Terminal 2 (Frontend):
echo      cd frontend
echo      npm run dev
echo.
echo    Then open http://localhost:5173 in your browser
echo.

pause
