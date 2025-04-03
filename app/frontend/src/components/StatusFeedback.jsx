<<<<<<< HEAD
import React, { useState, useEffect } from 'react';
import { controlService } from '../services/api';

// Component for displaying live status feedback for active agents
=======
import React, { useState, useEffect, useRef } from 'react';
import isEqual from 'lodash.isequal';
import {
  Box,
  VStack,
  Text,
  Flex,
  Spinner,
  Badge,
  Divider,
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
  GridItem
} from '@chakra-ui/react';
import { controlService } from '../services/api';

>>>>>>> manus-ui-restore
const StatusFeedback = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
<<<<<<< HEAD

  useEffect(() => {
    // Function to fetch agent status data
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        
        // Fetch active agents and their status
        const response = await controlService.getAgentStatus();
        setAgents(response.agents || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch agent status data');
        setLoading(false);
        console.error('Error fetching agent status:', err);
      }
    };

    // Initial fetch
    fetchAgentStatus();
    
    // Set up polling for real-time updates (every 2 seconds)
    const intervalId = setInterval(fetchAgentStatus, 2000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'running':
      case 'in_progress':
        return 'status-active';
      case 'idle':
      case 'waiting':
      case 'pending':
        return 'status-paused';
      case 'error':
      case 'failed':
        return 'status-error';
      case 'completed':
      case 'success':
        return 'status-completed';
      default:
        return '';
=======
  const lastAgentStateRef = useRef(null);
  const renderCountRef = useRef(0);

  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    // Track render count (for development only)
    renderCountRef.current += 1;
    if (process.env.NODE_ENV === "development") {
      console.log(`StatusFeedback render count: ${renderCountRef.current}`);
    }
  });

  useEffect(() => {
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        const fetchedAgentStatus = await controlService.getAgentStatus();

        if (!isEqual(fetchedAgentStatus, lastAgentStateRef.current)) {
          if (process.env.NODE_ENV === "development") {
            console.log('Agent status changed, updating state');
          }
          lastAgentStateRef.current = JSON.parse(JSON.stringify(fetchedAgentStatus));
          setAgents(fetchedAgentStatus);
        } else if (process.env.NODE_ENV === "development") {
          console.log('Agent status unchanged, skipping update');
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch agent status');
        setLoading(false);
        if (process.env.NODE_ENV === 'development') {
          console.error('Error fetching agent status:', err);
        }
      }
    };

    fetchAgentStatus();
    const intervalId = setInterval(fetchAgentStatus, 3000);
    return () => clearInterval(intervalId);
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
>>>>>>> manus-ui-restore
    }
  };

  if (loading) {
<<<<<<< HEAD
    return <div className="loading">Loading agent status...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="status-feedback">
      {agents.length > 0 ? (
        <div className="agent-status-list">
          {agents.map((agent) => (
            <div key={agent.id} className="agent-status-item">
              <div className="agent-header">
                <h4>
                  <span className={`status-indicator ${getStatusColor(agent.status)}`}></span>
                  {agent.name}
                </h4>
                <span className="agent-type">{agent.type}</span>
              </div>
              
              <div className="agent-details">
                <div className="status-row">
                  <span className="status-label">Status:</span>
                  <span className={`status-value ${getStatusColor(agent.status)}`}>{agent.status}</span>
                </div>
                
                {agent.current_task && (
                  <div className="status-row">
                    <span className="status-label">Current Task:</span>
                    <span className="status-value">{agent.current_task.title}</span>
                  </div>
                )}
                
                {agent.completion_state && (
                  <div className="status-row">
                    <span className="status-label">Completion:</span>
                    <span className="status-value">{agent.completion_state}</span>
                  </div>
                )}
                
                {agent.errors && agent.errors.length > 0 && (
                  <div className="status-row">
                    <span className="status-label">Errors:</span>
                    <span className="status-value error-count">{agent.errors.length}</span>
                  </div>
                )}
                
                {agent.retry_count > 0 && (
                  <div className="status-row">
                    <span className="status-label">Retries:</span>
                    <span className="status-value">{agent.retry_count}</span>
                  </div>
                )}
              </div>
              
              {/* Error details (expandable) */}
              {agent.errors && agent.errors.length > 0 && (
                <div className="error-details">
                  <details>
                    <summary>Error Details</summary>
                    <ul className="error-list">
                      {agent.errors.map((error, index) => (
                        <li key={index} className="error-item">
                          <span className="error-time">{new Date(error.timestamp).toLocaleString()}</span>
                          <span className="error-message">{error.message}</span>
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
              
              {/* Performance metrics */}
              {agent.metrics && (
                <div className="agent-metrics">
                  <details>
                    <summary>Performance Metrics</summary>
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <span className="metric-label">Tasks Completed:</span>
                        <span className="metric-value">{agent.metrics.tasks_completed || 0}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Avg. Response Time:</span>
                        <span className="metric-value">{agent.metrics.avg_response_time || 'N/A'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Success Rate:</span>
                        <span className="metric-value">{agent.metrics.success_rate || 'N/A'}</span>
                      </div>
                    </div>
                  </details>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">No active agents found</div>
      )}
    </div>
=======
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} minH="inherit">
          <Spinner size="xl" />
          <Text mt={4}>Loading agent status...</Text>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} color="red.500" minH="inherit">
          <Text fontSize="lg">{error}</Text>
        </Box>
      </Box>
    );
  }

  return (
    <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
      {agents.length > 0 ? (
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

                <Heading size="md" flex="1">
                  {agent.name}
                </Heading>

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
                  {agent.errors && agent.errors.length > 0 && (
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
                          {agent.errors.map((error, index) => (
                            <Box
                              key={index}
                              p={2}
                              borderWidth="1px"
                              borderRadius="md"
                              borderColor="red.200"
                              bg="red.50"
                              _dark={{ bg: 'red.900', borderColor: 'red.700' }}
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
      ) : (
        <Box
          textAlign="center"
          py={10}
          borderWidth="1px"
          borderRadius="md"
          borderStyle="dashed"
          borderColor={borderColor}
          minH="inherit"
        >
          <Text color="gray.500">No active agents found</Text>
        </Box>
      )}
    </Box>
>>>>>>> manus-ui-restore
  );
};

export default StatusFeedback;
