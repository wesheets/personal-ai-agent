"""
Orchestrator Credential Intake

This module implements the credential intake system for the Orchestrator, allowing
it to securely gather and store credentials needed for execution.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

class CredentialManager:
    """
    Manages the secure storage and retrieval of credentials.
    
    This class handles the intake of credentials from operators and provides
    secure access to those credentials for tools that need them.
    """
    
    def __init__(self, secrets_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/secrets"):
        """
        Initialize the credential manager.
        
        Args:
            secrets_directory: Directory to store credential files
        """
        self.secrets_directory = secrets_directory
        os.makedirs(secrets_directory, exist_ok=True)
        
    def store_credentials(self, goal_id: str, credentials: Dict[str, Any]) -> str:
        """
        Store credentials for a goal.
        
        Args:
            goal_id: ID of the goal these credentials are for
            credentials: Dictionary of credentials to store
            
        Returns:
            ID of the stored credentials
        """
        # Generate a unique ID for these credentials
        credential_id = str(uuid.uuid4())
        
        # Create the credential object
        credential_obj = {
            "credential_id": credential_id,
            "goal_id": goal_id,
            "created_at": datetime.datetime.now().isoformat(),
            "credentials": self._encrypt_credentials(credentials)
        }
        
        # Save the credentials to file
        self._save_credentials(credential_id, credential_obj)
        
        return credential_id
        
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive credential values.
        
        In a production environment, this would use proper encryption.
        For this implementation, we'll use a simple obfuscation technique.
        
        Args:
            credentials: Dictionary of credentials to encrypt
            
        Returns:
            Dictionary with encrypted credential values
        """
        # In a real implementation, this would use proper encryption
        # For now, we'll just mark sensitive fields as encrypted
        encrypted = {}
        
        for key, value in credentials.items():
            if isinstance(value, dict):
                # Recursively encrypt nested dictionaries
                encrypted[key] = self._encrypt_credentials(value)
            elif key in ["github_token", "stripe_keys", "api_key", "password", "secret", "token"]:
                # Mark sensitive fields as encrypted
                # In a real implementation, this would actually encrypt the value
                encrypted[key] = f"ENCRYPTED:{value}"
            else:
                # Non-sensitive fields are stored as-is
                encrypted[key] = value
                
        return encrypted
        
    def _decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive credential values.
        
        Args:
            encrypted_credentials: Dictionary of encrypted credentials
            
        Returns:
            Dictionary with decrypted credential values
        """
        # In a real implementation, this would use proper decryption
        decrypted = {}
        
        for key, value in encrypted_credentials.items():
            if isinstance(value, dict):
                # Recursively decrypt nested dictionaries
                decrypted[key] = self._decrypt_credentials(value)
            elif isinstance(value, str) and value.startswith("ENCRYPTED:"):
                # Decrypt sensitive fields
                # In a real implementation, this would actually decrypt the value
                decrypted[key] = value[10:]  # Remove "ENCRYPTED:" prefix
            else:
                # Non-sensitive fields are returned as-is
                decrypted[key] = value
                
        return decrypted
        
    def _save_credentials(self, credential_id: str, credential_obj: Dict[str, Any]) -> str:
        """
        Save credentials to a file.
        
        Args:
            credential_id: ID of the credentials
            credential_obj: Credential object to save
            
        Returns:
            Path to the saved credential file
        """
        # Generate the filename
        filename = f"cred_{credential_id}.json"
        filepath = os.path.join(self.secrets_directory, filename)
        
        # Write the credentials to file
        with open(filepath, "w") as f:
            json.dump(credential_obj, f, indent=2)
            
        return filepath
        
    def get_credentials(self, credential_id: str) -> Dict[str, Any]:
        """
        Get credentials by ID.
        
        Args:
            credential_id: ID of the credentials to retrieve
            
        Returns:
            Dictionary of decrypted credentials
        """
        # Generate the filename
        filename = f"cred_{credential_id}.json"
        filepath = os.path.join(self.secrets_directory, filename)
        
        # Read the credentials from file
        try:
            with open(filepath, "r") as f:
                credential_obj = json.load(f)
                
            # Decrypt the credentials
            decrypted_credentials = self._decrypt_credentials(credential_obj["credentials"])
            
            return decrypted_credentials
        except FileNotFoundError:
            raise ValueError(f"Credentials with ID {credential_id} not found")
            
    def get_credentials_for_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a specific goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Dictionary of decrypted credentials or None if not found
        """
        # List all credential files in the directory
        for filename in os.listdir(self.secrets_directory):
            if filename.startswith("cred_") and filename.endswith(".json"):
                filepath = os.path.join(self.secrets_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        credential_obj = json.load(f)
                        
                    # Check if these credentials are for the specified goal
                    if credential_obj["goal_id"] == goal_id:
                        # Decrypt the credentials
                        decrypted_credentials = self._decrypt_credentials(credential_obj["credentials"])
                        
                        return {
                            "credential_id": credential_obj["credential_id"],
                            "created_at": credential_obj["created_at"],
                            "credentials": decrypted_credentials
                        }
                except Exception as e:
                    print(f"Error loading credentials from {filepath}: {e}")
                    
        return None
        
    def list_credentials(self) -> List[Dict[str, Any]]:
        """
        List all stored credentials (without sensitive values).
        
        Returns:
            List of credential summary dictionaries
        """
        credentials = []
        
        # List all credential files in the directory
        for filename in os.listdir(self.secrets_directory):
            if filename.startswith("cred_") and filename.endswith(".json"):
                filepath = os.path.join(self.secrets_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        credential_obj = json.load(f)
                        
                    # Create a summary without sensitive values
                    summary = {
                        "credential_id": credential_obj["credential_id"],
                        "goal_id": credential_obj["goal_id"],
                        "created_at": credential_obj["created_at"],
                        "credential_types": list(credential_obj["credentials"].keys())
                    }
                    
                    credentials.append(summary)
                except Exception as e:
                    print(f"Error loading credentials from {filepath}: {e}")
                    
        # Sort credentials by created_at (newest first)
        credentials.sort(key=lambda c: c["created_at"], reverse=True)
        
        return credentials
        
    def delete_credentials(self, credential_id: str) -> bool:
        """
        Delete credentials by ID.
        
        Args:
            credential_id: ID of the credentials to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Generate the filename
        filename = f"cred_{credential_id}.json"
        filepath = os.path.join(self.secrets_directory, filename)
        
        # Delete the file if it exists
        try:
            os.remove(filepath)
            return True
        except FileNotFoundError:
            return False
            
    def inject_credentials(self, tool_name: str, tool_params: Dict[str, Any], goal_id: str) -> Dict[str, Any]:
        """
        Inject credentials into tool parameters.
        
        Args:
            tool_name: Name of the tool being called
            tool_params: Parameters for the tool
            goal_id: ID of the goal
            
        Returns:
            Updated tool parameters with injected credentials
        """
        # Get credentials for the goal
        creds = self.get_credentials_for_goal(goal_id)
        if not creds:
            return tool_params
            
        credentials = creds["credentials"]
        
        # Clone the tool parameters
        updated_params = tool_params.copy()
        
        # Inject credentials based on tool name
        if tool_name == "deploy.github.setup":
            if "github_repo" in credentials and "github_token" in credentials:
                updated_params["repo"] = credentials["github_repo"]
                updated_params["token"] = credentials["github_token"]
                
        elif tool_name == "env.secret.check":
            # Add all credentials as environment variables
            if "env_vars" not in updated_params:
                updated_params["env_vars"] = {}
                
            # Flatten nested credentials for environment variables
            flat_creds = self._flatten_dict(credentials)
            for key, value in flat_creds.items():
                updated_params["env_vars"][key.upper()] = value
                
        elif tool_name == "payment.init":
            if "stripe_keys" in credentials:
                updated_params["api_key"] = credentials["stripe_keys"].get("secret_key")
                updated_params["public_key"] = credentials["stripe_keys"].get("public_key")
                
        # Add more tool-specific credential injection as needed
        
        return updated_params
        
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """
        Flatten a nested dictionary.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested dictionaries
            sep: Separator for keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
                
        return dict(items)


class CredentialIntake:
    """
    Handles the intake of credentials from operators.
    
    This class provides methods for gathering credentials and storing them
    securely using the CredentialManager.
    """
    
    def __init__(self, credential_manager: CredentialManager):
        """
        Initialize the credential intake.
        
        Args:
            credential_manager: CredentialManager instance
        """
        self.credential_manager = credential_manager
        
    def gather_credentials(self, goal_id: str, credentials: Dict[str, Any]) -> str:
        """
        Gather and store credentials for a goal.
        
        Args:
            goal_id: ID of the goal these credentials are for
            credentials: Dictionary of credentials to store
            
        Returns:
            ID of the stored credentials
        """
        # Validate required credentials based on the provided data
        self._validate_credentials(credentials)
        
        # Store the credentials
        credential_id = self.credential_manager.store_credentials(goal_id, credentials)
        
        return credential_id
        
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Validate that the provided credentials contain required fields.
        
        Args:
            credentials: Dictionary of credentials to validate
            
        Raises:
            ValueError: If required credentials are missing
        """
        # Check for required fields based on what's provided
        
        # If GitHub credentials are provided, ensure both repo and token are present
        if "github_repo" in credentials and "github_token" not in credentials:
            raise ValueError("GitHub token is required when GitHub repo is provided")
            
        # If Stripe credentials are provided, ensure they contain required keys
        if "stripe_keys" in credentials:
            stripe_keys = credentials["stripe_keys"]
            if not isinstance(stripe_keys, dict):
                raise ValueError("stripe_keys must be a dictionary")
                
            if "secret_key" not in stripe_keys:
                raise ValueError("Stripe secret key is required in stripe_keys")
                
        # Validate environment setting if provided
        if "environment" in credentials:
            env = credentials["environment"]
            if env not in ["staging", "production"]:
                raise ValueError("environment must be either 'staging' or 'production'")
                
    def get_credential_requirements(self, goal_type: str) -> Dict[str, Any]:
        """
        Get the credential requirements for a specific goal type.
        
        Args:
            goal_type: Type of goal (website, application, marketing, content, general)
            
        Returns:
            Dictionary of credential requirements
        """
        # Define credential requirements based on goal type
        if goal_type == "website":
            return {
                "required": ["hosting_provider", "github_repo", "github_token"],
                "optional": ["domain_provider", "stripe_keys", "api_credentials"],
                "environment": ["staging", "production"]
            }
        elif goal_type == "application":
            return {
                "required": ["github_repo", "github_token"],
                "optional": ["hosting_provider", "domain_provider", "stripe_keys", "api_credentials"],
                "environment": ["staging", "production"]
            }
        elif goal_type == "marketing":
            return {
                "required": [],
                "optional": ["github_repo", "github_token", "api_credentials"],
                "environment": ["staging", "production"]
            }
        elif goal_type == "content":
            return {
                "required": [],
                "optional": ["github_repo", "github_token", "api_credentials"],
                "environment": ["staging", "production"]
            }
        else:  # general
            return {
                "required": [],
                "optional": ["hosting_provider", "github_repo", "github_token", "domain_provider", "stripe_keys", "api_credentials"],
                "environment": ["staging", "production"]
            }
