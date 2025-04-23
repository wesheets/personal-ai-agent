/**
 * FreezeStatusSchema.js
 * 
 * Schema definitions for the reflection freeze lock system.
 * Enforces data structures for freeze events, status, and resolution.
 */

// Schema for a freeze event
export const FreezeEventSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the freeze event',
    example: 'freeze_1650389421000_1234'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop that was frozen',
    example: 'loop_291'
  },
  status: {
    type: 'string',
    description: 'Current status of the freeze',
    enum: ['frozen', 'unfrozen'],
    example: 'frozen'
  },
  reason: {
    type: 'string',
    description: 'Reason for freezing the loop',
    example: 'low confidence and unresolved contradiction'
  },
  reasons: {
    type: 'array',
    description: 'List of reasons for freezing the loop',
    items: {
      type: 'string',
      enum: [
        'low_confidence',
        'low_trust',
        'unresolved_contradiction',
        'no_manual_override'
      ]
    },
    example: ['low_confidence', 'unresolved_contradiction']
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the loop was frozen',
    example: '2025-04-22T14:30:21.000Z'
  },
  required_action: {
    type: 'string',
    description: 'Action required to unfreeze the loop',
    enum: ['re-reflect', 'operator_override', 'none'],
    example: 're-reflect'
  },
  agent: {
    type: 'string',
    description: 'Agent associated with the loop',
    example: 'SAGE'
  },
  project_id: {
    type: 'string',
    description: 'Project ID for scoping',
    example: 'life_tree'
  },
  unfrozen_at: {
    type: 'string',
    description: 'ISO timestamp when the loop was unfrozen',
    example: '2025-04-22T14:35:42.000Z'
  },
  unfreeze_reason: {
    type: 'string',
    description: 'Reason for unfreezing the loop',
    enum: [
      'conditions_met',
      'manual_operator_override',
      'reflection_completed',
      'contradiction_resolved'
    ],
    example: 'manual_operator_override'
  },
  manual_override: {
    type: 'boolean',
    description: 'Whether the unfreeze was a manual override',
    example: true
  },
  original_state: {
    type: 'object',
    description: 'Original loop state that triggered the freeze',
    properties: {
      confidence_score: {
        type: 'number',
        description: 'Confidence score at time of freeze (0-1)',
        example: 0.48
      },
      trust_score: {
        type: 'number',
        description: 'Trust score at time of freeze (0-1)',
        example: 0.65
      },
      reflection_depth: {
        type: 'number',
        description: 'Reflection depth at time of freeze',
        example: 2
      },
      contradictions_unresolved: {
        type: 'number',
        description: 'Number of unresolved contradictions at time of freeze',
        example: 1
      },
      manual_override: {
        type: 'boolean',
        description: 'Whether there was a manual override at time of freeze',
        example: false
      }
    }
  }
};

// Schema for freeze status
export const FreezeStatusSchema = {
  loop_id: {
    type: 'string',
    description: 'ID of the loop',
    example: 'loop_291'
  },
  status: {
    type: 'string',
    description: 'Current status of the loop',
    enum: ['frozen', 'unfrozen', 'executing'],
    example: 'frozen'
  },
  reason: {
    type: 'string',
    description: 'Reason for the current status',
    example: 'low confidence and unresolved contradiction'
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp of the status update',
    example: '2025-04-22T14:30:21.000Z'
  },
  required_action: {
    type: 'string',
    description: 'Action required to proceed',
    enum: ['re-reflect', 'operator_override', 'none'],
    example: 're-reflect'
  }
};

// Schema for freeze log
export const FreezeLogSchema = {
  meta: {
    type: 'object',
    description: 'Metadata about the freeze log',
    properties: {
      version: {
        type: 'string',
        description: 'Version of the freeze log schema',
        example: '1.0'
      },
      description: {
        type: 'string',
        description: 'Description of the freeze log',
        example: 'Append-only log of all loop freezes and resolutions'
      },
      last_updated: {
        type: 'string',
        description: 'ISO timestamp of the last update to the log',
        example: '2025-04-22T20:56:21.000Z'
      }
    }
  },
  events: {
    type: 'array',
    description: 'Array of freeze events',
    items: FreezeEventSchema
  }
};

// Example of a complete freeze event
export const EXAMPLE_FREEZE_EVENT = {
  id: "freeze_1650389421000_1234",
  loop_id: "loop_291",
  status: "frozen",
  reason: "low confidence and unresolved contradiction",
  reasons: ["low_confidence", "unresolved_contradiction"],
  timestamp: "2025-04-22T14:30:21.000Z",
  required_action: "re-reflect",
  agent: "SAGE",
  project_id: "life_tree",
  original_state: {
    confidence_score: 0.48,
    trust_score: 0.65,
    reflection_depth: 2,
    contradictions_unresolved: 1,
    manual_override: false
  }
};

// Example of a complete unfrozen event
export const EXAMPLE_UNFROZEN_EVENT = {
  id: "freeze_1650389421000_1234",
  loop_id: "loop_291",
  status: "unfrozen",
  reason: "low confidence and unresolved contradiction",
  reasons: ["low_confidence", "unresolved_contradiction"],
  timestamp: "2025-04-22T14:30:21.000Z",
  required_action: "re-reflect",
  agent: "SAGE",
  project_id: "life_tree",
  unfrozen_at: "2025-04-22T14:35:42.000Z",
  unfreeze_reason: "manual_operator_override",
  manual_override: true,
  original_state: {
    confidence_score: 0.48,
    trust_score: 0.65,
    reflection_depth: 2,
    contradictions_unresolved: 1,
    manual_override: false
  }
};

// Example of a freeze status
export const EXAMPLE_FREEZE_STATUS = {
  loop_id: "loop_291",
  status: "frozen",
  reason: "low confidence and unresolved contradiction",
  timestamp: "2025-04-22T14:30:21.000Z",
  required_action: "re-reflect"
};

// Validation functions

/**
 * Validate a freeze event against the schema
 * 
 * @param {Object} event - Freeze event to validate
 * @returns {boolean} Whether the event is valid
 */
export const validateFreezeEvent = (event) => {
  // Check required fields
  const requiredFields = ['id', 'loop_id', 'status', 'reason', 'timestamp', 'required_action'];
  for (const field of requiredFields) {
    if (event[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check status enum
  if (!['frozen', 'unfrozen'].includes(event.status)) {
    console.error('Invalid status value');
    return false;
  }
  
  // Check required_action enum
  if (!['re-reflect', 'operator_override', 'none'].includes(event.required_action)) {
    console.error('Invalid required_action value');
    return false;
  }
  
  // If unfrozen, check unfrozen_at and unfreeze_reason
  if (event.status === 'unfrozen') {
    if (!event.unfrozen_at) {
      console.error('Missing unfrozen_at for unfrozen event');
      return false;
    }
    
    if (!event.unfreeze_reason) {
      console.error('Missing unfreeze_reason for unfrozen event');
      return false;
    }
  }
  
  return true;
};

/**
 * Validate freeze status against the schema
 * 
 * @param {Object} status - Freeze status to validate
 * @returns {boolean} Whether the status is valid
 */
export const validateFreezeStatus = (status) => {
  // Check required fields
  const requiredFields = ['loop_id', 'status', 'timestamp'];
  for (const field of requiredFields) {
    if (status[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check status enum
  if (!['frozen', 'unfrozen', 'executing'].includes(status.status)) {
    console.error('Invalid status value');
    return false;
  }
  
  // If frozen, check reason and required_action
  if (status.status === 'frozen') {
    if (!status.reason) {
      console.error('Missing reason for frozen status');
      return false;
    }
    
    if (!status.required_action) {
      console.error('Missing required_action for frozen status');
      return false;
    }
  }
  
  return true;
};

export default {
  FreezeEventSchema,
  FreezeStatusSchema,
  FreezeLogSchema,
  EXAMPLE_FREEZE_EVENT,
  EXAMPLE_UNFROZEN_EVENT,
  EXAMPLE_FREEZE_STATUS,
  validateFreezeEvent,
  validateFreezeStatus
};
