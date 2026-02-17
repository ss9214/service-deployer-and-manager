"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


# Service schemas
class ServiceBase(BaseModel):
    """Base service schema."""

    name: str
    repository_url: str
    repository_branch: str = "main"
    has_frontend: bool = False
    has_backend: bool = False
    has_database: bool = False
    frontend_framework: Optional[str] = None
    backend_framework: Optional[str] = None
    database_type: Optional[str] = None


class ServiceCreate(ServiceBase):
    """Schema for creating a service."""

    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service."""

    repository_branch: Optional[str] = None
    status: Optional[str] = None
    frontend_url: Optional[str] = None
    backend_url: Optional[str] = None
    estimated_monthly_cost: Optional[float] = None
    last_deployed_at: Optional[datetime] = None


class ServiceResponse(ServiceBase):
    """Schema for service responses."""

    id: int
    frontend_url: Optional[str] = None
    backend_url: Optional[str] = None
    status: str
    estimated_monthly_cost: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    last_deployed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Deployment schemas
class DeploymentBase(BaseModel):
    """Base deployment schema."""

    service_id: int
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    deployed_by: str = "system"


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment."""

    pass


class DeploymentResponse(DeploymentBase):
    """Schema for deployment responses."""

    id: int
    status: str
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Log schemas
class LogBase(BaseModel):
    """Base log schema."""

    service_id: int
    level: str = "info"
    message: str
    source: Optional[str] = None


class LogCreate(LogBase):
    """Schema for creating a log entry."""

    pass


class LogResponse(LogBase):
    """Schema for log responses."""

    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
