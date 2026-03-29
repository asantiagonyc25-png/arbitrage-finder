#!/bin/bash

# Arbitrage Finder - Quick Local Setup & Test Script
# Run in project directory: bash run_local.sh

set -e

echo "🚀 Arbitrage Finder - Local Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "✓ Python version: $python_version"

# Activate venv
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Kill any existing process on port 8080
echo "🧹 Cleaning up old processes..."
lsof -ti :8080 &>/dev/null && kill -9 $(lsof -ti :8080) || true
sleep 1

# Start the app
echo "🌐 Starting Flask app on localhost:8080..."
PORT=8080 python3 app.py &
APP_PID=$!
sleep 2

# Test the endpoints
echo ""
echo "✅ Testing endpoints..."
echo ""

# Health check
echo "Testing health endpoint..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    kill $APP_PID
    exit 1
fi

# Dashboard
echo "Testing dashboard..."
if curl -s http://localhost:8080/ | grep -q "Arbitrage Finder" > /dev/null 2>&1; then
    echo "✓ Dashboard loads successfully"
else
    echo "⚠ Dashboard test inconclusive"
fi

# API results
echo "Testing API results endpoint..."
if curl -s http://localhost:8080/api/results | grep -q "winning_products" > /dev/null 2>&1; then
    echo "✓ API results endpoint working"
else
    echo "⚠ API results check inconclusive"
fi

echo ""
echo "=================================="
echo "🎉 Local setup complete!"
echo "=================================="
echo ""
echo "📂 Dashboard: http://localhost:8080"
echo "📡 API: http://localhost:8080/api"
echo ""
echo "Quick test commands:"
echo "  Analyze: curl -X POST http://localhost:8080/api/analyze -H 'Content-Type: application/json' -d '{\"products\": [\"LED light bulbs\"]}'"
echo "  Results: curl http://localhost:8080/api/results"
echo ""
echo "Stop server: kill $APP_PID"
echo ""
echo "Ready to deploy? See QUICK_START.md for Railway deployment"
echo "=================================="
