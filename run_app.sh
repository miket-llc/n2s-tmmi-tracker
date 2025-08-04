#!/bin/bash

# N2S TMMi Tracker - Startup Script

echo "🔍 Starting N2S TMMi Tracker..."
echo "================================================"about:blank#blocked

# Set default environment variables for persistent storage
export TMMI_DB_PATH="${TMMI_DB_PATH:-data/assessments.db}"
export TMMI_BACKUP_DIR="${TMMI_BACKUP_DIR:-backups}"
export TMMI_QUESTIONS_PATH="${TMMI_QUESTIONS_PATH:-data/tmmi_questions.json}"

echo "Database path: $TMMI_DB_PATH"
echo "Backup directory: $TMMI_BACKUP_DIR"

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

# Create necessary directories
mkdir -p "$(dirname "$TMMI_DB_PATH")"
mkdir -p "$TMMI_BACKUP_DIR"
mkdir -p logs

# Create automatic backup on startup if database exists
if [ -f "$TMMI_DB_PATH" ]; then
    echo "Creating startup backup..."
    BACKUP_FILE="$TMMI_BACKUP_DIR/startup_backup_$(date +%Y%m%d_%H%M%S).db"
    cp "$TMMI_DB_PATH" "$BACKUP_FILE"
    echo "Backup created: $BACKUP_FILE"
fi

# Launch Streamlit app
echo "================================================"
echo "🚀 Launching N2S TMMi Tracker..."
echo "📊 Dashboard will open in your browser"
echo "💾 Database: $TMMI_DB_PATH"
echo "📂 Backups: $TMMI_BACKUP_DIR"
echo "🛑 Press Ctrl+C to stop the application"
echo "================================================"

streamlit run app.py --server.port 8501 --server.address localhost