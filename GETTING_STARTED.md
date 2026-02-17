# Getting Started Guide

## Overview

The Service Deployer and Manager is now set up with a complete foundation for automatically deploying web applications to AWS and Vercel.

## Project Structure

```
service-deployer-and-manager/
├── src/
│   ├── cli/                      # CLI commands (deploy, list, logs, etc.)
│   ├── config/                   # Configuration schemas and models
│   ├── analyzer/                 # Repository detection logic
│   ├── utils/                    # AWS cost estimator and utilities
│   └── platform/
│       ├── api/                  # FastAPI backend (port 8080)
│       └── frontend/             # React dashboard (port 3000)
├── terraform/
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Terraform variables
│   └── modules/
│       ├── vpc/                  # VPC and networking
│       ├── security/             # Security groups
│       ├── kubernetes/           # K3s cluster on EC2
│       ├── argocd/               # ArgoCD deployment
│       └── rds/                  # RDS database instances
├── docker/
│   └── setup/                    # Interactive setup container
├── docker-compose.yml            # Local development setup
├── pyproject.toml                # Python project configuration
└── requirements.txt              # Python dependencies
```

## Next Steps

### 1. Install Python Dependencies

```powershell
# Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

### 2. Run Initial Setup

The setup process will:
- Collect AWS, Vercel, and GitHub credentials
- Provision AWS infrastructure (VPC, EC2, K3s cluster)
- Install ArgoCD for GitOps deployments
- Deploy the management platform

```powershell
# Run the setup container
docker-compose up setup
```

This will take 15-20 minutes to complete.

### 3. Start the Management Platform

After setup completes, start the platform locally:

```powershell
# Start the backend API and database
docker-compose up platform

# In a separate terminal, start the frontend
cd src\platform\frontend
npm install
npm run dev
```

Access the dashboard at: http://localhost:3000

### 4. Deploy Your First Service

```powershell
# Deploy a web application
deployer deploy https://github.com/yourusername/your-webapp

# View deployed services
deployer list

# Check costs
deployer costs
```

## How It Works

### Repository Analysis

When you deploy a repository, the analyzer:
1. Clones the repository
2. Detects frontend framework (React, Next.js, Vue, etc.)
3. Detects backend framework (Node.js, Python, Go, etc.)
4. Identifies database requirements (PostgreSQL, MySQL, MongoDB)
5. Determines monorepo structure if applicable

### Deployment Flow

1. **Frontend** → Deployed to Vercel
   - Automatic framework detection
   - Build and deploy via Vercel API
   - Custom domain configuration (optional)

2. **Backend** → Deployed to AWS Kubernetes
   - Containerized using detected Dockerfile or generated template
   - Deployed via ArgoCD GitOps workflow
   - Exposed through nginx ingress controller

3. **Database** → AWS RDS
   - Provisioned using Terraform
   - Automatic connection configuration
   - Injected as environment variables

### Cost Estimation

Before deployment, the platform estimates monthly AWS costs:
- EC2 instance (K3s cluster): ~$30/month
- RDS database (if needed): ~$15/month per database
- Data transfer: ~$5/month
- Total: ~$50/month for a full-stack app

## CLI Commands Reference

### Deployment
```powershell
deployer deploy <github-url>              # Deploy repository
deployer deploy <url> --branch dev        # Deploy specific branch
deployer deploy <url> --name my-app       # Custom service name
deployer deploy <url> -e KEY=VALUE        # Set environment variables
```

### Management
```powershell
deployer list                             # List all services
deployer status <service-name>            # Check service status
deployer logs <service-name>              # View logs
deployer logs <service-name> --follow     # Stream logs
deployer costs                            # View cost summary
deployer costs --detailed                 # Detailed cost breakdown
```

### Service Actions
```powershell
deployer redeploy <service-name>          # Redeploy service
deployer destroy <service-name>           # Remove deployment
```

### Configuration
```powershell
deployer config show                      # Show configuration
deployer config validate                  # Validate configuration
```

### Platform
```powershell
deployer platform start                   # Start management UI
deployer platform stop                    # Stop management UI
deployer platform status                  # Check platform status
```

## Configuration

User configuration is stored in `config/user_config.yaml` (created during setup):

```yaml
aws:
  access_key_id: "YOUR_AWS_KEY"
  secret_access_key: "YOUR_AWS_SECRET"
  region: "us-east-1"

vercel:
  access_token: "YOUR_VERCEL_TOKEN"

github:
  personal_access_token: "YOUR_GITHUB_TOKEN"
  username: "yourusername"

domain:
  root_domain: "example.com"  # Optional
  use_custom_domain: true
  ssl_enabled: true

platform_name: "My Deployment Platform"
platform_port: 3000
```

## Development Workflow

### Backend API Development

```powershell
# Start PostgreSQL
docker-compose up postgres -d

# Run API server
cd src\platform\api
uvicorn main:app --reload --port 8080
```

### Frontend Development

```powershell
cd src\platform\frontend
npm run dev
```

### Testing Repository Analyzer

```python
from src.analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer("/path/to/repo")
result = analyzer.analyze()

print(f"Has Frontend: {result.has_frontend}")
print(f"Frontend Framework: {result.frontend_framework}")
print(f"Has Backend: {result.has_backend}")
print(f"Backend Framework: {result.backend_framework}")
print(f"Needs Database: {result.needs_database}")
```

### Testing Cost Estimator

```python
from src.utils import AWSCostEstimator
from src.config.schemas import DatabaseType

estimator = AWSCostEstimator()

estimate = estimator.estimate_deployment_cost(
    ec2_instance_type="t3.medium",
    has_database=True,
    database_type=DatabaseType.POSTGRES,
    database_instance_type="db.t3.micro",
    database_storage_gb=20,
    estimated_monthly_data_transfer_gb=50,
)

print(f"Total Monthly Cost: ${estimate.total_monthly}")
print(f"EC2: ${estimate.ec2_monthly}")
print(f"RDS: ${estimate.rds_monthly}")
print(f"Data Transfer: ${estimate.data_transfer_monthly}")
```

## Architecture Details

### AWS Infrastructure

- **VPC**: Dedicated VPC with public/private subnets across 2 AZs
- **EC2**: Ubuntu 22.04 LTS with K3s (lightweight Kubernetes)
- **Networking**: Internet Gateway, NAT Gateway, Route Tables
- **Security**: Security groups for K8s cluster and RDS databases
- **Storage**: EBS volumes for EC2, RDS storage for databases

### Kubernetes Stack

- **K3s**: Lightweight Kubernetes distribution
- **ArgoCD**: GitOps continuous deployment
- **Nginx Ingress**: HTTP/HTTPS traffic routing
- **Helm**: Package manager for Kubernetes apps

### Management Platform

- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React with TypeScript, TailwindCSS
- **Features**: Service catalog, deployment tracking, cost monitoring, logs

## Troubleshooting

### Setup Issues

**Problem**: Terraform fails during VPC creation
- Check AWS credentials are valid
- Ensure region has capacity
- Verify IAM permissions (EC2, VPC, RDS)

**Problem**: K3s installation fails
- SSH into EC2 instance: `ssh ubuntu@<instance-ip>`
- Check logs: `sudo journalctl -u k3s`
- Verify security groups allow port 6443

### Deployment Issues

**Problem**: Frontend not deploying to Vercel
- Verify Vercel token permissions
- Check repository is accessible
- Review Vercel deployment logs

**Problem**: Backend stuck in pending
- Check ArgoCD UI: `http://<ec2-ip>:8080`
- View ArgoCD logs: `kubectl logs -n argocd deployment/argocd-server`
- Verify Docker image builds successfully

### CLI Issues

**Problem**: `deployer: command not found`
- Ensure virtual environment is activated
- Reinstall: `pip install -e .`

**Problem**: Import errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.10+)

## Security Best Practices

1. **Credentials**: Never commit `config/user_config.yaml` to git
2. **AWS Keys**: Use IAM roles where possible
3. **Secrets**: Store sensitive data in AWS Secrets Manager or K8s secrets
4. **Network**: Use security groups to restrict access
5. **SSL**: Enable SSL certificates for custom domains

## Performance Optimization

1. **Instance Sizing**: Start with t3.small for low-traffic apps
2. **Database**: Use db.t4g.micro for cost savings (ARM-based)
3. **Auto-scaling**: Configure HPA in Kubernetes for peak traffic
4. **Caching**: Add CloudFront CDN for Vercel deployments
5. **Monitoring**: Set up CloudWatch alarms for cost overruns

## Roadmap

- [ ] Automatic SSL certificate provisioning (Let's Encrypt)
- [ ] Database backup and restore functionality
- [ ] Multi-environment support (staging, production)
- [ ] Built-in monitoring with Prometheus/Grafana
- [ ] Automatic scaling based on traffic
- [ ] Support for additional cloud providers
- [ ] CI/CD pipeline integration
- [ ] Service health checks and auto-recovery

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the management platform
3. Check AWS CloudWatch logs
4. Review ArgoCD deployment status

## Contributing

Contributions welcome! Areas to contribute:
- Additional framework detection
- Cost optimization features
- Monitoring and alerting
- Documentation improvements
- Bug fixes and testing

## License

MIT License - see LICENSE file for details
