/**
 * FreezeSchemaValidator.js
 * 
 * Utility functions for validating freeze-related data against schemas.
 * Ensures all components comply with the defined schemas.
 */

import { 
  validateFreezeEvent, 
  validateFreezeStatus,
  FreezeEventSchema,
  FreezeStatusSchema,
  FreezeLogSchema
} from '../schemas/FreezeStatusSchema';

/**
 * Validate a freeze event against the schema
 * 
 * @param {Object} event - Freeze event to validate
 * @returns {Object} Validation result with isValid and errors
 */
export const validateFreeze = (event) => {
  const errors = [];
  
  // Check required fields
  const requiredFields = ['id', 'loop_id', 'status', 'reason', 'timestamp', 'required_action'];
  for (const field of requiredFields) {
    if (event[field] === undefined) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // Check status enum
  if (event.status && !['frozen', 'unfrozen'].includes(event.status)) {
    errors.push(`Invalid status value: ${event.status}`);
  }
  
  // Check required_action enum
  if (event.required_action && !['re-reflect', 'operator_override', 'none'].includes(event.required_action)) {
    errors.push(`Invalid required_action value: ${event.required_action}`);
  }
  
  // If unfrozen, check unfrozen_at and unfreeze_reason
  if (event.status === 'unfrozen') {
    if (!event.unfrozen_at) {
      errors.push('Missing unfrozen_at for unfrozen event');
    }
    
    if (!event.unfreeze_reason) {
      errors.push('Missing unfreeze_reason for unfrozen event');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validate freeze status against the schema
 * 
 * @param {Object} status - Freeze status to validate
 * @returns {Object} Validation result with isValid and errors
 */
export const validateStatus = (status) => {
  const errors = [];
  
  // Check required fields
  const requiredFields = ['loop_id', 'status', 'timestamp'];
  for (const field of requiredFields) {
    if (status[field] === undefined) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // Check status enum
  if (status.status && !['frozen', 'unfrozen', 'executing'].includes(status.status)) {
    errors.push(`Invalid status value: ${status.status}`);
  }
  
  // If frozen, check reason and required_action
  if (status.status === 'frozen') {
    if (!status.reason) {
      errors.push('Missing reason for frozen status');
    }
    
    if (!status.required_action) {
      errors.push('Missing required_action for frozen status');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validate freeze log against the schema
 * 
 * @param {Object} log - Freeze log to validate
 * @returns {Object} Validation result with isValid, validEvents, invalidEvents, and errors
 */
export const validateFreezeLog = (log) => {
  const errors = [];
  const validEvents = [];
  const invalidEvents = [];
  
  // Check meta
  if (!log.meta) {
    errors.push('Missing meta section in freeze log');
  } else {
    if (!log.meta.version) {
      errors.push('Missing version in meta section');
    }
    
    if (!log.meta.last_updated) {
      errors.push('Missing last_updated in meta section');
    }
  }
  
  // Check events
  if (!log.events || !Array.isArray(log.events)) {
    errors.push('Missing or invalid events array in freeze log');
  } else {
    // Validate each event
    for (const event of log.events) {
      const validation = validateFreeze(event);
      
      if (validation.isValid) {
        validEvents.push(event);
      } else {
        invalidEvents.push({
          event,
          errors: validation.errors
        });
      }
    }
  }
  
  return {
    isValid: errors.length === 0 && invalidEvents.length === 0,
    validEvents,
    invalidEvents,
    errors
  };
};

/**
 * Get schema field description
 * 
 * @param {Object} schema - Schema object
 * @param {string} fieldPath - Path to the field (e.g., 'status', 'original_state.confidence_score')
 * @returns {Object|null} Field schema or null if not found
 */
export const getSchemaField = (schema, fieldPath) => {
  const parts = fieldPath.split('.');
  let current = schema;
  
  for (const part of parts) {
    if (current[part]) {
      current = current[part];
    } else if (current.properties && current.properties[part]) {
      current = current.properties[part];
    } else {
      return null;
    }
  }
  
  return current;
};

/**
 * Get allowed values for a field
 * 
 * @param {Object} schema - Schema object
 * @param {string} fieldPath - Path to the field
 * @returns {Array|null} Array of allowed values or null if not an enum
 */
export const getAllowedValues = (schema, fieldPath) => {
  const field = getSchemaField(schema, fieldPath);
  
  if (field && field.enum) {
    return field.enum;
  }
  
  return null;
};

/**
 * Check if a value is valid for a field
 * 
 * @param {Object} schema - Schema object
 * @param {string} fieldPath - Path to the field
 * @param {any} value - Value to check
 * @returns {boolean} Whether the value is valid
 */
export const isValidValue = (schema, fieldPath, value) => {
  const field = getSchemaField(schema, fieldPath);
  
  if (!field) {
    return false;
  }
  
  // Check type
  if (field.type === 'string' && typeof value !== 'string') {
    return false;
  }
  
  if (field.type === 'number' && typeof value !== 'number') {
    return false;
  }
  
  if (field.type === 'boolean' && typeof value !== 'boolean') {
    return false;
  }
  
  if (field.type === 'array' && !Array.isArray(value)) {
    return false;
  }
  
  if (field.type === 'object' && (typeof value !== 'object' || value === null || Array.isArray(value))) {
    return false;
  }
  
  // Check enum
  if (field.enum && !field.enum.includes(value)) {
    return false;
  }
  
  return true;
};

export default {
  validateFreeze,
  validateStatus,
  validateFreezeLog,
  getSchemaField,
  getAllowedValues,
  isValidValue,
  schemas: {
    FreezeEventSchema,
    FreezeStatusSchema,
    FreezeLogSchema
  }
};
