"""Platform API main application."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Deployer API",
    description="API for managing deployed services",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Service Deployer API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Service endpoints
@app.get("/api/services", response_model=List[schemas.ServiceResponse])
async def list_services(db: Session = Depends(get_db)):
    """List all deployed services."""
    services = db.query(models.Service).all()
    return services


@app.get("/api/services/{service_id}", response_model=schemas.ServiceResponse)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get a specific service by ID."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.post("/api/services", response_model=schemas.ServiceResponse)
async def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    """Create a new service deployment."""
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@app.put("/api/services/{service_id}", response_model=schemas.ServiceResponse)
async def update_service(
    service_id: int, service: schemas.ServiceUpdate, db: Session = Depends(get_db)
):
    """Update a service."""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    for key, value in service.dict(exclude_unset=True).items():
        setattr(db_service, key, value)

    db.commit()
    db.refresh(db_service)
    return db_service


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Delete a service."""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(db_service)
    db.commit()
    return {"message": "Service deleted successfully"}


# Deployment endpoints
@app.get("/api/deployments", response_model=List[schemas.DeploymentResponse])
async def list_deployments(db: Session = Depends(get_db)):
    """List all deployments."""
    deployments = db.query(models.Deployment).all()
    return deployments


@app.get("/api/services/{service_id}/deployments", response_model=List[schemas.DeploymentResponse])
async def list_service_deployments(service_id: int, db: Session = Depends(get_db)):
    """List deployments for a specific service."""
    deployments = (
        db.query(models.Deployment).filter(models.Deployment.service_id == service_id).all()
    )
    return deployments


@app.post("/api/deployments", response_model=schemas.DeploymentResponse)
async def create_deployment(
    deployment: schemas.DeploymentCreate, db: Session = Depends(get_db)
):
    """Create a new deployment record."""
    db_deployment = models.Deployment(**deployment.dict())
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    return db_deployment


# Cost endpoints
@app.get("/api/costs/summary")
async def get_cost_summary(db: Session = Depends(get_db)):
    """Get cost summary for all services."""
    services = db.query(models.Service).all()

    total_monthly = sum(service.estimated_monthly_cost or 0 for service in services)

    return {
        "total_monthly_cost": round(total_monthly, 2),
        "currency": "USD",
        "num_services": len(services),
        "services": [
            {
                "name": service.name,
                "monthly_cost": service.estimated_monthly_cost,
                "status": service.status,
            }
            for service in services
        ],
    }


@app.get("/api/costs/{service_id}")
async def get_service_costs(service_id: int, db: Session = Depends(get_db)):
    """Get detailed cost breakdown for a service."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Calculate cost breakdown
    # This is a simplified version - in production, integrate with AWS Cost Explorer API
    ec2_cost = 30.37  # Base EC2 cost
    rds_cost = 15.0 if service.has_database else 0
    data_transfer = 5.0

    return {
        "service_name": service.name,
        "breakdown": {
            "ec2": ec2_cost,
            "rds": rds_cost,
            "data_transfer": data_transfer,
            "total": ec2_cost + rds_cost + data_transfer,
        },
        "currency": "USD",
        "period": "monthly",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
