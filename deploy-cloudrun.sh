#!/bin/bash
# Deployment script for GCP Cloud Run
# Usage: ./deploy-cloudrun.sh <PROJECT_ID> <REGION>

set -e

# Configuration
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}
BACKEND_SERVICE="apartment-backend"
FRONTEND_SERVICE="apartment-frontend"

echo "=========================================="
echo "Deploying Apartment Rental Portal to GCP Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push backend image
echo ""
echo "Building backend image..."
cd backend
docker build -t gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest -f Dockerfile.cloudrun .
docker push gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest
cd ..

# Deploy backend to Cloud Run
echo ""
echo "Deploying backend to Cloud Run..."
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=$DATABASE_URL,JWT_SECRET_KEY=$JWT_SECRET_KEY" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Backend deployed at: $BACKEND_URL"

# Build and push frontend image
echo ""
echo "Building frontend image..."
cd frontend
docker build -t gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest -f Dockerfile.cloudrun .
docker push gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest
cd ..

# Deploy frontend to Cloud Run
echo ""
echo "Deploying frontend to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "BACKEND_URL=$BACKEND_URL" \
    --memory 256Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo "=========================================="
