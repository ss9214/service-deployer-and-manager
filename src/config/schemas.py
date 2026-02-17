"""Configuration schemas and models using Pydantic."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, SecretStr


class ServiceType(str, Enum):
    """Types of services that can be deployed."""

    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    FULLSTACK = "fullstack"


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


class AWSConfig(BaseModel):
    """AWS configuration and credentials."""

    access_key_id: SecretStr
    secret_access_key: SecretStr
    region: str = "us-east-1"
    ec2_key_pair_name: Optional[str] = None
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None


class VercelConfig(BaseModel):
    """Vercel configuration and credentials."""

    api_token: SecretStr
    team_id: Optional[str] = None
    org_id: Optional[str] = None


class GitHubConfig(BaseModel):
    """GitHub configuration and credentials."""

    personal_access_token: SecretStr
    username: str


class DomainConfig(BaseModel):
    """Domain and DNS configuration."""

    root_domain: Optional[str] = None
    use_custom_domain: bool = False
    ssl_enabled: bool = True


class UserConfig(BaseModel):
    """Complete user configuration for the platform."""

    aws: AWSConfig
    vercel: VercelConfig
    github: GitHubConfig
    domain: DomainConfig = Field(default_factory=DomainConfig)
    platform_name: str = "My Deployment Platform"
    platform_port: int = 3000


class RepositoryMetadata(BaseModel):
    """Metadata about a repository to be deployed."""

    url: HttpUrl
    name: str
    owner: str
    branch: str = "main"
    has_frontend: bool
    has_backend: bool
    needs_database: bool
    detected_frontend_framework: Optional[str] = None
    detected_backend_framework: Optional[str] = None
    detected_database_type: Optional[DatabaseType] = None
    build_command_frontend: Optional[str] = None
    build_command_backend: Optional[str] = None
    install_command: Optional[str] = None


class DatabaseConfig(BaseModel):
    """Database configuration for deployment."""

    type: DatabaseType
    instance_class: str = "db.t3.micro"
    allocated_storage: int = 20
    database_name: str
    username: str
    password: SecretStr
    port: int = 5432


class BackendDeploymentConfig(BaseModel):
    """Backend deployment configuration."""

    replicas: int = 2
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    environment_variables: dict[str, str] = Field(default_factory=dict)
    port: int = 8000


class FrontendDeploymentConfig(BaseModel):
    """Frontend deployment configuration for Vercel."""

    framework: Optional[str] = None
    build_command: Optional[str] = None
    output_directory: Optional[str] = None
    install_command: Optional[str] = None
    environment_variables: dict[str, str] = Field(default_factory=dict)


class DeploymentConfig(BaseModel):
    """Complete deployment configuration for a service."""

    service_name: str
    repository: RepositoryMetadata
    backend: Optional[BackendDeploymentConfig] = None
    frontend: Optional[FrontendDeploymentConfig] = None
    database: Optional[DatabaseConfig] = None
    enable_monitoring: bool = True
    enable_logging: bool = True
    auto_ssl: bool = True


class InfrastructureState(BaseModel):
    """Current state of provisioned infrastructure."""

    vpc_id: Optional[str] = None
    subnet_ids: list[str] = Field(default_factory=list)
    ec2_instance_id: Optional[str] = None
    ec2_public_ip: Optional[str] = None
    k8s_cluster_endpoint: Optional[str] = None
    argocd_url: Optional[str] = None
    argocd_admin_password: Optional[SecretStr] = None
    rds_endpoints: dict[str, str] = Field(default_factory=dict)
    setup_complete: bool = False


class CostEstimate(BaseModel):
    """AWS cost estimation for a deployment."""

    ec2_monthly: float
    rds_monthly: float
    data_transfer_monthly: float
    total_monthly: float
    currency: str = "USD"
    notes: list[str] = Field(default_factory=list)
