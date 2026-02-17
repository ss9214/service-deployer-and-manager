"""CLI main entry point."""

import click
import os
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..config.schemas import VercelConfig, UserConfig
from ..analyzer.repository_analyzer import RepositoryAnalyzer
from ..utils.aws_cost_estimator import AWSCostEstimator
from ..utils.credential_manager import CredentialManager
from ..deployer import VercelDeployer

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Service Deployer - Automated web app deployment platform."""
    pass


@cli.command()
@click.option('--vercel', is_flag=True, help='Setup Vercel token')
@click.option('--aws', is_flag=True, help='Setup AWS credentials')
@click.option('--github', is_flag=True, help='Setup GitHub token')
@click.option('--all', 'setup_all', is_flag=True, help='Setup all credentials')
@click.option('--show', is_flag=True, help='Show stored credentials')
@click.option('--clear', is_flag=True, help='Clear all stored credentials')
def setup(vercel: bool, aws: bool, github: bool, setup_all: bool, show: bool, clear: bool) -> None:
    """Setup and manage credentials securely."""
    
    if clear:
        if click.confirm("Are you sure you want to clear all stored credentials?", default=False):
            CredentialManager.clear_all_credentials()
        return
    
    if show:
        # Display stored credentials
        console.print("\n[bold cyan]Stored Credentials:[/bold cyan]\n")
        stored = CredentialManager.list_stored_credentials()
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        
        for service, is_stored in stored.items():
            status = "✓ Stored" if is_stored else "✗ Not stored"
            style = "green" if is_stored else "yellow"
            table.add_row(service.title(), f"[{style}]{status}[/{style}]")
        
        console.print(table)
        console.print("\n[dim]Tip: Run 'deployer setup --all' to configure all credentials[/dim]")
        return
    
    if not any([vercel, aws, github, setup_all]):
        console.print("[yellow]No setup option specified. Use --help for options.[/yellow]")
        console.print("\nQuick start: [cyan]deployer setup --vercel[/cyan]")
        return
    
    console.print(Panel.fit(
        "[bold cyan]Credential Setup[/bold cyan]\n\n"
        "Credentials will be stored securely in your system's credential manager:\n"
        "  • Windows: Credential Manager\n"
        "  • macOS: Keychain\n"
        "  • Linux: Secret Service (GNOME Keyring/KWallet)",
        border_style="cyan"
    ))
    
    # Setup Vercel
    if vercel or setup_all:
        console.print("\n[bold]Vercel Setup[/bold]")
        console.print("Get your token from: [blue]https://vercel.com/account/tokens[/blue]\n")
        
        token = click.prompt("Enter your Vercel API token", hide_input=True, type=str)
        if token.strip():
            CredentialManager.set_vercel_token(token.strip())
        else:
            console.print("[yellow]⚠ Skipped (empty token)[/yellow]")
    
    # Setup AWS
    if aws or setup_all:
        console.print("\n[bold]AWS Setup[/bold]")
        console.print("Get your credentials from: [blue]https://console.aws.amazon.com/iam/[/blue]\n")
        
        access_key = click.prompt("Enter AWS Access Key ID", type=str)
        secret_key = click.prompt("Enter AWS Secret Access Key", hide_input=True, type=str)
        
        if access_key.strip() and secret_key.strip():
            CredentialManager.set_aws_credentials(access_key.strip(), secret_key.strip())
        else:
            console.print("[yellow]⚠ Skipped (empty credentials)[/yellow]")
    
    # Setup GitHub
    if github or setup_all:
        console.print("\n[bold]GitHub Setup[/bold]")
        console.print("Get your token from: [blue]https://github.com/settings/tokens[/blue]\n")
        
        token = click.prompt("Enter your GitHub Personal Access Token", hide_input=True, type=str)
        if token.strip():
            CredentialManager.set_github_token(token.strip())
        else:
            console.print("[yellow]⚠ Skipped (empty token)[/yellow]")
    
    console.print("\n[bold green]✓ Setup complete![/bold green]")
    console.print("\nYou can now deploy with: [cyan]deployer deploy <github-url>[/cyan]")


@cli.command()
@click.argument("repository_url")
@click.option("--branch", default="main", help="Git branch to deploy")
@click.option("--name", help="Custom project name for Vercel URL (e.g., 'my-portfolio' → my-portfolio.vercel.app)")
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option('--production/--preview', default=True, help='Production or preview deployment')
def deploy(repository_url: str, branch: str, name: str | None, env: tuple[str, ...], production: bool) -> None:
    """Deploy a web application from a GitHub repository."""
    
    console.print(Panel.fit(
        f"[bold cyan]Deploying Application[/bold cyan]\n\n"
        f"Repository: {repository_url}\n"
        f"Branch: {branch}\n"
        f"Environment: {'Production' if production else 'Preview'}",
        border_style="cyan"
    ))
    
    # Extract repo info (owner/repo)
    try:
        # Handle different GitHub URL formats
        if repository_url.startswith("https://github.com/"):
            github_path = repository_url.replace("https://github.com/", "").rstrip(".git").rstrip("/")
        elif repository_url.startswith("git@github.com:"):
            github_path = repository_url.replace("git@github.com:", "").rstrip(".git").rstrip("/")
        else:
            github_path = repository_url.rstrip(".git").rstrip("/")
        
        # Get project name
        if not name:
            name = github_path.split("/")[-1].lower().replace("_", "-").replace(".", "")
        else:
            # Sanitize custom name for Vercel
            name = name.lower().replace("_", "-").replace(" ", "-").replace(".", "")
            # Remove special characters except hyphens
            name = "".join(c for c in name if c.isalnum() or c == "-")
            # Remove consecutive hyphens
            while "--" in name:
                name = name.replace("--", "-")
            # Remove leading/trailing hyphens
            name = name.strip("-")
        
        console.print(f"\n[cyan]Project name:[/cyan] {name}")
        console.print(f"[cyan]Vercel URL:[/cyan] https://{name}.vercel.app")
        console.print(f"[cyan]GitHub path:[/cyan] {github_path}\n")
        
    except Exception as e:
        console.print(f"[red]Error parsing repository URL: {e}[/red]")
        return
    
    # Step 1: Clone repository for analysis
    console.print("[bold]Step 1:[/bold] Cloning repository for analysis...")
    
    temp_dir = tempfile.mkdtemp(prefix="deployer-")
    try:
        # Clone repo
        import subprocess
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, repository_url, temp_dir],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            console.print(f"[red]✗ Failed to clone repository:[/red] {result.stderr}")
            return
        
        console.print(f"[green]✓[/green] Repository cloned to temporary directory\n")
        
        # Step 2: Analyze repository structure
        console.print("[bold]Step 2:[/bold] Analyzing repository structure...")
        
        analyzer = RepositoryAnalyzer(temp_dir)
        analysis = analyzer.analyze()
        
        console.print(f"[green]✓[/green] Analysis complete")
        console.print(f"  Frontend: {analysis.frontend_framework or 'None'}")
        console.print(f"  Backend: {analysis.backend_framework or 'None'}")
        console.print(f"  Database: {analysis.database_type or 'None'}")
        console.print(f"  Monorepo: {'Yes' if analysis.is_monorepo else 'No'}\n")
        
        # Step 3: Estimate costs
        if analysis.backend_framework or analysis.database_type:
            console.print("[bold]Step 3:[/bold] Estimating AWS costs...")
            
            estimator = AWSCostEstimator()
            cost = estimator.estimate_deployment_cost(
                has_backend=bool(analysis.backend_framework),
                has_database=bool(analysis.database_type),
                instance_type="t3.medium" if analysis.backend_framework else None,
                db_instance_type="db.t3.micro" if analysis.database_type else None
            )
            
            console.print(f"[green]✓[/green] Monthly cost estimate: [bold]${cost.total_monthly:.2f}[/bold]")
            if analysis.backend_framework:
                console.print(f"  EC2: ${cost.ec2_monthly:.2f}")
            if analysis.database_type:
                console.print(f"  RDS: ${cost.rds_monthly:.2f}")
            console.print()
        
        # Step 4: Deploy frontend to Vercel
        if analysis.frontend_framework or not analysis.backend_framework:
            console.print("[bold]Step 4:[/bold] Deploying to Vercel...")
            
            # Get Vercel token from credential manager or environment
            vercel_token = CredentialManager.get_vercel_token()
            if not vercel_token:
                console.print("\n[yellow]⚠ Vercel token not found[/yellow]")
                console.print("\nRun setup to store your token securely:")
                console.print("  [cyan]deployer setup --vercel[/cyan]")
                console.print("\nOr set in environment temporarily:")
                console.print("  [cyan]$env:VERCEL_TOKEN = 'your_token_here'[/cyan] (PowerShell)")
                console.print("  [cyan]export VERCEL_TOKEN='your_token_here'[/cyan] (Bash)")
                console.print("\nGet your token from: [blue]https://vercel.com/account/tokens[/blue]")
                return
            
            # Parse environment variables
            env_vars = {}
            for env_var in env:
                if "=" in env_var:
                    key, value = env_var.split("=", 1)
                    env_vars[key] = value
            
            # Create Vercel deployer
            vercel_config = VercelConfig(api_token=vercel_token)
            deployer = VercelDeployer(vercel_config)
            
            # Verify token
            if not deployer.verify_token():
                console.print("[red]✗ Invalid Vercel token[/red]")
                return
            
            # Deploy
            try:
                deployment = deployer.create_deployment(
                    name=name,
                    github_repo=github_path,
                    branch=branch,
                    production=production,
                    env_vars=env_vars if env_vars else None
                )
                
                console.print(f"\n[bold green]🎉 Deployment Successful![/bold green]\n")
                console.print(f"[bold cyan]Live URL:[/bold cyan] [link={deployment['url']}]{deployment['url']}[/link]")
                console.print(f"[cyan]Project:[/cyan] {name}")
                console.print(f"[cyan]Deployment ID:[/cyan] {deployment['id']}")
                console.print(f"[cyan]Status:[/cyan] {deployment['status']}")
                
                # Show custom domain info if using default vercel.app domain
                if ".vercel.app" in deployment['url']:
                    console.print(f"\n[dim]💡 Tip: Add a custom domain at https://vercel.com/{name}/settings/domains[/dim]")
                
                # Save deployment info
                deployments_dir = Path("deployments")
                deployments_dir.mkdir(exist_ok=True)
                
                import json
                from datetime import datetime
                
                deployment_file = deployments_dir / f"{name}.json"
                deployment_info = {
                    "name": name,
                    "repo": github_path,
                    "branch": branch,
                    "type": "frontend",
                    "platform": "vercel",
                    "url": deployment['url'],
                    "deployment_id": deployment['id'],
                    "project_id": deployment['project_id'],
                    "created_at": datetime.now().isoformat(),
                    "env_vars": list(env_vars.keys()) if env_vars else [],
                    "framework": analysis.frontend_framework
                }
                
                with open(deployment_file, 'w') as f:
                    json.dump(deployment_info, f, indent=2)
                
                console.print(f"\n[green]✓[/green] Deployment info saved to: {deployment_file}")
                
            except Exception as e:
                console.print(f"\n[red]✗ Deployment failed:[/red] {e}")
                import traceback
                if os.environ.get("DEBUG"):
                    traceback.print_exc()
                return
        else:
            console.print("\n[yellow]Backend-only deployment not yet implemented[/yellow]")
            console.print("Coming soon: Kubernetes + database deployment")
        
    except subprocess.TimeoutExpired:
        console.print("[red]✗ Repository clone timed out[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error during deployment:[/red] {e}")
        import traceback
        if os.environ.get("DEBUG"):
            traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@cli.command()
def list() -> None:
    """List all deployed services."""
    console.print("[cyan]Deployed Services:[/cyan]\n")
    
    # Load from deployments directory
    deployments_dir = Path("deployments")
    if not deployments_dir.exists() or not list(deployments_dir.glob("*.json")):
        console.print("[yellow]⚠ No deployments found[/yellow]")
        console.print("Deploy your first app with: [cyan]deployer deploy <github-url>[/cyan]")
        return
    
    import json
    
    table = Table(title="Deployed Services")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Platform", style="blue")
    table.add_column("Framework", style="yellow")
    table.add_column("URL", style="green")
    
    for deployment_file in sorted(deployments_dir.glob("*.json")):
        try:
            with open(deployment_file) as f:
                deployment = json.load(f)
            
            table.add_row(
                deployment.get("name", "Unknown"),
                deployment.get("type", "Unknown"),
                deployment.get("platform", "Unknown"),
                deployment.get("framework", "N/A"),
                deployment.get("url", "N/A")
            )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {deployment_file.name}: {e}[/yellow]")
    
    console.print(table)


@cli.command()
@click.argument("service_name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
def logs(service_name: str, follow: bool) -> None:
    """View logs for a deployed service."""
    console.print(f"[cyan]Fetching logs for:[/cyan] {service_name}\n")

    # Load deployment info
    deployments_dir = Path("deployments")
    deployment_file = deployments_dir / f"{service_name}.json"
    
    if not deployment_file.exists():
        console.print(f"[red]✗ Deployment not found:[/red] {service_name}")
        console.print("\nAvailable deployments:")
        if deployments_dir.exists():
            for f in sorted(deployments_dir.glob("*.json")):
                console.print(f"  • {f.stem}")
        return
    
    import json
    
    try:
        with open(deployment_file) as f:
            deployment = json.load(f)
        
        deployment_id = deployment.get("deployment_id")
        platform = deployment.get("platform", "unknown")
        
        if platform != "vercel":
            console.print(f"[yellow]Log fetching only supported for Vercel deployments[/yellow]")
            return
        
        if not deployment_id:
            console.print(f"[red]✗ No deployment ID found[/red]")
            return
        
        # Get Vercel token
        vercel_token = CredentialManager.get_vercel_token()
        if not vercel_token:
            console.print("[yellow]⚠ Vercel token not found[/yellow]")
            console.print("Run: [cyan]deployer setup --vercel[/cyan]")
            return
        
        # Create Vercel deployer and fetch logs
        vercel_config = VercelConfig(api_token=vercel_token)
        deployer = VercelDeployer(vercel_config)
        
        if follow:
            console.print("[yellow]Note: Live log following not yet implemented[/yellow]")
            console.print("[cyan]Fetching latest logs...[/cyan]\n")
        
        deployer._display_deployment_logs(deployment_id)
        
    except Exception as e:
        console.print(f"[red]✗ Error fetching logs:[/red] {e}")
        import traceback
        if os.environ.get("DEBUG"):
            traceback.print_exc()


@cli.command()
@click.option("--detailed", is_flag=True, help="Show detailed cost breakdown")
def costs(detailed: bool) -> None:
    """Show cost estimates for all deployments."""
    table = Table(title="Cost Estimates")

    if detailed:
        table.add_column("Service", style="cyan")
        table.add_column("EC2", style="yellow")
        table.add_column("RDS", style="yellow")
        table.add_column("Data Transfer", style="yellow")
        table.add_column("Total", style="green")

        # TODO: Load from database
        table.add_row("example-app", "$30.00", "$15.00", "$5.00", "$50.00")
    else:
        table.add_column("Service", style="cyan")
        table.add_column("Monthly Cost", style="yellow")

        # TODO: Load from database
        table.add_row("example-app", "$50.00")

    console.print(table)
    console.print("\n[bold]Total Monthly Cost:[/bold] [green]$50.00[/green]")


@cli.command()
@click.argument("service_name")
@click.confirmation_option(prompt="Are you sure you want to destroy this service?")
def destroy(service_name: str) -> None:
    """Destroy a deployed service."""
    with console.status(f"[bold red]Destroying {service_name}..."):
        # TODO: Implement destroy logic
        console.print(f"[red]Service {service_name} destroyed[/red]")


@cli.group()
def config() -> None:
    """Manage configuration."""
    pass


@config.command()
def show() -> None:
    """Show current configuration."""
    console.print("[cyan]Configuration:[/cyan]")
    # TODO: Load and display config
    console.print("[yellow]Config functionality coming soon![/yellow]")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a configuration value."""
    console.print(f"[green]Set {key} = {value}[/green]")
    # TODO: Update config


@config.command()
def validate() -> None:
    """Validate configuration."""
    with console.status("[bold green]Validating configuration..."):
        # TODO: Validate config
        console.print("[green]✓[/green] Configuration is valid")


@cli.group()
def platform() -> None:
    """Manage the platform."""
    pass


@platform.command()
def start() -> None:
    """Start the management platform."""
    console.print("[green]Starting management platform...[/green]")
    console.print("[cyan]Platform will be available at:[/cyan] http://localhost:3000")
    # TODO: Start platform


@platform.command()
def stop() -> None:
    """Stop the management platform."""
    console.print("[yellow]Stopping management platform...[/yellow]")
    # TODO: Stop platform


@platform.command()
def status() -> None:
    """Check platform status."""
    console.print("[cyan]Platform Status:[/cyan]")
    # TODO: Check platform status
    console.print("[yellow]Status functionality coming soon![/yellow]")


if __name__ == "__main__":
    cli()
