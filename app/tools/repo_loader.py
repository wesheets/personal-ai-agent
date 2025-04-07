"""
Repo Loader Tool for Autonomous Coding Agents.

This module provides functionality to load the structure of a GitHub repository
into agent memory for better context awareness.
"""

import os
import sys
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union
import git

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoLoader:
    """
    Tool for loading the structure of a GitHub repository into agent memory.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the RepoLoader.
        
        Args:
            memory_manager: Optional memory manager for storing repository structure
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        repo_path: str,
        include_file_contents: bool = False,
        file_types: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        max_file_size: int = 1024 * 1024,  # 1MB
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Load the structure of a GitHub repository.
        
        Args:
            repo_path: Path to the local repository
            include_file_contents: Whether to include file contents in the result
            file_types: Optional list of file extensions to include (e.g., ['.py', '.js'])
            exclude_dirs: Optional list of directories to exclude (e.g., ['node_modules', 'venv'])
            max_file_size: Maximum file size to include contents for (in bytes)
            store_memory: Whether to store repository structure in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing repository structure
        """
        try:
            # Validate inputs
            if not os.path.exists(repo_path):
                return {
                    "status": "error",
                    "error": f"Repository path does not exist: {repo_path}"
                }
            
            if not os.path.isdir(repo_path):
                return {
                    "status": "error",
                    "error": f"Repository path is not a directory: {repo_path}"
                }
            
            # Set default file types if not provided
            if file_types is None:
                file_types = ['.py', '.js', '.ts', '.html', '.css', '.md', '.json', '.yaml', '.yml']
            
            # Set default exclude dirs if not provided
            if exclude_dirs is None:
                exclude_dirs = ['node_modules', 'venv', '.venv', 'env', '.env', '__pycache__', '.git', 'dist', 'build']
            
            # Check if it's a git repository
            try:
                repo = git.Repo(repo_path)
                is_git_repo = True
                
                # Get repository information
                repo_info = {
                    "name": os.path.basename(repo.working_dir),
                    "remote_urls": [remote.url for remote in repo.remotes],
                    "active_branch": repo.active_branch.name,
                    "branches": [branch.name for branch in repo.branches],
                    "last_commit": {
                        "hash": repo.head.commit.hexsha,
                        "author": repo.head.commit.author.name,
                        "email": repo.head.commit.author.email,
                        "date": repo.head.commit.committed_datetime.isoformat(),
                        "message": repo.head.commit.message
                    }
                }
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                is_git_repo = False
                repo_info = {
                    "name": os.path.basename(repo_path),
                    "is_git_repo": False
                }
            
            # Scan repository structure
            structure = self._scan_directory(
                repo_path,
                include_file_contents,
                file_types,
                exclude_dirs,
                max_file_size
            )
            
            # Prepare result
            result = {
                "status": "success",
                "repo_path": repo_path,
                "is_git_repo": is_git_repo,
                "repo_info": repo_info,
                "structure": structure
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "repo_structure",
                    "repo_path": repo_path,
                    "is_git_repo": is_git_repo,
                    "repo_info": repo_info,
                    "structure": structure
                }
                
                tags = memory_tags or ["repo", "structure"]
                
                # Add repo name to tags
                repo_name = repo_info["name"]
                if repo_name not in tags:
                    tags.append(repo_name)
                
                await self.memory_manager.store(
                    input_text=f"Load repository structure for {repo_name}",
                    output_text=f"Loaded repository structure with {len(structure['files'])} files and {len(structure['directories'])} directories.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading repository structure: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _scan_directory(
        self,
        directory: str,
        include_file_contents: bool,
        file_types: List[str],
        exclude_dirs: List[str],
        max_file_size: int,
        relative_path: str = ""
    ) -> Dict[str, Any]:
        """
        Recursively scan a directory and build its structure.
        
        Args:
            directory: Directory to scan
            include_file_contents: Whether to include file contents
            file_types: List of file extensions to include
            exclude_dirs: List of directories to exclude
            max_file_size: Maximum file size to include contents for
            relative_path: Relative path from the repository root
            
        Returns:
            Dictionary containing directory structure
        """
        files = []
        directories = []
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            item_relative_path = os.path.join(relative_path, item) if relative_path else item
            
            if os.path.isdir(item_path):
                # Skip excluded directories
                if item in exclude_dirs:
                    continue
                
                # Recursively scan subdirectory
                subdirectory = self._scan_directory(
                    item_path,
                    include_file_contents,
                    file_types,
                    exclude_dirs,
                    max_file_size,
                    item_relative_path
                )
                
                directories.append({
                    "name": item,
                    "path": item_relative_path,
                    "structure": subdirectory
                })
            
            elif os.path.isfile(item_path):
                # Check file extension
                _, ext = os.path.splitext(item)
                if file_types and ext.lower() not in file_types:
                    continue
                
                file_info = {
                    "name": item,
                    "path": item_relative_path,
                    "extension": ext.lower(),
                    "size": os.path.getsize(item_path)
                }
                
                # Include file contents if requested and file is not too large
                if include_file_contents and os.path.getsize(item_path) <= max_file_size:
                    try:
                        with open(item_path, 'r', encoding='utf-8') as f:
                            file_info["contents"] = f.read()
                    except UnicodeDecodeError:
                        # Skip binary files
                        file_info["contents"] = "<binary file>"
                
                files.append(file_info)
        
        return {
            "files": files,
            "directories": directories
        }
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_repo_loader(memory_manager=None):
    """
    Get a RepoLoader instance.
    
    Args:
        memory_manager: Optional memory manager for storing repository structure
        
    Returns:
        RepoLoader instance
    """
    return RepoLoader(memory_manager=memory_manager)
