/**
 * ReflectionSchema.js
 * 
 * Schema definitions for the recursive reflection and uncertainty threshold system.
 * Enforces data structures for reflection events, depth tracking, and confidence thresholds.
 */

// Schema for a reflection event
export const ReflectionEventSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the reflection event',
    example: 'reflection_1650389421000_1234'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop where the reflection was triggered',
    example: 'loop_289'
  },
  triggered_by: {
    type: 'string',
    description: 'Reason that triggered the reflection',
    enum: [
      'low_confidence',
      'trust_decay',
      'unresolved_contradiction',
      'high_drift',
      'no_manual_override',
      'uncertainty_threshold'
    ],
    example: 'uncertainty_threshold'
  },
  reflection_depth: {
    type: 'number',
    description: 'Depth level of this reflection (1-based)',
    example: 2
  },
  agent: {
    type: 'string',
    description: 'Agent that performed the reflection',
    example: 'SAGE'
  },
  project_id: {
    type: 'string',
    description: 'Project ID for scoping',
    example: 'life_tree'
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the reflection was triggered',
    example: '2025-04-22T14:30:21.000Z'
  },
  status: {
    type: 'string',
    description: 'Current status of the reflection',
    enum: ['active', 'completed', 'cancelled'],
    example: 'active'
  },
  confidence: {
    type: 'number',
    description: 'Confidence score after reflection (0-1)',
    example: 0.71
  },
  completed_at: {
    type: 'string',
    description: 'ISO timestamp when the reflection was completed',
    example: '2025-04-22T14:31:45.000Z'
  },
  original_state: {
    type: 'object',
    description: 'Original loop state that triggered the reflection',
    properties: {
      confidence_score: {
        type: 'number',
        description: 'Original confidence score (0-1)',
        example: 0.48
      },
      trust_score: {
        type: 'number',
        description: 'Trust score at time of reflection (0-1)',
        example: 0.65
      },
      trust_delta: {
        type: 'number',
        description: 'Change in trust score',
        example: -0.15
      },
      contradiction_unresolved: {
        type: 'boolean',
        description: 'Whether there was an unresolved contradiction',
        example: true
      },
      drift_score: {
        type: 'number',
        description: 'Drift score at time of reflection (0-1)',
        example: 0.72
      },
      manual_override: {
        type: 'boolean',
        description: 'Whether there was a manual override',
        example: false
      }
    }
  },
  result: {
    type: 'object',
    description: 'Result of the reflection',
    properties: {
      confidence_score: {
        type: 'number',
        description: 'New confidence score after reflection (0-1)',
        example: 0.71
      },
      updated_beliefs: {
        type: 'array',
        description: 'Beliefs that were updated during reflection',
        items: {
          type: 'string'
        },
        example: ['belief_privacy_001', 'belief_safety_003']
      },
      resolved_contradictions: {
        type: 'array',
        description: 'Contradictions that were resolved during reflection',
        items: {
          type: 'string'
        },
        example: ['contradiction_1650389421000_5678']
      }
    }
  }
};

// Schema for loop reflection history
export const LoopReflectionHistorySchema = {
  loop_id: {
    type: 'string',
    description: 'ID of the loop',
    example: 'loop_289'
  },
  project_id: {
    type: 'string',
    description: 'Project ID for scoping',
    example: 'life_tree'
  },
  reflections: {
    type: 'array',
    description: 'Array of reflection events for this loop',
    items: {
      type: 'object',
      properties: {
        depth: {
          type: 'number',
          description: 'Depth level of this reflection (1-based)',
          example: 1
        },
        agent: {
          type: 'string',
          description: 'Agent that performed the reflection',
          example: 'SAGE'
        },
        confidence: {
          type: 'number',
          description: 'Confidence score after reflection (0-1)',
          example: 0.52
        },
        timestamp: {
          type: 'string',
          description: 'ISO timestamp when the reflection was triggered',
          example: '2025-04-22T14:30:21.000Z'
        },
        reason: {
          type: 'string',
          description: 'Reason that triggered the reflection',
          example: 'low_confidence'
        },
        status: {
          type: 'string',
          description: 'Status of the reflection',
          enum: ['active', 'completed', 'cancelled'],
          example: 'completed'
        }
      }
    }
  },
  current_depth: {
    type: 'number',
    description: 'Current reflection depth for this loop',
    example: 2
  },
  max_depth_reached: {
    type: 'boolean',
    description: 'Whether the maximum reflection depth has been reached',
    example: false
  },
  last_reflection: {
    type: 'string',
    description: 'ISO timestamp of the last reflection',
    example: '2025-04-22T14:31:45.000Z'
  }
};

// Schema for reflection depth log
export const ReflectionDepthLogSchema = {
  meta: {
    type: 'object',
    description: 'Metadata about the reflection depth log',
    properties: {
      version: {
        type: 'string',
        description: 'Version of the reflection depth log schema',
        example: '1.0'
      },
      description: {
        type: 'string',
        description: 'Description of the reflection depth log',
        example: 'Tracks reflection depth for each loop to prevent infinite recursion'
      },
      last_updated: {
        type: 'string',
        description: 'ISO timestamp of the last update to the log',
        example: '2025-04-22T20:56:21.000Z'
      },
      max_depth: {
        type: 'number',
        description: 'Maximum allowed reflection depth',
        example: 3
      }
    }
  },
  loops: {
    type: 'array',
    description: 'Array of loop reflection histories',
    items: LoopReflectionHistorySchema
  }
};

// Schema for confidence thresholds
export const ConfidenceThresholdsSchema = {
  default: {
    type: 'object',
    description: 'Default thresholds for all projects',
    properties: {
      min_confidence: {
        type: 'number',
        description: 'Minimum confidence score required (0-1)',
        example: 0.55
      },
      max_drift: {
        type: 'number',
        description: 'Maximum allowed drift score (0-1)',
        example: 0.65
      },
      min_trust_score: {
        type: 'number',
        description: 'Minimum trust score required (0-1)',
        example: 0.4
      },
      min_trust_delta: {
        type: 'number',
        description: 'Minimum allowed trust delta',
        example: -0.2
      },
      max_reflection_depth: {
        type: 'number',
        description: 'Maximum allowed reflection depth',
        example: 3
      }
    }
  },
  project_specific: {
    type: 'object',
    description: 'Project-specific thresholds',
    additionalProperties: {
      type: 'object',
      description: 'Thresholds for a specific project',
      properties: {
        min_confidence: {
          type: 'number',
          description: 'Minimum confidence score required (0-1)',
          example: 0.7
        },
        max_drift: {
          type: 'number',
          description: 'Maximum allowed drift score (0-1)',
          example: 0.5
        },
        min_trust_score: {
          type: 'number',
          description: 'Minimum trust score required (0-1)',
          example: 0.5
        },
        min_trust_delta: {
          type: 'number',
          description: 'Minimum allowed trust delta',
          example: -0.15
        },
        max_reflection_depth: {
          type: 'number',
          description: 'Maximum allowed reflection depth',
          example: 4
        }
      }
    }
  }
};

// Example of a complete reflection event
export const EXAMPLE_REFLECTION_EVENT = {
  id: "reflection_1650389421000_1234",
  loop_id: "loop_289",
  triggered_by: "uncertainty_threshold",
  reflection_depth: 2,
  agent: "SAGE",
  project_id: "life_tree",
  timestamp: "2025-04-22T14:30:21.000Z",
  status: "completed",
  confidence: 0.71,
  completed_at: "2025-04-22T14:31:45.000Z",
  original_state: {
    confidence_score: 0.48,
    trust_score: 0.65,
    trust_delta: -0.15,
    contradiction_unresolved: true,
    drift_score: 0.72,
    manual_override: false
  },
  result: {
    confidence_score: 0.71,
    updated_beliefs: ["belief_privacy_001", "belief_safety_003"],
    resolved_contradictions: ["contradiction_1650389421000_5678"]
  }
};

// Example of a complete loop reflection history
export const EXAMPLE_LOOP_REFLECTION_HISTORY = {
  loop_id: "loop_289",
  project_id: "life_tree",
  reflections: [
    {
      depth: 1,
      agent: "SAGE",
      confidence: 0.52,
      timestamp: "2025-04-22T14:30:21.000Z",
      reason: "low_confidence",
      status: "completed"
    },
    {
      depth: 2,
      agent: "CRITIC",
      confidence: 0.71,
      timestamp: "2025-04-22T14:31:45.000Z",
      reason: "unresolved_contradiction",
      status: "completed"
    }
  ],
  current_depth: 2,
  max_depth_reached: false,
  last_reflection: "2025-04-22T14:31:45.000Z"
};

// Validation functions

/**
 * Validate a reflection event against the schema
 * 
 * @param {Object} event - Reflection event to validate
 * @returns {boolean} Whether the event is valid
 */
export const validateReflectionEvent = (event) => {
  // Check required fields
  const requiredFields = ['id', 'loop_id', 'triggered_by', 'reflection_depth', 'agent', 'timestamp', 'status'];
  for (const field of requiredFields) {
    if (event[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check reflection depth range
  if (typeof event.reflection_depth !== 'number' || event.reflection_depth < 1) {
    console.error('Reflection depth must be a positive number');
    return false;
  }
  
  // Check status enum
  if (!['active', 'completed', 'cancelled'].includes(event.status)) {
    console.error('Invalid status value');
    return false;
  }
  
  // Check confidence score range if present
  if (event.confidence !== undefined && (typeof event.confidence !== 'number' || event.confidence < 0 || event.confidence > 1)) {
    console.error('Confidence score must be a number between 0 and 1');
    return false;
  }
  
  return true;
};

/**
 * Validate loop reflection history against the schema
 * 
 * @param {Object} history - Loop reflection history to validate
 * @returns {boolean} Whether the history is valid
 */
export const validateLoopReflectionHistory = (history) => {
  // Check required fields
  const requiredFields = ['loop_id', 'reflections', 'current_depth'];
  for (const field of requiredFields) {
    if (history[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check reflections array
  if (!Array.isArray(history.reflections)) {
    console.error('Reflections must be an array');
    return false;
  }
  
  // Check current depth
  if (typeof history.current_depth !== 'number' || history.current_depth < 0) {
    console.error('Current depth must be a non-negative number');
    return false;
  }
  
  return true;
};

export default {
  ReflectionEventSchema,
  LoopReflectionHistorySchema,
  ReflectionDepthLogSchema,
  ConfidenceThresholdsSchema,
  EXAMPLE_REFLECTION_EVENT,
  EXAMPLE_LOOP_REFLECTION_HISTORY,
  validateReflectionEvent,
  validateLoopReflectionHistory
};
