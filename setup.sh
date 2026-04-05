#!/bin/bash

# Delhi AQI Prediction System - Setup Script
# This script sets up both backend and frontend

set -e

echo "🚀 Setting up Delhi AQI Prediction System..."

# Backend Setup
echo ""
echo "📦 Setting up Backend..."
cd backend

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your OpenWeatherMap API key"
fi

cd ..

# Frontend Setup
echo ""
echo "📦 Setting up Frontend..."
cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Install npm dependencies
echo "Installing Node dependencies..."
npm install

# Copy .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit backend/.env with your OpenWeatherMap API key"
echo "   2. Run the following commands in separate terminals:"
echo ""
echo "   Terminal 1 (Backend):"
echo "     cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
echo "   Terminal 2 (Frontend):"
echo "     cd frontend && npm run dev"
echo ""
echo "   Then open http://localhost:5173 in your browser"
echo ""
