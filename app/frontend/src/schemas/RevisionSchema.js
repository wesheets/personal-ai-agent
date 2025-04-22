/**
 * Schema definitions for the Loop Revision and Reflection Retraction system
 * This file defines the data structures used throughout the revision system
 */

// Schema for a loop revision
export const LoopRevisionSchema = {
  loop_id: {
    type: 'string',
    description: 'Unique identifier for the new loop',
    example: 'loop_456'
  },
  revised_from_loop_id: {
    type: 'string',
    description: 'ID of the original loop being revised',
    example: 'loop_123'
  },
  agent: {
    type: 'string',
    description: 'Agent that created the revision',
    example: 'SAGE'
  },
  reason: {
    type: 'string',
    description: 'Reason for the revision',
    enum: ['misalignment', 'drift', 'operator_override', 'contradiction'],
    example: 'misalignment'
  },
  timestamp: {
    type: 'string',
    description: 'ISO timestamp when the revision was created',
    example: '2025-04-22T15:30:45.123Z'
  },
  status: {
    type: 'string',
    description: 'Current status of the revision',
    enum: ['revised', 'pending', 'replanned'],
    example: 'revised'
  },
  project_id: {
    type: 'string',
    description: 'ID of the project this revision belongs to',
    example: 'life_tree'
  },
  original_reflection: {
    type: 'string',
    description: 'The original reflection content',
    example: 'The user wants to implement a feature that maximizes efficiency regardless of user comfort.'
  },
  revised_reflection: {
    type: 'string',
    description: 'The revised reflection content',
    example: 'The user wants to implement a feature that balances efficiency with user comfort and emotional safety.'
  }
};

// Schema for a replan operation
export const ReplanOperationSchema = {
  loop_id: {
    type: 'string',
    description: 'Unique identifier for the new loop',
    example: 'loop_456'
  },
  revised_from_loop_id: {
    type: 'string',
    description: 'ID of the original loop being revised',
    example: 'loop_123'
  },
  agent: {
    type: 'string',
    description: 'Agent that will handle the replanning',
    example: 'SAGE'
  },
  reason: {
    type: 'string',
    description: 'Reason for the replan',
    enum: ['misalignment', 'drift', 'operator_override', 'contradiction'],
    example: 'misalignment'
  },
  revised_reflection: {
    type: 'string',
    description: 'The revised reflection to use for replanning',
    example: 'The user wants to implement a feature that balances efficiency with user comfort and emotional safety.'
  },
  project_id: {
    type: 'string',
    description: 'ID of the project this replan belongs to',
    example: 'life_tree'
  },
  status: {
    type: 'string',
    description: 'Current status of the replan operation',
    enum: ['starting', 'replanning', 'completed', 'failed'],
    example: 'replanning'
  }
};

// Example of a complete loop revision record
export const EXAMPLE_REVISION = {
  loop_id: "loop_456",
  revised_from_loop_id: "loop_123",
  agent: "SAGE",
  reason: "misalignment",
  timestamp: "2025-04-22T15:30:45.123Z",
  status: "revised",
  project_id: "life_tree",
  original_reflection: "The user wants to implement a feature that maximizes efficiency regardless of user comfort.",
  revised_reflection: "The user wants to implement a feature that balances efficiency with user comfort and emotional safety."
};

// Example of a complete replan operation
export const EXAMPLE_REPLAN = {
  loop_id: "loop_456",
  revised_from_loop_id: "loop_123",
  agent: "SAGE",
  reason: "misalignment",
  revised_reflection: "The user wants to implement a feature that balances efficiency with user comfort and emotional safety.",
  project_id: "life_tree",
  status: "replanning"
};

export default {
  LoopRevisionSchema,
  ReplanOperationSchema,
  EXAMPLE_REVISION,
  EXAMPLE_REPLAN
};
