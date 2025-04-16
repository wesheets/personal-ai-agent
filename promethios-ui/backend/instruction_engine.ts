/**
 * Instruction Schema Engine for the Orchestrator
 * Phase 10.0 Implementation
 */

/**
 * Interface for instruction expected output
 */
export interface InstructionExpectedOutput {
  type: 'memory' | 'reflection' | 'checkpoint';
  tag: string;
  required: boolean;
}

/**
 * Interface for instruction object
 */
export interface Instruction {
  instruction_id: string;
  goal_id: string;
  thread_id?: string;
  agent_id: string;
  task_summary: string;
  tools_required: string[];
  expected_outputs: InstructionExpectedOutput[];
  loop_enforcement: number;
  allow_retry: boolean;
  escalate_on_failure: boolean;
  status: 'pending' | 'in_progress' | 'complete' | 'failed';
  last_updated: Date;
}

/**
 * Interface for instruction creation options
 */
export interface InstructionOptions {
  loop_enforcement?: number;
  allow_retry?: boolean;
  escalate_on_failure?: boolean;
  thread_id?: string;
}

/**
 * Class for managing instruction objects
 */
export class InstructionRegistry {
  private instructions: Map<string, Instruction> = new Map();

  /**
   * Create a new instruction
   */
  createInstruction(
    goal_id: string,
    agent_id: string,
    task_summary: string,
    tools_required: string[],
    expected_outputs: InstructionExpectedOutput[],
    options: InstructionOptions = {}
  ): Instruction {
    const instruction_id = this.generateInstructionId();
    const instruction: Instruction = {
      instruction_id,
      goal_id,
      thread_id: options.thread_id,
      agent_id,
      task_summary,
      tools_required,
      expected_outputs,
      loop_enforcement: options.loop_enforcement ?? 3,
      allow_retry: options.allow_retry ?? true,
      escalate_on_failure: options.escalate_on_failure ?? true,
      status: 'pending',
      last_updated: new Date()
    };

    this.instructions.set(instruction_id, instruction);
    return instruction;
  }

  /**
   * Get an instruction by ID
   */
  getInstruction(instruction_id: string): Instruction | undefined {
    return this.instructions.get(instruction_id);
  }

  /**
   * Get all instructions for a specific agent
   */
  getInstructionsForAgent(agent_id: string): Instruction[] {
    return Array.from(this.instructions.values()).filter(
      (instruction) => instruction.agent_id === agent_id
    );
  }

  /**
   * Get all instructions for a specific goal
   */
  getInstructionsForGoal(goal_id: string): Instruction[] {
    return Array.from(this.instructions.values()).filter(
      (instruction) => instruction.goal_id === goal_id
    );
  }

  /**
   * Update instruction status
   */
  updateInstructionStatus(
    instruction_id: string,
    status: 'pending' | 'in_progress' | 'complete' | 'failed'
  ): Instruction | undefined {
    const instruction = this.instructions.get(instruction_id);
    if (!instruction) return undefined;

    instruction.status = status;
    instruction.last_updated = new Date();
    this.instructions.set(instruction_id, instruction);

    return instruction;
  }

  /**
   * Generate a unique instruction ID
   */
  private generateInstructionId(): string {
    return (
      'inst_' +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }
}

/**
 * Orchestrator Instructions static class for creating and managing instructions
 */
export class OrchestratorInstructions {
  /**
   * Create an instruction for an agent
   */
  static createInstructionForAgent(
    goal_id: string,
    agent_id: string,
    task_summary: string,
    tools_required: string[],
    expected_outputs: InstructionExpectedOutput[],
    options: InstructionOptions = {}
  ): Instruction {
    return instructionRegistry.createInstruction(
      goal_id,
      agent_id,
      task_summary,
      tools_required,
      expected_outputs,
      options
    );
  }

  /**
   * Generate a unique goal ID
   */
  static generateGoalId(): string {
    return (
      'goal_' +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }

  /**
   * Validate if a tool is allowed for an instruction
   */
  static isToolAllowed(instruction: Instruction, tool: string): boolean {
    return instruction.tools_required.includes(tool);
  }
}

// Create a singleton instance of the instruction registry
export const instructionRegistry = new InstructionRegistry();
