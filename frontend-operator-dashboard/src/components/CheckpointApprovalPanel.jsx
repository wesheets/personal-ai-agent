import React from 'react';
import {
  Box,
  Flex,
  Text,
  Badge,
  useColorModeValue,
  VStack,
  HStack,
  Button,
  Textarea,
  IconButton,
  Divider
} from '@chakra-ui/react';
import { FiCheck, FiX, FiMessageSquare } from 'react-icons/fi';

const CheckpointApprovalPanel = () => {
  // Mock data for checkpoints - would be replaced with actual data from API
  const checkpoints = [
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
  ];
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hardBgColor = useColorModeValue('red.50', 'red.900');
  const hardBorderColor = useColorModeValue('red.200', 'red.700');
  const softBgColor = useColorModeValue('yellow.50', 'yellow.900');
  const softBorderColor = useColorModeValue('yellow.200', 'yellow.700');
  
  // Format timestamp
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Handle checkpoint approval
  const handleApprove = (checkpointId) => {
    console.log(`Approved checkpoint: ${checkpointId}`);
    // In a real implementation, this would call an API
  };
  
  // Handle checkpoint rejection
  const handleReject = (checkpointId) => {
    console.log(`Rejected checkpoint: ${checkpointId}`);
    // In a real implementation, this would call an API
  };
  
  // Handle comment submission
  const handleSubmitComment = (checkpointId, comment) => {
    console.log(`Comment submitted for checkpoint ${checkpointId}: ${comment}`);
    // In a real implementation, this would call an API
  };

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
      mb={4}
    >
      {checkpoints.length === 0 ? (
        <Box p={4} textAlign="center">
          <Text color="gray.500">No pending checkpoints</Text>
        </Box>
      ) : (
        <VStack spacing={0} align="stretch" divider={<Divider />}>
          {checkpoints.map((checkpoint) => (
            <Box 
              key={checkpoint.id} 
              p={4}
              borderLeftWidth="4px"
              borderLeftColor={checkpoint.type === 'hard' ? 'red.500' : 'yellow.500'}
              bg={checkpoint.type === 'hard' ? hardBgColor : softBgColor}
            >
              <HStack mb={2} justify="space-between">
                <Badge colorScheme={checkpoint.type === 'hard' ? 'red' : 'yellow'}>
                  {checkpoint.type.toUpperCase()}
                </Badge>
                <Text fontSize="xs" color="gray.500">
                  {formatTime(checkpoint.timestamp)}
                </Text>
              </HStack>
              
              <Text fontWeight="bold" mb={1}>{checkpoint.tag}</Text>
              <Text mb={2}>{checkpoint.description}</Text>
              
              <HStack mb={2} fontSize="sm">
                <Badge colorScheme="blue">{checkpoint.agentId}</Badge>
                <Text>•</Text>
                <Badge colorScheme="purple">{checkpoint.goalId}</Badge>
              </HStack>
              
              {checkpoint.toolOutput && (
                <Box 
                  p={2} 
                  bg={useColorModeValue('blackAlpha.50', 'blackAlpha.300')} 
                  borderRadius="md"
                  mb={3}
                  fontSize="sm"
                  fontFamily="monospace"
                >
                  {checkpoint.toolOutput}
                </Box>
              )}
              
              <Flex mt={3} flexDir={{ base: 'column', sm: 'row' }} gap={2}>
                <Button 
                  size="sm" 
                  colorScheme="green" 
                  leftIcon={<FiCheck />}
                  onClick={() => handleApprove(checkpoint.id)}
                >
                  Approve
                </Button>
                <Button 
                  size="sm" 
                  colorScheme="red" 
                  leftIcon={<FiX />}
                  onClick={() => handleReject(checkpoint.id)}
                >
                  Reject
                </Button>
                
                <Flex flex="1" ml={{ base: 0, sm: 2 }} mt={{ base: 2, sm: 0 }}>
                  <Textarea 
                    size="sm"
                    placeholder="Add comment..."
                    resize="none"
                    rows={1}
                  />
                  <IconButton
                    aria-label="Send comment"
                    icon={<FiMessageSquare />}
                    size="sm"
                    ml={1}
                    onClick={() => handleSubmitComment(checkpoint.id, "Sample comment")}
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
