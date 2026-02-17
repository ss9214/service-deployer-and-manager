# 📚 Complete Platform Walkthrough

## 🎯 What This Platform Does

This is an **end-to-end automated deployment system** that takes a GitHub repository containing a web application and deploys it to production infrastructure with a single command.

**Input:** GitHub repository URL  
**Output:** Running production application with frontend on Vercel, backend on AWS Kubernetes, and managed database

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
│  CLI: deployer deploy https://github.com/user/repo          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               REPOSITORY ANALYZER                            │
│  • Clones repository                                         │
│  • Detects frontend (React/Next/Vue)                         │
│  • Detects backend (Node/Python/Go)                          │
│  • Detects database needs (Postgres/MySQL/Mongo)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               COST ESTIMATOR                                 │
│  • Calculates EC2 costs (~$30/month)                         │
│  • Calculates RDS costs (~$15/month per DB)                  │
│  • Estimates data transfer                                   │
│  • Shows total before deployment                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│   FRONTEND       │    │   BACKEND        │
│   (Vercel)       │    │   (AWS K8s)      │
│                  │    │                  │
│ • Auto-build     │    │ • Dockerize      │
│ • CDN deploy     │    │ • ArgoCD deploy  │
│ • Custom domain  │    │ • Nginx ingress  │
└──────────────────┘    └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   DATABASE       │
                        │   (AWS RDS)      │
                        │                  │
                        │ • Auto-provision │
                        │ • Inject env vars│
                        └──────────────────┘
```

---

## 📂 File-by-File Walkthrough

### **1. Configuration System** (`src/config/`)

#### `schemas.py` - The Data Models
This file defines the "shape" of all data in the system using Pydantic:

**UserConfig**: Your credentials
```python
aws:
  access_key_id: "AKIA..."
  secret_access_key: "xyz..."
  region: "us-east-1"
vercel:
  access_token: "vercel_token..."
github:
  personal_access_token: "ghp_..."
```

**RepositoryMetadata**: Info about the app being deployed
```python
url: "https://github.com/user/my-app"
name: "my-app"
has_frontend: True
has_backend: True
needs_database: True
detected_frontend_framework: "Next.js"
detected_backend_framework: "FastAPI"
detected_database_type: "postgres"
```

**DeploymentConfig**: How to deploy
```python
service_name: "my-app"
backend:
  replicas: 2
  cpu_limit: "500m"
  memory_limit: "512Mi"
frontend:
  build_command: "npm run build"
database:
  type: "postgres"
  instance_class: "db.t3.micro"
```

**CostEstimate**: Monthly costs
```python
ec2_monthly: 30.37
rds_monthly: 15.00
data_transfer_monthly: 5.00
total_monthly: 50.37
```

---

### **2. Repository Analyzer** (`src/analyzer/repository_analyzer.py`)

This is the "brain" that figures out what your app needs.

**How it works:**

1. **Clone repository** to local temp folder
2. **Scan for files:**
   - `package.json` → Check for React, Next.js, Vue, Express, etc.
   - `requirements.txt` → Check for FastAPI, Django, Flask
   - `go.mod` → Check for Gin, Echo
   - `pom.xml` → Check for Spring Boot

3. **Detect structure:**
```python
# Monorepo detection
if "frontend/" folder exists with package.json:
    has_frontend = True
if "backend/" folder exists with server code:
    has_backend = True
```

4. **Detect database:**
```python
# Look for database packages
if "psycopg2" in requirements.txt:
    needs_database = True
    database_type = "postgres"
if "mongoose" in package.json:
    needs_database = True
    database_type = "mongodb"
```

**Example output:**
```python
AnalysisResult(
    has_frontend=True,
    has_backend=True,
    needs_database=True,
    frontend_framework="Next.js",
    backend_framework="FastAPI",
    database_type="postgres",
    frontend_build_command="npm run build",
    install_command="npm install"
)
```

---

### **3. Cost Estimator** (`src/utils/aws_cost_estimator.py`)

Calculates AWS costs **before** deploying so there are no surprises.

**Pricing data (February 2026):**
```python
EC2_PRICING = {
    "t3.micro": $7.59/month,
    "t3.small": $15.18/month,
    "t3.medium": $30.37/month,  # Default
}

RDS_PRICING = {
    "db.t3.micro": $12.78/month,  # Default
    "db.t3.small": $25.55/month,
}

DATA_TRANSFER = $0.09/GB
```

**Example calculation:**
```python
estimator = AWSCostEstimator()
estimate = estimator.estimate_deployment_cost(
    ec2_instance_type="t3.medium",
    has_database=True,
    database_type="postgres",
)

# Returns:
# ec2_monthly: $30.37 (instance) + $3.00 (storage) = $33.37
# rds_monthly: $12.78 (instance) + $2.30 (20GB storage) = $15.08
# data_transfer: $4.50 (50GB)
# TOTAL: $52.95/month
```

---

### **4. CLI Tool** (`src/cli/main.py`)

The command-line interface using **Click** (commands) + **Rich** (pretty output).

**Commands:**

```bash
# Deploy
deployer deploy https://github.com/user/repo
  ↓
  1. Clones repo
  2. Runs analyzer
  3. Shows cost estimate
  4. Asks for confirmation
  5. Deploys frontend to Vercel
  6. Deploys backend to Kubernetes
  7. Creates database if needed
  8. Returns URLs

# List services
deployer list
  ↓
  Shows table of all deployed services with status

# View logs
deployer logs my-app --follow
  ↓
  Streams logs from Kubernetes pods

# Check costs
deployer costs --detailed
  ↓
  Shows cost breakdown by service
```

**Internal flow:**
```python
@cli.command()
def deploy(repository_url, branch, name, env):
    # 1. Analyze repository
    analyzer = RepositoryAnalyzer(repo_path)
    result = analyzer.analyze()
    
    # 2. Estimate costs
    estimator = AWSCostEstimator()
    cost = estimator.estimate_deployment_cost(...)
    
    # 3. Deploy frontend (if detected)
    if result.has_frontend:
        deploy_to_vercel(repo_url, result.frontend_framework)
    
    # 4. Deploy backend (if detected)
    if result.has_backend:
        deploy_to_kubernetes(repo_url, result.backend_framework)
    
    # 5. Provision database (if needed)
    if result.needs_database:
        provision_rds(result.database_type)
```

---

### **5. Infrastructure (Terraform)**

#### **VPC Module** (`terraform/modules/vpc/`)
Creates your private network in AWS:
```
VPC (10.0.0.0/16)
  ├── Public Subnet 1 (10.0.0.0/24) - us-east-1a
  ├── Public Subnet 2 (10.0.1.0/24) - us-east-1b
  ├── Private Subnet 1 (10.0.10.0/24) - us-east-1a
  └── Private Subnet 2 (10.0.11.0/24) - us-east-1b

Internet Gateway → Public Subnets
NAT Gateway → Private Subnets (for database)
```

#### **Kubernetes Module** (`terraform/modules/kubernetes/`)
Provisions EC2 instance with K3s:
```bash
# User data script (runs on boot)
1. Install Docker
2. Install K3s (lightweight Kubernetes)
3. Install Helm (package manager)
4. Install nginx ingress controller
5. Expose Kubernetes API on port 6443
```

#### **ArgoCD Module** (`terraform/modules/argocd/`)
GitOps deployment automation:
```
ArgoCD watches your GitHub repo
  ↓
Detects changes to main branch
  ↓
Automatically pulls changes
  ↓
Applies to Kubernetes cluster
  ↓
Your app updates automatically!
```

#### **RDS Module** (`terraform/modules/rds/`)
Creates managed database:
```
Database Instance (PostgreSQL 16)
  ├── Instance: db.t3.micro
  ├── Storage: 20GB encrypted
  ├── Backups: 7 days retention
  ├── Networking: Private subnet
  └── Access: Only from K8s cluster
```

---

### **6. Management Platform**

#### **Backend API** (`src/platform/api/`)

**Database Models** (`models.py`):
```python
Service:
  - id, name, repository_url
  - has_frontend, has_backend, has_database
  - frontend_url, backend_url
  - status, estimated_monthly_cost
  - created_at, last_deployed_at

Deployment:
  - service_id
  - commit_sha, commit_message
  - status (pending/success/failed)
  - started_at, completed_at

Log:
  - service_id
  - level (info/error)
  - message, timestamp
```

**API Endpoints** (`main.py`):
```python
GET  /api/services              # List all services
POST /api/services              # Create new service
GET  /api/services/{id}         # Get specific service
PUT  /api/services/{id}         # Update service
DELETE /api/services/{id}       # Delete service

GET  /api/deployments           # List all deployments
GET  /api/services/{id}/deployments  # Service deployments

GET  /api/costs/summary         # Total costs
GET  /api/costs/{service_id}    # Service cost breakdown
```

#### **Frontend Dashboard** (`src/platform/frontend/`)

**Tech Stack:**
- React 18 + TypeScript
- Vite (build tool)
- React Router (routing)
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- Lucide React (icons)

**Pages:**

1. **Dashboard** (`pages/Dashboard.tsx`)
   - 4 stat cards (total services, running, cost, deployments)
   - Recent services list
   - Status badges

2. **Services** (`pages/Services.tsx`)
   - Grid of service cards
   - Each card shows:
     - Repository URL (clickable)
     - Status, branch, cost, last deployed
     - Framework badges (frontend/backend/database)
     - Quick actions (redeploy, destroy)

3. **Costs** (`pages/Costs.tsx`)
   - Large cost total card
   - Infrastructure breakdown (EC2, RDS, data transfer)
   - Per-service cost list
   - Cost optimization tips

4. **Settings** (`pages/Settings.tsx`)
   - AWS configuration
   - Vercel configuration
   - Platform settings

---

## 🔧 TypeScript Errors Explained

The errors you're seeing are **expected** because:

1. **No `node_modules`**: The npm packages haven't been installed yet
2. **Type declarations missing**: React, react-router-dom, etc. types aren't available

**These will all disappear when you run:**
```bash
cd src/platform/frontend
npm install
```

The `npm install` command will download all packages listed in `package.json`, including their TypeScript type declarations.

---

## 🚀 How to Use This Platform

### **Step 1: Initial Setup**

```powershell
# Install Python dependencies
pip install -e .

# This makes the 'deployer' command available
```

### **Step 2: Run Setup Container**

```powershell
docker-compose up setup
```

This interactive wizard will:
1. Ask for AWS credentials
2. Ask for Vercel token  
3. Ask for GitHub token
4. Run Terraform to create infrastructure (15-20 min)
5. Install K3s Kubernetes
6. Install ArgoCD

### **Step 3: Start Management Platform**

```powershell
# Terminal 1: Start backend + database
docker-compose up platform

# Terminal 2: Start frontend
cd src\platform\frontend
npm install
npm run dev
```

Access dashboard: http://localhost:3000

### **Step 4: Deploy Your First App**

```powershell
deployer deploy https://github.com/yourusername/your-web-app
```

**What happens:**
1. Clones your repository
2. Analyzes structure
3. Shows cost estimate
4. Asks confirmation
5. Deploys frontend to Vercel
6. Deploys backend to Kubernetes
7. Creates database (if needed)
8. Shows URLs where app is live

---

## 🎓 Understanding the Flow

### **Example: Deploying a Next.js + FastAPI App**

**Your Repository:**
```
my-app/
├── frontend/          # Next.js app
│   ├── package.json
│   ├── pages/
│   └── components/
├── backend/           # FastAPI app
│   ├── requirements.txt
│   ├── main.py
│   └── models.py
└── README.md
```

**Deployment Flow:**

1. **Analyzer scans:**
   ```
   ✓ Found frontend/package.json with "next"
   → has_frontend = True, framework = "Next.js"
   
   ✓ Found backend/requirements.txt with "fastapi" and "psycopg2"
   → has_backend = True, framework = "FastAPI"
   → needs_database = True, type = "postgres"
   ```

2. **Cost estimator:**
   ```
   EC2 (t3.medium):         $33.37/month
   RDS (db.t3.micro):       $15.08/month
   Data transfer:            $4.50/month
   ──────────────────────────────────────
   TOTAL:                   $52.95/month
   ```

3. **Deployment:**
   ```
   [FRONTEND]
   → Push to Vercel API
   → Vercel detects Next.js
   → Builds and deploys
   → Returns: https://my-app.vercel.app
   
   [BACKEND]
   → Generate Dockerfile
   → Build container image
   → Push to GitHub Container Registry
   → Create Kubernetes manifest
   → ArgoCD deploys to cluster
   → Returns: https://api.my-app.example.com
   
   [DATABASE]
   → Run Terraform RDS module
   → Provision PostgreSQL instance
   → Create database user/password
   → Inject connection string as env var to backend
   ```

4. **Result:**
   ```
   ✓ Frontend:  https://my-app.vercel.app
   ✓ Backend:   https://api.my-app.example.com
   ✓ Database:  my-app-db.xxxx.us-east-1.rds.amazonaws.com
   ✓ Cost:      $52.95/month
   ```

---

## 💡 Key Concepts

### **Why Kubernetes (K3s)?**
- Container orchestration (run multiple services)
- Auto-healing (restarts crashed containers)
- Load balancing
- Easy scaling
- **K3s** = Lightweight version, perfect for single-node setups

### **Why ArgoCD?**
- **GitOps**: Your Git repo is the source of truth
- Push to GitHub → ArgoCD automatically deploys
- Easy rollbacks (revert Git commit)
- Visual deployment status

### **Why Vercel for Frontend?**
- Automatic builds from Git
- Global CDN (fast worldwide)
- Free SSL certificates
- Zero configuration for Next.js/React
- Instant deployments

### **Why Terraform?**
- **Infrastructure as Code**: Your infrastructure is versioned
- Reproducible (can recreate everything)
- Safe (shows plan before applying)
- Modular (reusable components)

---

## 🎯 Next Steps

1. ✅ **Install npm packages**: `cd src/platform/frontend && npm install`
2. ✅ **Run setup**: Configure your credentials
3. ✅ **Deploy test app**: Try with a simple Next.js app
4. ⏩ **Customize**: Modify detection rules, add more frameworks
5. ⏩ **Production**: Add CI/CD, monitoring, alerting

The TypeScript errors will resolve once you run `npm install` in the frontend folder!
