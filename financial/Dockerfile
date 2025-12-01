
FROM python:3.9-slim

# Set working directory
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*
# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed models logs

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"

# Command to run the application
CMD ["streamlit", "run", "financial/dashboards/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]