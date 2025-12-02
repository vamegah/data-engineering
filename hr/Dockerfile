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

# Copy shared utilities and project files from root context
COPY shared/ ./shared/
COPY hr/ ./hr/

# Create data directories (data folder not in git)
RUN mkdir -p ./data/raw ./data/processed

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8005/health')"

CMD ["uvicorn", "hr.api.app:app", "--host", "0.0.0.0", "--port", "8005"]
