/**
 * Escalation service for the Orchestrator Instruction Schema Engine
 * Phase 10.0 Implementation
 */

import { Instruction } from '../../backend/instruction_engine';
import { checkpointService } from './checkpointService';
import { reflectionService } from './reflectionService';

/**
 * Interface for escalation data
 */
export interface Escalation {
  escalation_id: string;
  instruction_id: string;
  agent_id: string;
  reason: 'validation_failed' | 'loop_exceeded' | 'missing_outputs' | 'tool_violation';
  details: string;
  created_at: Date;
  status: 'pending' | 'resolved';
}

/**
 * EscalationService class for managing escalations
 */
export class EscalationService {
  private escalations: Map<string, Escalation> = new Map();

  /**
   * Create a new escalation
   */
  createEscalation(
    instruction_id: string,
    agent_id: string,
    reason: Escalation['reason'],
    details: string
  ): Escalation {
    const escalation_id = this.generateEscalationId();
    const escalation: Escalation = {
      escalation_id,
      instruction_id,
      agent_id,
      reason,
      details,
      created_at: new Date(),
      status: 'pending'
    };

    this.escalations.set(escalation_id, escalation);
    return escalation;
  }

  /**
   * Get an escalation by ID
   */
  getEscalation(escalation_id: string): Escalation | undefined {
    return this.escalations.get(escalation_id);
  }

  /**
   * Get all escalations for a specific instruction
   */
  getEscalationsForInstruction(instruction_id: string): Escalation[] {
    return Array.from(this.escalations.values()).filter(
      (escalation) => escalation.instruction_id === instruction_id
    );
  }

  /**
   * Update escalation status
   */
  updateEscalationStatus(
    escalation_id: string,
    status: 'pending' | 'resolved'
  ): Escalation | undefined {
    const escalation = this.escalations.get(escalation_id);
    if (!escalation) return undefined;

    escalation.status = status;
    this.escalations.set(escalation_id, escalation);

    return escalation;
  }

  /**
   * Check if an instruction should be escalated
   */
  shouldEscalateInstruction(
    instruction: Instruction,
    loop_count: number,
    tool_used?: string
  ): { shouldEscalate: boolean; reason?: Escalation['reason']; details?: string } {
    // Check if loop count exceeds limit
    if (loop_count > instruction.loop_enforcement) {
      return {
        shouldEscalate: true,
        reason: 'loop_exceeded',
        details: `Loop count (${loop_count}) exceeds limit (${instruction.loop_enforcement})`
      };
    }

    // Check if tool usage is valid
    if (tool_used && !instruction.tools_required.includes(tool_used)) {
      return {
        shouldEscalate: true,
        reason: 'tool_violation',
        details: `Tool "${tool_used}" is not in the allowed tools list: ${instruction.tools_required.join(', ')}`
      };
    }

    // Check if all required checkpoints are approved
    if (
      instruction.status === 'in_progress' &&
      !checkpointService.areAllRequiredCheckpointsApproved(instruction)
    ) {
      const requiredCheckpoints = instruction.expected_outputs
        .filter((output: any) => output.type === 'checkpoint' && output.required)
        .map((output: any) => output.tag)
        .join(', ');

      return {
        shouldEscalate: true,
        reason: 'validation_failed',
        details: `Required checkpoints not approved: ${requiredCheckpoints}`
      };
    }

    // Check if all required reflections are created
    if (
      instruction.status === 'in_progress' &&
      !reflectionService.areAllRequiredReflectionsCreated(instruction)
    ) {
      const requiredReflections = instruction.expected_outputs
        .filter((output: any) => output.type === 'reflection' && output.required)
        .map((output: any) => output.tag)
        .join(', ');

      return {
        shouldEscalate: true,
        reason: 'missing_outputs',
        details: `Required reflections not created: ${requiredReflections}`
      };
    }

    // Check if instruction has failed and escalation is enabled
    if (instruction.status === 'failed' && instruction.escalate_on_failure) {
      return {
        shouldEscalate: true,
        reason: 'validation_failed',
        details: 'Instruction failed and escalation is enabled'
      };
    }

    return { shouldEscalate: false };
  }

  /**
   * Generate a unique escalation ID
   */
  private generateEscalationId(): string {
    return (
      'esc_' +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }
}

// Create a singleton instance of the escalation service
export const escalationService = new EscalationService();
