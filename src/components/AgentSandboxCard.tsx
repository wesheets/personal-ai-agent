import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Avatar,
  useColorModeValue,
  Divider,
  Flex
} from '@chakra-ui/react';

interface AgentSandboxCardProps {
  agentId: string;
  status: 'idle' | 'active' | 'thinking' | 'executing' | 'paused' | 'reflecting';
  lastMemory: string;
  activeTool: string;
  toolkit: string[];
  reflection: string;
  isVisible?: boolean;
}

const AgentSandboxCard: React.FC<AgentSandboxCardProps> = ({
  agentId,
  status,
  lastMemory,
  activeTool,
  toolkit,
  reflection,
  isVisible = true
}) => {
  // Get agent color based on name
  const getAgentColor = (id: string) => {
    if (!id) return 'gray';

    switch (id.toLowerCase()) {
      case 'hal':
        return 'blue';
      case 'ash':
        return 'teal';
      case 'nova':
        return 'orange';
      case 'orchestrator':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const agentColor = getAgentColor(agentId);
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'gray';
      case 'active':
        return 'green';
      case 'thinking':
        return 'blue';
      case 'executing':
        return 'orange';
      case 'paused':
        return 'yellow';
      case 'reflecting':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const statusColor = getStatusColor(status);

  // Animation style for thinking state
  const pulseStyle =
    status === 'thinking'
      ? {
          opacity: 0.8,
          transition: 'opacity 1.5s ease-in-out',
          animation: 'pulse 2s infinite'
        }
      : {};

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      p={4}
      mb={4}
      borderLeftWidth="3px"
      borderLeftColor={`${agentColor}.500`}
      display={isVisible ? 'block' : 'none'}
      transition="all 0.3s ease"
      width="100%"
      sx={pulseStyle}
    >
      <HStack mb={3} spacing={3}>
        <Avatar size="sm" name={agentId} bg={`${agentColor}.500`} color="white" />
        <Box>
          <HStack>
            <Text fontWeight="bold">{agentId}</Text>
            {agentId.toLowerCase() === 'orchestrator' && (
              <Badge colorScheme="purple" variant="subtle">
                System
              </Badge>
            )}
          </HStack>
          <Badge colorScheme={statusColor}>{status}</Badge>
        </Box>
      </HStack>

      <Divider mb={3} />

      <VStack align="stretch" spacing={3}>
        <Box>
          <Text fontSize="xs" fontWeight="medium" color={useColorModeValue('gray.500', 'gray.400')}>
            LAST MEMORY
          </Text>
          <Text fontSize="sm" fontStyle="italic">
            {lastMemory}
          </Text>
        </Box>

        <Box>
          <Text fontSize="xs" fontWeight="medium" color={useColorModeValue('gray.500', 'gray.400')}>
            ACTIVE TOOL
          </Text>
          <Text fontSize="sm">{activeTool || 'None'}</Text>
        </Box>

        <Box>
          <Text fontSize="xs" fontWeight="medium" color={useColorModeValue('gray.500', 'gray.400')}>
            TOOLKIT
          </Text>
          <Flex flexWrap="wrap" gap={1} mt={1}>
            {toolkit.map((tool, index) => (
              <Badge key={index} colorScheme={agentColor} variant="subtle">
                {tool}
              </Badge>
            ))}
          </Flex>
        </Box>

        <Box>
          <Text fontSize="xs" fontWeight="medium" color={useColorModeValue('gray.500', 'gray.400')}>
            {agentId.toLowerCase() === 'orchestrator' ? 'THINKING STATE' : 'CURRENT REFLECTION'}
          </Text>
          <Text fontSize="sm">{reflection}</Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default AgentSandboxCard;
