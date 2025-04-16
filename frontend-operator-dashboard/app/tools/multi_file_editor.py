"""
Multi-File Editor Tool for Autonomous Coding Agents.

This module provides functionality to update multiple files with consistency,
allowing agents to make coordinated changes across a codebase.
"""

import os
import sys
import logging
import tempfile
import difflib
from typing import Dict, Any, List, Optional, Union, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiFileEditor:
    """
    Tool for updating multiple files with consistency.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the MultiFileEditor.
        
        Args:
            memory_manager: Optional memory manager for storing edit operations
        """
        self.memory_manager = memory_manager
    
    async def run(
        self,
        file_changes: List[Dict[str, Any]],
        base_dir: str = "",
        create_backup: bool = True,
        dry_run: bool = False,
        store_memory: bool = True,
        memory_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update multiple files with consistency.
        
        Args:
            file_changes: List of file change operations
                Each operation should have:
                - 'file_path': Path to the file (relative to base_dir if provided)
                - 'operation': Type of operation ('modify', 'create', 'delete')
                - 'content': New content for 'create' or 'modify' operations
                - 'changes': List of specific changes for 'modify' operations (optional)
                  Each change should have:
                  - 'type': Type of change ('replace', 'insert', 'delete')
                  - 'line_start': Starting line number (0-based)
                  - 'line_end': Ending line number (0-based) for 'replace' and 'delete'
                  - 'content': New content for 'replace' and 'insert'
            base_dir: Base directory for file paths
            create_backup: Whether to create backup files before making changes
            dry_run: Whether to simulate changes without actually modifying files
            store_memory: Whether to store edit operations in memory
            memory_tags: Tags to apply to memory entries
            
        Returns:
            Dictionary containing results of file operations
        """
        try:
            # Validate inputs
            if not isinstance(file_changes, list):
                return {
                    "status": "error",
                    "error": "file_changes must be a list"
                }
            
            if base_dir and not os.path.exists(base_dir):
                return {
                    "status": "error",
                    "error": f"Base directory does not exist: {base_dir}"
                }
            
            # Process file changes
            results = []
            
            for change in file_changes:
                # Validate change operation
                if not isinstance(change, dict) or 'file_path' not in change or 'operation' not in change:
                    results.append({
                        "status": "error",
                        "error": "Each change must be a dictionary with 'file_path' and 'operation' keys",
                        "change": change
                    })
                    continue
                
                file_path = change['file_path']
                operation = change['operation']
                
                # Resolve full path
                full_path = os.path.join(base_dir, file_path) if base_dir else file_path
                
                # Process based on operation type
                if operation == 'create':
                    if 'content' not in change:
                        results.append({
                            "status": "error",
                            "error": "Create operation requires 'content' key",
                            "file_path": file_path
                        })
                        continue
                    
                    result = self._create_file(full_path, change['content'], dry_run)
                    result['file_path'] = file_path
                    result['operation'] = 'create'
                    results.append(result)
                
                elif operation == 'modify':
                    if 'content' in change and 'changes' in change:
                        results.append({
                            "status": "error",
                            "error": "Modify operation should have either 'content' or 'changes', not both",
                            "file_path": file_path
                        })
                        continue
                    
                    if 'content' in change:
                        result = self._modify_file_content(full_path, change['content'], create_backup, dry_run)
                    elif 'changes' in change:
                        result = self._modify_file_changes(full_path, change['changes'], create_backup, dry_run)
                    else:
                        results.append({
                            "status": "error",
                            "error": "Modify operation requires either 'content' or 'changes' key",
                            "file_path": file_path
                        })
                        continue
                    
                    result['file_path'] = file_path
                    result['operation'] = 'modify'
                    results.append(result)
                
                elif operation == 'delete':
                    result = self._delete_file(full_path, create_backup, dry_run)
                    result['file_path'] = file_path
                    result['operation'] = 'delete'
                    results.append(result)
                
                else:
                    results.append({
                        "status": "error",
                        "error": f"Unknown operation: {operation}",
                        "file_path": file_path
                    })
            
            # Prepare result
            success_count = sum(1 for r in results if r['status'] == 'success')
            error_count = len(results) - success_count
            
            result = {
                "status": "success" if error_count == 0 else "partial_success" if success_count > 0 else "error",
                "total_operations": len(results),
                "success_count": success_count,
                "error_count": error_count,
                "dry_run": dry_run,
                "results": results
            }
            
            # Store in memory if requested
            if store_memory and self.memory_manager and not dry_run:
                memory_content = {
                    "type": "multi_file_edit",
                    "file_changes": file_changes,
                    "results": results,
                    "success_count": success_count,
                    "error_count": error_count
                }
                
                tags = memory_tags or ["edit", "multi_file"]
                
                # Add operation types to tags
                operations = set(change['operation'] for change in file_changes)
                for op in operations:
                    if f"operation_{op}" not in tags:
                        tags.append(f"operation_{op}")
                
                # Add file extensions to tags
                extensions = set(os.path.splitext(change['file_path'])[1] for change in file_changes if os.path.splitext(change['file_path'])[1])
                for ext in extensions:
                    if ext.startswith('.'):
                        ext = ext[1:]
                    if ext and ext not in tags:
                        tags.append(ext)
                
                await self.memory_manager.store(
                    input_text=f"Edit multiple files ({', '.join(operations)})",
                    output_text=f"Performed {len(results)} file operations: {success_count} successful, {error_count} failed.",
                    metadata={
                        "content": memory_content,
                        "tags": tags
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-file edit: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": self._get_exception_traceback()
            }
    
    def _create_file(self, file_path: str, content: str, dry_run: bool) -> Dict[str, Any]:
        """
        Create a new file.
        
        Args:
            file_path: Path to the file
            content: Content to write to the file
            dry_run: Whether to simulate the operation
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Check if file already exists
            if os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File already exists: {file_path}"
                }
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                if not dry_run:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
            
            # Create file
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created file: {file_path}")
            
            return {
                "status": "success",
                "message": f"{'Would create' if dry_run else 'Created'} file: {file_path}",
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _modify_file_content(self, file_path: str, content: str, create_backup: bool, dry_run: bool) -> Dict[str, Any]:
        """
        Modify a file by replacing its entire content.
        
        Args:
            file_path: Path to the file
            content: New content for the file
            create_backup: Whether to create a backup file
            dry_run: Whether to simulate the operation
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File does not exist: {file_path}"
                }
            
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create diff
            diff = self._create_diff(original_content, content, file_path)
            
            # Create backup if requested
            if create_backup and not dry_run:
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                logger.info(f"Created backup: {backup_path}")
            
            # Modify file
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Modified file: {file_path}")
            
            return {
                "status": "success",
                "message": f"{'Would modify' if dry_run else 'Modified'} file: {file_path}",
                "diff": diff,
                "backup": f"{file_path}.bak" if create_backup and not dry_run else None,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Error modifying file {file_path}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _modify_file_changes(self, file_path: str, changes: List[Dict[str, Any]], create_backup: bool, dry_run: bool) -> Dict[str, Any]:
        """
        Modify a file by applying specific changes.
        
        Args:
            file_path: Path to the file
            changes: List of specific changes to apply
            create_backup: Whether to create a backup file
            dry_run: Whether to simulate the operation
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File does not exist: {file_path}"
                }
            
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Create backup if requested
            if create_backup and not dry_run:
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                logger.info(f"Created backup: {backup_path}")
            
            # Apply changes
            new_lines = lines.copy()
            applied_changes = []
            
            # Sort changes in reverse order to avoid line number shifts
            sorted_changes = sorted(changes, key=lambda c: c.get('line_start', 0), reverse=True)
            
            for change in sorted_changes:
                change_type = change.get('type')
                line_start = change.get('line_start', 0)
                
                if change_type == 'replace':
                    line_end = change.get('line_end', line_start)
                    content = change.get('content', '')
                    
                    # Validate line numbers
                    if line_start < 0 or line_end >= len(new_lines) or line_start > line_end:
                        applied_changes.append({
                            "status": "error",
                            "error": f"Invalid line numbers: {line_start}-{line_end}",
                            "change": change
                        })
                        continue
                    
                    # Replace lines
                    content_lines = content.splitlines(True)
                    new_lines[line_start:line_end + 1] = content_lines
                    
                    applied_changes.append({
                        "status": "success",
                        "type": "replace",
                        "line_start": line_start,
                        "line_end": line_end,
                        "lines_replaced": line_end - line_start + 1,
                        "lines_added": len(content_lines)
                    })
                
                elif change_type == 'insert':
                    content = change.get('content', '')
                    
                    # Validate line number
                    if line_start < 0 or line_start > len(new_lines):
                        applied_changes.append({
                            "status": "error",
                            "error": f"Invalid line number: {line_start}",
                            "change": change
                        })
                        continue
                    
                    # Insert lines
                    content_lines = content.splitlines(True)
                    new_lines[line_start:line_start] = content_lines
                    
                    applied_changes.append({
                        "status": "success",
                        "type": "insert",
                        "line_start": line_start,
                        "lines_added": len(content_lines)
                    })
                
                elif change_type == 'delete':
                    line_end = change.get('line_end', line_start)
                    
                    # Validate line numbers
                    if line_start < 0 or line_end >= len(new_lines) or line_start > line_end:
                        applied_changes.append({
                            "status": "error",
                            "error": f"Invalid line numbers: {line_start}-{line_end}",
                            "change": change
                        })
                        continue
                    
                    # Delete lines
                    del new_lines[line_start:line_end + 1]
                    
                    applied_changes.append({
                        "status": "success",
                        "type": "delete",
                        "line_start": line_start,
                        "line_end": line_end,
                        "lines_deleted": line_end - line_start + 1
                    })
                
                else:
                    applied_changes.append({
                        "status": "error",
                        "error": f"Unknown change type: {change_type}",
                        "change": change
                    })
            
            # Create diff
            original_content = ''.join(lines)
            new_content = ''.join(new_lines)
            diff = self._create_diff(original_content, new_content, file_path)
            
            # Write modified content
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                logger.info(f"Modified file: {file_path}")
            
            return {
                "status": "success",
                "message": f"{'Would modify' if dry_run else 'Modified'} file: {file_path}",
                "changes_applied": applied_changes,
                "diff": diff,
                "backup": f"{file_path}.bak" if create_backup and not dry_run else None,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Error modifying file {file_path}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _delete_file(self, file_path: str, create_backup: bool, dry_run: bool) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            create_backup: Whether to create a backup file
            dry_run: Whether to simulate the operation
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File does not exist: {file_path}"
                }
            
            # Create backup if requested
            if create_backup and not dry_run:
                backup_path = f"{file_path}.bak"
                with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"Created backup: {backup_path}")
            
            # Delete file
            if not dry_run:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            
            return {
                "status": "success",
                "message": f"{'Would delete' if dry_run else 'Deleted'} file: {file_path}",
                "backup": f"{file_path}.bak" if create_backup and not dry_run else None,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_diff(self, original: str, modified: str, file_path: str) -> str:
        """
        Create a unified diff between original and modified content.
        
        Args:
            original: Original content
            modified: Modified content
            file_path: Path to the file
            
        Returns:
            Unified diff as string
        """
        original_lines = original.splitlines(True)
        modified_lines = modified.splitlines(True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3
        )
        
        return ''.join(diff)
    
    def _get_exception_traceback(self) -> str:
        """
        Get traceback for the current exception.
        
        Returns:
            Traceback as a string
        """
        import traceback
        return traceback.format_exc()

# Factory function for tool router
def get_multi_file_editor(memory_manager=None):
    """
    Get a MultiFileEditor instance.
    
    Args:
        memory_manager: Optional memory manager for storing edit operations
        
    Returns:
        MultiFileEditor instance
    """
    return MultiFileEditor(memory_manager=memory_manager)
