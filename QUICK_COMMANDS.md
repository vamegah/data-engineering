# 🚀 Quick Commands Reference

Essential commands for running all production components.

---

## Validation

```bash
# Validate all projects are production-ready
python validate_production.py
```

---

## Testing

### Run All Tests

```bash
# Run all project tests with coverage
pytest tests/test_fraud.py -v --cov=fraud
pytest tests/test_ecommerce.py -v --cov=ecommerce
pytest tests/test_financial.py -v --cov=financial
pytest tests/test_healthcare.py -v --cov=healthcare
pytest tests/test_hr.py -v --cov=hr
pytest tests/test_restaurant.py -v --cov=restaurant

# Or run all at once
pytest tests/ -v --cov=. --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_fraud.py::TestFraudETL::test_extract_data -v
```

---

## APIs

### Start Individual APIs

```bash
# Fraud Detection API (Port 8001)
uvicorn fraud.api.app:app --host 0.0.0.0 --port 8001 --reload

# E-commerce API (Port 8002)
uvicorn ecommerce.api.app:app --host 0.0.0.0 --port 8002 --reload

# Financial API (Port 8003)
uvicorn financial.api.app:app --host 0.0.0.0 --port 8003 --reload

# Healthcare API (Port 8004)
uvicorn healthcare.api.app:app --host 0.0.0.0 --port 8004 --reload

# HR API (Port 8005)
uvicorn hr.api.app:app --host 0.0.0.0 --port 8005 --reload

# Restaurant API (Port 8006)
uvicorn restaurant.api.app:app --host 0.0.0.0 --port 8006 --reload
```

### Test API Endpoints

```bash
# Health checks
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health

# View API documentation
# Open in browser:
# http://localhost:8001/docs
# http://localhost:8002/docs
# http://localhost:8003/docs
# http://localhost:8004/docs
# http://localhost:8005/docs
# http://localhost:8006/docs
```

---

## Docker

### Build Images

```bash
# Build all Docker images
docker build -t fraud-api:latest -f fraud/Dockerfile .
docker build -t ecommerce-api:latest -f ecommerce/Dockerfile .
docker build -t financial-api:latest -f financial/Dockerfile .
docker build -t healthcare-api:latest -f healthcare/Dockerfile .
docker build -t hr-api:latest -f hr/Dockerfile .
docker build -t restaurant-api:latest -f restaurant/Dockerfile .
```

### Run Containers

```bash
# Run containers with environment files
docker run -d -p 8001:8001 --env-file fraud/.env --name fraud-api fraud-api:latest
docker run -d -p 8002:8002 --env-file ecommerce/.env --name ecommerce-api ecommerce-api:latest
docker run -d -p 8003:8003 --env-file financial/.env --name financial-api financial-api:latest
docker run -d -p 8004:8004 --env-file healthcare/.env --name healthcare-api healthcare-api:latest
docker run -d -p 8005:8005 --env-file hr/.env --name hr-api hr-api:latest
docker run -d -p 8006:8006 --env-file restaurant/.env --name restaurant-api restaurant-api:latest
```

### Container Management

```bash
# View running containers
docker ps

# View logs
docker logs fraud-api
docker logs -f fraud-api  # Follow logs

# Stop containers
docker stop fraud-api ecommerce-api financial-api healthcare-api hr-api restaurant-api

# Remove containers
docker rm fraud-api ecommerce-api financial-api healthcare-api hr-api restaurant-api

# View container health
docker inspect --format='{{.State.Health.Status}}' fraud-api
```

---

## Monitoring

### Run Monitoring Scripts

```bash
# Fraud monitoring
python fraud/scripts/monitoring.py

# E-commerce monitoring
python ecommerce/scripts/monitoring.py

# Financial monitoring
python financial/scripts/monitoring.py

# Healthcare monitoring
python healthcare/scripts/monitoring.py

# HR monitoring
python hr/scripts/monitoring.py

# Restaurant monitoring
python restaurant/scripts/monitoring.py
```

### Check Logs

```bash
# View monitoring logs
cat logs/fraud_monitoring.log
cat logs/ecommerce_monitoring.log
cat logs/financial_monitoring.log
cat logs/healthcare_monitoring.log
cat logs/hr_monitoring.log
cat logs/restaurant_monitoring.log

# Tail logs (real-time)
tail -f logs/fraud_monitoring.log
```

---

## Airflow

### Setup Airflow

```bash
# Install Airflow (if not installed)
pip install apache-airflow==2.7.0

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Copy DAGs to Airflow folder
mkdir -p ~/airflow/dags
cp fraud/dags/*.py ~/airflow/dags/
cp ecommerce/dags/*.py ~/airflow/dags/
cp financial/dags/*.py ~/airflow/dags/
cp healthcare/dags/*.py ~/airflow/dags/
cp hr/dags/*.py ~/airflow/dags/
cp restaurant/dags/*.py ~/airflow/dags/
```

### Start Airflow

```bash
# Start webserver (Terminal 1)
airflow webserver --port 8080

# Start scheduler (Terminal 2)
airflow scheduler

# Access UI: http://localhost:8080
```

### Airflow CLI

```bash
# List all DAGs
airflow dags list

# Test a DAG
airflow dags test fraud_detection_pipeline 2024-01-01

# Trigger a DAG manually
airflow dags trigger fraud_detection_pipeline

# View DAG runs
airflow dags list-runs -d fraud_detection_pipeline

# Pause/Unpause DAG
airflow dags pause fraud_detection_pipeline
airflow dags unpause fraud_detection_pipeline
```

---

## ETL Pipelines

### Run ETL Scripts

```bash
# Fraud ETL
python fraud/scripts/etl_pipeline.py

# E-commerce ETL
python ecommerce/scripts/etl_pipeline.py

# Financial ETL
python financial/scripts/etl_pipeline.py

# Healthcare ETL
python healthcare/scripts/etl_pipeline.py

# HR ETL
python hr/scripts/etl_pipeline.py

# Restaurant ETL
python restaurant/scripts/etl_pipeline.py
```

---

## Dashboards

### Start Streamlit Dashboards

```bash
# Fraud dashboard
streamlit run fraud/dashboards/streamlit_app.py --server.port 8501

# E-commerce dashboard
streamlit run ecommerce/dashboards/streamlit_app.py --server.port 8502

# Financial dashboard
streamlit run financial/dashboards/streamlit_app.py --server.port 8503

# Healthcare dashboard
streamlit run healthcare/dashboards/streamlit_app.py --server.port 8504

# HR dashboard
streamlit run hr/dashboards/streamlit_app.py --server.port 8505

# Restaurant dashboard
streamlit run restaurant/dashboards/streamlit_app.py --server.port 8506
```

---

## CI/CD

### GitHub Actions

```bash
# Workflows are automatically triggered on:
# - Push to main/develop
# - Pull requests to main

# View workflow status
# Go to: https://github.com/[username]/[repo]/actions

# Manual trigger (if configured)
gh workflow run fraud_ci.yml
```

### Local CI Testing

```bash
# Run linting
flake8 fraud/ --count --select=E9,F63,F7,F82
flake8 ecommerce/ --count --select=E9,F63,F7,F82

# Run security checks
pip install bandit safety
bandit -r fraud/
safety check --file requirements.txt
```

---

## Database

### PostgreSQL Setup

```bash
# Start PostgreSQL (Docker)
docker run -d \
  --name portfolio-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=portfolio \
  -p 5432:5432 \
  postgres:13

# Run schema setup
psql -h localhost -U postgres -d portfolio -f fraud/sql/schema_setup.sql
psql -h localhost -U postgres -d portfolio -f ecommerce/sql/schema_setup.sql
# ... (all projects)
```

### Database Queries

```bash
# Connect to database
psql -h localhost -U postgres -d portfolio

# Run SQL files
psql -h localhost -U postgres -d portfolio -f fraud/sql/fraud_queries.sql
```

---

## Environment Configuration

### Setup Environment Files

```bash
# Copy example files to actual .env files
cp fraud/.env.example fraud/.env
cp ecommerce/.env.example ecommerce/.env
cp financial/.env.example financial/.env
cp healthcare/.env.example healthcare/.env
cp hr/.env.example hr/.env
cp restaurant/.env.example restaurant/.env

# Edit with your values
nano fraud/.env  # or use any text editor
```

### Validate Environment

```bash
# Check environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv('fraud/.env'); import os; print('Loaded:', bool(os.getenv('DATABASE_URL')))"
```

---

## Maintenance

### Update Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update requirements
pip install --upgrade -r requirements.txt

# Freeze new requirements
pip freeze > requirements.txt
```

### Clean Up

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove test cache
rm -rf .pytest_cache
rm -f .coverage
rm -rf htmlcov/

# Remove Docker resources
docker system prune -a
```

---

## Troubleshooting

### Check System Status

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check Docker
docker --version
docker ps

# Check PostgreSQL
pg_isready -h localhost -p 5432
```

### Debug APIs

```bash
# Run API with debug output
uvicorn fraud.api.app:app --reload --log-level debug

# Test with verbose curl
curl -v http://localhost:8001/health
```

### Debug Tests

```bash
# Run tests with verbose output
pytest tests/test_fraud.py -vv -s

# Run single test with debugging
pytest tests/test_fraud.py::TestFraudETL::test_extract_data -vv -s --pdb
```

---

## Port Reference

| Service              | Port | URL                   |
| -------------------- | ---- | --------------------- |
| Fraud API            | 8001 | http://localhost:8001 |
| E-commerce API       | 8002 | http://localhost:8002 |
| Financial API        | 8003 | http://localhost:8003 |
| Healthcare API       | 8004 | http://localhost:8004 |
| HR API               | 8005 | http://localhost:8005 |
| Restaurant API       | 8006 | http://localhost:8006 |
| Airflow UI           | 8080 | http://localhost:8080 |
| Fraud Dashboard      | 8501 | http://localhost:8501 |
| E-commerce Dashboard | 8502 | http://localhost:8502 |
| Financial Dashboard  | 8503 | http://localhost:8503 |
| Healthcare Dashboard | 8504 | http://localhost:8504 |
| HR Dashboard         | 8505 | http://localhost:8505 |
| Restaurant Dashboard | 8506 | http://localhost:8506 |
| PostgreSQL           | 5432 | localhost:5432        |

---

## Quick Full Stack Start

```bash
# 1. Start Database
docker run -d --name portfolio-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:13

# 2. Start All APIs (in separate terminals)
uvicorn fraud.api.app:app --port 8001 &
uvicorn ecommerce.api.app:app --port 8002 &
uvicorn financial.api.app:app --port 8003 &
uvicorn healthcare.api.app:app --port 8004 &
uvicorn hr.api.app:app --port 8005 &
uvicorn restaurant.api.app:app --port 8006 &

# 3. Start Airflow
airflow webserver --port 8080 &
airflow scheduler &

# 4. Verify Everything
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
```

---

**For detailed documentation, see:**

- `FINAL_PRODUCTION_REPORT.md` - Complete production report
- `PRODUCTION_UPGRADE_COMPLETE.md` - Upgrade summary
- Individual project `README.md` files
