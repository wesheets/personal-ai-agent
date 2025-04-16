import React, { useState } from 'react';
import {
  Box,
  Button,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  Checkbox,
  HStack,
  Tag,
  TagLabel,
  TagCloseButton,
  useToast,
  Divider
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import {
  Instruction,
  OrchestratorInstructions,
  InstructionExpectedOutput
} from '../../backend/instruction_engine';
import InstructionPreviewCard from './InstructionPreviewCard';
import { checkpointService } from '../services/checkpointService';
import { reflectionService } from '../services/reflectionService';
import { escalationService } from '../services/escalationService';

/**
 * Component for testing the Instruction Schema Engine
 * Allows creating test instructions and simulating validation scenarios
 */
const InstructionTester: React.FC = () => {
  const toast = useToast();
  const [goalId, setGoalId] = useState<string>(OrchestratorInstructions.generateGoalId());
  const [agentId, setAgentId] = useState<string>('hal');
  const [taskSummary, setTaskSummary] = useState<string>('');
  const [toolInput, setToolInput] = useState<string>('');
  const [toolsRequired, setToolsRequired] = useState<string[]>(['file_read', 'file_write']);
  const [outputType, setOutputType] = useState<string>('memory');
  const [outputTag, setOutputTag] = useState<string>('');
  const [outputRequired, setOutputRequired] = useState<boolean>(true);
  const [expectedOutputs, setExpectedOutputs] = useState<InstructionExpectedOutput[]>([]);
  const [loopEnforcement, setLoopEnforcement] = useState<number>(1);
  const [allowRetry, setAllowRetry] = useState<boolean>(true);
  const [escalateOnFailure, setEscalateOnFailure] = useState<boolean>(true);

  const [createdInstruction, setCreatedInstruction] = useState<Instruction | null>(null);
  const [completedOutputs, setCompletedOutputs] = useState<{ type: string; tag: string }[]>([]);
  const [loopCount, setLoopCount] = useState<number>(0);
  const [usedTool, setUsedTool] = useState<string>('');

  // Add a tool to the list
  const addTool = () => {
    if (!toolInput.trim()) return;
    if (toolsRequired.includes(toolInput)) {
      toast({
        title: 'Tool already added',
        status: 'warning',
        duration: 2000
      });
      return;
    }
    setToolsRequired([...toolsRequired, toolInput]);
    setToolInput('');
  };

  // Remove a tool from the list
  const removeTool = (tool: string) => {
    setToolsRequired(toolsRequired.filter((t) => t !== tool));
  };

  // Add an expected output
  const addExpectedOutput = () => {
    if (!outputTag.trim()) return;
    const newOutput: InstructionExpectedOutput = {
      type: outputType as 'memory' | 'reflection' | 'checkpoint',
      tag: outputTag,
      required: outputRequired
    };
    setExpectedOutputs([...expectedOutputs, newOutput]);
    setOutputTag('');
  };

  // Remove an expected output
  const removeExpectedOutput = (index: number) => {
    setExpectedOutputs(expectedOutputs.filter((_, i) => i !== index));
  };

  // Create a test instruction
  const createInstruction = () => {
    if (!taskSummary.trim()) {
      toast({
        title: 'Task summary is required',
        status: 'error',
        duration: 2000
      });
      return;
    }

    if (expectedOutputs.length === 0) {
      toast({
        title: 'At least one expected output is required',
        status: 'error',
        duration: 2000
      });
      return;
    }

    const instruction = OrchestratorInstructions.createInstructionForAgent(
      goalId,
      agentId,
      taskSummary,
      toolsRequired,
      expectedOutputs,
      {
        loop_enforcement: loopEnforcement,
        allow_retry: allowRetry,
        escalate_on_failure: escalateOnFailure
      }
    );

    setCreatedInstruction(instruction);
    setCompletedOutputs([]);
    setLoopCount(0);
    setUsedTool('');

    toast({
      title: 'Instruction created',
      description: `Instruction ID: ${instruction.instruction_id}`,
      status: 'success',
      duration: 3000
    });
  };

  // Simulate completing an output
  const completeOutput = (type: string, tag: string) => {
    if (!createdInstruction) return;

    // Add to completed outputs
    const newOutput = { type, tag };
    setCompletedOutputs([...completedOutputs, newOutput]);

    // Create the appropriate record based on type
    if (type === 'checkpoint') {
      const checkpoint = checkpointService.createCheckpoint(
        tag,
        `Test checkpoint for ${tag}`,
        createdInstruction.agent_id,
        createdInstruction.instruction_id
      );

      // Auto-approve the checkpoint
      checkpointService.updateCheckpointStatus(checkpoint.checkpoint_id, 'approved');

      toast({
        title: 'Checkpoint created and approved',
        description: `Tag: ${tag}`,
        status: 'success',
        duration: 2000
      });
    } else if (type === 'reflection') {
      reflectionService.createReflection(
        tag,
        `Test reflection for ${tag}`,
        createdInstruction.agent_id,
        createdInstruction.instruction_id
      );

      toast({
        title: 'Reflection created',
        description: `Tag: ${tag}`,
        status: 'success',
        duration: 2000
      });
    } else {
      toast({
        title: 'Memory output completed',
        description: `Tag: ${tag}`,
        status: 'success',
        duration: 2000
      });
    }
  };

  // Simulate using a tool
  const simulateToolUsage = () => {
    if (!createdInstruction || !usedTool) return;

    const escalationCheck = escalationService.shouldEscalateInstruction(
      createdInstruction,
      loopCount,
      usedTool
    );

    if (escalationCheck.shouldEscalate) {
      escalationService.createEscalation(
        createdInstruction.instruction_id,
        createdInstruction.agent_id,
        escalationCheck.reason!,
        escalationCheck.details!
      );

      toast({
        title: 'Escalation triggered',
        description: escalationCheck.details,
        status: 'error',
        duration: 3000
      });
    } else {
      toast({
        title: 'Tool usage allowed',
        description: `Tool "${usedTool}" is in the allowed tools list`,
        status: 'success',
        duration: 2000
      });
    }
  };

  // Increment loop count
  const incrementLoopCount = () => {
    if (!createdInstruction) return;

    const newLoopCount = loopCount + 1;
    setLoopCount(newLoopCount);

    const escalationCheck = escalationService.shouldEscalateInstruction(
      createdInstruction,
      newLoopCount
    );

    if (escalationCheck.shouldEscalate) {
      escalationService.createEscalation(
        createdInstruction.instruction_id,
        createdInstruction.agent_id,
        escalationCheck.reason!,
        escalationCheck.details!
      );

      toast({
        title: 'Escalation triggered',
        description: escalationCheck.details,
        status: 'error',
        duration: 3000
      });
    }
  };

  // Check validation status
  const checkValidationStatus = () => {
    if (!createdInstruction) return;

    const checkpointsValid =
      checkpointService.areAllRequiredCheckpointsApproved(createdInstruction);
    const reflectionsValid = reflectionService.areAllRequiredReflectionsCreated(createdInstruction);

    if (checkpointsValid && reflectionsValid) {
      toast({
        title: 'Validation passed',
        description: 'All required checkpoints and reflections are completed',
        status: 'success',
        duration: 3000
      });
    } else {
      let message = '';
      if (!checkpointsValid) message += 'Required checkpoints not approved. ';
      if (!reflectionsValid) message += 'Required reflections not created.';

      toast({
        title: 'Validation failed',
        description: message,
        status: 'error',
        duration: 3000
      });
    }
  };

  return (
    <Box p={5} borderWidth="1px" borderRadius="lg" maxWidth="800px" mx="auto">
      <Heading size="lg" mb={4}>
        Instruction Schema Engine Tester
      </Heading>

      <VStack spacing={6} align="stretch">
        {/* Instruction Creation Form */}
        <Box>
          <Heading size="md" mb={3}>
            Create Test Instruction
          </Heading>

          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Goal ID</FormLabel>
              <Input
                value={goalId}
                onChange={(e) => setGoalId(e.target.value)}
                placeholder="Goal ID"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Agent ID</FormLabel>
              <Select value={agentId} onChange={(e) => setAgentId(e.target.value)}>
                <option value="hal">HAL</option>
                <option value="ash">ASH</option>
                <option value="nova">NOVA</option>
                <option value="orchestrator">Orchestrator</option>
              </Select>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Task Summary</FormLabel>
              <Textarea
                value={taskSummary}
                onChange={(e) => setTaskSummary(e.target.value)}
                placeholder="Describe the task..."
              />
            </FormControl>

            <FormControl>
              <FormLabel>Tools Required</FormLabel>
              <HStack>
                <Input
                  value={toolInput}
                  onChange={(e) => setToolInput(e.target.value)}
                  placeholder="Add a tool..."
                />
                <Button leftIcon={<AddIcon />} onClick={addTool}>
                  Add
                </Button>
              </HStack>
              <Box mt={2}>
                {toolsRequired.map((tool) => (
                  <Tag
                    key={tool}
                    size="md"
                    borderRadius="full"
                    variant="solid"
                    colorScheme="blue"
                    m={1}
                  >
                    <TagLabel>{tool}</TagLabel>
                    <TagCloseButton onClick={() => removeTool(tool)} />
                  </Tag>
                ))}
              </Box>
            </FormControl>

            <FormControl>
              <FormLabel>Expected Outputs</FormLabel>
              <HStack>
                <Select value={outputType} onChange={(e) => setOutputType(e.target.value)}>
                  <option value="memory">Memory</option>
                  <option value="reflection">Reflection</option>
                  <option value="checkpoint">Checkpoint</option>
                </Select>
                <Input
                  value={outputTag}
                  onChange={(e) => setOutputTag(e.target.value)}
                  placeholder="Tag name..."
                />
                <Checkbox
                  isChecked={outputRequired}
                  onChange={(e) => setOutputRequired(e.target.checked)}
                >
                  Required
                </Checkbox>
                <Button leftIcon={<AddIcon />} onClick={addExpectedOutput}>
                  Add
                </Button>
              </HStack>
              <Box mt={2}>
                {expectedOutputs.map((output, index) => (
                  <Tag
                    key={index}
                    size="md"
                    borderRadius="full"
                    variant="solid"
                    colorScheme={output.required ? 'red' : 'green'}
                    m={1}
                  >
                    <TagLabel>
                      {output.type}: {output.tag}
                    </TagLabel>
                    <TagCloseButton onClick={() => removeExpectedOutput(index)} />
                  </Tag>
                ))}
              </Box>
            </FormControl>

            <HStack>
              <FormControl>
                <FormLabel>Loop Enforcement</FormLabel>
                <Input
                  type="number"
                  value={loopEnforcement}
                  onChange={(e) => setLoopEnforcement(parseInt(e.target.value))}
                  min={1}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Options</FormLabel>
                <VStack align="start">
                  <Checkbox
                    isChecked={allowRetry}
                    onChange={(e) => setAllowRetry(e.target.checked)}
                  >
                    Allow Retry
                  </Checkbox>
                  <Checkbox
                    isChecked={escalateOnFailure}
                    onChange={(e) => setEscalateOnFailure(e.target.checked)}
                  >
                    Escalate on Failure
                  </Checkbox>
                </VStack>
              </FormControl>
            </HStack>

            <Button colorScheme="blue" onClick={createInstruction}>
              Create Instruction
            </Button>
          </VStack>
        </Box>

        <Divider />

        {/* Instruction Testing */}
        {createdInstruction && (
          <Box>
            <Heading size="md" mb={3}>
              Test Instruction
            </Heading>

            <InstructionPreviewCard
              instruction={createdInstruction}
              completedOutputs={completedOutputs}
            />

            <VStack mt={4} spacing={4} align="stretch">
              <Box>
                <Heading size="sm" mb={2}>
                  Complete Outputs
                </Heading>
                <VStack align="stretch">
                  {createdInstruction.expected_outputs.map((output, index) => (
                    <Button
                      key={index}
                      onClick={() => completeOutput(output.type, output.tag)}
                      isDisabled={completedOutputs.some(
                        (o) => o.type === output.type && o.tag === output.tag
                      )}
                      colorScheme="green"
                      size="sm"
                    >
                      Complete {output.type}: {output.tag}
                    </Button>
                  ))}
                </VStack>
              </Box>

              <Box>
                <Heading size="sm" mb={2}>
                  Simulate Tool Usage
                </Heading>
                <HStack>
                  <Input
                    value={usedTool}
                    onChange={(e) => setUsedTool(e.target.value)}
                    placeholder="Enter tool name..."
                  />
                  <Button onClick={simulateToolUsage} colorScheme="orange" size="sm">
                    Use Tool
                  </Button>
                </HStack>
              </Box>

              <Box>
                <Heading size="sm" mb={2}>
                  Loop Control
                </Heading>
                <HStack>
                  <Button onClick={incrementLoopCount} colorScheme="purple" size="sm">
                    Increment Loop Count (Current: {loopCount})
                  </Button>
                </HStack>
              </Box>

              <Button onClick={checkValidationStatus} colorScheme="blue">
                Check Validation Status
              </Button>
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default InstructionTester;
