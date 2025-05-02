/**
 * ContradictionSchema.js
 * 
 * Schema definitions for the contradiction detection and dissonance monitoring system.
 * This file defines the data structures used throughout the contradiction system.
 */

// Schema for a contradiction event
export const ContradictionEventSchema = {
  contradiction_id: {
    type: 'string',
    description: 'Unique identifier for the contradiction',
    example: 'contradiction_1650389421000_1234'
  },
  loop_id: {
    type: 'string',
    description: 'ID of the loop where the contradiction was detected',
    example: 'loop_789'
  },
  agent: {
    type: 'string',
    description: 'Agent that produced the contradicting statements',
    example: 'SAGE'
  },
  belief_1: {
    type: 'string',
    description: 'First statement in the contradiction',
    example: 'The system should prioritize user privacy over data collection.'
  },
  belief_2: {
    type: 'string',
    description: 'Second statement in the contradiction',
    example: 'Comprehensive data collection is necessary for optimal system performance.'
  },
  detected_at: {
    type: 'string',
    description: 'ISO timestamp when the contradiction was detected',
    example: '2025-04-22T14:30:21.000Z'
  },
  resolution: {
    type: 'string',
    description: 'Current resolution status of the contradiction',
    enum: ['unresolved', 'flagged', 'revised'],
    example: 'unresolved'
  },
  type: {
    type: 'string',
    description: 'Type of contradiction detected',
    enum: ['logical_opposite', 'conflicting_intent', 'divergent_values', 'semantic_conflict', 'temporal_inconsistency'],
    example: 'divergent_values'
  },
  score: {
    type: 'number',
    description: 'Confidence score of the contradiction detection (0-1)',
    example: 0.87
  },
  item1_type: {
    type: 'string',
    description: 'Type of the first item in the contradiction',
    enum: ['belief', 'reflection', 'summary'],
    example: 'belief'
  },
  item2_type: {
    type: 'string',
    description: 'Type of the second item in the contradiction',
    enum: ['belief', 'reflection', 'summary'],
    example: 'reflection'
  },
  item1_id: {
    type: 'string',
    description: 'ID of the first item in the contradiction',
    example: 'belief_privacy_001'
  },
  item2_id: {
    type: 'string',
    description: 'ID of the second item in the contradiction',
    example: 'reflection_789_001'
  }
};

// Schema for the contradiction log metadata
export const ContradictionLogMetaSchema = {
  last_updated: {
    type: 'string',
    description: 'ISO timestamp of the last update to the log',
    example: '2025-04-22T14:50:25.000Z'
  },
  version: {
    type: 'string',
    description: 'Version of the contradiction log schema',
    example: '1.0'
  },
  total_count: {
    type: 'number',
    description: 'Total number of contradictions in the log',
    example: 5
  },
  unresolved_count: {
    type: 'number',
    description: 'Number of unresolved contradictions',
    example: 3
  },
  flagged_count: {
    type: 'number',
    description: 'Number of flagged contradictions',
    example: 1
  },
  revised_count: {
    type: 'number',
    description: 'Number of revised contradictions',
    example: 1
  }
};

// Schema for the complete contradiction log
export const ContradictionLogSchema = {
  contradictions: {
    type: 'array',
    description: 'Array of contradiction events',
    items: ContradictionEventSchema
  },
  meta: {
    type: 'object',
    description: 'Metadata about the contradiction log',
    properties: ContradictionLogMetaSchema
  }
};

// Example of a complete contradiction event
export const EXAMPLE_CONTRADICTION = {
  contradiction_id: "contradiction_1650389421000_1234",
  loop_id: "loop_789",
  agent: "SAGE",
  belief_1: "The system should prioritize user privacy over data collection.",
  belief_2: "Comprehensive data collection is necessary for optimal system performance.",
  detected_at: "2025-04-22T14:30:21.000Z",
  resolution: "unresolved",
  type: "divergent_values",
  score: 0.87,
  item1_type: "belief",
  item2_type: "reflection",
  item1_id: "belief_privacy_001",
  item2_id: "reflection_789_001"
};

// Example of a complete contradiction log
export const EXAMPLE_CONTRADICTION_LOG = {
  contradictions: [EXAMPLE_CONTRADICTION],
  meta: {
    last_updated: "2025-04-22T14:50:25.000Z",
    version: "1.0",
    total_count: 1,
    unresolved_count: 1,
    flagged_count: 0,
    revised_count: 0
  }
};

export default {
  ContradictionEventSchema,
  ContradictionLogMetaSchema,
  ContradictionLogSchema,
  EXAMPLE_CONTRADICTION,
  EXAMPLE_CONTRADICTION_LOG
};
