# Management Platform

This folder contains the **optional** web-based management dashboard for monitoring and managing deployed services.

## Overview

The Management Platform provides a visual interface to:
- View all deployed services
- Monitor deployment status
- Track AWS costs
- View logs
- Manage service lifecycle

## Components

### Backend API (`platform/api/`)
- **FastAPI** REST API (port 8080)
- **PostgreSQL** database for tracking services
- Endpoints for services, deployments, costs, and logs

### Frontend Dashboard (`platform/frontend/`)
- **React + TypeScript** web application (port 3000)
- Real-time service monitoring
- Cost tracking and visualization
- Service management interface

## When to Use

The Management Platform is **optional** and recommended for:
- ✅ Managing multiple deployed services
- ✅ Team collaboration and visibility
- ✅ Cost monitoring and optimization
- ✅ Visual service management

**You don't need it to use the CLI!** The core deployment functionality works without the platform.

## Setup

### Backend
```powershell
# Start PostgreSQL
docker-compose up postgres -d

# Navigate to API folder
cd "Management Platform\platform\api"

# Run API server
uvicorn main:app --reload --port 8080
```

### Frontend
```powershell
# Navigate to frontend folder
cd "Management Platform\platform\frontend"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Access dashboard at: http://localhost:3000

## Quick Start with Docker

Uncomment the `platform` service in the root `docker-compose.yml` and run:
```powershell
docker-compose up platform
```

## Architecture

```
Management Platform/
├── platform/
│   ├── api/              # FastAPI backend
│   │   ├── main.py       # API endpoints
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── database.py   # DB connection
│   │
│   └── frontend/         # React frontend
│       ├── src/
│       │   ├── App.tsx           # Main app
│       │   ├── pages/            # Dashboard, Services, Costs, Settings
│       │   └── main.tsx          # Entry point
│       ├── package.json
│       └── vite.config.ts
│
└── docker/               # Docker configs (if needed)
```

## API Endpoints

```
GET  /api/services              # List all services
POST /api/services              # Create service
GET  /api/services/{id}         # Get service details
PUT  /api/services/{id}         # Update service
DELETE /api/services/{id}       # Delete service

GET  /api/deployments           # List deployments
GET  /api/costs/summary         # Cost overview
GET  /api/costs/{service_id}    # Service cost breakdown
```

## Development

The Management Platform is **decoupled** from core CLI functionality. You can:
- Build CLI features without touching this folder
- Deploy services without running the platform
- Add the platform later for monitoring

Focus on the core deployment logic first, then enhance with the visual dashboard when needed!
