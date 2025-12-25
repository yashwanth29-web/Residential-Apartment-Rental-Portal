# Residential Apartment Rental Portal

A full-stack web application for residential apartment rental management. Users can browse available flats, view amenities, and request bookings. Administrators can manage towers, units, amenities, approve/decline bookings, manage tenants, and view occupancy reports.

## Tech Stack

- **Frontend**: Angular 20 with Tailwind CSS
- **Backend**: Python Flask REST API
- **Database**: Neon PostgreSQL
- **Containerization**: Docker & Docker Compose

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
