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

// Mock data for initial development - will be replaced with API calls
const mockAgents = [
  {
    id: 'builder',
    config: {
      name: 'Builder Agent',
      description: 'Creates and manages development projects'
    }
  },
  {
    id: 'ops',
    config: {
      name: 'Ops Agent',
      description: 'Handles operations and infrastructure tasks'
    }
  },
  {
    id: 'research',
    config: {
      name: 'Research Agent',
      description: 'Conducts research and gathers information'
    }
  },
  {
    id: 'memory',
    config: {
      name: 'Memory Agent',
      description: 'Manages knowledge and information storage'
    }
  }
];

const mockLogs = [
  { id: 1, timestamp: '2025-03-31T10:15:00Z', message: 'Builder agent completed task: Create React component', agent: 'builder' },
  { id: 2, timestamp: '2025-03-31T10:10:00Z', message: 'Memory agent stored new information', agent: 'memory' },
  { id: 3, timestamp: '2025-03-31T10:05:00Z', message: 'Research agent found 5 relevant articles', agent: 'research' },
  { id: 4, timestamp: '2025-03-31T10:00:00Z', message: 'Ops agent deployed new version', agent: 'ops' }
];

// Agent Card Component with null-safe property access
const AgentCard = ({ agent }) => {
  const { colorMode } = useColorMode();
  const navigate = (path) => {
    window.location.href = path;
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
        <Heading size="md" color={colorMode === 'light' ? 'brand.600' : 'brand.300'}>
          {agent?.config?.name ?? "Agent"}
        </Heading>
      </CardHeader>
      <CardBody>
        <Text>{agent?.config?.description ?? "No description"}</Text>
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
        isClosable: true,
      });
    }, 1000);
  };

  // Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshLogs();
    }, 10000);
    
    return () => clearInterval(interval);
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
          <Button 
            size="sm" 
            leftIcon={<FiRefreshCw />} 
            onClick={refreshLogs}
            isLoading={loading}
          >
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
                <Badge colorScheme={
                  log?.agent === 'builder' ? 'blue' : 
                  log?.agent === 'ops' ? 'green' : 
                  log?.agent === 'research' ? 'purple' : 
                  log?.agent === 'memory' ? 'orange' : 'gray'
                }>
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
  const [loading, setLoading] = useState(true);

  // Simulate API call to fetch agents
  useEffect(() => {
    // This will be replaced with actual API call
    setTimeout(() => {
      setAgents(mockAgents);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <Flex justify="center" align="center" height="100%" p={10}>
        <Spinner size="xl" color="brand.500" thickness="4px" />
      </Flex>
    );
  }

  return (
    <Box p={4}>
      <Heading mb={6} size="lg">Dashboard</Heading>
      
      <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(4, 1fr)" }} gap={6} mb={8}>
        {agents?.map((agent) => (
          <AgentCard key={agent?.id ?? Math.random()} agent={agent} />
        )) ?? (
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
