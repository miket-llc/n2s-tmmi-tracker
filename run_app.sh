#!/bin/bash

# TMMi Assessment Tracker - Startup Script

echo "🔍 Starting TMMi Assessment Tracker..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

# Launch Streamlit app
echo "================================================"
echo "🚀 Launching TMMi Assessment Tracker..."
echo "📊 Dashboard will open in your browser"
echo "🛑 Press Ctrl+C to stop the application"
echo "================================================"

streamlit run app.py --server.port 8501 --server.address localhost