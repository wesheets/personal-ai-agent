"""
Schema Validation Module for Loop Lineage Export System

This module provides schema validation functions for the loop lineage export system.
It ensures that all exports conform to the defined schemas before writing to disk.
"""

import json
import os
import logging
from datetime import datetime
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(
    filename='/debug/schema_trace.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('schema_validation')

# Schema paths
SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schemas')
MD_EXPORT_SCHEMA_PATH = os.path.join(SCHEMA_DIR, 'md_export_format.schema.json')
HTML_EXPORT_SCHEMA_PATH = os.path.join(SCHEMA_DIR, 'html_export_format.schema.json')
LOOP_LINEAGE_SCHEMA_PATH = os.path.join(SCHEMA_DIR, 'loop_lineage_export.schema.json')

def load_schema(schema_path):
    """Load a JSON schema from the given path."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schema from {schema_path}: {str(e)}")
        raise

def validate_schema(data, schema_type):
    """
    Validate data against the specified schema type.
    
    Args:
        data: The data to validate
        schema_type: The type of schema to validate against ('md', 'html', 'lineage')
        
    Returns:
        tuple: (is_valid, error_message)
    """
    schema_path = {
        'md': MD_EXPORT_SCHEMA_PATH,
        'html': HTML_EXPORT_SCHEMA_PATH,
        'lineage': LOOP_LINEAGE_SCHEMA_PATH
    }.get(schema_type)
    
    if not schema_path:
        error_msg = f"Unknown schema type: {schema_type}"
        logger.error(error_msg)
        return False, error_msg
    
    try:
        schema = load_schema(schema_path)
        validate(instance=data, schema=schema)
        
        # Log successful validation
        logger.info(f"Schema validation successful for {schema_type} export")
        
        # Add validation metadata
        if isinstance(data, dict):
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['schema_validated'] = True
            data['metadata']['validation_timestamp'] = datetime.now().isoformat()
        
        return True, None
    except ValidationError as e:
        error_msg = f"Schema validation failed: {str(e)}"
        logger.error(error_msg)
        
        # Add validation metadata
        if isinstance(data, dict):
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['schema_validated'] = False
            data['metadata']['validation_errors'] = [str(e)]
            data['metadata']['validation_timestamp'] = datetime.now().isoformat()
        
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error during schema validation: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def validate_before_export(export_data, export_format):
    """
    Validate export data before writing to disk.
    
    Args:
        export_data: The data to be exported
        export_format: The format of the export ('md' or 'html')
        
    Returns:
        bool: Whether the data is valid
    """
    is_valid, error = validate_schema(export_data, export_format)
    
    if not is_valid:
        logger.warning(f"Invalid {export_format} export data: {error}")
        
        # Log to system status
        try:
            with open('/system/status.json', 'r+') as f:
                status = json.load(f)
                if 'schema_validation' not in status:
                    status['schema_validation'] = {'failures': 0, 'last_failure': None, 'last_failure_reason': None}
                
                status['schema_validation']['failures'] += 1
                status['schema_validation']['last_failure'] = datetime.now().isoformat()
                status['schema_validation']['last_failure_reason'] = error
                
                f.seek(0)
                json.dump(status, f, indent=2)
                f.truncate()
        except Exception as e:
            logger.error(f"Failed to update system status: {str(e)}")
    
    return is_valid
