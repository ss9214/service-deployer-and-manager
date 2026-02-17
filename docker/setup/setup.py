#!/usr/bin/env python3
"""Interactive setup script for the deployment platform."""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from getpass import getpass
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║   Service Deployer & Manager - Initial Setup     ║
    ║   Automated Web App Deployment Platform          ║
    ╚═══════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold cyan"))


def collect_aws_config():
    """Collect AWS configuration."""
    console.print("\n[bold cyan]AWS Configuration[/bold cyan]")
    console.print("We need your AWS credentials to provision infrastructure.\n")

    return {
        "access_key_id": Prompt.ask("AWS Access Key ID", password=True),
        "secret_access_key": Prompt.ask("AWS Secret Access Key", password=True),
        "region": Prompt.ask("AWS Region", default="us-east-1"),
    }


def collect_vercel_config():
    """Collect Vercel configuration."""
    console.print("\n[bold cyan]Vercel Configuration[/bold cyan]")
    console.print("Get your token at: https://vercel.com/account/tokens\n")

    return {
        "access_token": Prompt.ask("Vercel Access Token", password=True),
        "team_id": Prompt.ask("Vercel Team ID (optional, press Enter to skip)", default=""),
    }


def collect_github_config():
    """Collect GitHub configuration."""
    console.print("\n[bold cyan]GitHub Configuration[/bold cyan]")
    console.print("Create a token at: https://github.com/settings/tokens\n")
    console.print("Required scopes: repo, read:org\n")

    return {
        "personal_access_token": Prompt.ask("GitHub Personal Access Token", password=True),
        "username": Prompt.ask("GitHub Username"),
    }


def collect_domain_config():
    """Collect domain configuration."""
    console.print("\n[bold cyan]Domain Configuration[/bold cyan]")

    use_custom_domain = Confirm.ask("Do you have a custom domain?", default=False)

    if use_custom_domain:
        return {
            "root_domain": Prompt.ask("Root domain (e.g., example.com)"),
            "use_custom_domain": True,
            "ssl_enabled": True,
        }
    else:
        return {"use_custom_domain": False, "ssl_enabled": True}


def collect_platform_config():
    """Collect platform configuration."""
    console.print("\n[bold cyan]Platform Configuration[/bold cyan]")

    return {
        "platform_name": Prompt.ask("Platform Name", default="My Deployment Platform"),
        "platform_port": int(Prompt.ask("Management Platform Port", default="3000")),
    }


def save_config(config, output_path):
    """Save configuration to YAML file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(f"\n[green]✓[/green] Configuration saved to {output_path}")


def run_terraform_init(terraform_dir):
    """Initialize Terraform."""
    console.print("\n[bold cyan]Initializing Terraform...[/bold cyan]")

    try:
        subprocess.run(
            ["terraform", "init"],
            cwd=terraform_dir,
            check=True,
            capture_output=True,
        )
        console.print("[green]✓[/green] Terraform initialized")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Terraform initialization failed: {e}")
        return False


def run_terraform_apply(terraform_dir, var_file):
    """Apply Terraform configuration."""
    console.print("\n[bold cyan]Provisioning AWS infrastructure...[/bold cyan]")
    console.print("[yellow]This may take 15-20 minutes. Please be patient.[/yellow]\n")

    try:
        # Run terraform plan first
        console.print("Running Terraform plan...")
        subprocess.run(
            ["terraform", "plan", f"-var-file={var_file}"],
            cwd=terraform_dir,
            check=True,
        )

        # Confirm before applying
        if not Confirm.ask("\nProceed with infrastructure provisioning?", default=True):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return False

        # Apply
        subprocess.run(
            ["terraform", "apply", "-auto-approve", f"-var-file={var_file}"],
            cwd=terraform_dir,
            check=True,
        )

        console.print("\n[green]✓[/green] Infrastructure provisioned successfully")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗[/red] Infrastructure provisioning failed: {e}")
        return False


def create_terraform_vars(config, output_path):
    """Create Terraform variables file."""
    tfvars_content = f"""
aws_access_key = "{config['aws']['access_key_id']}"
aws_secret_key = "{config['aws']['secret_access_key']}"
aws_region     = "{config['aws']['region']}"
platform_name  = "{config.get('platform_name', 'deployment-platform')}"
"""

    with open(output_path, "w") as f:
        f.write(tfvars_content)

    console.print(f"[green]✓[/green] Terraform variables created")


def display_summary(config):
    """Display configuration summary."""
    console.print("\n[bold cyan]Configuration Summary[/bold cyan]")
    console.print(f"AWS Region: {config['aws']['region']}")
    console.print(f"Platform Name: {config.get('platform_name', 'N/A')}")
    console.print(f"Custom Domain: {config['domain'].get('root_domain', 'Not configured')}")
    console.print(f"Platform Port: {config.get('platform_port', 3000)}")


def main():
    """Main setup flow."""
    print_banner()

    console.print("[yellow]This setup will guide you through configuring your deployment platform.[/yellow]\n")

    # Collect all configuration
    config = {
        "aws": collect_aws_config(),
        "vercel": collect_vercel_config(),
        "github": collect_github_config(),
        "domain": collect_domain_config(),
    }

    platform_config = collect_platform_config()
    config.update(platform_config)

    # Display summary
    display_summary(config)

    if not Confirm.ask("\n[bold]Save configuration and proceed?[/bold]", default=True):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    # Save configuration
    config_dir = Path("/workspace/config")
    save_config(config, config_dir / "user_config.yaml")

    # Create Terraform variables
    terraform_dir = Path("/workspace/terraform")
    create_terraform_vars(config, terraform_dir / "terraform.tfvars")

    # Initialize and apply Terraform
    if run_terraform_init(terraform_dir):
        if run_terraform_apply(terraform_dir, "terraform.tfvars"):
            console.print("\n[bold green]🎉 Setup completed successfully![/bold green]")
            console.print("\nYou can now use the CLI to deploy applications:")
            console.print("  [cyan]deployer deploy <github-url>[/cyan]")
            console.print(f"\nManagement platform: [cyan]http://localhost:{config.get('platform_port', 3000)}[/cyan]")
        else:
            console.print("\n[red]Setup failed during infrastructure provisioning.[/red]")
            sys.exit(1)
    else:
        console.print("\n[red]Setup failed during Terraform initialization.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
