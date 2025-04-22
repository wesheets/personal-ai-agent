/**
 * Schema definitions for the Belief Anchoring and Misalignment Alerts system
 * This file defines the data structures used throughout the belief monitoring system
 */

// Schema for an anchored belief
export const AnchoredBeliefSchema = {
  belief_id: {
    type: 'string',
    description: 'Unique identifier for the belief',
    example: 'life_tree_intent_001'
  },
  content: {
    type: 'string',
    description: 'The actual belief statement',
    example: 'The system should prioritize emotional safety over technical completeness.'
  },
  critical: {
    type: 'boolean',
    description: 'Whether this is a critical belief that should never be violated',
    example: true
  },
  project_id: {
    type: 'string',
    description: 'ID of the project this belief is associated with',
    example: 'life_tree'
  },
  agent_origin: {
    type: 'string',
    description: 'The agent that originally defined this belief',
    enum: ['SAGE', 'HAL', 'NOVA', 'CRITIC', 'OPERATOR'],
    example: 'SAGE'
  },
  drift_threshold: {
    type: 'number',
    description: 'Threshold for detecting drift from this belief (0-1)',
    example: 0.7
  },
  deprecated: {
    type: 'boolean',
    description: 'Whether this belief has been deprecated',
    example: false
  },
  last_violated_loop: {
    type: 'string',
    description: 'ID of the last loop where this belief was violated',
    example: 'loop_289'
  },
  drift_score: {
    type: 'number',
    description: 'Current drift score for this belief (0-1)',
    example: 0.84
  }
};

// Schema for a misalignment alert
export const MisalignmentAlertSchema = {
  id: {
    type: 'string',
    description: 'Unique identifier for the alert',
    example: 'alert_001'
  },
  belief_id: {
    type: 'string',
    description: 'ID of the belief that was violated',
    example: 'life_tree_intent_001'
  },
  belief_content: {
    type: 'string',
    description: 'Content of the belief that was violated',
    example: 'The system should prioritize emotional safety over technical completeness.'
  },
  agent_involved: {
    type: 'string',
    description: 'The agent that violated the belief',
    example: 'SAGE'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop where the violation occurred',
    example: 'loop_289'
  },
  drift_score: {
    type: 'number',
    description: 'Calculated drift score for this violation (0-1)',
    example: 0.84
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the violation was detected',
    example: '2025-04-22T15:30:45.123Z'
  },
  violation_content: {
    type: 'string',
    description: 'The content that violated the belief',
    example: 'Proceeding with technical implementation despite user expressing discomfort with the approach.'
  },
  status: {
    type: 'string',
    description: 'Current status of the alert',
    enum: ['active', 'reflecting', 'replanning', 'resolved'],
    example: 'active'
  },
  resolution: {
    type: 'string',
    description: 'How the alert was resolved (if resolved)',
    enum: ['reflected', 'replanned', 'override_approved', null],
    example: 'reflected'
  }
};

// Schema for a belief drift check result
export const DriftCheckResultSchema = {
  content: {
    type: 'string',
    description: 'The content that was checked',
    example: 'We should implement this feature immediately to meet the deadline.'
  },
  violations: {
    type: 'array',
    description: 'List of beliefs that were violated',
    items: {
      type: 'object',
      properties: {
        belief_id: {
          type: 'string',
          description: 'ID of the violated belief',
          example: 'life_tree_intent_001'
        },
        belief_content: {
          type: 'string',
          description: 'Content of the violated belief',
          example: 'The system should prioritize emotional safety over technical completeness.'
        },
        drift_score: {
          type: 'number',
          description: 'Calculated drift score',
          example: 0.84
        },
        threshold: {
          type: 'number',
          description: 'Threshold that was exceeded',
          example: 0.7
        },
        critical: {
          type: 'boolean',
          description: 'Whether this is a critical belief',
          example: true
        }
      }
    }
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp of the check',
    example: '2025-04-22T15:30:45.123Z'
  },
  passed: {
    type: 'boolean',
    description: 'Whether the content passed all belief checks',
    example: false
  }
};

// Example of a complete belief record
export const EXAMPLE_BELIEF = {
  belief_id: "life_tree_intent_001",
  content: "The system should prioritize emotional safety over technical completeness.",
  critical: true,
  project_id: "life_tree",
  agent_origin: "SAGE",
  drift_threshold: 0.7,
  deprecated: false,
  last_violated_loop: "loop_289",
  drift_score: 0.84
};

// Example of a complete misalignment alert
export const EXAMPLE_ALERT = {
  id: "alert_001",
  belief_id: "life_tree_intent_001",
  belief_content: "The system should prioritize emotional safety over technical completeness.",
  agent_involved: "SAGE",
  loop_id: "loop_289",
  drift_score: 0.84,
  timestamp: "2025-04-22T15:30:45.123Z",
  violation_content: "Proceeding with technical implementation despite user expressing discomfort with the approach.",
  status: "active",
  resolution: null
};

export default {
  AnchoredBeliefSchema,
  MisalignmentAlertSchema,
  DriftCheckResultSchema,
  EXAMPLE_BELIEF,
  EXAMPLE_ALERT
};
