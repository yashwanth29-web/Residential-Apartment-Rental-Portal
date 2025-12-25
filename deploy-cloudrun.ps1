# Deployment script for GCP Cloud Run (PowerShell)
# Usage: .\deploy-cloudrun.ps1 -ProjectId "your-project-id" -Region "us-central1"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseUrl = $env:DATABASE_URL,
    
    [Parameter(Mandatory=$false)]
    [string]$JwtSecretKey = $env:JWT_SECRET_KEY
)

$ErrorActionPreference = "Stop"

$BackendService = "apartment-backend"
$FrontendService = "apartment-frontend"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploying Apartment Rental Portal to GCP Cloud Run" -ForegroundColor Cyan
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "Error: gcloud CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Validate environment variables
if (-not $DatabaseUrl) {
    Write-Host "Error: DATABASE_URL is required." -ForegroundColor Red
    Write-Host "Set it as environment variable: `$env:DATABASE_URL = 'postgresql+psycopg://...'" -ForegroundColor Yellow
    Write-Host "Or pass -DatabaseUrl parameter" -ForegroundColor Yellow
    exit 1
}

if (-not $JwtSecretKey) {
    $JwtSecretKey = "super-secret-jwt-key-change-in-production"
    Write-Host "Warning: Using default JWT_SECRET_KEY. Set a secure key for production!" -ForegroundColor Yellow
}

# Set project
Write-Host "`nSetting GCP project..." -ForegroundColor Green
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "`nEnabling required GCP APIs..." -ForegroundColor Green
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Configure Docker for GCR
Write-Host "`nConfiguring Docker for GCR..." -ForegroundColor Green
gcloud auth configure-docker --quiet

# Build and push backend image
Write-Host "`nBuilding backend image..." -ForegroundColor Green
Push-Location backend
docker build -t "gcr.io/$ProjectId/${BackendService}:latest" -f Dockerfile.cloudrun .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Backend build failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "Pushing backend image to GCR..." -ForegroundColor Green
docker push "gcr.io/$ProjectId/${BackendService}:latest"
Pop-Location

# Deploy backend to Cloud Run
Write-Host "`nDeploying backend to Cloud Run..." -ForegroundColor Green
gcloud run deploy $BackendService `
    --image "gcr.io/$ProjectId/${BackendService}:latest" `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "DATABASE_URL=$DatabaseUrl,JWT_SECRET_KEY=$JwtSecretKey,FLASK_ENV=production" `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --timeout 300

# Get backend URL
$BackendUrl = gcloud run services describe $BackendService --region=$Region --format='value(status.url)'
Write-Host "Backend deployed at: $BackendUrl" -ForegroundColor Green

# Build and push frontend image
Write-Host "`nBuilding frontend image..." -ForegroundColor Green
Push-Location frontend
docker build -t "gcr.io/$ProjectId/${FrontendService}:latest" -f Dockerfile.cloudrun .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Frontend build failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "Pushing frontend image to GCR..." -ForegroundColor Green
docker push "gcr.io/$ProjectId/${FrontendService}:latest"
Pop-Location

# Deploy frontend to Cloud Run
Write-Host "`nDeploying frontend to Cloud Run..." -ForegroundColor Green
gcloud run deploy $FrontendService `
    --image "gcr.io/$ProjectId/${FrontendService}:latest" `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "BACKEND_URL=$BackendUrl" `
    --memory 256Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10

# Get frontend URL
$FrontendUrl = gcloud run services describe $FrontendService --region=$Region --format='value(status.url)'

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor Yellow
Write-Host "Backend URL:  $BackendUrl" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nDemo Credentials:" -ForegroundColor White
Write-Host "  Admin: admin@example.com / admin123" -ForegroundColor Gray
Write-Host "  User:  user@example.com / user123" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
