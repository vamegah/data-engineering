FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
# Create directories first
RUN mkdir -p ./shared ./data/raw ./data/processed

# Copy project files
COPY fraud/ ./fraud/
COPY shared/ ./shared/

# Expose API port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health')"

# Run API
CMD ["uvicorn", "fraud.api.app:app", "--host", "0.0.0.0", "--port", "8001"]
