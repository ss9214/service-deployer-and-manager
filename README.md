# Service Deployer and Manager

An automated deployment and management platform for web applications. Deploy full-stack web apps (frontend, backend, database) to AWS and Vercel with a single command.

## Features

- 🚀 **One-Command Deployment**: Deploy complete web applications from GitHub repositories
- ☁️ **Multi-Cloud**: Backend on AWS (EC2 + Kubernetes), Frontend on Vercel
- 🗄️ **Managed Databases**: Automatic RDS provisioning for PostgreSQL, MySQL, or MongoDB
- 📊 **Management Dashboard**: Web UI to monitor deployments, view logs, and track costs
- 💰 **Cost Tracking**: Real-time AWS cost estimation and resource monitoring
- 🔒 **Secure**: Automated SSL certificates and secure credential management
- 🎯 **Single User**: Designed for individual developers and small teams

## Architecture

### Backend Infrastructure (AWS)
- **EC2** instances with nginx reverse proxy
- **Kubernetes** (K3s) for container orchestration
- **ArgoCD** for GitOps-based deployments
- **Helm** for package management
- **RDS** for managed databases

### Frontend Deployment
- **Vercel** for frontend hosting and CDN

### Infrastructure as Code
- **Terraform** for AWS resource provisioning
- **Docker** for containerization

## Quick Start

### Prerequisites

- Docker installed on your machine
- AWS account with appropriate permissions
- Vercel account and access token
- GitHub account and personal access token

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd service-deployer-and-manager
   ```

2. **Run the setup container**:
   ```bash
   docker-compose up setup
   ```

3. **Follow the interactive prompts** to configure:
   - AWS credentials and region
   - Vercel access token
   - GitHub personal access token
   - Domain settings (optional)

4. **Wait for infrastructure provisioning** (15-20 minutes):
   - VPC and networking setup
   - EC2 instance with Kubernetes
   - ArgoCD installation
   - Management platform deployment

### Deploy Your First App

```bash
# Install the CLI
pip install -e .

# Deploy a web application
deployer deploy https://github.com/yourusername/your-webapp

# List deployed services
deployer list

# View logs
deployer logs my-webapp

# Check cost estimates
deployer costs

# Destroy a deployment
deployer destroy my-webapp
```

## Project Structure

```
service-deployer-and-manager/
├── src/
│   ├── cli/                  # CLI tool
│   ├── config/               # Configuration schemas
│   ├── analyzer/             # Repository analysis
│   ├── deployer/             # Deployment orchestration
│   ├── platform/             # Management platform
│   │   ├── api/              # FastAPI backend
│   │   └── frontend/         # React dashboard
│   └── utils/                # Shared utilities
├── terraform/
│   ├── modules/              # Reusable Terraform modules
│   │   ├── vpc/
│   │   ├── ec2/
│   │   ├── rds/
│   │   └── kubernetes/
│   └── main.tf
├── docker/
│   ├── setup/                # Setup container
│   └── platform/             # Platform container
├── helm-charts/              # Helm charts for deployments
└── config/                   # User configuration (gitignored)
```

## Supported Web App Frameworks

### Frontend
- React / Next.js
- Vue / Nuxt.js
- Angular
- Svelte / SvelteKit
- Static sites

### Backend
- Node.js (Express, NestJS, Fastify)
- Python (FastAPI, Django, Flask)
- Go (Gin, Echo)
- Java/Kotlin (Spring Boot)

### Databases
- PostgreSQL
- MySQL
- MongoDB
- Redis

## CLI Commands

```bash
# Deployment
deployer deploy <github-url>              # Deploy a repository
deployer redeploy <service-name>          # Redeploy existing service
deployer destroy <service-name>           # Remove deployment

# Management
deployer list                             # List all deployments
deployer status <service-name>            # Check service status
deployer logs <service-name> [--follow]   # View logs
deployer costs [--detailed]               # View cost estimates

# Configuration
deployer config show                      # Show current configuration
deployer config set <key> <value>         # Update configuration
deployer config validate                  # Validate configuration

# Platform
deployer platform start                   # Start management UI
deployer platform stop                    # Stop management UI
deployer platform status                  # Check platform status
```

## Management Platform

Access the web dashboard at `http://localhost:3000` (or configured port):

- 📋 **Service Catalog**: View all deployed services
- 📊 **Deployment Status**: Real-time deployment progress
- 📝 **Logs Viewer**: Aggregate logs from all services
- 💰 **Cost Dashboard**: AWS cost breakdown and trends
- ⚙️ **Service Actions**: Redeploy, rollback, scale, or destroy

## Configuration

User configuration is stored in `config/user_config.yaml`:

```yaml
aws:
  access_key_id: "YOUR_KEY"
  secret_access_key: "YOUR_SECRET"
  region: "us-east-1"

vercel:
  access_token: "YOUR_TOKEN"

github:
  personal_access_token: "YOUR_TOKEN"
  username: "yourusername"

domain:
  root_domain: "example.com"
  use_custom_domain: true
  ssl_enabled: true

platform_name: "My Deployment Platform"
platform_port: 3000
```

## Cost Optimization

The platform includes several cost optimization features:

- **Right-sizing**: Automatic resource allocation based on app requirements
- **Cost Estimation**: Pre-deployment cost calculation
- **Resource Tagging**: All resources tagged for cost tracking
- **Monitoring**: Alerts for unexpected cost increases

### Typical Monthly Costs (us-east-1)

- **EC2 (t3.medium)**: ~$30/month
- **RDS (db.t3.micro)**: ~$15/month per database
- **Data Transfer**: ~$5-20/month
- **Vercel**: Free tier available, Pro at $20/month

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/

# Type checking
mypy src/
```

## Security

- All credentials stored securely with encryption
- AWS IAM roles for service-to-service authentication
- Automatic SSL certificate provisioning
- Network security groups with minimal required access
- Secrets managed via Kubernetes secrets

## Troubleshooting

### Common Issues

1. **Setup fails during Terraform apply**
   - Check AWS credentials and permissions
   - Verify region has available capacity

2. **Deployment stuck in pending**
   - Check ArgoCD logs: `deployer logs argocd`
   - Verify GitHub repository is accessible

3. **Frontend not deploying to Vercel**
   - Verify Vercel token has correct permissions
   - Check repository has vercel.json or proper framework detection

## Roadmap

- [ ] Support for more cloud providers (GCP, Azure)
- [ ] Automatic scaling based on traffic
- [ ] Built-in CI/CD pipelines
- [ ] Multi-environment support (staging, production)
- [ ] Database backup and restore
- [ ] Enhanced monitoring with Prometheus/Grafana

## License

MIT

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.