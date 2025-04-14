import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Avatar,
  Flex,
  useColorMode,
  Divider,
  Badge,
  Icon,
  Button,
  Spinner,
  Input,
  InputGroup,
  InputRightElement,
  useToast
} from '@chakra-ui/react';
import { FiSend, FiUser, FiCpu, FiRefreshCw, FiMessageSquare } from 'react-icons/fi';
import DEBUG_MODE from '../config/debug';

// Mock data for initial development - will be replaced with API calls
const mockActivities = [
  {
    id: 'act-1',
    type: 'user_message',
    content: 'Can you help me analyze this dataset?',
    timestamp: '2025-03-31T10:15:00Z',
    sender: 'user'
  },
  {
    id: 'act-2',
    type: 'agent_response',
    content: 'I\'ll help you analyze the dataset. Let me break it down into steps: 1) Data cleaning, 2) Exploratory analysis, 3) Visualization, 4) Insights generation.',
    timestamp: '2025-03-31T10:16:00Z',
    sender: 'research',
    agentName: 'Research Agent'
  },
  {
    id: 'act-3',
    type: 'task_completion',
    content: 'Task "Build React Component" has been completed successfully.',
    timestamp: '2025-03-31T10:20:00Z',
    sender: 'builder',
    agentName: 'Builder Agent',
    taskId: 'task-123'
  },
  {
    id: 'act-4',
    type: 'memory_storage',
    content: 'New information has been stored in memory: "Project requirements document"',
    timestamp: '2025-03-31T10:25:00Z',
    sender: 'memory',
    agentName: 'Memory Agent',
    memoryId: 'mem-456'
  },
  {
    id: 'act-5',
    type: 'user_message',
    content: 'Can you deploy the latest version to production?',
    timestamp: '2025-03-31T10:30:00Z',
    sender: 'user'
  },
  {
    id: 'act-6',
    type: 'agent_response',
    content: 'I\'ll deploy the latest version to production. First, I\'ll run tests, then prepare the deployment package, and finally push to the production environment.',
    timestamp: '2025-03-31T10:31:00Z',
    sender: 'ops',
    agentName: 'Ops Agent'
  }
];

const ActivityFeedPanel = () => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const messagesEndRef = useRef(null);
  
  // State for activities
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for user input
  const [userInput, setUserInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  
  // Function to format timestamp
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (error) {
      return 'Unknown time';
    }
  };
  
  // Function to refresh activities with debounce
  const refreshActivities = async () => {
    // Prevent rapid consecutive calls
    if (loading) return;
    
    setLoading(true);
    setError(null);
    
    // Set up failsafe timeout to reset loading state after 8 seconds
    const failsafeTimeout = setTimeout(() => {
      console.warn('⏱️ Failsafe triggered: Forcing loading reset after 8s');
      setLoading(false);
      setError('Loading took too long. Please try refreshing.');
      
      toast({
        title: 'Loading timeout',
        description: 'Loading activities took longer than expected. Showing any available data.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
    }, 8000);
    
    try {
      // Add debug log
      console.debug("ActivityFeedPanel - Refreshing activities ⏳");
      
      // This will be replaced with actual API call
      // const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api/logs/latest`;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate response
      setActivities(mockActivities);
      console.debug("ActivityFeedPanel - Activities refreshed successfully ✅");
    } catch (err) {
      console.error('Error fetching activities:', err);
      setError('Failed to fetch activities. Please try again.');
      
      toast({
        title: 'Error',
        description: 'Failed to fetch activities. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      console.debug("ActivityFeedPanel - Error refreshing activities ❌");
    } finally {
      clearTimeout(failsafeTimeout);
      setLoading(false);
    }
  };
  
  // Fetch activities on component mount
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    let intervalId = null;
    
    const fetchData = async () => {
      try {
        if (!isMounted) return;
        setLoading(true);
        
        // Add debug log
        console.debug("Loaded: ActivityFeedPanel - Fetching activities ⏳");
        
        // Make a real API call with fallback to mock data
        try {
          const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/logs/system`;
          const response = await fetch(apiUrl, {
            signal: controller.signal,
            headers: {
              'Accept': 'application/json'
            }
          });
          
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          
          const data = await response.json();
          
          // Check if we got valid data
          if (data && Array.isArray(data.activities) && data.activities.length > 0) {
            // Only update state if component is still mounted
            if (isMounted) {
              setActivities(data.activities);
              setError(null);
              console.debug("Loaded: ActivityFeedPanel - Activities loaded successfully ✅", data);
            }
            return;
          } else {
            console.warn("API returned empty or invalid data, falling back to mock data");
            throw new Error("Empty or invalid data");
          }
        } catch (apiError) {
          console.warn("API call failed, using mock data:", apiError);
          
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Only update state if component is still mounted
          if (isMounted) {
            setActivities(mockActivities);
            setError(null);
            console.debug("Loaded: ActivityFeedPanel - Using mock activities as fallback ⚠️");
          }
        }
      } catch (err) {
        // Ignore abort errors as they're expected during cleanup
        if (err.name === 'AbortError') {
          console.debug("ActivityFeedPanel - Fetch aborted during cleanup");
          return;
        }
        
        console.error('Error fetching activities:', err);
        
        // Only update state if component is still mounted
        if (isMounted) {
          setError('Failed to fetch activities. Please try again.');
          
          toast({
            title: 'Error',
            description: 'Failed to fetch activities. Please try again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          console.debug("Loaded: ActivityFeedPanel - Error loading activities ❌");
        }
      } finally {
        // Only update state if component is still mounted
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    // Add a 3 second delay before initial fetch
    const initialTimeout = setTimeout(() => {
      if (isMounted) {
        fetchData();
        
        // Set up auto-refresh every 10 seconds only if not in debug mode
        // This ensures we don't have polling in production
        if (!DEBUG_MODE) {
          intervalId = setInterval(() => {
            if (isMounted) {
              fetchData();
            }
          }, 10000);
        }
      }
    }, 3000);
    
    return () => {
      isMounted = false;
      controller.abort(); // Abort any in-flight fetch
      clearTimeout(initialTimeout);
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, []);
  
  // Scroll to bottom when new messages arrive
  useEffect(() => {
    let isMounted = true;
    
    if (isMounted && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    
    return () => {
      isMounted = false;
    };
  }, [activities]);
  
  // Handle user input submission
  const handleSubmit = async (e) => {
    e?.preventDefault();
    
    if (!userInput.trim()) return;
    
    setIsSending(true);
    
    try {
      // Add user message to activities immediately
      const userMessage = {
        id: `user-${Date.now()}`,
        type: 'user_message',
        content: userInput,
        timestamp: new Date().toISOString(),
        sender: 'user'
      };
      
      setActivities(prev => [...prev, userMessage]);
      
      // Clear input
      setUserInput('');
      
      // Simulate API call for agent response
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Simulate agent response
      const agentResponse = {
        id: `agent-${Date.now()}`,
        type: 'agent_response',
        content: `I'll process your request: "${userInput}"`,
        timestamp: new Date().toISOString(),
        sender: 'builder',
        agentName: 'Builder Agent'
      };
      
      setActivities(prev => [...prev, agentResponse]);
    } catch (err) {
      console.error('Error sending message:', err);
      
      toast({
        title: 'Error',
        description: 'Failed to send message. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSending(false);
    }
  };
  
  // Function to render activity item based on type
  const renderActivityItem = (activity) => {
    const isUser = activity?.sender === 'user';
    
    // Common styling for all message types
    const messageBg = isUser 
      ? (colorMode === 'light' ? 'blue.50' : 'blue.900') 
      : (colorMode === 'light' ? 'gray.50' : 'gray.700');
    
    const messageBorder = isUser
      ? (colorMode === 'light' ? 'blue.200' : 'blue.700')
      : (colorMode === 'light' ? 'gray.200' : 'gray.600');
    
    // Determine icon based on sender
    let avatarIcon = FiUser;
    let avatarBg = 'blue.500';
    
    if (!isUser) {
      switch(activity?.sender) {
        case 'builder':
          avatarIcon = FiCpu;
          avatarBg = 'green.500';
          break;
        case 'ops':
          avatarIcon = FiCpu;
          avatarBg = 'orange.500';
          break;
        case 'research':
          avatarIcon = FiCpu;
          avatarBg = 'purple.500';
          break;
        case 'memory':
          avatarIcon = FiCpu;
          avatarBg = 'pink.500';
          break;
        default:
          avatarIcon = FiCpu;
          avatarBg = 'gray.500';
      }
    }
    
    return (
      <Box 
        key={activity?.id ?? Math.random()} 
        w="100%"
        mb={4}
      >
        <Flex justify={isUser ? 'flex-end' : 'flex-start'}>
          <HStack spacing={2} align="flex-start" maxW="80%">
            {!isUser && (
              <Avatar 
                size="sm" 
                bg={avatarBg} 
                icon={<Icon as={avatarIcon} color="white" />} 
              />
            )}
            
            <Box>
              <HStack mb={1}>
                {!isUser && (
                  <Text fontWeight="bold" fontSize="sm">
                    {activity?.agentName ?? 'Agent'}
                  </Text>
                )}
                <Text fontSize="xs" color="gray.500">
                  {formatTime(activity?.timestamp ?? '')}
                </Text>
                {activity?.type === 'task_completion' && (
                  <Badge colorScheme="green" fontSize="xs">
                    Task Completed
                  </Badge>
                )}
                {activity?.type === 'memory_storage' && (
                  <Badge colorScheme="purple" fontSize="xs">
                    Memory Stored
                  </Badge>
                )}
              </HStack>
              
              <Box 
                p={3} 
                borderRadius="lg" 
                bg={messageBg}
                borderWidth="1px"
                borderColor={messageBorder}
                boxShadow="sm"
              >
                <Text>{activity?.content ?? 'No content'}</Text>
                
                {activity?.taskId && (
                  <Text fontSize="xs" mt={2} color="gray.500">
                    Task ID: {activity.taskId}
                  </Text>
                )}
                
                {activity?.memoryId && (
                  <Text fontSize="xs" mt={2} color="gray.500">
                    Memory ID: {activity.memoryId}
                  </Text>
                )}
              </Box>
            </Box>
            
            {isUser && (
              <Avatar 
                size="sm" 
                bg="blue.500" 
                icon={<Icon as={FiUser} color="white" />} 
              />
            )}
          </HStack>
        </Flex>
      </Box>
    );
  };
  
  return (
    <Flex 
      direction="column" 
      h="calc(100vh - 80px)"
      maxW="800px"
      mx="auto"
      position="relative"
    >
      {/* Header */}
      <Flex 
        justify="space-between" 
        align="center" 
        py={2} 
        px={4}
        borderBottomWidth="1px"
        borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
        bg={colorMode === 'light' ? 'white' : 'gray.800'}
        position="sticky"
        top="0"
        zIndex="10"
      >
        <HStack>
          <Icon as={FiMessageSquare} />
          <Text fontWeight="bold">Activity Feed</Text>
        </HStack>
        <Button 
          size="sm" 
          leftIcon={<FiRefreshCw />} 
          onClick={refreshActivities}
          isLoading={loading}
          variant="ghost"
        >
          Refresh
        </Button>
      </Flex>
      
      {/* Messages area with smooth scrolling */}
      <Box 
        flex="1" 
        overflowY="auto" 
        px={4} 
        py={4}
        css={{
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            width: '10px',
            background: colorMode === 'light' ? '#f1f1f1' : '#2d3748',
          },
          '&::-webkit-scrollbar-thumb': {
            background: colorMode === 'light' ? '#888' : '#4a5568',
            borderRadius: '24px',
          },
        }}
      >
        {loading && activities.length === 0 ? (
          <Flex justify="center" align="center" height="100%">
            <Spinner size="xl" color="brand.500" thickness="4px" />
          </Flex>
        ) : error ? (
          <Box p={4} bg={colorMode === 'light' ? 'red.50' : 'red.900'} borderRadius="md">
            <Text>{error}</Text>
          </Box>
        ) : activities?.length > 0 ? (
          <VStack spacing={4} align="stretch">
            {activities.map(activity => renderActivityItem(activity))}
          </VStack>
        ) : (
          <Flex direction="column" justify="center" align="center" height="100%">
            <Icon as={FiMessageSquare} boxSize={10} color="gray.400" mb={4} />
            <Text color="gray.500">No activity yet</Text>
          </Flex>
        )}
        
        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input area */}
      <Box 
        p={4} 
        borderTopWidth="1px"
        borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
        bg={colorMode === 'light' ? 'white' : 'gray.800'}
      >
        <form onSubmit={handleSubmit}>
          <InputGroup size="md">
            <Input
              placeholder="Type a message..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              pr="4.5rem"
              bg={colorMode === 'light' ? 'white' : 'gray.700'}
              disabled={isSending}
            />
            <InputRightElement width="4.5rem">
              <Button 
                h="1.75rem" 
                size="sm" 
                onClick={handleSubmit}
                isLoading={isSending}
                colorScheme="blue"
                disabled={!userInput.trim()}
              >
                <Icon as={FiSend} />
              </Button>
            </InputRightElement>
          </InputGroup>
        </form>
      </Box>
    </Flex>
  );
};

export default ActivityFeedPanel;
