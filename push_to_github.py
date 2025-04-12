#!/usr/bin/env python3
import os
import subprocess
import sys

def push_to_github():
    """Push the memory system fixes to GitHub on the main branch"""
    
    # Get the GitHub token from environment variable or use the latest provided token
    github_token = os.environ.get('GITHUB_TOKEN', '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')
    github_username = "wesheets"
    repo_name = "personal-ai-agent"
    branch_name = "main"
    
    try:
        # Configure Git
        subprocess.run(["git", "config", "user.name", "Manus AI Agent"], check=True)
        subprocess.run(["git", "config", "user.email", "manus-agent@example.com"], check=True)
        
        # Commit the changes
        try:
            # Try to checkout existing branch
            subprocess.run(["git", "checkout", branch_name], check=True)
            print(f"Checked out existing branch: {branch_name}")
        except subprocess.CalledProcessError:
            # If branch doesn't exist, create it
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            print(f"Created and checked out new branch: {branch_name}")
            
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "feat: deploy memory system fixes with schema + regression tests"], check=True)
        print("Changes committed successfully")
        
        # Add remote
        remote_url = f"https://{github_username}:{github_token}@github.com/{github_username}/{repo_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        print("Remote added successfully")
        
        # Push to GitHub
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
        print(f"Successfully pushed to GitHub branch: {branch_name}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = push_to_github()
    sys.exit(0 if success else 1)
