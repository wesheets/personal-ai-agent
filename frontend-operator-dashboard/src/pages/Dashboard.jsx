import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  VStack,
  HStack,
  Divider,
  useColorMode,
  Spinner,
  Badge,
  Flex,
  Icon,
  useToast
} from '@chakra-ui/react';
import { FiRefreshCw, FiClock, FiAlertCircle } from 'react-icons/fi';
import DEBUG_MODE from '../config/debug';
import { getVisibleAgents } from '../utils/agentUtils';
import { safeFetch } from '../utils/safeFetch';

// Mock data for activity feed - will be replaced with API calls
const mockLogs = [
  {
    id: 1,
    timestamp: '2025-03-31T10:15:00Z',
    message: 'Builder agent completed task: Create React component',
    agent: 'builder'
  },
  {
    id: 2,
    timestamp: '2025-03-31T10:10:00Z',
    message: 'Memory agent stored new information',
    agent: 'memory'
  },
  {
    id: 3,
    timestamp: '2025-03-31T10:05:00Z',
    message: 'Research agent found 5 relevant articles',
    agent: 'research'
  },
  {
    id: 4,
    timestamp: '2025-03-31T10:00:00Z',
    message: 'Ops agent deployed new version',
    agent: 'ops'
  }
];

// Agent Card Component with dynamic metadata display
const AgentCard = ({ agent }) => {
  const { colorMode } = useColorMode();
  const navigate = (path) => {
    window.location.href = path;
  };

  // Get agent color based on type
  const getAgentColor = (type) => {
    switch (type) {
      case 'system':
        return 'blue';
      case 'persona':
        return 'purple';
      default:
        return 'gray';
    }
  };

  return (
    <Card
      direction="column"
      overflow="hidden"
      variant="outline"
      bg={colorMode === 'light' ? 'white' : 'gray.700'}
      boxShadow="md"
      borderRadius="lg"
      _hover={{
        transform: 'translateY(-4px)',
        boxShadow: 'lg',
        transition: 'all 0.3s ease'
      }}
      cursor="pointer"
      onClick={() => navigate(`/${agent?.id ?? ''}`)}
      height="100%"
    >
      <CardHeader pb={0}>
        <HStack>
          <Heading size="md" color={colorMode === 'light' ? 'brand.600' : 'brand.300'}>
            {agent?.icon && <span style={{ marginRight: '8px' }}>{agent.icon}</span>}
            {agent?.name ?? 'Agent'}
          </Heading>
          {agent?.type && <Badge colorScheme={getAgentColor(agent.type)}>{agent.type}</Badge>}
        </HStack>
      </CardHeader>
      <CardBody>
        <Text>{agent?.description ?? 'No description'}</Text>
        {agent?.tone && (
          <Badge mt={2} colorScheme="teal" variant="outline">
            {agent.tone}
          </Badge>
        )}
      </CardBody>
      <CardFooter pt={0}>
        <Button variant="ghost" colorScheme="blue" size="sm">
          Open Agent
        </Button>
      </CardFooter>
    </Card>
  );
};

// Activity Feed Component
const ActivityFeed = () => {
  const { colorMode } = useColorMode();
  const [logs, setLogs] = useState(mockLogs);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const toast = useToast();

  // Function to format timestamp
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (error) {
      return 'Unknown time';
    }
  };

  // Function to refresh logs
  const refreshLogs = () => {
    setLoading(true);

    // Simulate API call - will be replaced with actual API call
    setTimeout(() => {
      setLogs(mockLogs);
      setLastRefresh(new Date());
      setLoading(false);

      toast({
        title: 'Logs refreshed',
        status: 'success',
        duration: 2000,
        isClosable: true
      });
    }, 1000);
  };

  // Auto-refresh every 10 seconds
  useEffect(() => {
    let isMounted = true;

    // Only set up auto-refresh if not in debug mode
    if (!DEBUG_MODE) {
      const interval = setInterval(() => {
        if (isMounted) {
          refreshLogs();
        }
      }, 10000);

      return () => {
        isMounted = false;
        clearInterval(interval);
      };
    }

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <Box
      bg={colorMode === 'light' ? 'white' : 'gray.700'}
      p={4}
      borderRadius="lg"
      boxShadow="md"
      height="100%"
    >
      <HStack justifyContent="space-between" mb={4}>
        <Heading size="md">Recent Activity</Heading>
        <HStack>
          <Text fontSize="sm" color="gray.500">
            <Icon as={FiClock} mr={1} />
            Last updated: {lastRefresh.toLocaleTimeString()}
          </Text>
          <Button size="sm" leftIcon={<FiRefreshCw />} onClick={refreshLogs} isLoading={loading}>
            Refresh
          </Button>
        </HStack>
      </HStack>

      <Divider mb={4} />

      {logs?.length > 0 ? (
        <VStack spacing={3} align="stretch">
          {logs.map((log) => (
            <Box
              key={log?.id ?? Math.random()}
              p={3}
              borderRadius="md"
              bg={colorMode === 'light' ? 'gray.50' : 'gray.600'}
            >
              <HStack justifyContent="space-between" mb={1}>
                <Badge
                  colorScheme={
                    log?.agent === 'builder'
                      ? 'blue'
                      : log?.agent === 'ops'
                        ? 'green'
                        : log?.agent === 'research'
                          ? 'purple'
                          : log?.agent === 'memory'
                            ? 'orange'
                            : 'gray'
                  }
                >
                  {log?.agent ?? 'unknown'}
                </Badge>
                <Text fontSize="xs" color="gray.500">
                  {formatTime(log?.timestamp ?? '')}
                </Text>
              </HStack>
              <Text>{log?.message ?? 'No message'}</Text>
            </Box>
          ))}
        </VStack>
      ) : (
        <Flex direction="column" align="center" justify="center" py={10}>
          <Icon as={FiAlertCircle} boxSize={10} color="gray.400" mb={4} />
          <Text color="gray.500">No recent activity</Text>
        </Flex>
      )}
    </Box>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { colorMode } = useColorMode();
  const [agents, setAgents] = useState([]);
  const [systemData, setSystemData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemError, setSystemError] = useState(false);
  const toast = useToast();

  // Fetch system overview data
  useEffect(() => {
    let isMounted = true;

    const fetchSystemOverview = async () => {
      try {
        // Use the safeFetch utility with timeout and error handling
        await safeFetch(
          '/api/system/overview',
          (data) => {
            if (isMounted) {
              setSystemData(data);
              setSystemError(false);
            }
          },
          (hasError) => {
            if (isMounted && hasError) {
              setSystemError(true);
              toast({
                title: 'Error',
                description: 'Failed to load system overview. Using fallback data.',
                status: 'warning',
                duration: 5000,
                isClosable: true
              });
            }
          },
          8000
        ); // 8 second timeout
      } catch (err) {
        if (isMounted) {
          console.error('Error fetching system overview:', err);
        }
      }
    };

    fetchSystemOverview();

    return () => {
      isMounted = false;
    };
  }, [toast]);

  // Fetch agents from the API using the centralized utility
  useEffect(() => {
    let isMounted = true;

    const fetchAgents = async () => {
      try {
        setLoading(true);

        // Use the centralized getVisibleAgents utility instead of direct fetch
        const visibleAgents = await getVisibleAgents({ includeInactive: true });

        // Only update state if component is still mounted
        if (isMounted) {
          setAgents(visibleAgents);
          setError(null);
        }
      } catch (err) {
        // Only update state if component is still mounted
        if (isMounted) {
          setError('Failed to load agents. Please try again later.');
          toast({
            title: 'Error',
            description: 'Failed to load agents. Please try again later.',
            status: 'error',
            duration: 5000,
            isClosable: true
          });
        }
      } finally {
        // Only update state if component is still mounted
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Add a short delay to prevent immediate fetch on first render
    const timeout = setTimeout(() => {
      if (isMounted) {
        fetchAgents();
      }
    }, 1000);

    return () => {
      isMounted = false;
      clearTimeout(timeout);
    };
  }, [toast]);

  // Show loading state with timeout
  useEffect(() => {
    const loadingTimeout = setTimeout(() => {
      setLoading(false);
    }, 8000); // Force loading to end after 8 seconds

    return () => clearTimeout(loadingTimeout);
  }, []);

  if (loading && !agents.length) {
    return (
      <Flex justify="center" align="center" height="100%" p={10}>
        <VStack spacing={4}>
          <Spinner size="xl" color="brand.500" thickness="4px" />
          <Text>Loading dashboard data...</Text>
          <Button size="sm" onClick={() => window.location.reload()}>
            Refresh Page
          </Button>
        </VStack>
      </Flex>
    );
  }

  if (error && !agents.length) {
    return (
      <Box p={4}>
        <Heading mb={6} size="lg">
          Dashboard
        </Heading>
        <Box p={5} borderWidth="1px" borderRadius="lg" bg="red.50">
          <Heading size="md" color="red.500" mb={2}>
            Error
          </Heading>
          <Text>{error}</Text>
          <Button mt={4} colorScheme="red" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Heading mb={6} size="lg">
        Dashboard
      </Heading>

      {/* System Overview Section */}
      {systemData && !systemError && (
        <Box
          mb={6}
          p={4}
          borderWidth="1px"
          borderRadius="lg"
          bg={colorMode === 'light' ? 'blue.50' : 'blue.900'}
        >
          <Heading size="md" mb={3}>
            System Overview
          </Heading>
          <Grid
            templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }}
            gap={4}
          >
            <Box>
              <Text fontWeight="bold">Active Agents</Text>
              <Text>{systemData.agent_count || 'Unknown'}</Text>
            </Box>
            <Box>
              <Text fontWeight="bold">System Mode</Text>
              <Badge colorScheme={systemData.system_mode === 'production' ? 'green' : 'orange'}>
                {systemData.system_mode || 'Unknown'}
              </Badge>
            </Box>
            <Box>
              <Text fontWeight="bold">Status</Text>
              <Badge colorScheme={systemData.status === 'healthy' ? 'green' : 'red'}>
                {systemData.status || 'Unknown'}
              </Badge>
            </Box>
            <Box>
              <Text fontWeight="bold">Uptime</Text>
              <Text>{systemData.uptime || 'Unknown'}</Text>
            </Box>
          </Grid>
        </Box>
      )}

      {systemError && (
        <Box
          mb={6}
          p={4}
          borderWidth="1px"
          borderRadius="lg"
          bg={colorMode === 'light' ? 'red.50' : 'red.900'}
        >
          <Heading size="md" mb={3}>
            System Overview
          </Heading>
          <Text>Unable to load system data. Please try again later.</Text>
          <Button mt={3} size="sm" onClick={() => window.location.reload()}>
            Refresh
          </Button>
        </Box>
      )}

      <Grid
        templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }}
        gap={6}
        mb={8}
      >
        {agents?.length > 0 ? (
          agents.map((agent) => <AgentCard key={agent?.id ?? Math.random()} agent={agent} />)
        ) : (
          <Text>No agents available</Text>
        )}
      </Grid>

      <Box mt={8}>
        <ActivityFeed />
      </Box>
    </Box>
  );
};

export default Dashboard;
