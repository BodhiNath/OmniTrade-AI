#!/bin/bash

# OmniTrade AI - Local Start Script (Without Docker)
# Use this for development or if Docker is not available

set -e

echo "================================================"
echo "OmniTrade AI - Local Start"
echo "================================================"
echo ""

# Check Python version
if ! command -v python3.11 &> /dev/null; then
    echo "Error: Python 3.11 not found"
    echo "Please install Python 3.11 or adjust the script"
    exit 1
fi

echo "✓ Python 3.11 found"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found, creating from template..."
    cp .env.example .env
    echo "⚠ Please edit .env and add your API keys!"
    echo ""
fi

# Install dependencies
echo "Installing Python dependencies..."
cd backend
pip3 install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create logs directory
mkdir -p ../logs

# Set environment for local run
export DATABASE_URL=${DATABASE_URL:-"postgresql://test:test@localhost:5432/test"}
export REDIS_URL=${REDIS_URL:-"redis://localhost:6379/0"}
export ENABLE_TRADING=${ENABLE_TRADING:-"false"}

echo ""
echo "================================================"
echo "Starting OmniTrade AI Backend..."
echo "================================================"
echo ""
echo "⚠ WARNING: This is a REAL trading system!"
echo "⚠ Make sure ENABLE_TRADING=false for testing"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the application
python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

