"""Database models for the platform."""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Service(Base):
    """Service model representing a deployed application."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    repository_url = Column(String, nullable=False)
    repository_branch = Column(String, default="main")

    # Service type flags
    has_frontend = Column(Boolean, default=False)
    has_backend = Column(Boolean, default=False)
    has_database = Column(Boolean, default=False)

    # Framework detection
    frontend_framework = Column(String, nullable=True)
    backend_framework = Column(String, nullable=True)
    database_type = Column(String, nullable=True)

    # Deployment URLs
    frontend_url = Column(String, nullable=True)
    backend_url = Column(String, nullable=True)

    # Status
    status = Column(String, default="pending")  # pending, deploying, running, failed, stopped

    # Cost
    estimated_monthly_cost = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_deployed_at = Column(DateTime, nullable=True)

    # Relationships
    deployments = relationship("Deployment", back_populates="service", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="service", cascade="all, delete-orphan")


class Deployment(Base):
    """Deployment history for services."""

    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Deployment info
    commit_sha = Column(String, nullable=True)
    commit_message = Column(Text, nullable=True)
    deployed_by = Column(String, default="system")

    # Status
    status = Column(String, default="pending")  # pending, in_progress, success, failed, rolled_back
    error_message = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    service = relationship("Service", back_populates="deployments")


class Log(Base):
    """Log entries for services."""

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Log info
    level = Column(String, default="info")  # debug, info, warning, error, critical
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True)  # frontend, backend, deployment, system

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    service = relationship("Service", back_populates="logs")
