/**
 * Reflection validation service for the Orchestrator Instruction Schema Engine
 * Phase 10.0 Implementation
 */

import { Instruction } from '../backend/instruction_engine';

/**
 * Interface for reflection data
 */
export interface Reflection {
  reflection_id: string;
  tag: string;
  content: string;
  agent_id: string;
  instruction_id: string;
  created_at: Date;
}

/**
 * ReflectionService class for managing reflections
 */
export class ReflectionService {
  private reflections: Map<string, Reflection> = new Map();
  
  /**
   * Create a new reflection
   */
  createReflection(
    tag: string,
    content: string,
    agent_id: string,
    instruction_id: string
  ): Reflection {
    const reflection_id = this.generateReflectionId();
    const reflection: Reflection = {
      reflection_id,
      tag,
      content,
      agent_id,
      instruction_id,
      created_at: new Date()
    };
    
    this.reflections.set(reflection_id, reflection);
    return reflection;
  }
  
  /**
   * Get a reflection by ID
   */
  getReflection(reflection_id: string): Reflection | undefined {
    return this.reflections.get(reflection_id);
  }
  
  /**
   * Get all reflections for a specific instruction
   */
  getReflectionsForInstruction(instruction_id: string): Reflection[] {
    return Array.from(this.reflections.values())
      .filter(reflection => reflection.instruction_id === instruction_id);
  }
  
  /**
   * Check if all required reflections for an instruction are created
   */
  areAllRequiredReflectionsCreated(instruction: Instruction): boolean {
    // Get all required reflection tags from the instruction
    const requiredReflectionTags = instruction.expected_outputs
      .filter((output: any) => output.type === 'reflection' && output.required)
      .map((output: any) => output.tag);
    
    // Get all reflections for this instruction
    const instructionReflections = this.getReflectionsForInstruction(instruction.instruction_id);
    
    // Check if all required reflection tags have reflections
    return requiredReflectionTags.every((tag: string) => 
      instructionReflections.some(reflection => reflection.tag === tag)
    );
  }
  
  /**
   * Generate a unique reflection ID
   */
  private generateReflectionId(): string {
    return 'refl_' + Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }
}

// Create a singleton instance of the reflection service
export const reflectionService = new ReflectionService();
