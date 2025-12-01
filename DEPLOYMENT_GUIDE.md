# 🚀 Deployment Guide - Data Engineering Portfolio

Complete guide to deploy your portfolio for showcase purposes.

---

## 📋 Table of Contents

1. [Local Deployment](#local-deployment)
2. [Cloud Deployment Options](#cloud-deployment-options)
3. [Heroku Deployment](#heroku-deployment)
4. [AWS Deployment](#aws-deployment)
5. [DigitalOcean Deployment](#digitalocean-deployment)
6. [Google Cloud Deployment](#google-cloud-deployment)
7. [Render Deployment](#render-deployment-easiest)
8. [Railway Deployment](#railway-deployment)

---

## 🏠 Local Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Access APIs
- Main Dashboard: http://localhost
- Fraud API: http://localhost/api/fraud/docs
- E-commerce API: http://localhost/api/ecommerce/docs
- Financial API: http://localhost/api/financial/docs
- Healthcare API: http://localhost/api/healthcare/docs
- HR API: http://localhost/api/hr/docs
- Restaurant API: http://localhost/api/restaurant/docs

# Stop services
docker-compose down
```

### Manual Local Deployment

```bash
# Terminal 1 - Database
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:13

# Terminal 2 - Fraud API
uvicorn fraud.api.app:app --host 0.0.0.0 --port 8001

# Terminal 3 - E-commerce API
uvicorn ecommerce.api.app:app --host 0.0.0.0 --port 8002

# Terminal 4 - Financial API
uvicorn financial.api.app:app --host 0.0.0.0 --port 8003

# Terminal 5 - Healthcare API
uvicorn healthcare.api.app:app --host 0.0.0.0 --port 8004

# Terminal 6 - HR API
uvicorn hr.api.app:app --host 0.0.0.0 --port 8005

# Terminal 7 - Restaurant API
uvicorn restaurant.api.app:app --host 0.0.0.0 --port 8006
```

---

## ☁️ Cloud Deployment Options

### Option 1: Render (Easiest - FREE Tier) ⭐

**Best for:** Quick showcase deployment with minimal configuration

#### Step 1: Prepare Blueprint

Create `render.yaml`:

```yaml
services:
  # Fraud Detection API
  - type: web
    name: fraud-api
    env: docker
    dockerfilePath: ./fraud/Dockerfile
    envVars:
      - key: PORT
        value: 8001
      - key: DATABASE_URL
        fromDatabase:
          name: portfolio-db
          property: connectionString

  # E-commerce API
  - type: web
    name: ecommerce-api
    env: docker
    dockerfilePath: ./ecommerce/Dockerfile
    envVars:
      - key: PORT
        value: 8002

  # Add other services similarly...

databases:
  - name: portfolio-db
    databaseName: portfolio
    user: portfolio_user
```

#### Step 2: Deploy

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

**URL:** `https://your-app.onrender.com`

---

### Option 2: Railway (Easy - FREE $5/month credit) ⭐

**Best for:** Simple deployment with great UX

#### Deploy via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add PostgreSQL
railway add postgresql

# Open deployment
railway open
```

#### Deploy via GitHub

1. Connect repository to Railway
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically on push

**URL:** `https://your-app.railway.app`

---

### Option 3: Heroku (Easy - FREE Tier Available)

**Best for:** Traditional PaaS deployment

#### Step 1: Create Procfile

```
web: uvicorn fraud.api.app:app --host 0.0.0.0 --port $PORT
```

#### Step 2: Deploy

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create apps for each service
heroku create portfolio-fraud-api
heroku create portfolio-ecommerce-api
heroku create portfolio-financial-api
heroku create portfolio-healthcare-api
heroku create portfolio-hr-api
heroku create portfolio-restaurant-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev --app portfolio-fraud-api

# Deploy fraud API
git subtree push --prefix fraud heroku-fraud main

# Deploy others similarly
```

**URL:** `https://your-app.herokuapp.com`

---

### Option 4: AWS Deployment (Advanced)

**Best for:** Production-grade deployment with full control

#### Using AWS ECS + Fargate

```bash
# Install AWS CLI
# Download from: https://aws.amazon.com/cli/

# Configure AWS
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name fraud-api
aws ecr create-repository --repository-name ecommerce-api
# ... create for all services

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push images
docker build -t fraud-api:latest -f fraud/Dockerfile .
docker tag fraud-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/fraud-api:latest

# Create ECS cluster
aws ecs create-cluster --cluster-name portfolio-cluster

# Create task definitions and services
# Use AWS Console or CloudFormation templates
```

#### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker portfolio-fraud-api

# Create environment
eb create portfolio-fraud-env

# Deploy
eb deploy

# Open in browser
eb open
```

**Cost:** ~$20-50/month for minimal setup

---

### Option 5: DigitalOcean (Medium Difficulty)

**Best for:** Cost-effective cloud hosting

#### Using App Platform

1. **Connect GitHub:**

   - Go to DigitalOcean App Platform
   - Connect your GitHub repository

2. **Configure Services:**

   - Add each API as a service
   - Set Dockerfile paths
   - Configure environment variables

3. **Add Database:**

   - Add managed PostgreSQL database
   - Link to services

4. **Deploy:**
   - Click Deploy
   - Wait for build and deployment

**URL:** `https://your-app.ondigitalocean.app`

**Cost:** $5-12/month per service

---

### Option 6: Google Cloud Run (Serverless)

**Best for:** Pay-per-use serverless deployment

```bash
# Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy fraud API
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fraud-api fraud/
gcloud run deploy fraud-api --image gcr.io/YOUR_PROJECT_ID/fraud-api --platform managed --region us-central1 --allow-unauthenticated

# Deploy other services similarly
```

**Cost:** Pay only for usage, very cheap for demos

---

## 🎯 Recommended Deployment Strategy for Showcase

### Best Option: **Render + GitHub** (FREE)

**Why?**

- ✅ Completely FREE
- ✅ Auto-deploys from GitHub
- ✅ Easy setup (5 minutes)
- ✅ Professional URLs
- ✅ SSL included
- ✅ Good for portfolio showcase

### Quick Setup:

1. **Push to GitHub** (Already done! ✅)

2. **Create Render Account:**

   - Visit https://render.com
   - Sign up with GitHub

3. **Create New Web Service:**

   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select "Docker" as environment
   - Set Dockerfile path: `fraud/Dockerfile`
   - Click "Create Web Service"

4. **Repeat for other services:**

   - Create 5 more web services
   - Use respective Dockerfile paths

5. **Add Database:**

   - Click "New +" → "PostgreSQL"
   - Free tier available
   - Copy connection string to services

6. **Done!** Your APIs are live at:
   - `https://portfolio-fraud-api.onrender.com`
   - `https://portfolio-ecommerce-api.onrender.com`
   - etc.

---

## 📱 Alternative: Single Demo Page

If you want a simple showcase without deploying all services:

### Create GitHub Pages Demo

```bash
# Create demo branch
git checkout -b gh-pages

# Create index.html with portfolio showcase
# (See portfolio landing page template below)

# Push to GitHub
git push origin gh-pages

# Enable GitHub Pages in repository settings
```

**URL:** `https://vamegah.github.io/data-engineering`

---

## 🖥️ Portfolio Landing Page Template

Create a showcase page with:

- Project descriptions
- Architecture diagrams
- API documentation links
- GitHub repository link
- Demo video/screenshots
- Tech stack badges
- Contact information

I can help you create this if needed!

---

## 🔐 Security Considerations

### Before Deploying:

1. **Set Environment Variables:**

   ```bash
   # Don't commit real credentials
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-secret-key
   API_KEY=your-api-key
   ```

2. **Enable CORS Properly:**

   ```python
   # In FastAPI apps
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Add Rate Limiting:**

   ```python
   # Install: pip install slowapi
   from slowapi import Limiter

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

4. **Use HTTPS:**
   - All cloud platforms provide free SSL
   - Enable automatic HTTPS redirect

---

## 📊 Monitoring Your Deployment

### Health Checks

```bash
# Check all services
curl https://your-fraud-api.onrender.com/health
curl https://your-ecommerce-api.onrender.com/health
# ... check all services
```

### Uptime Monitoring (FREE)

- **UptimeRobot:** https://uptimerobot.com
- **Pingdom:** https://pingdom.com
- **StatusCake:** https://www.statuscake.com

### Analytics

Add to your showcase page:

- Google Analytics
- Plausible Analytics (privacy-friendly)

---

## 🎬 Next Steps After Deployment

1. **Update README with live URLs:**

   ```markdown
   ## 🌐 Live Demo

   - Fraud Detection API: https://portfolio-fraud-api.onrender.com/docs
   - E-commerce API: https://portfolio-ecommerce-api.onrender.com/docs
     ...
   ```

2. **Create Demo Video:**

   - Record API usage with Postman
   - Show dashboards
   - Explain architecture
   - Upload to YouTube

3. **Add to LinkedIn:**

   - Project showcase
   - Link to live demo
   - Add to experience section

4. **Add to Resume:**
   - "Deployed production-ready data engineering portfolio"
   - Include live demo URL
   - Highlight tech stack

---

## 💡 Tips for Showcase

1. **Keep it Running:**

   - Free tiers may sleep after inactivity
   - Use UptimeRobot to ping every 5 minutes
   - Or upgrade to paid tier ($7/month)

2. **Add Landing Page:**

   - Professional entry point
   - Link to all APIs
   - Explain projects
   - Show architecture diagram

3. **Documentation:**

   - Ensure all API docs are accessible
   - Add example requests/responses
   - Include Postman collection

4. **Monitoring:**
   - Set up error tracking (Sentry)
   - Monitor API usage
   - Track response times

---

## 🆘 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs fraud-api

# Rebuild
docker-compose build --no-cache fraud-api
docker-compose up -d fraud-api
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose ps

# Check connection string
docker-compose exec fraud-api env | grep DATABASE_URL
```

### Port Already in Use

```bash
# Find and kill process (Windows)
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

---

## 📞 Support

If you encounter issues:

1. Check service logs
2. Verify environment variables
3. Test locally first
4. Review cloud platform documentation
5. Check GitHub Issues

---

**Ready to showcase your amazing data engineering portfolio!** 🚀

Choose **Render** for the easiest free deployment, or **Railway** for a great developer experience.

Good luck with your showcase! 🎯
