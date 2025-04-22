/**
 * TrustSchema.js
 * 
 * Schema definitions for the trust feedback loop system.
 * Enforces data structure for trust scores, events, and agent status.
 */

// Schema for a trust score event
export const TrustScoreEventSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the trust event',
    example: 'trust_1650389421000_1234'
  },
  agent: {
    type: 'string',
    description: 'Agent identifier',
    example: 'SAGE'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop where the trust was evaluated',
    example: 'loop_284'
  },
  trust_score: {
    type: 'number',
    description: 'Trust score value (0-1)',
    example: 0.72
  },
  delta: {
    type: 'number',
    description: 'Change in trust score from previous evaluation',
    example: -0.13
  },
  reason: {
    type: 'string',
    description: 'Reason for trust score change',
    example: 'contradiction detected + unresolved'
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the trust was evaluated',
    example: '2025-04-22T14:30:21.000Z'
  },
  status: {
    type: 'string',
    description: 'Current status of the agent',
    enum: ['active', 'demoted', 're-evaluating'],
    example: 'active'
  },
  metrics: {
    type: 'object',
    description: 'Performance metrics used for trust evaluation',
    properties: {
      summary_realism: {
        type: 'number',
        description: 'Score for summary realism (0-1)',
        example: 0.85
      },
      loop_success: {
        type: 'number',
        description: 'Score for loop success (0-1)',
        example: 0.92
      },
      reflection_clarity: {
        type: 'number',
        description: 'Score for reflection clarity (0-1)',
        example: 0.78
      },
      contradiction_frequency: {
        type: 'number',
        description: 'Frequency of contradictions (0-1)',
        example: 0.15
      },
      revision_rate: {
        type: 'number',
        description: 'Rate of revisions (0-1)',
        example: 0.23
      },
      operator_override: {
        type: 'number',
        description: 'Frequency of operator overrides (0-1)',
        example: 0.05
      }
    }
  }
};

// Schema for agent demotion event
export const AgentDemotionSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the demotion event',
    example: 'demotion_1650389421000_5678'
  },
  agent: {
    type: 'string',
    description: 'Agent that was demoted',
    example: 'HAL'
  },
  fallback_agent: {
    type: 'string',
    description: 'Agent that will replace the demoted agent',
    example: 'NOVA'
  },
  trust_score: {
    type: 'number',
    description: 'Trust score at time of demotion',
    example: 0.35
  },
  reason: {
    type: 'string',
    description: 'Reason for demotion',
    example: 'contradiction detected + unresolved'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop where the demotion occurred',
    example: 'loop_284'
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the demotion occurred',
    example: '2025-04-22T14:30:21.000Z'
  },
  status: {
    type: 'string',
    description: 'Current status of the demotion',
    enum: ['active', 'restored', 'reset'],
    example: 'active'
  },
  manual: {
    type: 'boolean',
    description: 'Whether the demotion was manually triggered',
    example: false
  }
};

// Schema for agent promotion event
export const AgentPromotionSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the promotion event',
    example: 'promotion_1650389421000_9012'
  },
  agent: {
    type: 'string',
    description: 'Agent that was promoted',
    example: 'HAL'
  },
  trust_score: {
    type: 'number',
    description: 'Trust score at time of promotion',
    example: 0.65
  },
  reason: {
    type: 'string',
    description: 'Reason for promotion',
    example: 'trust score recovery'
  },
  previous_demotion: {
    type: 'object',
    description: 'Reference to the previous demotion event',
    properties: AgentDemotionSchema
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the promotion occurred',
    example: '2025-04-22T15:45:33.000Z'
  },
  manual: {
    type: 'boolean',
    description: 'Whether the promotion was manually triggered',
    example: false
  }
};

// Schema for trust score history
export const TrustHistorySchema = {
  agent: {
    type: 'string',
    description: 'Agent identifier',
    example: 'SAGE'
  },
  history: {
    type: 'array',
    description: 'Array of trust score events',
    items: TrustScoreEventSchema
  }
};

// Schema for trust score state
export const TrustScoreStateSchema = {
  scores: {
    type: 'object',
    description: 'Current trust scores for all agents',
    example: {
      'SAGE': 0.92,
      'HAL': 0.65,
      'NOVA': 0.78,
      'CRITIC': 0.81
    }
  },
  history: {
    type: 'object',
    description: 'Trust history for all agents',
    properties: TrustHistorySchema
  },
  demoted_agents: {
    type: 'object',
    description: 'Currently demoted agents',
    example: {
      'HAL': {
        timestamp: '2025-04-22T14:30:21.000Z',
        reason: 'contradiction detected + unresolved',
        score: 0.35
      }
    }
  },
  last_updated: {
    type: 'string',
    description: 'ISO timestamp of last update',
    example: '2025-04-22T15:45:33.000Z'
  },
  project_id: {
    type: 'string',
    description: 'Project ID for scoping',
    example: 'main_project'
  }
};

// Example of a complete trust score event
export const EXAMPLE_TRUST_EVENT = {
  id: "trust_1650389421000_1234",
  agent: "SAGE",
  loop_id: "loop_284",
  trust_score: 0.72,
  delta: -0.13,
  reason: "contradiction detected + unresolved",
  timestamp: "2025-04-22T14:30:21.000Z",
  status: "active",
  metrics: {
    summary_realism: 0.85,
    loop_success: 0.92,
    reflection_clarity: 0.78,
    contradiction_frequency: 0.15,
    revision_rate: 0.23,
    operator_override: 0.05
  }
};

// Example of a complete demotion event
export const EXAMPLE_DEMOTION = {
  id: "demotion_1650389421000_5678",
  agent: "HAL",
  fallback_agent: "NOVA",
  trust_score: 0.35,
  reason: "contradiction detected + unresolved",
  loop_id: "loop_284",
  timestamp: "2025-04-22T14:30:21.000Z",
  status: "active",
  manual: false
};

// Example of a complete trust state
export const EXAMPLE_TRUST_STATE = {
  scores: {
    'SAGE': 0.92,
    'HAL': 0.35,
    'NOVA': 0.78,
    'CRITIC': 0.81
  },
  history: {
    'SAGE': [EXAMPLE_TRUST_EVENT],
    'HAL': [],
    'NOVA': [],
    'CRITIC': []
  },
  demoted_agents: {
    'HAL': EXAMPLE_DEMOTION
  },
  last_updated: "2025-04-22T15:45:33.000Z",
  project_id: "main_project"
};

// Validation functions

/**
 * Validate a trust score event against the schema
 * 
 * @param {Object} event - Trust score event to validate
 * @returns {boolean} Whether the event is valid
 */
export const validateTrustEvent = (event) => {
  // Check required fields
  const requiredFields = ['id', 'agent', 'loop_id', 'trust_score', 'timestamp', 'status'];
  for (const field of requiredFields) {
    if (event[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check trust score range
  if (typeof event.trust_score !== 'number' || event.trust_score < 0 || event.trust_score > 1) {
    console.error('Trust score must be a number between 0 and 1');
    return false;
  }
  
  // Check status enum
  if (!['active', 'demoted', 're-evaluating'].includes(event.status)) {
    console.error('Invalid status value');
    return false;
  }
  
  return true;
};

/**
 * Validate a demotion event against the schema
 * 
 * @param {Object} event - Demotion event to validate
 * @returns {boolean} Whether the event is valid
 */
export const validateDemotionEvent = (event) => {
  // Check required fields
  const requiredFields = ['id', 'agent', 'fallback_agent', 'trust_score', 'timestamp', 'status'];
  for (const field of requiredFields) {
    if (event[field] === undefined) {
      console.error(`Missing required field: ${field}`);
      return false;
    }
  }
  
  // Check trust score range
  if (typeof event.trust_score !== 'number' || event.trust_score < 0 || event.trust_score > 1) {
    console.error('Trust score must be a number between 0 and 1');
    return false;
  }
  
  // Check status enum
  if (!['active', 'restored', 'reset'].includes(event.status)) {
    console.error('Invalid status value');
    return false;
  }
  
  return true;
};

export default {
  TrustScoreEventSchema,
  AgentDemotionSchema,
  AgentPromotionSchema,
  TrustHistorySchema,
  TrustScoreStateSchema,
  EXAMPLE_TRUST_EVENT,
  EXAMPLE_DEMOTION,
  EXAMPLE_TRUST_STATE,
  validateTrustEvent,
  validateDemotionEvent
};
