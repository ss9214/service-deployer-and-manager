"""Secure credential management using system keyring."""

import os
import keyring
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv

console = Console()

# Load .env file if it exists
load_dotenv()

# Service name for keyring storage
SERVICE_NAME = "service-deployer-manager"


class CredentialManager:
    """Manages secure storage of API tokens and credentials."""
    
    @staticmethod
    def get_vercel_token() -> Optional[str]:
        """
        Get Vercel token from environment, .env file, or keyring.
        
        Priority:
        1. VERCEL_TOKEN environment variable
        2. .env file (loaded automatically)
        3. Stored in system keyring
        
        Returns:
            Token string or None if not found
        """
        # Check environment (includes .env file via load_dotenv())
        token = os.environ.get("VERCEL_TOKEN")
        if token:
            return token
        
        # Check keyring
        token = keyring.get_password(SERVICE_NAME, "vercel_token")
        return token
    
    @staticmethod
    def set_vercel_token(token: str) -> None:
        """
        Store Vercel token in system keyring.
        
        Args:
            token: Vercel API token
        """
        keyring.set_password(SERVICE_NAME, "vercel_token", token)
        console.print("[green]✓[/green] Vercel token saved securely")
    
    @staticmethod
    def delete_vercel_token() -> None:
        """Delete Vercel token from keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, "vercel_token")
            console.print("[green]✓[/green] Vercel token deleted")
        except keyring.errors.PasswordDeleteError:
            console.print("[yellow]⚠[/yellow] No token found to delete")
    
    @staticmethod
    def get_aws_credentials() -> Optional[dict]:
        """
        Get AWS credentials from environment, .env file, or keyring.
        
        Returns:
            Dict with access_key and secret_key, or None
        """
        # Check environment first
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        
        if access_key and secret_key:
            return {"access_key": access_key, "secret_key": secret_key}
        
        # Check keyring
        access_key = keyring.get_password(SERVICE_NAME, "aws_access_key")
        secret_key = keyring.get_password(SERVICE_NAME, "aws_secret_key")
        
        if access_key and secret_key:
            return {"access_key": access_key, "secret_key": secret_key}
        
        return None
    
    @staticmethod
    def set_aws_credentials(access_key: str, secret_key: str) -> None:
        """
        Store AWS credentials in system keyring.
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
        """
        keyring.set_password(SERVICE_NAME, "aws_access_key", access_key)
        keyring.set_password(SERVICE_NAME, "aws_secret_key", secret_key)
        console.print("[green]✓[/green] AWS credentials saved securely")
    
    @staticmethod
    def delete_aws_credentials() -> None:
        """Delete AWS credentials from keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, "aws_access_key")
            keyring.delete_password(SERVICE_NAME, "aws_secret_key")
            console.print("[green]✓[/green] AWS credentials deleted")
        except keyring.errors.PasswordDeleteError:
            console.print("[yellow]⚠[/yellow] No AWS credentials found to delete")
    
    @staticmethod
    def get_github_token() -> Optional[str]:
        """Get GitHub token from environment, .env file, or keyring."""
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token
        
        return keyring.get_password(SERVICE_NAME, "github_token")
    
    @staticmethod
    def set_github_token(token: str) -> None:
        """Store GitHub token in system keyring."""
        keyring.set_password(SERVICE_NAME, "github_token", token)
        console.print("[green]✓[/green] GitHub token saved securely")
    
    @staticmethod
    def delete_github_token() -> None:
        """Delete GitHub token from keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, "github_token")
            console.print("[green]✓[/green] GitHub token deleted")
        except keyring.errors.PasswordDeleteError:
            console.print("[yellow]⚠[/yellow] No token found to delete")
    
    @staticmethod
    def list_stored_credentials() -> dict[str, bool]:
        """
        Check which credentials are stored.
        
        Returns:
            Dict mapping credential name to whether it's stored
        """
        return {
            "vercel": keyring.get_password(SERVICE_NAME, "vercel_token") is not None,
            "aws": (
                keyring.get_password(SERVICE_NAME, "aws_access_key") is not None
                and keyring.get_password(SERVICE_NAME, "aws_secret_key") is not None
            ),
            "github": keyring.get_password(SERVICE_NAME, "github_token") is not None,
        }
    
    @staticmethod
    def clear_all_credentials() -> None:
        """Delete all stored credentials."""
        CredentialManager.delete_vercel_token()
        CredentialManager.delete_aws_credentials()
        CredentialManager.delete_github_token()
        console.print("\n[green]✓[/green] All credentials cleared")
