import React from 'react';
import { Box, Heading, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react';
import InstructionTester from '../components/InstructionTester';

/**
 * Test page for the Instruction Schema Engine
 * Provides a UI for testing the Phase 10.0 implementation
 */
const TestPage: React.FC = () => {
  return (
    <Box p={5}>
      <Heading mb={5}>Phase 10.0 Instruction Schema Engine Test</Heading>
      
      <Tabs variant="enclosed">
        <TabList>
          <Tab>Instruction Tester</Tab>
          <Tab>Documentation</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <InstructionTester />
          </TabPanel>
          
          <TabPanel>
            <Box p={5} borderWidth="1px" borderRadius="lg">
              <Heading size="md" mb={4}>Instruction Schema Engine Documentation</Heading>
              
              <Heading size="sm" mb={2}>Overview</Heading>
              <Box mb={4}>
                <p>The Instruction Schema Engine provides a formal schema for agent instructions, ensuring all instructions are schema-bound, trackable, and validated throughout the execution process.</p>
              </Box>
              
              <Heading size="sm" mb={2}>Key Components</Heading>
              <Box mb={4}>
                <ul>
                  <li><strong>Instruction Object:</strong> Defines the structure of agent instructions with properties like instruction_id, goal_id, thread_id, agent_id, task_summary, tools_required, expected_outputs, and control parameters.</li>
                  <li><strong>InstructionRegistry:</strong> Manages instruction objects, providing methods for creating, updating, and validating instructions.</li>
                  <li><strong>OrchestratorInstructions:</strong> Functions for generating structured instruction objects when the operator sends a goal.</li>
                  <li><strong>AgentInstructionValidation:</strong> Functions for validating tool usage, checkpoints, and reflections.</li>
                </ul>
              </Box>
              
              <Heading size="sm" mb={2}>Validation Services</Heading>
              <Box mb={4}>
                <ul>
                  <li><strong>CheckpointService:</strong> Manages checkpoints and validates if all required checkpoints for an instruction are approved.</li>
                  <li><strong>ReflectionService:</strong> Manages reflections and validates if all required reflections for an instruction are created.</li>
                  <li><strong>EscalationService:</strong> Handles escalation logic for failed validations, loop enforcement, and tool violations.</li>
                </ul>
              </Box>
              
              <Heading size="sm" mb={2}>UI Components</Heading>
              <Box mb={4}>
                <ul>
                  <li><strong>InstructionPreviewCard:</strong> Displays instruction details in a card format.</li>
                  <li><strong>AgentSandboxCard:</strong> Includes an Active Instruction panel to display the current instruction for an agent.</li>
                  <li><strong>AgentChat:</strong> Logs instruction assignments and shows progress indicators.</li>
                </ul>
              </Box>
              
              <Heading size="sm" mb={2}>Usage</Heading>
              <Box>
                <p>The Instruction Schema Engine is used by the Orchestrator to generate structured instruction objects when the operator sends a goal. Agents accept these instructions and execute tasks using only the specified tools. The engine validates that all required outputs are created and escalates to the Orchestrator when necessary.</p>
              </Box>
            </Box>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default TestPage;
