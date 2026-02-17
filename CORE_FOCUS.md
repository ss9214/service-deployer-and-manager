# Service Deployer & Manager - Core Focus

This is the **core deployment engine** - everything you need to deploy web apps automatically.

## 🎯 Focus Areas (Priority Order)

### 1. CLI Tool (`src/cli/`)
The command-line interface for deploying applications:
- ✅ `deploy` - Deploy from GitHub URL
- ✅ `list` - Show deployed services  
- ✅ `logs` - View service logs
- ✅ `costs` - Cost estimates
- ✅ `destroy` - Remove deployments
- 🔨 TODO: Implement actual deployment logic

### 2. Repository Analyzer (`src/analyzer/`)
Smart detection of web app structure:
- ✅ Detects 15+ frameworks (React, Next.js, FastAPI, etc.)
- ✅ Identifies monorepo structures
- ✅ Finds database requirements
- 🔨 TODO: Add more framework patterns

### 3. AWS Cost Estimator (`src/utils/`)
Pre-deployment cost calculations:
- ✅ EC2/RDS pricing
- ✅ Monthly cost estimates
- ✅ Per-service breakdown
- 🔨 TODO: Real-time cost tracking via AWS Cost Explorer API

### 4. Deployment Engine (TO BUILD)
Core deployment orchestration:
- 🔨 Vercel API integration for frontend
- 🔨 Kubernetes deployment via kubectl/ArgoCD
- 🔨 RDS provisioning via Terraform
- 🔨 Environment variable management
- 🔨 Health checks and rollback

### 5. Infrastructure
ture (`terraform/`)
AWS resource provisioning:
- ✅ VPC and networking
- ✅ EC2 with K3s Kubernetes
- ✅ RDS database modules
- ✅ ArgoCD setup
- 🔨 TODO: Make infrastructure dynamic per deployment

## 📂 Project Structure (Core Only)

```
service-deployer-and-manager/
├── src/
│   ├── cli/              ⭐ Command-line interface
│   │   └── main.py       → Click commands (deploy, list, logs, etc.)
│   │
│   ├── config/           ⭐ Configuration schemas
│   │   └── schemas.py    → Pydantic models (UserConfig, DeploymentConfig)
│   │
│   ├── analyzer/         ⭐ Repository analysis
│   │   └── repository_analyzer.py → Framework detection
│   │
│   ├── utils/            ⭐ Utilities
│   │   └── aws_cost_estimator.py → Cost calculations
│   │
│   └── deployer/         🔨 TO BUILD - Core deployment logic
│       ├── vercel.py     → Frontend deployment
│       ├── kubernetes.py → Backend deployment
│       ├── database.py   → RDS provisioning
│       └── orchestrator.py → Main deployment flow
│
├── terraform/            ⭐ Infrastructure as Code
│   ├── main.tf
│   └── modules/          → VPC, K8s, RDS, ArgoCD
│
├── docker/               ⭐ Setup tooling
│   └── setup/            → Interactive configuration wizard
│
├── Management Platform/  💡 Optional monitoring UI
│   └── (Separated - work on this later)
│
├── pyproject.toml        ⭐ Python project config
├── requirements.txt      ⭐ Dependencies
└── docker-compose.yml    ⭐ Local services
```

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install core packages
pip install -e .
```

### 2. Test Components

**Analyzer:**
```powershell
python
>>> from src.analyzer import RepositoryAnalyzer
>>> analyzer = RepositoryAnalyzer("path/to/repo")
>>> result = analyzer.analyze()
>>> print(f"Frontend: {result.frontend_framework}")
>>> print(f"Backend: {result.backend_framework}")
```

**Cost Estimator:**
```powershell
python
>>> from src.utils import AWSCostEstimator
>>> estimator = AWSCostEstimator()
>>> cost = estimator.estimate_deployment_cost()
>>> print(f"Monthly cost: ${cost.total_monthly}")
```

**CLI:**
```powershell
deployer --help
deployer list
deployer costs
```

### 3. Configure Credentials
```powershell
# Run interactive setup
docker-compose up setup
```

This creates `config/user_config.yaml` with your AWS, Vercel, and GitHub credentials.

## 🔨 Next Development Steps

### Phase 1: Core Deployment (Current Focus)
1. **Create `src/deployer/` module**
   - Vercel API client for frontend deployment
   - Kubernetes client for backend deployment
   - Terraform wrapper for RDS provisioning

2. **Implement actual deployment in CLI**
   - Connect `deploy` command to deployment engine
   - Add progress tracking
   - Handle errors and rollbacks

3. **Add deployment tracking**
   - Save deployment metadata to local JSON/SQLite
   - Track service URLs, costs, status

### Phase 2: Enhanced Features
1. **Environment management**
   - Support for staging/production
   - Environment variable handling
   - Secret management

2. **Monitoring & Logs**
   - Kubernetes log streaming
   - Health check endpoints
   - Error alerting

3. **Rollback & Updates**
   - Automatic rollback on failure
   - Zero-downtime updates
   - Version management

### Phase 3: Polish & UX
1. **Better error messages**
2. **Interactive prompts** (select framework, instance type, etc.)
3. **Cost warnings** before expensive operations
4. **Progress bars** for long operations

## 💡 Design Principles

1. **CLI First** - Everything works from command line
2. **Convention over Configuration** - Smart defaults, minimal setup
3. **Cost Transparent** - Show costs before deploying
4. **Infrastructure as Code** - All resources versioned
5. **Stateless** - No complex state management initially

## 🎓 How Deployment Should Work

```
┌─────────────────────────────────────────────────────┐
│  USER: deployer deploy https://github.com/user/repo │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  1. ANALYZE REPOSITORY                               │
│     → Clone repo to /tmp                             │
│     → Detect: Next.js frontend + FastAPI backend     │
│     → Detect: PostgreSQL database needed             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  2. ESTIMATE COSTS                                   │
│     → EC2 t3.medium: $30.37/month                    │
│     → RDS db.t3.micro: $15.08/month                  │
│     → Total: $45.45/month                            │
│     → Ask user confirmation                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  3. DEPLOY FRONTEND (if detected)                   │
│     → Call Vercel API                                │
│     → Push repo URL                                  │
│     → Wait for build                                 │
│     → Return: https://my-app.vercel.app              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  4. PROVISION DATABASE (if needed)                   │
│     → Run: terraform apply -target=module.rds        │
│     → Wait for RDS ready (~5 min)                    │
│     → Get connection string                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  5. DEPLOY BACKEND (if detected)                     │
│     → Generate Dockerfile                            │
│     → Build and push to registry                     │
│     → Create Kubernetes manifests                    │
│     → Apply via kubectl                              │
│     → Inject DB connection as secret                 │
│     → Return: https://api.my-app.example.com         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  6. SAVE DEPLOYMENT INFO                             │
│     → Save to deployments/my-app.json                │
│     → Track URLs, costs, timestamps                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  SUCCESS!                                            │
│  ✓ Frontend: https://my-app.vercel.app               │
│  ✓ Backend:  https://api.my-app.example.com          │
│  ✓ Database: my-app.xxxx.rds.amazonaws.com           │
│  ✓ Cost:     $45.45/month                            │
└──────────────────────────────────────────────────────┘
```

## 📝 Notes

- **Management Platform** is in `/Management Platform` folder - work on it later for visual monitoring
- Focus on making the **CLI deployment work end-to-end** first
- Keep it simple - local JSON storage is fine initially
- Add complexity (database tracking, web UI) after core works

## 🎯 Success Criteria

The project is "working" when:
1. ✅ `deployer deploy <url>` successfully deploys a Next.js app to Vercel
2. ✅ `deployer deploy <url>` successfully deploys a FastAPI app to Kubernetes
3. ✅ Database is automatically provisioned and connected
4. ✅ `deployer list` shows deployed services
5. ✅ `deployer costs` shows accurate monthly estimates
6. ✅ `deployer destroy <name>` cleanly removes everything

Let's build this! 🚀
