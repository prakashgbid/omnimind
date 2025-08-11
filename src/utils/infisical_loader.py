"""
Infisical Secret Loader for OmniMind

Automatically loads API keys from Infisical.
"""

import os
import subprocess
import json
from typing import Dict, Optional


class InfisicalLoader:
    """Load secrets from Infisical."""
    
    @staticmethod
    def load_secrets(project_id: str = "74508327-34e2-43c2-b5d1-dda08dad998b") -> Dict[str, str]:
        """
        Load secrets from Infisical using CLI.
        
        Requires Infisical CLI to be installed and logged in.
        """
        try:
            # Check if Infisical CLI is installed
            result = subprocess.run(
                ["infisical", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Infisical CLI not installed")
                print("   Install with: brew install infisical/get-cli/infisical")
                return {}
            
            # Pull secrets
            result = subprocess.run(
                ["infisical", "secrets", "get", "--plain"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                secrets = {}
                for line in result.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key] = value
                
                print(f"✅ Loaded {len(secrets)} secrets from Infisical")
                return secrets
            else:
                print("❌ Failed to load secrets from Infisical")
                return {}
                
        except Exception as e:
            print(f"❌ Error loading from Infisical: {e}")
            return {}
    
    @staticmethod
    def update_env_file(secrets: Dict[str, str], env_path: str = ".env"):
        """Update .env file with secrets from Infisical."""
        
        # Read existing .env
        existing = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing[key] = value
        
        # Update with new secrets
        existing.update(secrets)
        
        # Write back
        with open(env_path, 'w') as f:
            for key, value in existing.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Updated {env_path} with Infisical secrets")


def sync_from_infisical():
    """Quick function to sync secrets from Infisical to .env"""
    loader = InfisicalLoader()
    secrets = loader.load_secrets()
    
    if secrets:
        # Filter for API keys we care about
        api_keys = {
            k: v for k, v in secrets.items()
            if 'API_KEY' in k or 'TOKEN' in k
        }
        
        if api_keys:
            loader.update_env_file(api_keys)
            print("\nFound API Keys:")
            for key in api_keys:
                print(f"  • {key}")
        else:
            print("No API keys found in Infisical")
    else:
        print("Could not load secrets from Infisical")


if __name__ == "__main__":
    sync_from_infisical()