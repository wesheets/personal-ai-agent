import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  useColorModeValue,
  Button,
  Icon
} from '@chakra-ui/react';
import { FiCheck, FiX, FiMessageSquare } from 'react-icons/fi';

interface CheckpointApprovalPanelProps {
  checkpoints: Array<{
    id: string;
    title: string;
    description: string;
    type: 'hard' | 'soft';
    status: 'pending' | 'approved' | 'rejected';
    timestamp: Date;
  }>;
  onApprove: (checkpointId: string) => void;
  onReject: (checkpointId: string) => void;
  onComment: (checkpointId: string) => void;
}

const CheckpointApprovalPanel: React.FC<CheckpointApprovalPanelProps> = ({
  checkpoints,
  onApprove,
  onReject,
  onComment
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Active checkpoints (pending approval)
  const activeCheckpoints = checkpoints.filter((cp) => cp.status === 'pending');

  return (
    <Box borderWidth="1px" borderRadius="lg" borderColor={borderColor} bg={bgColor} p={4} mb={4}>
      <Text fontWeight="bold" mb={3}>
        Checkpoint Approval
      </Text>

      {activeCheckpoints.length === 0 ? (
        <Text fontSize="sm" color={useColorModeValue('gray.500', 'gray.400')}>
          No active checkpoints requiring approval
        </Text>
      ) : (
        <VStack align="stretch" spacing={3}>
          {activeCheckpoints.map((checkpoint) => (
            <Box
              key={checkpoint.id}
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              borderLeftWidth="3px"
              borderLeftColor={checkpoint.type === 'hard' ? 'red.500' : 'yellow.500'}
            >
              <HStack mb={1} justify="space-between">
                <HStack>
                  <Text fontWeight="medium">{checkpoint.title}</Text>
                  <Badge colorScheme={checkpoint.type === 'hard' ? 'red' : 'yellow'}>
                    {checkpoint.type === 'hard' ? 'Required' : 'Optional'}
                  </Badge>
                </HStack>
                <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
                  {formatTime(checkpoint.timestamp)}
                </Text>
              </HStack>

              <Text fontSize="sm" mb={3}>
                {checkpoint.description}
              </Text>

              <HStack spacing={2} justify="flex-end">
                <Button
                  size="sm"
                  leftIcon={<Icon as={FiMessageSquare} />}
                  variant="ghost"
                  onClick={() => onComment(checkpoint.id)}
                >
                  Comment
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={FiX} />}
                  colorScheme="red"
                  variant="outline"
                  onClick={() => onReject(checkpoint.id)}
                >
                  Reject
                </Button>
                <Button
                  size="sm"
                  leftIcon={<Icon as={FiCheck} />}
                  colorScheme="green"
                  onClick={() => onApprove(checkpoint.id)}
                >
                  Approve
                </Button>
              </HStack>
            </Box>
          ))}
        </VStack>
      )}
    </Box>
  );
};

export default CheckpointApprovalPanel;
