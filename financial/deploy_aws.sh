#!/bin/bash
# AWS Deployment Script for Financial Analysis App

echo "🚀 Deploying Financial Analysis App to AWS..."

# Build Docker image
docker build -t financial-analysis-app .

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag financial-analysis-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/financial-analysis-app:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/financial-analysis-app:latest

# Update ECS service
aws ecs update-service --cluster financial-cluster --service financial-service --force-new-deployment
echo "✅ Deployment completed!"