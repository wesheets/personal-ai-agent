import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Text,
  Flex,
  Spinner,
  Badge,
  useColorModeValue,
  Heading,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Grid,
} from '@chakra-ui/react';
import { controlService } from '../services/api';

const StatusFeedback = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        const data = await controlService.getAgentStatus();
        setAgents(data);
      } catch (err) {
        setError('Failed to fetch agent status');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgentStatus();
    const interval = setInterval(fetchAgentStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'running':
      case 'in_progress':
        return 'blue';
      case 'idle':
      case 'waiting':
      case 'pending':
        return 'yellow';
      case 'error':
      case 'failed':
        return 'red';
      case 'completed':
      case 'success':
        return 'green';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading agent status...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
        <Text fontSize="lg">{error}</Text>
      </Box>
    );
  }

  if (agents.length === 0) {
    return (
      <Box
        textAlign="center"
        py={10}
        borderWidth="1px"
        borderRadius="md"
        borderStyle="dashed"
        borderColor={borderColor}
      >
        <Text color="gray.500">No active agents found</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={4} align="stretch">
      {agents.map((agent) => (
        <Box
          key={agent.id}
          borderWidth="1px"
          borderRadius="lg"
          overflow="hidden"
          bg={bgColor}
          borderColor={borderColor}
        >
          <Flex
            p={4}
            alignItems="center"
            bg={`${getStatusColor(agent.status)}.50`}
            _dark={{ bg: `${getStatusColor(agent.status)}.900` }}
            borderBottomWidth="1px"
          >
            <Badge
              colorScheme={getStatusColor(agent.status)}
              fontSize="0.8em"
              p={1}
              borderRadius="full"
              mr={3}
            >
              {agent.status}
            </Badge>

            <Heading size="md" flex="1">{agent.name}</Heading>

            <Badge colorScheme="purple" fontSize="0.8em">
              {agent.type}
            </Badge>
          </Flex>

          <Box p={4}>
            {agent.current_task && (
              <Box mb={3}>
                <Text fontWeight="bold" fontSize="sm" color="gray.500">
                  Current Task:
                </Text>
                <Text>{agent.current_task.title}</Text>
              </Box>
            )}

            {agent.completion_state && (
              <Box mb={3}>
                <Text fontWeight="bold" fontSize="sm" color="gray.500">
                  Completion:
                </Text>
                <Text>{agent.completion_state}</Text>
              </Box>
            )}

            <Accordion allowToggle mt={3}>
              {agent.errors?.length > 0 && (
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box flex="1" textAlign="left">
                        <Flex alignItems="center">
                          <Badge colorScheme="red" mr={2}>
                            {agent.errors.length}
                          </Badge>
                          Error Details
                        </Flex>
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack spacing={2} align="stretch">
                      {agent.errors.map((error, idx) => (
                        <Box
                          key={idx}
                          p={2}
                          borderWidth="1px"
                          borderRadius="md"
                          borderColor="red.200"
                          bg="red.50"
                          _dark={{ bg: "red.900", borderColor: "red.700" }}
                        >
                          <Text fontSize="xs" color="gray.500">
                            {new Date(error.timestamp).toLocaleString()}
                          </Text>
                          <Text>{error.message}</Text>
                        </Box>
                      ))}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              )}

              {agent.metrics && (
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box flex="1" textAlign="left">
                        Performance Metrics
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Stat>
                        <StatLabel>Tasks Completed</StatLabel>
                        <StatNumber>{agent.metrics.tasks_completed || 0}</StatNumber>
                      </Stat>

                      <Stat>
                        <StatLabel>Avg. Response Time</StatLabel>
                        <StatNumber>{agent.metrics.avg_response_time || 'N/A'}</StatNumber>
                        <StatHelpText>seconds</StatHelpText>
                      </Stat>

                      <Stat>
                        <StatLabel>Success Rate</StatLabel>
                        <StatNumber>{agent.metrics.success_rate || 'N/A'}</StatNumber>
                        <StatHelpText>percent</StatHelpText>
                      </Stat>
                    </Grid>
                  </AccordionPanel>
                </AccordionItem>
              )}
            </Accordion>
          </Box>
        </Box>
      ))}
    </VStack>
  );
};

export default StatusFeedback;
