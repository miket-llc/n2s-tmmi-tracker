# N2S TMMi Tracker Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/persistent_data/backups \
    && mkdir -p /app/logs \
    && mkdir -p /app/data

# Copy questions file to persistent location if it doesn't exist
COPY data/tmmi_questions.json /app/persistent_data/tmmi_questions.json

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set environment variables
ENV TMMI_DB_PATH=/app/persistent_data/assessments.db
ENV TMMI_BACKUP_DIR=/app/persistent_data/backups
ENV TMMI_QUESTIONS_PATH=/app/persistent_data/tmmi_questions.json

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]