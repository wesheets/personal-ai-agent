"""
GitHub Commit Tool for the Personal AI Agent System.

This module provides functionality to commit and push code changes to GitHub repositories.
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("github_commit")

def run(
    repo_url: str,
    files: List[Dict[str, str]],
    commit_message: str,
    branch: str = "main",
    token: Optional[str] = None,
    author_name: Optional[str] = None,
    author_email: Optional[str] = None,
    create_branch: bool = False,
    create_pr: bool = False,
    pr_title: Optional[str] = None,
    pr_body: Optional[str] = None,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["github", "code_commit", "development"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Commit and push code changes to a GitHub repository.
    
    Args:
        repo_url: GitHub repository URL or path
        files: List of files to commit, each with 'path' and 'content' keys
        commit_message: Commit message
        branch: Branch to commit to (default: "main")
        token: GitHub personal access token for authentication
        author_name: Git author name
        author_email: Git author email
        create_branch: Whether to create a new branch
        create_pr: Whether to create a pull request
        pr_title: Pull request title (required if create_pr is True)
        pr_body: Pull request description
        store_memory: Whether to store the commit information in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing commit results and metadata
    """
    logger.info(f"Committing to GitHub repository: {repo_url}")
    
    try:
        # In a real implementation, this would use actual Git operations
        # For now, we'll simulate the GitHub commit process
        
        # Validate inputs
        if not repo_url:
            raise ValueError("Repository URL is required")
            
        if not files or not isinstance(files, list):
            raise ValueError("Files must be provided as a list of dictionaries")
            
        for file in files:
            if not isinstance(file, dict) or 'path' not in file or 'content' not in file:
                raise ValueError("Each file must be a dictionary with 'path' and 'content' keys")
                
        if not commit_message:
            raise ValueError("Commit message is required")
            
        if create_pr and not pr_title:
            raise ValueError("PR title is required when creating a pull request")
        
        # Simulate GitHub commit
        commit_result = _simulate_github_commit(
            repo_url, files, commit_message, branch, token,
            author_name, author_email, create_branch, create_pr,
            pr_title, pr_body
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                file_paths = [file['path'] for file in files]
                
                memory_entry = {
                    "type": "github_commit",
                    "repository": repo_url,
                    "branch": branch,
                    "commit_message": commit_message,
                    "files_changed": file_paths,
                    "commit_hash": commit_result.get("commit_hash", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                if create_pr:
                    memory_entry["pull_request"] = {
                        "title": pr_title,
                        "url": commit_result.get("pr_url", "")
                    }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored GitHub commit information in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store GitHub commit in memory: {str(e)}")
        
        return commit_result
    except Exception as e:
        error_msg = f"Error committing to GitHub: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "repository": repo_url
        }

def _simulate_github_commit(
    repo_url: str,
    files: List[Dict[str, str]],
    commit_message: str,
    branch: str,
    token: Optional[str],
    author_name: Optional[str],
    author_email: Optional[str],
    create_branch: bool,
    create_pr: bool,
    pr_title: Optional[str],
    pr_body: Optional[str]
) -> Dict[str, Any]:
    """
    Simulate GitHub commit operations for development purposes.
    
    Args:
        repo_url: GitHub repository URL or path
        files: List of files to commit
        commit_message: Commit message
        branch: Branch to commit to
        token: GitHub personal access token
        author_name: Git author name
        author_email: Git author email
        create_branch: Whether to create a new branch
        create_pr: Whether to create a pull request
        pr_title: Pull request title
        pr_body: Pull request description
        
    Returns:
        Dictionary with simulated commit results
    """
    # Extract repository name from URL
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_owner = repo_url.split("/")[-2] if "/" in repo_url else "owner"
    
    # Generate a simulated commit hash
    commit_hash = f"{hash(repo_url + commit_message) % 10000000:07x}"
    
    # Prepare result
    result = {
        "success": True,
        "repository": repo_url,
        "branch": branch,
        "commit_message": commit_message,
        "commit_hash": commit_hash,
        "files_changed": len(files),
        "file_paths": [file['path'] for file in files],
        "commit_url": f"https://github.com/{repo_owner}/{repo_name}/commit/{commit_hash}"
    }
    
    # Add branch creation info if applicable
    if create_branch:
        result["branch_created"] = True
        result["branch_url"] = f"https://github.com/{repo_owner}/{repo_name}/tree/{branch}"
    
    # Add PR info if applicable
    if create_pr:
        pr_number = hash(repo_url + pr_title) % 1000
        result["pr_created"] = True
        result["pr_number"] = pr_number
        result["pr_title"] = pr_title
        result["pr_url"] = f"https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}"
    
    return result
