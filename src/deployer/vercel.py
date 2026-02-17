"""Vercel deployment client for frontend applications."""

import os
import time
from typing import Optional, Dict, Any
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config.schemas import VercelConfig

console = Console()


class VercelDeploymentError(Exception):
    """Raised when Vercel deployment fails."""
    pass


class VercelDeployer:
    """Client for deploying frontend applications to Vercel."""
    
    BASE_URL = "https://api.vercel.com"
    
    def __init__(self, config: VercelConfig):
        """
        Initialize Vercel deployer.
        
        Args:
            config: Vercel configuration with API token and optional team
        """
        self.config = config
        self.token = config.api_token.get_secret_value()
        self.team_id = config.team_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Vercel API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            data: JSON payload for POST/PATCH requests
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            VercelDeploymentError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add team_id to params if configured
        if self.team_id:
            params = params or {}
            params["teamId"] = self.team_id
            
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                console.print(f"[yellow]Rate limited, waiting {retry_after}s...[/yellow]")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Vercel API error: {e}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"Vercel API error: {error_data.get('error', {}).get('message', str(e))}"
                except:
                    pass
            raise VercelDeploymentError(error_msg)
        except requests.exceptions.RequestException as e:
            raise VercelDeploymentError(f"Request failed: {e}")
    
    def verify_token(self) -> bool:
        """
        Verify that the API token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            self._make_request("GET", "/v2/user")
            console.print("[green]✓[/green] Vercel token verified")
            return True
        except VercelDeploymentError:
            console.print("[red]✗[/red] Invalid Vercel token")
            return False
    
    def get_or_create_project(self, name: str, github_repo: str) -> str:
        """
        Get existing project or create new one.
        
        Args:
            name: Project name (sanitized, lowercase, no special chars)
            github_repo: GitHub repository in format "owner/repo"
            
        Returns:
            Project ID
        """
        # Try to get existing project
        try:
            response = self._make_request("GET", f"/v9/projects/{name}")
            project_id = response["id"]
            console.print(f"[cyan]Found existing project:[/cyan] {name}")
            return project_id
        except VercelDeploymentError:
            # Project doesn't exist, create it
            pass
        
        # Create new project
        console.print(f"[cyan]Creating new project:[/cyan] {name}")
        
        project_data = {
            "name": name,
            "framework": None,  # Auto-detect
            "gitRepository": {
                "type": "github",
                "repo": github_repo
            }
        }
        
        response = self._make_request("POST", "/v10/projects", data=project_data)
        project_id = response["id"]
        console.print(f"[green]✓[/green] Project created: {project_id}")
        return project_id
    
    def create_deployment(
        self, 
        name: str,
        github_repo: str,
        branch: str = "main",
        production: bool = True,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new deployment from GitHub repository.
        
        Args:
            name: Project name
            github_repo: GitHub repository in format "owner/repo"
            branch: Git branch to deploy (default: main)
            production: Whether this is a production deployment (default: True)
            env_vars: Optional environment variables
            
        Returns:
            Deployment information with URL and status
        """
        # Ensure project exists and get project info
        project_id = self.get_or_create_project(name, github_repo)
        
        console.print(f"\n[bold cyan]Deploying to Vercel...[/bold cyan]")
        console.print(f"Repository: {github_repo}")
        console.print(f"Branch: {branch}")
        console.print(f"Environment: {'production' if production else 'preview'}\n")
        
        # Get project details to find linked repository
        try:
            project_info = self._make_request("GET", f"/v9/projects/{name}")
            
            # Check if project has a linked repository
            if "link" not in project_info or "type" not in project_info["link"]:
                console.print("[yellow]⚠ Project not linked to GitHub. Linking now...[/yellow]")
                # Update project to link GitHub repo
                link_data = {
                    "gitRepository": {
                        "type": "github",
                        "repo": github_repo
                    }
                }
                self._make_request("PATCH", f"/v9/projects/{name}", data=link_data)
                console.print("[green]✓[/green] Project linked to GitHub")
                
                # Re-fetch project info
                project_info = self._make_request("GET", f"/v9/projects/{name}")
            
            # Trigger a deployment via project hook
            # This approach lets Vercel handle the GitHub integration
            deployment_data = {
                "name": name,
                "target": "production" if production else "preview",
                "gitSource": {
                    "type": "github",
                    "ref": branch,
                    "repoId": project_info["link"].get("repoId") if "link" in project_info else None
                }
            }
            
            # Add environment variables if provided
            if env_vars:
                deployment_data["env"] = [
                    {"key": k, "value": v, "target": ["production", "preview"]}
                    for k, v in env_vars.items()
                ]
            
            # Remove repoId if not available, let Vercel auto-connect
            if deployment_data["gitSource"]["repoId"] is None:
                del deployment_data["gitSource"]["repoId"]
            
            response = self._make_request("POST", "/v13/deployments", data=deployment_data)
            
        except VercelDeploymentError as e:
            error_msg = str(e)
            if "repoId" in error_msg or "gitSource" in error_msg:
                # Fallback: Create deployment hook to trigger automatic deployment
                console.print("[yellow]Using alternative deployment method...[/yellow]")
                
                # Get deployments for this project to see if any exist
                try:
                    deployments_response = self._make_request("GET", f"/v6/deployments", params={"projectId": project_id, "limit": 1})
                    
                    if deployments_response.get("deployments"):
                        latest = deployments_response["deployments"][0]
                        deployment_id = latest["uid"]
                        deployment_url = latest.get("url", f"https://{name}.vercel.app")
                        
                        console.print(f"[green]✓[/green] Found existing deployment: {deployment_id}")
                        console.print("[cyan]Note:[/cyan] To trigger a new deployment, push to your GitHub repository")
                        console.print("[cyan]Vercel will automatically deploy on push once the project is linked[/cyan]")
                        
                        return {
                            "id": deployment_id,
                            "url": f"https://{deployment_url}" if not deployment_url.startswith("http") else deployment_url,
                            "status": latest.get("state", "READY"),
                            "project_id": project_id,
                            "name": name
                        }
                    else:
                        raise VercelDeploymentError(
                            "Project created but deployment failed. "
                            "Please link the project manually at https://vercel.com/dashboard and push to your repo."
                        )
                except Exception:
                    raise VercelDeploymentError(
                        f"Deployment failed: {error_msg}\n"
                        "Please link your GitHub repository manually at https://vercel.com/dashboard"
                    )
            else:
                raise e
        
        deployment_id = response["id"]
        deployment_url = response.get("url", f"https://{name}.vercel.app")
        
        console.print(f"[green]✓[/green] Deployment created: {deployment_id}")
        
        # Wait for deployment to complete
        final_status = self._wait_for_deployment(deployment_id)
        
        return {
            "id": deployment_id,
            "url": f"https://{deployment_url}" if not deployment_url.startswith("http") else deployment_url,
            "status": final_status,
            "project_id": project_id,
            "name": name
        }
    
    def _wait_for_deployment(self, deployment_id: str, timeout: int = 600) -> str:
        """
        Wait for deployment to complete and show progress.
        
        Args:
            deployment_id: Deployment ID to monitor
            timeout: Maximum time to wait in seconds (default: 10 minutes)
            
        Returns:
            Final deployment status
            
        Raises:
            VercelDeploymentError: If deployment fails or times out
        """
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Building and deploying...", total=None)
            
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    raise VercelDeploymentError(f"Deployment timed out after {timeout}s")
                
                # Get deployment status
                try:
                    response = self._make_request("GET", f"/v13/deployments/{deployment_id}")
                    
                    # Handle if response is unexpectedly a list
                    if isinstance(response, list):
                        console.print("[yellow]Warning: Unexpected API response format[/yellow]")
                        time.sleep(5)
                        continue
                    
                    status = response.get("readyState", "UNKNOWN")
                    
                    # Update progress message
                    progress.update(task, description=f"[cyan]Status: {status}...")
                    
                    # Check if completed
                    if status == "READY":
                        progress.update(task, description="[green]✓ Deployment ready!")
                        console.print(f"\n[bold green]Deployment successful![/bold green]")
                        return status
                    elif status == "ERROR":
                        error_msg = response.get("error", {}).get("message", "Unknown error")
                        progress.update(task, description="[red]✗ Deployment failed!")
                        console.print(f"\n[bold red]Deployment failed![/bold red]")
                        
                        # Fetch and display build logs
                        console.print("\n[yellow]Fetching build logs...[/yellow]")
                        self._display_deployment_logs(deployment_id)
                        
                        raise VercelDeploymentError(f"Deployment failed: {error_msg}")
                    elif status == "CANCELED":
                        raise VercelDeploymentError("Deployment was canceled")
                    
                    # Still building, wait and retry
                    time.sleep(5)
                    
                except VercelDeploymentError:
                    raise
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not check status: {e}[/yellow]")
                    time.sleep(5)
    
    def get_deployment_logs(self, deployment_id: str, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Get deployment build logs and events.
        
        Args:
            deployment_id: Deployment ID
            limit: Maximum number of events to fetch (default: 100)
            
        Returns:
            List of log event objects
        """
        try:
            response = self._make_request(
                "GET", 
                f"/v2/deployments/{deployment_id}/events",
                params={"limit": limit}
            )
            
            # Handle if response is a list (some API versions return events directly)
            if isinstance(response, list):
                return response
            
            # Handle if response is a dict with events key
            if isinstance(response, dict):
                return response.get("events", [])
            
            console.print(f"[yellow]Warning: Unexpected response type: {type(response)}[/yellow]")
            return []
            
        except VercelDeploymentError as e:
            console.print(f"[yellow]Warning: Could not fetch logs: {e}[/yellow]")
            return []
        except Exception as e:
            console.print(f"[yellow]Warning: Error parsing logs: {e}[/yellow]")
            return []
    
    def _display_deployment_logs(self, deployment_id: str) -> None:
        """
        Fetch and display deployment logs in a readable format.
        
        Args:
            deployment_id: Deployment ID
        """
        events = self.get_deployment_logs(deployment_id, limit=200)
        
        if not events:
            console.print("[yellow]No logs available[/yellow]")
            return
        
        console.print("\n[cyan]═══════════════════ Build Logs ═══════════════════[/cyan]\n")
        
        # Display logs grouped by type
        for event in events:
            try:
                # Skip if event is not a dict
                if not isinstance(event, dict):
                    continue
                
                event_type = event.get("type", "unknown")
                text = event.get("text", "")
                
                # Try to get text from payload if not in main event
                if not text and "payload" in event and isinstance(event["payload"], dict):
                    text = event["payload"].get("text", "")
                
                if not text:
                    continue
                
                # Format based on event type
                if event_type == "stdout":
                    # Standard output - show as-is
                    console.print(text, style="dim")
                elif event_type == "stderr":
                    # Error output - highlight in red
                    console.print(text, style="red")
                elif event_type == "command":
                    # Commands - show in cyan
                    console.print(f"$ {text}", style="cyan bold")
                elif event_type == "build-step":
                    # Build steps - show in yellow
                    console.print(f"\n▶ {text}", style="yellow bold")
                else:
                    # Other events
                    if "error" in text.lower() or "fail" in text.lower():
                        console.print(text, style="red")
                    else:
                        console.print(text)
            except Exception as e:
                # Skip malformed events
                if os.environ.get("DEBUG"):
                    console.print(f"[dim]Debug: Error parsing event: {e}[/dim]")
        
        console.print("\n[cyan]═══════════════════════════════════════════════════[/cyan]\n")
    
    def delete_deployment(self, deployment_id: str) -> bool:
        """
        Delete a deployment.
        
        Args:
            deployment_id: Deployment ID to delete
            
        Returns:
            True if successful
        """
        try:
            self._make_request("DELETE", f"/v13/deployments/{deployment_id}")
            console.print(f"[green]✓[/green] Deployment deleted: {deployment_id}")
            return True
        except VercelDeploymentError as e:
            console.print(f"[red]✗[/red] Failed to delete deployment: {e}")
            return False
    
    def delete_project(self, project_name: str) -> bool:
        """
        Delete a project and all its deployments.
        
        Args:
            project_name: Project name to delete
            
        Returns:
            True if successful
        """
        try:
            self._make_request("DELETE", f"/v9/projects/{project_name}")
            console.print(f"[green]✓[/green] Project deleted: {project_name}")
            return True
        except VercelDeploymentError as e:
            console.print(f"[red]✗[/red] Failed to delete project: {e}")
            return False
    
    def list_deployments(self, project_name: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        List all deployments, optionally filtered by project.
        
        Args:
            project_name: Optional project name to filter by
            
        Returns:
            List of deployment objects
        """
        params = {}
        if project_name:
            params["projectId"] = project_name
        
        try:
            response = self._make_request("GET", "/v6/deployments", params=params)
            return response.get("deployments", [])
        except VercelDeploymentError:
            return []
