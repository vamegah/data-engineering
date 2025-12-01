FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ecommerce/ ./ecommerce/
COPY shared/ ./shared/

# Create data directories (APIs work without actual data files)
RUN mkdir -p ./data/raw ./data/processed

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8002/health')"

CMD ["uvicorn", "ecommerce.api.app:app", "--host", "0.0.0.0", "--port", "8002"]
