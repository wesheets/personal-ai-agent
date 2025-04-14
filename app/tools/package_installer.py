"""
Package Installer Tool for Autonomous Coding Agents.

This module provides functionality to detect missing Python packages and install them securely.
"""

import os
import sys
import subprocess
import logging
import tempfile
import re
import json
import importlib
import pkg_resources
from typing import Dict, Any, List, Optional, Union, Set, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PackageInstaller:
    """
    Tool for detecting missing Python packages and installing them securely.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the PackageInstaller.
        
        Args:
            memory_manager: Optional memory manager for storing installation results
        """
        self.memory_manager = memory_manager
        self.installed_packages = set()
        self.failed_packages = set()
    
    async def run(
        self,
        packages: Optional[List[str]] = None,
        requirements_file: Optional[str] = None,
        detect_imports: Optional[str] = None,
        use_venv: bool = True,
        upgrade: bool = False,
        trusted_hosts: Optional[List[str]] = None,
        index_url: Optional[str] = None,
        extra_index_url: Optional[List[str]] = None,
        no_deps: bool = False,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect missing Python packages and install them securely.
        
        Args:
            packages: Optional list of packages to install
            requirements_file: Optional path to requirements.txt file
            detect_imports: Optional path to Python file or directory to detect imports from
            use_venv: Whether to use a virtual environment (if available)
            upgrade: Whether to upgrade packages if already installed
            trusted_hosts: Optional list of trusted hosts for pip
            index_url: Optional custom PyPI index URL
            extra_index_url: Optional list of extra PyPI index URLs
            no_deps: Whether to skip installing dependencies
            store_memory: Whether to store installation results in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing installation results
        """
        try:
            # Validate inputs
            if not packages and not requirements_file and not detect_imports:
                return {
                    "status": "error",
                    "error": "At least one of 'packages', 'requirements_file', or 'detect_imports' must be provided"
                }
            
            if requirements_file and not os.path.exists(requirements_file):
                return {
                    "status": "error",
                    "error": f"Requirements file does not exist: {requirements_file}"
                }
            
            if detect_imports and not os.path.exists(detect_imports):
                return {
                    "status": "error",
                    "error": f"Path for import detection does not exist: {detect_imports}"
                }
            
            # Collect packages to install
            packages_to_install = set()
            
            # Add explicitly specified packages
            if packages:
                packages_to_install.update(packages)
            
            # Add packages from requirements file
            if requirements_file:
                req_packages = self._parse_requirements_file(requirements_file)
                packages_to_install.update(req_packages)
            
            # Detect imports from Python files
            if detect_imports:
                imported_packages = self._detect_imports(detect_imports)
                packages_to_install.update(imported_packages)
            
            if not packages_to_install:
                return {
                    "status": "success",
                    "message": "No packages to install",
                    "installed_packages": [],
                    "failed_packages": []
                }
            
            # Filter out already installed packages (unless upgrade is requested)
            if not upgrade:
                installed_packages = self._get_installed_packages()
                packages_to_install = {pkg for pkg in packages_to_install if self._get_package_name(pkg) not in installed_packages}
            
            if not packages_to_install:
                return {
                    "status": "success",
                    "message": "All packages are already installed",
                    "installed_packages": [],
                    "failed_packages": []
                }
            
            # Install packages
            self.installed_packages = set()
            self.failed_packages = set()
            
            for package in packages_to_install:
                success = self._install_package(
                    package,
                    use_venv=use_venv,
                    upgrade=upgrade,
                    trusted_hosts=trusted_hosts,
                    index_url=index_url,
                    extra_index_url=extra_index_url,
                    no_deps=no_deps
                )
                
                if success:
                    self.installed_packages.add(package)
                else:
                    self.failed_packages.add(package)
            
            # Prepare result
            result = {
                "status": "success" if not self.failed_packages else "partial_success" if self.installed_packages else "error",
                "message": f"Installed {len(self.installed_packages)} packages, {len(self.failed_packages)} failed",
                "installed_packages": list(self.installed_packages),
                "failed_packages": list(self.failed_packages)
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager:
                memory_content = {
                    "type": "package_installation",
                    "packages_requested": list(packages_to_install),
                    "installed_packages": list(self.installed_packages),
                    "failed_packages": list(self.failed_packages)
                }
                
                tags = memory_tags or ["package", "installation"]
                
                # Add package names to tags
                for pkg in self.installed_packages:
                    pkg_name = self._get_package_name(pkg)
                    if pkg_name not in tags:
                        tags.append(pkg_name)
                
                await self.memory_manager.store(
                    input_text=f"Install packages: {', '.join(packages_to_install)}",
                    output_text=f"Installed {len(self.installed_packages)} packages, {len(self.failed_packages)} failed.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error installing packages: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _parse_requirements_file(self, requirements_file: str) -> Set[str]:
        """
        Parse a requirements.txt file.
        
        Args:
            requirements_file: Path to requirements.txt file
            
        Returns:
            Set of package specifications
        """
        packages = set()
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Skip options
                if line.startswith('-'):
                    continue
                
                # Handle URLs and other complex specifications
                if ' @ ' in line:
                    packages.add(line)
                    continue
                
                # Handle normal package specifications
                package = line.split('#')[0].strip()  # Remove inline comments
                if package:
                    packages.add(package)
        
        return packages
    
    def _detect_imports(self, path: str) -> Set[str]:
        """
        Detect imports from Python files.
        
        Args:
            path: Path to Python file or directory
            
        Returns:
            Set of imported package names
        """
        imports = set()
        
        if os.path.isfile(path) and path.endswith('.py'):
            imports.update(self._extract_imports_from_file(path))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        imports.update(self._extract_imports_from_file(file_path))
        
        # Filter out standard library modules
        stdlib_modules = self._get_stdlib_modules()
        imports = {imp for imp in imports if imp not in stdlib_modules}
        
        return imports
    
    def _extract_imports_from_file(self, file_path: str) -> Set[str]:
        """
        Extract imports from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Set of imported package names
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract import statements
            import_pattern = r'^import\s+([a-zA-Z0-9_.,\s]+)'
            from_pattern = r'^from\s+([a-zA-Z0-9_.]+)\s+import'
            
            # Find all import statements
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                modules = match.group(1).split(',')
                for module in modules:
                    module = module.strip()
                    if module:
                        # Get the top-level package
                        top_level = module.split('.')[0]
                        imports.add(top_level)
            
            # Find all from ... import statements
            for match in re.finditer(from_pattern, content, re.MULTILINE):
                module = match.group(1)
                if module and not module.startswith('.'):
                    # Get the top-level package
                    top_level = module.split('.')[0]
                    imports.add(top_level)
            
            return imports
            
        except Exception as e:
            logger.error(f"Error extracting imports from {file_path}: {str(e)}")
            return set()
    
    def _get_stdlib_modules(self) -> Set[str]:
        """
        Get a set of standard library module names.
        
        Returns:
            Set of standard library module names
        """
        stdlib_modules = set()
        
        # Common standard library modules
        stdlib_modules.update([
            'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'concurrent',
            'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'difflib', 'enum',
            'functools', 'glob', 'gzip', 'hashlib', 'hmac', 'html', 'http', 'importlib',
            'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'multiprocessing',
            'operator', 'os', 'pathlib', 'pickle', 'platform', 'pprint', 'queue',
            're', 'random', 'shutil', 'signal', 'socket', 'sqlite3', 'statistics',
            'string', 'struct', 'subprocess', 'sys', 'tempfile', 'threading', 'time',
            'timeit', 'traceback', 'types', 'typing', 'unittest', 'urllib', 'uuid',
            'warnings', 'weakref', 'xml', 'zipfile', 'zlib'
        ])
        
        return stdlib_modules
    
    def _get_installed_packages(self) -> Set[str]:
        """
        Get a set of installed package names.
        
        Returns:
            Set of installed package names
        """
        installed_packages = set()
        
        try:
            for dist in pkg_resources.working_set:
                installed_packages.add(dist.project_name.lower())
        except Exception as e:
            logger.error(f"Error getting installed packages: {str(e)}")
        
        return installed_packages
    
    def _get_package_name(self, package_spec: str) -> str:
        """
        Extract the package name from a package specification.
        
        Args:
            package_spec: Package specification (e.g., 'package==1.0.0')
            
        Returns:
            Package name
        """
        # Handle URL installations
        if ' @ ' in package_spec:
            return package_spec.split(' @ ')[0].lower()
        
        # Handle version specifiers
        for operator in ['==', '>=', '<=', '>', '<', '~=', '!=']:
            if operator in package_spec:
                return package_spec.split(operator)[0].lower()
        
        # Handle extras
        if '[' in package_spec:
            return package_spec.split('[')[0].lower()
        
        return package_spec.lower()
    
    def _install_package(
        self,
        package: str,
        use_venv: bool = True,
        upgrade: bool = False,
        trusted_hosts: Optional[List[str]] = None,
        index_url: Optional[str] = None,
        extra_index_url: Optional[List[str]] = None,
        no_deps: bool = False
    ) -> bool:
        """
        Install a Python package securely.
        
        Args:
            package: Package specification
            use_venv: Whether to use a virtual environment (if available)
            upgrade: Whether to upgrade the package if already installed
            trusted_hosts: Optional list of trusted hosts for pip
            index_url: Optional custom PyPI index URL
            extra_index_url: Optional list of extra PyPI index URLs
            no_deps: Whether to skip installing dependencies
            
        Returns:
            True if installation was successful, False otherwise
        """
        try:
            # Build pip command
            cmd = [sys.executable, '-m', 'pip', 'install']
            
            # Add options
            if upgrade:
                cmd.append('--upgrade')
            
            if no_deps:
                cmd.append('--no-deps')
            
            if trusted_hosts:
                for host in trusted_hosts:
                    cmd.extend(['--trusted-host', host])
            
            if index_url:
                cmd.extend(['--index-url', index_url])
            
            if extra_index_url:
                for url in extra_index_url:
                    cmd.extend(['--extra-index-url', url])
            
            # Add package
            cmd.append(package)
            
            # Run pip in a subprocess
            logger.info(f"Installing package: {package}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {package}")
                return True
            else:
                logger.error(f"Failed to install {package}: {result.stderr}")
                return False
            
        except Exception as e:
            logger.error(f"Error installing {package}: {str(e)}")
            return False
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_package_installer(memory_manager=None):
    """
    Get a PackageInstaller instance.
    
    Args:
        memory_manager: Optional memory manager for storing installation results
        
    Returns:
        PackageInstaller instance
    """
    return PackageInstaller(memory_manager=memory_manager)
