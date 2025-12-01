FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install NLP libraries
RUN pip install nltk textblob && \
    python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"

# Create directories first
RUN mkdir -p ./shared ./data/raw ./data/processed

# Copy project files
COPY hr/ ./hr/
COPY shared/ ./shared/

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8005/health')"

CMD ["uvicorn", "hr.api.app:app", "--host", "0.0.0.0", "--port", "8005"]
