import React from 'react';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { Instruction } from '../../backend/instruction_engine';

interface AgentSandboxCardProps {
  agentId: string;
  agentName: string;
  status: 'idle' | 'thinking' | 'executing' | 'error';
  activeInstruction?: Instruction;
  lastMemory?: string;
  activeTool?: string;
  toolkit?: string[];
  currentReflection?: string;
}

/**
 * Component for displaying agent sandbox information
 * Includes active instruction panel for Phase 10.0
 */
const AgentSandboxCard: React.FC<AgentSandboxCardProps> = ({
  agentId,
  agentName,
  status,
  activeInstruction,
  lastMemory,
  activeTool,
  toolkit = [],
  currentReflection
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Status color mapping
  const statusColorScheme = {
    idle: 'gray',
    thinking: 'blue',
    executing: 'green',
    error: 'red'
  };

  return (
    <Box
      p={4}
      borderWidth="1px"
      borderRadius="lg"
      boxShadow="sm"
      bg={bgColor}
      borderColor={borderColor}
      width="100%"
    >
      <VStack align="stretch" spacing={4}>
        <HStack justifyContent="space-between">
          <Heading size="md">{agentName}</Heading>
          <Badge
            colorScheme={statusColorScheme[status]}
            fontSize="sm"
            px={2}
            py={1}
            borderRadius="md"
          >
            {status}
          </Badge>
        </HStack>

        <Text fontSize="xs" color="gray.500">
          Agent ID: {agentId}
        </Text>

        <Divider />

        {/* Active Instruction Panel - Phase 10.0 */}
        {activeInstruction && (
          <Box>
            <Heading size="sm" mb={2}>
              Active Instruction
            </Heading>
            <Box
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={useColorModeValue('gray.50', 'gray.700')}
            >
              <VStack align="stretch" spacing={2}>
                <Text fontWeight="bold">{activeInstruction.task_summary}</Text>

                <HStack>
                  <Badge
                    colorScheme={
                      activeInstruction.status === 'complete'
                        ? 'green'
                        : activeInstruction.status === 'failed'
                          ? 'red'
                          : activeInstruction.status === 'in_progress'
                            ? 'blue'
                            : 'gray'
                    }
                  >
                    {activeInstruction.status}
                  </Badge>

                  <Text fontSize="xs" color="gray.500">
                    ID: {activeInstruction.instruction_id.substring(0, 8)}...
                  </Text>
                </HStack>

                <Box>
                  <Text fontSize="xs" fontWeight="semibold">
                    Required Outputs:
                  </Text>
                  <HStack flexWrap="wrap" mt={1}>
                    {activeInstruction.expected_outputs
                      .filter((output: any) => output.required)
                      .map((output: any, i: number) => (
                        <Badge key={i} colorScheme="red" size="sm">
                          {output.type}: {output.tag}
                        </Badge>
                      ))}
                  </HStack>
                </Box>
              </VStack>
            </Box>
          </Box>
        )}

        {/* Last Memory */}
        {lastMemory && (
          <Box>
            <Heading size="sm" mb={2}>
              Last Memory
            </Heading>
            <Box
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={useColorModeValue('gray.50', 'gray.700')}
            >
              <Text fontSize="sm" noOfLines={3}>
                {lastMemory}
              </Text>
            </Box>
          </Box>
        )}

        {/* Active Tool */}
        {activeTool && (
          <Box>
            <Heading size="sm" mb={2}>
              Active Tool
            </Heading>
            <Badge colorScheme="purple" fontSize="md" px={2} py={1}>
              {activeTool}
            </Badge>
          </Box>
        )}

        {/* Toolkit */}
        {toolkit.length > 0 && (
          <Box>
            <Heading size="sm" mb={2}>
              Toolkit
            </Heading>
            <HStack flexWrap="wrap">
              {toolkit.map((tool, i) => (
                <Badge key={i} colorScheme="blue" m={1}>
                  {tool}
                </Badge>
              ))}
            </HStack>
          </Box>
        )}

        {/* Current Reflection */}
        {currentReflection && (
          <Box>
            <Heading size="sm" mb={2}>
              Current Reflection
            </Heading>
            <Box
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={useColorModeValue('gray.50', 'gray.700')}
            >
              <Text fontSize="sm" fontStyle="italic" noOfLines={4}>
                {currentReflection}
              </Text>
            </Box>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default AgentSandboxCard;
