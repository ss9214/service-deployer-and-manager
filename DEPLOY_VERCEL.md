# Vercel Deployment - Quick Start

## 🎯 Deploy Your Portfolio

You now have a working Vercel deployer! Here's how to deploy your portfolio:

### 1. Get Your Vercel Token

1. Go to [https://vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Click **"Create Token"**
3. Name it something like "Service Deployer"
4. Copy the token

### 2. Set Environment Variable

**PowerShell (Windows):**
```powershell
$env:VERCEL_TOKEN = "your_token_here"
```

**Bash (Linux/Mac):**
```bash
export VERCEL_TOKEN="your_token_here"
```

**To persist across sessions:**
```powershell
# PowerShell - Add to profile
Add-Content $PROFILE "`n`$env:VERCEL_TOKEN = 'your_token_here'"
```

### 3. Deploy Your Portfolio

```powershell
# Basic deployment
deployer deploy https://github.com/yourusername/your-portfolio

# With custom name
deployer deploy https://github.com/yourusername/your-portfolio --name my-portfolio

# With environment variables
deployer deploy https://github.com/yourusername/your-portfolio -e API_URL=https://api.example.com -e GA_ID=UA-123456

# Deploy specific branch
deployer deploy https://github.com/yourusername/your-portfolio --branch develop

# Preview deployment (not production)
deployer deploy https://github.com/yourusername/your-portfolio --preview
```

## 📋 What Happens During Deployment

```
┌─────────────────────────────────────────────────────────┐
│  1. CLONE REPOSITORY                                    │
│     → Clones your repo to temp directory                │
│     → Analyzes structure (framework detection)          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2. ANALYZE PROJECT                                     │
│     → Detects frontend framework (React, Next, Vue...)  │
│     → Checks for backend (FastAPI, Express...)          │
│     → Identifies database requirements                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3. ESTIMATE COSTS (if backend/database needed)         │
│     → Shows monthly AWS costs                           │
│     → EC2, RDS pricing breakdown                        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  4. DEPLOY TO VERCEL                                    │
│     → Creates/updates Vercel project                    │
│     → Links GitHub repository                           │
│     → Starts build process                              │
│     → Monitors deployment status                        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  5. SAVE DEPLOYMENT INFO                                │
│     → Saves to deployments/<name>.json                  │
│     → Tracks URL, deployment ID, framework              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                    SUCCESS! 🎉
```

## 🔍 View Your Deployments

```powershell
# List all deployments
deployer list
```

Output:
```
┌──────────────┬──────────┬──────────┬───────────┬─────────────────────────────┐
│ Name         │ Type     │ Platform │ Framework │ URL                         │
├──────────────┼──────────┼──────────┼───────────┼─────────────────────────────┤
│ my-portfolio │ frontend │ vercel   │ React     │ https://my-portfolio.vercel │
└──────────────┴──────────┴──────────┴───────────┴─────────────────────────────┘
```

## 📁 Deployment Files

After deployment, a JSON file is created at `deployments/<name>.json`:

```json
{
  "name": "my-portfolio",
  "repo": "yourusername/your-portfolio",
  "branch": "main",
  "type": "frontend",
  "platform": "vercel",
  "url": "https://my-portfolio.vercel.app",
  "deployment_id": "dpl_abc123xyz",
  "project_id": "prj_xyz789",
  "created_at": "2026-02-04T10:30:00.000000",
  "env_vars": ["API_URL", "GA_ID"],
  "framework": "React"
}
```

## 🎨 Supported Frontend Frameworks

The analyzer automatically detects:

- ✅ **React** (Vite, CRA)
- ✅ **Next.js** (App Router, Pages Router)
- ✅ **Vue.js** (Vue 3, Nuxt)
- ✅ **Angular**
- ✅ **Svelte** (SvelteKit)
- ✅ **Solid.js**
- ✅ **Astro**
- ✅ **Remix**
- ✅ **Gatsby**
- ✅ **Static HTML/CSS/JS**

Vercel handles the build configuration automatically!

## 🐛 Troubleshooting

### "Invalid Vercel token"
- Token might be expired or revoked
- Create a new token at [vercel.com/account/tokens](https://vercel.com/account/tokens)
- Make sure to set it: `$env:VERCEL_TOKEN = "new_token"`

### "Failed to clone repository"
- Check that the repository URL is correct
- Ensure you have access to the repository
- Try with HTTPS URL: `https://github.com/user/repo`
- For private repos, use a personal access token in the URL

### "Rate limited, waiting Xs..."
- Vercel API has rate limits
- The tool automatically waits and retries
- Wait for the retry to complete

### See detailed errors
Set DEBUG environment variable:
```powershell
$env:DEBUG = "1"
deployer deploy <url>
```

## 🚀 Next Steps

Now that Vercel deployment works:

1. ✅ Deploy your portfolio
2. ✅ Verify it works
3. 🔨 Next: Add backend deployment (Kubernetes)
4. 🔨 Next: Add database provisioning (RDS)

## 💡 Pro Tips

**Environment Variables:**
- Keep secrets out of your repo
- Pass them via `-e KEY=VALUE` flags
- They're injected into Vercel deployment

**Branch Deployments:**
- `--branch main` → Production deployment
- `--branch develop` → Preview deployment
- `--preview` flag → Always preview (not production)

**Custom Names:**
- `--name` sanitizes automatically (lowercase, hyphens)
- Use descriptive names: `company-website`, `api-dashboard`

**Monorepos:**
- Analyzer detects monorepo structure
- Will show all detected frameworks
- For now, deploys root package.json

## 📝 Example Workflows

**Portfolio Site:**
```powershell
deployer deploy https://github.com/user/portfolio --name personal-site
```

**Client Project:**
```powershell
deployer deploy https://github.com/client/website --name acme-website -e API_URL=https://api.acme.com
```

**Staging Environment:**
```powershell
deployer deploy https://github.com/team/app --branch staging --preview
```

---

**Ready to deploy? 🚀**

```powershell
deployer deploy https://github.com/yourusername/your-portfolio
```
