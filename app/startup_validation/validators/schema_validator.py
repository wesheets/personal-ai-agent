"""
Schema Validator

This module validates schemas listed in the Product/Infrastructure Cognition Engine (PICE).
It checks if schemas are parseable and reachable.
"""

import os
import json
import jsonschema
import logging
from typing import Dict, List, Any, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.schema_validator')

def validate_schemas(pice_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Validate all schemas listed in the PICE.
    
    Args:
        pice_data: The loaded PICE data
        
    Returns:
        Tuple containing:
        - Health score as a percentage (0-100)
        - List of drift issues detected
    """
    logger.info("Starting schema validation")
    
    if "schemas" not in pice_data:
        logger.error("PICE data does not contain 'schemas' key")
        return 0.0, [{"type": "schema", "path": "PICE", "issue": "Missing 'schemas' key in PICE"}]
    
    schemas = pice_data["schemas"]
    if not schemas:
        logger.warning("No schemas found in PICE")
        return 100.0, []
    
    valid_count = 0
    drift_issues = []
    
    for schema in schemas:
        if "name" not in schema:
            logger.error("Schema missing 'name' attribute")
            drift_issues.append({
                "type": "schema",
                "path": "unknown",
                "issue": "Schema missing 'name' attribute"
            })
            continue
            
        if "file" not in schema:
            logger.error(f"Schema {schema['name']} missing 'file' attribute")
            drift_issues.append({
                "type": "schema",
                "path": schema['name'],
                "issue": "Schema missing 'file' attribute"
            })
            continue
        
        schema_name = schema["name"]
        schema_file = schema["file"]
        logger.info(f"Validating schema: {schema_name} (file: {schema_file})")
        
        # Check if schema exists
        if not check_schema_exists(schema_file):
            logger.error(f"Schema file {schema_file} does not exist")
            drift_issues.append({
                "type": "schema",
                "path": schema_file,
                "issue": "Schema file does not exist"
            })
            continue
        
        # Check if schema is parseable
        if not check_schema_parseable(schema_file):
            logger.error(f"Schema {schema_name} is not parseable")
            drift_issues.append({
                "type": "schema",
                "path": schema_file,
                "issue": "Schema cannot be parsed (invalid JSON Schema)"
            })
            continue
        
        # If we get here, the schema is valid
        valid_count += 1
        logger.info(f"Schema {schema_name} validated successfully")
    
    # Calculate health score
    health_score = (valid_count / len(schemas)) * 100 if schemas else 100.0
    logger.info(f"Schema validation complete. Health score: {health_score:.1f}%")
    
    return health_score, drift_issues

def check_schema_exists(schema_path: str) -> bool:
    """
    Check if a schema file exists.
    
    Args:
        schema_path: Path to the schema to check
        
    Returns:
        True if the schema file exists, False otherwise
    """
    # Normalize schema path
    if not schema_path.startswith('/'):
        schema_path = f"/app/schemas/{schema_path}"
    
    # Check if file exists
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, schema_path.lstrip('/'))
    
    exists = os.path.isfile(full_path)
    logger.debug(f"Schema file check: {'exists' if exists else 'not found'} at {full_path}")
    return exists

def check_schema_parseable(schema_path: str) -> bool:
    """
    Check if a schema can be parsed without errors.
    
    Args:
        schema_path: Path to the schema to check
        
    Returns:
        True if the schema can be parsed, False otherwise
    """
    # Normalize schema path
    if not schema_path.startswith('/'):
        schema_path = f"/app/schemas/{schema_path}"
    
    # Get full path to schema file
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, schema_path.lstrip('/'))
    
    if not os.path.isfile(full_path):
        logger.debug(f"Cannot parse schema: file not found at {full_path}")
        return False
    
    try:
        # Try to load and parse the schema
        with open(full_path, 'r') as f:
            schema_data = json.load(f)
        
        # Validate that it's a valid JSON Schema
        jsonschema.Draft7Validator.check_schema(schema_data)
        
        logger.debug(f"Successfully parsed schema at {full_path}")
        return True
    except json.JSONDecodeError as e:
        logger.debug(f"Error parsing schema JSON: {str(e)}")
        return False
    except jsonschema.exceptions.SchemaError as e:
        logger.debug(f"Invalid JSON Schema: {str(e)}")
        return False
    except Exception as e:
        logger.debug(f"Error validating schema: {str(e)}")
        return False
