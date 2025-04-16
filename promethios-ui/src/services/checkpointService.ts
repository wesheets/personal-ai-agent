/**
 * Checkpoint validation service for the Orchestrator Instruction Schema Engine
 * Phase 10.0 Implementation
 */

import { Instruction } from '../../backend/instruction_engine';

/**
 * Interface for checkpoint data
 */
export interface Checkpoint {
  checkpoint_id: string;
  tag: string;
  content: string;
  agent_id: string;
  instruction_id: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: Date;
}

/**
 * CheckpointService class for managing checkpoints
 */
export class CheckpointService {
  private checkpoints: Map<string, Checkpoint> = new Map();

  /**
   * Create a new checkpoint
   */
  createCheckpoint(
    tag: string,
    content: string,
    agent_id: string,
    instruction_id: string
  ): Checkpoint {
    const checkpoint_id = this.generateCheckpointId();
    const checkpoint: Checkpoint = {
      checkpoint_id,
      tag,
      content,
      agent_id,
      instruction_id,
      status: 'pending',
      created_at: new Date()
    };

    this.checkpoints.set(checkpoint_id, checkpoint);
    return checkpoint;
  }

  /**
   * Get a checkpoint by ID
   */
  getCheckpoint(checkpoint_id: string): Checkpoint | undefined {
    return this.checkpoints.get(checkpoint_id);
  }

  /**
   * Get all checkpoints for a specific instruction
   */
  getCheckpointsForInstruction(instruction_id: string): Checkpoint[] {
    return Array.from(this.checkpoints.values()).filter(
      (checkpoint) => checkpoint.instruction_id === instruction_id
    );
  }

  /**
   * Update checkpoint status
   */
  updateCheckpointStatus(
    checkpoint_id: string,
    status: 'pending' | 'approved' | 'rejected'
  ): Checkpoint | undefined {
    const checkpoint = this.checkpoints.get(checkpoint_id);
    if (!checkpoint) return undefined;

    checkpoint.status = status;
    this.checkpoints.set(checkpoint_id, checkpoint);

    return checkpoint;
  }

  /**
   * Check if all required checkpoints for an instruction are approved
   */
  areAllRequiredCheckpointsApproved(instruction: Instruction): boolean {
    // Get all required checkpoint tags from the instruction
    const requiredCheckpointTags = instruction.expected_outputs
      .filter((output: any) => output.type === 'checkpoint' && output.required)
      .map((output: any) => output.tag);

    // Get all checkpoints for this instruction
    const instructionCheckpoints = this.getCheckpointsForInstruction(instruction.instruction_id);

    // Check if all required checkpoint tags have approved checkpoints
    return requiredCheckpointTags.every((tag: string) =>
      instructionCheckpoints.some(
        (checkpoint) => checkpoint.tag === tag && checkpoint.status === 'approved'
      )
    );
  }

  /**
   * Generate a unique checkpoint ID
   */
  private generateCheckpointId(): string {
    return (
      'chk_' +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }
}

// Create a singleton instance of the checkpoint service
export const checkpointService = new CheckpointService();
