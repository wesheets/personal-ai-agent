import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  Badge,
  useColorModeValue,
  HStack,
  VStack,
  Divider,
  Textarea,
  IconButton
} from '@chakra-ui/react';
import { FiCheck, FiX, FiMessageSquare } from 'react-icons/fi';

interface CheckpointApprovalPanelProps {
  // Props can be extended as needed
}

interface Checkpoint {
  id: string;
  agentId: string;
  goalId: string;
  tag: string;
  description: string;
  type: 'hard' | 'soft';
  timestamp: Date;
  memoryId?: string;
  toolOutput?: string;
}

const CheckpointApprovalPanel: React.FC<CheckpointApprovalPanelProps> = () => {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([
    {
      id: 'cp1',
      agentId: 'hal',
      goalId: 'goal-123',
      tag: 'api-schema-validation',
      description: 'Verify the API schema matches the requirements document',
      type: 'hard',
      timestamp: new Date(),
      memoryId: 'mem-456',
      toolOutput: 'Schema validation complete. 3 endpoints verified.'
    },
    {
      id: 'cp2',
      agentId: 'nova',
      goalId: 'goal-456',
      tag: 'content-review',
      description: 'Review generated blog post for technical accuracy',
      type: 'soft',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      toolOutput: 'Content generated with 95% confidence score.'
    }
  ]);
  
  const [comments, setComments] = useState<Record<string, string>>({});
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Handle checkpoint approval
  const handleApprove = (checkpointId: string) => {
    // In a real implementation, this would call an API
    setCheckpoints(checkpoints.filter(cp => cp.id !== checkpointId));
    // Could add a toast notification here
  };
  
  // Handle checkpoint rejection
  const handleReject = (checkpointId: string) => {
    // In a real implementation, this would call an API
    setCheckpoints(checkpoints.filter(cp => cp.id !== checkpointId));
    // Could add a toast notification here
  };
  
  // Handle comment change
  const handleCommentChange = (checkpointId: string, comment: string) => {
    setComments({
      ...comments,
      [checkpointId]: comment
    });
  };
  
  // Handle comment submission
  const handleSubmitComment = (checkpointId: string) => {
    // In a real implementation, this would call an API
    console.log(`Comment submitted for checkpoint ${checkpointId}: ${comments[checkpointId]}`);
    // Clear the comment field
    setComments({
      ...comments,
      [checkpointId]: ''
    });
    // Could add a toast notification here
  };
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
    >
      <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Checkpoint Approval</Heading>
          <Badge colorScheme="red">{checkpoints.length} Pending</Badge>
        </Flex>
      </Box>
      
      {checkpoints.length === 0 ? (
        <Box p={4} textAlign="center">
          <Text color="gray.500">No pending checkpoints</Text>
        </Box>
      ) : (
        <VStack spacing={0} align="stretch" divider={<Divider />}>
          {checkpoints.map((checkpoint) => (
            <Box key={checkpoint.id} p={4}>
              <HStack mb={2}>
                <Badge colorScheme={checkpoint.type === 'hard' ? 'red' : 'yellow'}>
                  {checkpoint.type.toUpperCase()}
                </Badge>
                <Text fontWeight="bold" fontSize="sm">{checkpoint.tag}</Text>
                <Text fontSize="xs" color="gray.500" ml="auto">
                  {formatTime(checkpoint.timestamp)}
                </Text>
              </HStack>
              
              <Text mb={2}>{checkpoint.description}</Text>
              
              <HStack mb={2} fontSize="sm">
                <Badge colorScheme="blue">{checkpoint.agentId}</Badge>
                <Text>•</Text>
                <Badge colorScheme="purple">{checkpoint.goalId}</Badge>
              </HStack>
              
              {checkpoint.toolOutput && (
                <Box 
                  p={2} 
                  bg={useColorModeValue('gray.50', 'gray.700')} 
                  borderRadius="md"
                  mb={3}
                  fontSize="sm"
                >
                  {checkpoint.toolOutput}
                </Box>
              )}
              
              <Flex mt={3}>
                <Button 
                  size="sm" 
                  colorScheme="green" 
                  leftIcon={<FiCheck />}
                  mr={2}
                  onClick={() => handleApprove(checkpoint.id)}
                >
                  Approve
                </Button>
                <Button 
                  size="sm" 
                  colorScheme="red" 
                  leftIcon={<FiX />}
                  mr={2}
                  onClick={() => handleReject(checkpoint.id)}
                >
                  Reject
                </Button>
                
                <Flex flex="1" ml={2}>
                  <Textarea 
                    size="sm"
                    placeholder="Add comment..."
                    value={comments[checkpoint.id] || ''}
                    onChange={(e) => handleCommentChange(checkpoint.id, e.target.value)}
                    resize="none"
                    rows={1}
                  />
                  <IconButton
                    aria-label="Send comment"
                    icon={<FiMessageSquare />}
                    size="sm"
                    ml={1}
                    onClick={() => handleSubmitComment(checkpoint.id)}
                    isDisabled={!comments[checkpoint.id]}
                  />
                </Flex>
              </Flex>
            </Box>
          ))}
        </VStack>
      )}
    </Box>
  );
};

export default CheckpointApprovalPanel;
