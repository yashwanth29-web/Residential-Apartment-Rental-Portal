# Residential Apartment Rental Portal

A full-stack web application for residential apartment rental management. Users can browse available flats, view amenities, and request bookings. Administrators can manage towers, units, amenities, approve/decline bookings, manage tenants, and view occupancy reports.

## Tech Stack

- **Frontend**: Angular 20 with Tailwind CSS
- **Backend**: Python Flask REST API
- **Database**: Neon PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Cloud Deployment**: Google Cloud Run

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [Neon PostgreSQL](https://neon.tech/) account (free tier available)

### For Local Development (Optional)

- [Node.js](https://nodejs.org/) (v20+)
- [Python](https://www.python.org/) (v3.11+)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd apartment-rental-portal
```

### 2. Configure Environment Variables

Copy the example environment file and update with your Neon PostgreSQL connection string:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
# Neon PostgreSQL Database Connection
DATABASE_URL=postgresql://username:password@host.neon.tech:5432/database?sslmode=require

# JWT Secret Key - Change this in production!
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
```

### 3. Start the Application

```bash
docker-compose up --build
```

This will:
- Build the Angular frontend and serve it via nginx on port 80
- Build the Flask backend and run it on port 5000
- Run database migrations automatically
- Seed the database with demo data

### 4. Access the Application

- **User Portal**: http://localhost
- **API**: http://localhost:5000/api

## Demo Credentials

| Role  | Email               | Password  |
|-------|---------------------|-----------|
| Admin | admin@example.com   | admin123  |
| User  | user@example.com    | user123   |

## Docker Commands

### Start Services
```bash
docker-compose up
```

### Start Services (Detached Mode)
```bash
docker-compose up -d
```

### Rebuild and Start
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart a Service
```bash
docker-compose restart backend
```

## Project Structure

```
apartment-rental-portal/
├── frontend/                 # Angular 20 application
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/        # Auth service, guards, interceptors
│   │   │   ├── features/    # Feature modules (auth, flats, bookings, admin)
│   │   │   └── shared/      # Shared components
│   │   └── environments/
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                  # Flask REST API
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── seed.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Flats (User)
- `GET /api/flats` - List available flats (supports filters)
- `GET /api/flats/:id` - Get flat details

### Amenities (User)
- `GET /api/amenities` - List all amenities
- `GET /api/amenities/:id` - Get amenity details

### Bookings (User)
- `POST /api/bookings` - Create booking request
- `GET /api/bookings` - Get user's bookings
- `GET /api/bookings/:id` - Get booking details

### Admin Endpoints
- `GET/POST/PUT/DELETE /api/admin/towers` - Tower management
- `GET/POST/PUT/DELETE /api/admin/flats` - Flat management
- `GET/POST/PUT/DELETE /api/admin/amenities` - Amenity management
- `GET /api/admin/bookings` - List all bookings
- `PUT /api/admin/bookings/:id/approve` - Approve booking
- `PUT /api/admin/bookings/:id/decline` - Decline booking
- `GET /api/admin/tenants` - List tenants
- `DELETE /api/admin/leases/:id` - Terminate lease
- `GET /api/admin/reports/occupancy` - Occupancy report
- `GET /api/admin/reports/bookings` - Booking report

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database URL

# Run the application
python run.py
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
ng serve
```

The frontend dev server runs on http://localhost:4200

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
ng test
```

## Troubleshooting

### Database Connection Issues

1. Verify your Neon PostgreSQL connection string is correct
2. Ensure the database exists and is accessible
3. Check that SSL mode is enabled (`?sslmode=require`)

### Port Conflicts

If ports 80 or 5000 are in use, modify `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change 80 to 8080
  backend:
    ports:
      - "5001:5000"  # Change 5000 to 5001
```

### Container Build Failures

```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

## License

MIT License

---

## GCP Cloud Run Deployment

### Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. A GCP project with billing enabled
3. Docker installed locally

### Quick Deploy

#### Windows (PowerShell)

```powershell
# Set environment variables
$env:DATABASE_URL = "postgresql+psycopg://user:pass@host/db?sslmode=require"
$env:JWT_SECRET_KEY = "your-production-secret-key"

# Deploy
.\deploy-cloudrun.ps1 -ProjectId "your-gcp-project-id" -Region "us-central1"
```

#### Linux/Mac (Bash)

```bash
# Set environment variables
export DATABASE_URL="postgresql+psycopg://user:pass@host/db?sslmode=require"
export JWT_SECRET_KEY="your-production-secret-key"

# Make script executable and deploy
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh your-gcp-project-id us-central1
```

### Manual Deployment Steps

#### 1. Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### 3. Configure Docker for GCR

```bash
gcloud auth configure-docker
```

#### 4. Build and Push Backend

```bash
cd backend
docker build -t gcr.io/YOUR_PROJECT_ID/apartment-backend:latest -f Dockerfile.cloudrun .
docker push gcr.io/YOUR_PROJECT_ID/apartment-backend:latest
```

#### 5. Deploy Backend to Cloud Run

```bash
gcloud run deploy apartment-backend \
    --image gcr.io/YOUR_PROJECT_ID/apartment-backend:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=YOUR_DATABASE_URL,JWT_SECRET_KEY=YOUR_SECRET" \
    --memory 512Mi
```

#### 6. Get Backend URL

```bash
BACKEND_URL=$(gcloud run services describe apartment-backend --region=us-central1 --format='value(status.url)')
echo $BACKEND_URL
```

#### 7. Build and Push Frontend

```bash
cd frontend
docker build -t gcr.io/YOUR_PROJECT_ID/apartment-frontend:latest -f Dockerfile.cloudrun .
docker push gcr.io/YOUR_PROJECT_ID/apartment-frontend:latest
```

#### 8. Deploy Frontend to Cloud Run

```bash
gcloud run deploy apartment-frontend \
    --image gcr.io/YOUR_PROJECT_ID/apartment-frontend:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "BACKEND_URL=$BACKEND_URL" \
    --memory 256Mi
```

### CI/CD with Cloud Build

The project includes a `cloudbuild.yaml` for automated deployments:

```bash
# Trigger a build manually
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_DATABASE_URL="your-db-url",_JWT_SECRET_KEY="your-secret"
```

### Cloud Run Configuration Files

| File | Description |
|------|-------------|
| `backend/Dockerfile.cloudrun` | Backend Dockerfile optimized for Cloud Run |
| `frontend/Dockerfile.cloudrun` | Frontend Dockerfile optimized for Cloud Run |
| `frontend/nginx.cloudrun.conf` | Nginx config with dynamic backend URL |
| `cloudbuild.yaml` | Cloud Build CI/CD configuration |
| `deploy-cloudrun.sh` | Bash deployment script |
| `deploy-cloudrun.ps1` | PowerShell deployment script |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (use `postgresql+psycopg://` prefix) | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Yes |
| `BACKEND_URL` | Backend service URL (auto-set for frontend) | Auto |

### Cost Optimization

Cloud Run charges only for actual usage. To minimize costs:

- `min-instances: 0` - Scale to zero when not in use
- `max-instances: 10` - Limit maximum instances
- Use appropriate memory settings (512Mi backend, 256Mi frontend)
