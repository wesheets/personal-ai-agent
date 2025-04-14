import React from 'react';
import { Box, Heading, VStack, HStack, Text, Badge, Divider } from '@chakra-ui/react';
import { Instruction } from '../../backend/instruction_engine';

interface InstructionPreviewCardProps {
  instruction: Instruction;
  completedOutputs?: Array<{ type: string; tag: string }>;
}

/**
 * Component for displaying instruction details in a card format
 */
const InstructionPreviewCard: React.FC<InstructionPreviewCardProps> = ({ 
  instruction,
  completedOutputs = []
}) => {
  return (
    <Box 
      p={4} 
      borderWidth="1px" 
      borderRadius="lg" 
      boxShadow="sm"
      bg="white"
    >
      <VStack align="stretch" spacing={3}>
        <HStack justifyContent="space-between">
          <Heading size="md">{instruction.task_summary}</Heading>
          <Badge 
            colorScheme={
              instruction.status === 'complete' ? 'green' : 
              instruction.status === 'failed' ? 'red' : 
              instruction.status === 'in_progress' ? 'blue' : 'gray'
            }
            fontSize="sm"
            px={2}
            py={1}
            borderRadius="md"
          >
            {instruction.status}
          </Badge>
        </HStack>
        
        <Divider />
        
        <Box>
          <Text fontWeight="semibold" fontSize="sm" mb={1}>Instruction ID:</Text>
          <Text fontSize="xs" fontFamily="monospace">{instruction.instruction_id}</Text>
        </Box>
        
        <HStack>
          <Box flex="1">
            <Text fontWeight="semibold" fontSize="sm" mb={1}>Goal ID:</Text>
            <Text fontSize="xs" fontFamily="monospace">{instruction.goal_id}</Text>
          </Box>
          
          {instruction.thread_id && (
            <Box flex="1">
              <Text fontWeight="semibold" fontSize="sm" mb={1}>Thread ID:</Text>
              <Text fontSize="xs" fontFamily="monospace">{instruction.thread_id}</Text>
            </Box>
          )}
        </HStack>
        
        <Box>
          <Text fontWeight="semibold" fontSize="sm" mb={1}>Agent:</Text>
          <Text fontSize="sm">{instruction.agent_id}</Text>
        </Box>
        
        <Box>
          <Text fontWeight="semibold" fontSize="sm" mb={1}>Tools Required:</Text>
          <HStack flexWrap="wrap" mt={1}>
            {instruction.tools_required.map((tool, i) => (
              <Badge key={i} colorScheme="blue" m={1}>{tool}</Badge>
            ))}
          </HStack>
        </Box>
        
        <Box>
          <Text fontWeight="semibold" fontSize="sm" mb={1}>Expected Outputs:</Text>
          <VStack align="stretch" mt={1} spacing={1}>
            {instruction.expected_outputs.map((output, i) => {
              const isCompleted = completedOutputs.some(
                o => o.type === output.type && o.tag === output.tag
              );
              
              return (
                <HStack key={i} spacing={2}>
                  <Badge 
                    colorScheme={output.required ? "red" : "gray"}
                    variant="outline"
                  >
                    {output.required ? "required" : "optional"}
                  </Badge>
                  <Text fontSize="sm">{output.type}: {output.tag}</Text>
                  {isCompleted && (
                    <Badge colorScheme="green">completed</Badge>
                  )}
                </HStack>
              );
            })}
          </VStack>
        </Box>
        
        <HStack>
          <Box>
            <Text fontWeight="semibold" fontSize="sm" mb={1}>Loop Enforcement:</Text>
            <Text fontSize="sm">{instruction.loop_enforcement}</Text>
          </Box>
          
          <Box>
            <Text fontWeight="semibold" fontSize="sm" mb={1}>Allow Retry:</Text>
            <Text fontSize="sm">{instruction.allow_retry ? 'Yes' : 'No'}</Text>
          </Box>
          
          <Box>
            <Text fontWeight="semibold" fontSize="sm" mb={1}>Escalate on Failure:</Text>
            <Text fontSize="sm">{instruction.escalate_on_failure ? 'Yes' : 'No'}</Text>
          </Box>
        </HStack>
        
        <Box>
          <Text fontWeight="semibold" fontSize="sm" mb={1}>Last Updated:</Text>
          <Text fontSize="sm">{instruction.last_updated.toLocaleString()}</Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default InstructionPreviewCard;
