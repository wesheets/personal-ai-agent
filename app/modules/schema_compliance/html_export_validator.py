"""
HTML Export Format Schema Validator Module

This module provides functions for validating HTML export format data
against the schema for Phase 2 of the Schema Compliance initiative.
"""

import json
import os
import logging
from datetime import datetime
import sys

# Import schema validation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.schema_validation import validate_schema

# Configure logging
logging.basicConfig(
    filename='/debug/schema_trace.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('html_export_validator')

def validate_html_export(export_data):
    """
    Validate HTML export data against the schema.
    
    Args:
        export_data: Dictionary containing the export data
        
    Returns:
        tuple: (is_valid, validated_data, error_message)
    """
    # Ensure required fields are present
    required_fields = ['format', 'loop_id', 'content', 'metadata']
    for field in required_fields:
        if field not in export_data:
            error_msg = f"Missing required field: {field}"
            logger.error(error_msg)
            return False, None, error_msg
    
    # Ensure format is html
    if export_data['format'] != 'html':
        error_msg = f"Invalid format: {export_data['format']}, expected 'html'"
        logger.error(error_msg)
        return False, None, error_msg
    
    # Validate against schema
    is_valid, error = validate_schema(export_data, 'html')
    
    if not is_valid:
        logger.error(f"HTML export validation failed: {error}")
        
        # Add validation metadata
        export_data['schema_validated'] = False
        export_data['validation_timestamp'] = datetime.utcnow().isoformat()
        export_data['validation_errors'] = [error]
        
        return False, export_data, error
    
    # Add validation metadata
    validated_data = export_data.copy()
    validated_data['schema_validated'] = True
    validated_data['validation_timestamp'] = datetime.utcnow().isoformat()
    validated_data['validation_errors'] = []
    
    logger.info(f"HTML export validation successful for loop {export_data['loop_id']}")
    
    return True, validated_data, None

def create_html_export(loop_id, content, metadata=None, export_type=None):
    """
    Create a validated HTML export object.
    
    Args:
        loop_id: ID of the loop
        content: HTML content
        metadata: Optional metadata dictionary
        export_type: Optional export type (e.g., 'loop_map', 'lineage', 'summary')
        
    Returns:
        tuple: (is_valid, export_data, error_message)
    """
    # Create default metadata if not provided
    if metadata is None:
        metadata = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'format_version': '1.0'
        }
    
    # Ensure metadata has required fields
    if 'export_timestamp' not in metadata:
        metadata['export_timestamp'] = datetime.utcnow().isoformat()
    
    if 'format_version' not in metadata:
        metadata['format_version'] = '1.0'
    
    # Add export type if provided
    if export_type:
        metadata['export_type'] = export_type
    
    # Create export data
    export_data = {
        'format': 'html',
        'loop_id': loop_id,
        'content': content,
        'metadata': metadata
    }
    
    # Validate export data
    return validate_html_export(export_data)

def write_validated_html_export(loop_id, content, output_path, metadata=None, export_type=None):
    """
    Create a validated HTML export and write it to a file.
    
    Args:
        loop_id: ID of the loop
        content: HTML content
        output_path: Path to write the file
        metadata: Optional metadata dictionary
        export_type: Optional export type (e.g., 'loop_map', 'lineage', 'summary')
        
    Returns:
        tuple: (success, error_message)
    """
    # Create and validate export data
    is_valid, export_data, error = create_html_export(loop_id, content, metadata, export_type)
    
    if not is_valid:
        return False, f"Validation failed: {error}"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Write content to file
        with open(output_path, 'w') as f:
            f.write(content)
        
        # Write metadata to separate file if needed
        metadata_path = f"{output_path}.meta.json"
        with open(metadata_path, 'w') as f:
            json.dump(export_data['metadata'], f, indent=2)
        
        logger.info(f"Wrote validated HTML export to {output_path}")
        return True, None
    
    except Exception as e:
        error_msg = f"Failed to write HTML export: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def validate_html_document(html_content, loop_id, export_type=None):
    """
    Validate an HTML document string.
    
    Args:
        html_content: HTML content string
        loop_id: ID of the loop
        export_type: Optional export type (e.g., 'loop_map', 'lineage', 'summary')
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Create metadata
    metadata = {
        'export_timestamp': datetime.utcnow().isoformat(),
        'format_version': '1.0'
    }
    
    # Add export type if provided
    if export_type:
        metadata['export_type'] = export_type
    
    # Create export data
    export_data = {
        'format': 'html',
        'loop_id': loop_id,
        'content': html_content,
        'metadata': metadata
    }
    
    # Validate export data
    is_valid, _, error = validate_html_export(export_data)
    
    return is_valid, error
