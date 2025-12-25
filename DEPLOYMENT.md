# GCP Cloud Run Deployment Guide

This guide provides step-by-step instructions to deploy the Apartment Rental Portal to Google Cloud Run.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GCP Project Setup](#gcp-project-setup)
3. [Local Environment Setup](#local-environment-setup)
4. [Deployment Options](#deployment-options)
   - [Option A: Automated Script Deployment](#option-a-automated-script-deployment)
   - [Option B: Manual Step-by-Step Deployment](#option-b-manual-step-by-step-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Cost Management](#cost-management)

---

## Prerequisites

Before you begin, ensure you have the following:

### Required Tools

| Tool | Version | Download Link |
|------|---------|---------------|
| Google Cloud SDK | Latest | https://cloud.google.com/sdk/docs/install |
| Docker Desktop | 20.10+ | https://docs.docker.com/get-docker/ |
| Git | Latest | https://git-scm.com/downloads |

### Required Accounts

- **Google Cloud Platform Account** with billing enabled
- **Neon PostgreSQL Account** (or any PostgreSQL database) - https://neon.tech

### Required Information

Before deployment, gather the following:

```
GCP_PROJECT_ID     = your-gcp-project-id
DATABASE_URL       = postgresql+psycopg://user:password@host/database?sslmode=require
JWT_SECRET_KEY     = your-secure-secret-key (min 32 characters)
REGION             = us-central1 (or your preferred region)
```

---

## GCP Project Setup

### Step 1: Create a GCP Project (if needed)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., `apartment-rental-portal`)
5. Click "Create"
6. Note down your **Project ID** (not the project name)

### Step 2: Enable Billing

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Link a billing account to your project
3. Cloud Run has a generous free tier (2 million requests/month)

### Step 3: Enable Required APIs

Run these commands in your terminal:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Or enable via Console:
1. Go to [APIs & Services](https://console.cloud.google.com/apis/library)
2. Search and enable:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Artifact Registry API

---

## Local Environment Setup

### Step 1: Install Google Cloud SDK

**Windows:**
1. Download installer from https://cloud.google.com/sdk/docs/install
2. Run the installer
3. Open a new PowerShell window

**Mac:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2: Authenticate with GCP

```bash
# Login to your Google account
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Configure Docker to use GCP credentials
gcloud auth configure-docker
```

### Step 3: Verify Setup

```bash
# Check gcloud is configured
gcloud config list

# Check Docker is running
docker --version
```

---

## Deployment Options

### Option A: Automated Script Deployment

This is the easiest method using the provided deployment script.

#### Windows (PowerShell)

```powershell
# Step 1: Set environment variables
$env:DATABASE_URL = "postgresql+psycopg://neondb_owner:YOUR_PASSWORD@YOUR_HOST/neondb?sslmode=require"
$env:JWT_SECRET_KEY = "your-super-secure-jwt-secret-key-min-32-chars"

# Step 2: Run the deployment script
.\deploy-cloudrun.ps1 -ProjectId "your-gcp-project-id" -Region "us-central1"
```

#### Linux/Mac (Bash)

```bash
# Step 1: Set environment variables
export DATABASE_URL="postgresql+psycopg://neondb_owner:YOUR_PASSWORD@YOUR_HOST/neondb?sslmode=require"
export JWT_SECRET_KEY="your-super-secure-jwt-secret-key-min-32-chars"

# Step 2: Make script executable and run
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh your-gcp-project-id us-central1
```

The script will:
1. ✅ Enable required GCP APIs
2. ✅ Build backend Docker image
3. ✅ Push backend image to Container Registry
4. ✅ Deploy backend to Cloud Run
5. ✅ Build frontend Docker image
6. ✅ Push frontend image to Container Registry
7. ✅ Deploy frontend to Cloud Run with backend URL configured
8. ✅ Output both service URLs

---

### Option B: Manual Step-by-Step Deployment

If you prefer manual control or the script fails, follow these steps:

#### Step 1: Set Environment Variables

**Windows PowerShell:**
```powershell
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$DATABASE_URL = "postgresql+psycopg://user:pass@host/db?sslmode=require"
$JWT_SECRET_KEY = "your-secure-secret-key"
```

**Linux/Mac:**
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export DATABASE_URL="postgresql+psycopg://user:pass@host/db?sslmode=require"
export JWT_SECRET_KEY="your-secure-secret-key"
```

#### Step 2: Configure GCP

```bash
gcloud config set project $PROJECT_ID
gcloud auth configure-docker
```

#### Step 3: Build Backend Docker Image

```bash
# Navigate to project root
docker build -t gcr.io/$PROJECT_ID/apartment-backend:latest -f backend/Dockerfile.cloudrun backend
```

#### Step 4: Push Backend Image to Container Registry

```bash
docker push gcr.io/$PROJECT_ID/apartment-backend:latest
```

#### Step 5: Deploy Backend to Cloud Run

```bash
gcloud run deploy apartment-backend \
    --image gcr.io/$PROJECT_ID/apartment-backend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=$DATABASE_URL,JWT_SECRET_KEY=$JWT_SECRET_KEY,FLASK_ENV=production" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300
```

#### Step 6: Get Backend URL

```bash
# Get the backend service URL
BACKEND_URL=$(gcloud run services describe apartment-backend --region=$REGION --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

**Save this URL** - you'll need it for the frontend deployment.

#### Step 7: Build Frontend Docker Image

```bash
docker build -t gcr.io/$PROJECT_ID/apartment-frontend:latest -f frontend/Dockerfile.cloudrun frontend
```

#### Step 8: Push Frontend Image to Container Registry

```bash
docker push gcr.io/$PROJECT_ID/apartment-frontend:latest
```

#### Step 9: Deploy Frontend to Cloud Run

```bash
gcloud run deploy apartment-frontend \
    --image gcr.io/$PROJECT_ID/apartment-frontend:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "BACKEND_URL=$BACKEND_URL" \
    --memory 256Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10
```

#### Step 10: Get Frontend URL

```bash
FRONTEND_URL=$(gcloud run services describe apartment-frontend --region=$REGION --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

---

## Post-Deployment Verification

### Step 1: Test Backend API

```bash
# Test the API health
curl $BACKEND_URL/api/towers

# Expected: JSON array of towers
```

### Step 2: Test Frontend

1. Open the Frontend URL in your browser
2. You should see the login page
3. Try logging in with demo credentials:
   - **Admin:** admin@example.com / admin123
   - **User:** user@example.com / user123

### Step 3: Verify Database Connection

```bash
# Check backend logs
gcloud run services logs read apartment-backend --region=$REGION --limit=50
```

Look for:
- "Running database migrations..."
- "Starting gunicorn server..."

---

## Troubleshooting

### Common Issues

#### Issue: "Permission denied" when pushing to GCR

```bash
# Re-authenticate Docker with GCP
gcloud auth configure-docker --quiet
```

#### Issue: Backend fails to start

Check logs:
```bash
gcloud run services logs read apartment-backend --region=$REGION --limit=100
```

Common causes:
- Invalid DATABASE_URL format (must use `postgresql+psycopg://`)
- Database not accessible from Cloud Run
- Missing environment variables

#### Issue: Frontend can't connect to backend

1. Verify BACKEND_URL is set correctly:
```bash
gcloud run services describe apartment-frontend --region=$REGION --format='value(spec.template.spec.containers[0].env)'
```

2. Check if backend is running:
```bash
gcloud run services describe apartment-backend --region=$REGION --format='value(status.conditions)'
```

#### Issue: Database connection timeout

Ensure your database allows connections from Cloud Run:
- For Neon: Connections are allowed by default
- For Cloud SQL: Enable Cloud Run connection or use public IP with SSL

#### Issue: "Container failed to start"

```bash
# Check detailed logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apartment-backend" --limit=50
```

### Useful Commands

```bash
# List all Cloud Run services
gcloud run services list

# Get service details
gcloud run services describe apartment-backend --region=$REGION

# View logs in real-time
gcloud run services logs tail apartment-backend --region=$REGION

# Delete a service
gcloud run services delete apartment-backend --region=$REGION

# Update environment variables
gcloud run services update apartment-backend \
    --region=$REGION \
    --set-env-vars "NEW_VAR=value"
```

---

## Cost Management

### Cloud Run Pricing

Cloud Run charges based on:
- **CPU time:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GiB-second
- **Requests:** $0.40 per million requests

### Free Tier (Monthly)

- 2 million requests
- 360,000 GiB-seconds of memory
- 180,000 vCPU-seconds of compute time

### Cost Optimization Tips

1. **Set min-instances to 0** (already configured)
   - Services scale to zero when not in use
   - No charges when idle

2. **Use appropriate memory settings**
   - Backend: 512Mi (sufficient for Flask + gunicorn)
   - Frontend: 256Mi (nginx serving static files)

3. **Set max-instances limit**
   - Prevents unexpected scaling costs
   - Currently set to 10 for both services

4. **Monitor usage**
   ```bash
   # View billing report
   gcloud billing accounts list
   ```

### Estimated Monthly Cost

For a low-traffic application:
- **Free tier:** $0/month
- **Light usage (10k requests/day):** ~$5-10/month
- **Medium usage (100k requests/day):** ~$20-50/month

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                      │
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │   Cloud Run     │         │   Cloud Run     │            │
│  │   (Frontend)    │────────▶│   (Backend)     │            │
│  │   Angular+Nginx │         │   Flask+Gunicorn│            │
│  │   Port 8080     │         │   Port 8080     │            │
│  └────────┬────────┘         └────────┬────────┘            │
│           │                           │                      │
│           │                           │                      │
└───────────┼───────────────────────────┼──────────────────────┘
            │                           │
            │                           ▼
            │                  ┌─────────────────┐
            │                  │  Neon PostgreSQL │
            │                  │  (External DB)   │
            │                  └─────────────────┘
            │
            ▼
      ┌───────────┐
      │  Browser  │
      │  (Users)  │
      └───────────┘
```

---

## Quick Reference

### Service URLs (after deployment)

| Service | URL Pattern |
|---------|-------------|
| Frontend | `https://apartment-frontend-XXXXX-uc.a.run.app` |
| Backend | `https://apartment-backend-XXXXX-uc.a.run.app` |

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| User | user@example.com | user123 |

### Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| DATABASE_URL | Backend | PostgreSQL connection string |
| JWT_SECRET_KEY | Backend | Secret for JWT tokens |
| FLASK_ENV | Backend | Set to "production" |
| BACKEND_URL | Frontend | Backend service URL |

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Cloud Run logs in GCP Console
3. Verify all environment variables are set correctly
4. Ensure database is accessible from Cloud Run

