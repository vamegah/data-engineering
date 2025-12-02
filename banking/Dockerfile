# Dockerfile for Banking Churn Prediction Dashboard
# Production-ready containerization

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-test.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-test.txt && \
    pip install streamlit plotly

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "banking/dashboards/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
