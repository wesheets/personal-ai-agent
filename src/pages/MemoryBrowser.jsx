import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  useColorMode,
  Card,
  CardBody,
  Divider,
  Button,
  Spinner,
  Collapse,
  Badge,
  Icon,
  Flex,
  useToast
} from '@chakra-ui/react';
import { FiChevronDown, FiChevronUp, FiRefreshCw, FiClock, FiFileText } from 'react-icons/fi';
import DEBUG_MODE from '../config/debug';
import { debounce } from '../utils/debounceUtils';

// Mock data for initial development - will be replaced with API calls
const mockMemories = [
  {
    id: 'mem-1',
    title: 'Project Requirements',
    content: 'The project requires a React frontend with Chakra UI. It should include a dashboard, agent panels, memory management, and settings. The UI should be responsive and support light/dark mode.',
    timestamp: '2025-03-31T10:15:00Z',
    type: 'text'
  },
  {
    id: 'mem-2',
    title: 'API Documentation',
    content: 'Backend API endpoints include /api/agent/delegate for task delegation, /api/memory for storing and retrieving memory, and /api/logs/latest for activity logs. All endpoints support standard HTTP methods.',
    timestamp: '2025-03-31T09:45:00Z',
    type: 'text'
  },
  {
    id: 'mem-3',
    title: 'Meeting Notes',
    content: 'In the meeting, we discussed the timeline for the project. The frontend should be completed by April 15, and the backend is already ready for integration. We need to ensure proper error handling and null-safe property access throughout the application.',
    timestamp: '2025-03-30T14:30:00Z',
    type: 'text'
  },
  {
    id: 'file-1',
    title: 'design_specs.pdf',
    content: 'PDF file containing design specifications and wireframes for the UI.',
    timestamp: '2025-03-29T11:20:00Z',
    type: 'file',
    fileType: 'pdf',
    fileSize: 2048
  }
];

const MemoryBrowser = () => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  
  // State for memories
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for expanded items
  const [expandedItems, setExpandedItems] = useState({});
  
  // Function to toggle expanded state
  const toggleExpand = (id) => {
    setExpandedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  // Function to format timestamp
  const formatDate = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Unknown date';
    }
  };
  
  // Function to refresh memories with debounce
  const refreshMemories = async () => {
    // Prevent rapid consecutive calls
    if (loading) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // This will be replaced with actual API call
      // const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api/memory`;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Simulate response
      setMemories(mockMemories);
    } catch (err) {
      console.error('Error fetching memories:', err);
      setError('Failed to fetch memories. Please try again.');
      
      toast({
        title: 'Error',
        description: 'Failed to fetch memories. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Create debounced fetch function
  const debouncedFetchData = useRef(
    debounce(async (isMountedRef, setLoadingFn, setMemoriesFn, setErrorFn, toastFn) => {
      try {
        setLoadingFn(true);
        
        // Add debug log
        console.debug("Loaded: MemoryBrowser - Fetching memories ⏳");
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setMemoriesFn(mockMemories);
          setErrorFn(null);
          console.debug("Loaded: MemoryBrowser - Memories loaded successfully ✅");
        }
      } catch (err) {
        console.error('Error fetching memories:', err);
        
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setErrorFn('Failed to fetch memories. Please try again.');
          
          toastFn({
            title: 'Error',
            description: 'Failed to fetch memories. Please try again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          console.debug("Loaded: MemoryBrowser - Error loading memories ❌");
        }
      } finally {
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setLoadingFn(false);
        }
      }
    }, 500)
  ).current;
  
  // Set up failsafe timeout ref
  const failsafeTimeoutRef = useRef(null);
  
  // Fetch memories on component mount
  useEffect(() => {
    const isMountedRef = { current: true };
    const controller = new AbortController();
    
    // Set up failsafe timeout to reset loading state after 8 seconds
    failsafeTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current && loading) {
        console.warn('⏱️ Failsafe triggered: Forcing loading reset after 8s');
        setLoading(false);
        setError('Loading took too long. Please try refreshing.');
        
        toast({
          title: 'Loading timeout',
          description: 'Loading memories took longer than expected. Showing any available data.',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    }, 8000);
    
    // Create a modified fetch function that uses AbortController
    const fetchWithAbort = async () => {
      try {
        setLoading(true);
        
        // Add debug log
        console.debug("Loaded: MemoryBrowser - Fetching memories ⏳");
        
        // This would be a real fetch in production
        // const response = await fetch('/api/memory', {
        //   signal: controller.signal
        // });
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setMemories(mockMemories);
          setError(null);
          console.debug("Loaded: MemoryBrowser - Memories loaded successfully ✅");
        }
      } catch (err) {
        // Ignore abort errors as they're expected during cleanup
        if (err.name === 'AbortError') {
          console.debug("MemoryBrowser - Fetch aborted during cleanup");
          return;
        }
        
        console.error('Error fetching memories:', err);
        
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setError('Failed to fetch memories. Please try again.');
          
          toast({
            title: 'Error',
            description: 'Failed to fetch memories. Please try again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          console.debug("Loaded: MemoryBrowser - Error loading memories ❌");
        }
      } finally {
        // Only update state if component is still mounted
        if (isMountedRef.current) {
          setLoading(false);
        }
      }
    };
    
    // Only fetch data if not in DEBUG_MODE (prevents polling in production)
    if (!DEBUG_MODE) {
      // Trigger fetch with a 3 second delay to prevent immediate fetch on first render
      setTimeout(() => {
        if (isMountedRef.current) {
          fetchWithAbort();
        }
      }, 3000);
    } else {
      // In debug mode, use the debounced fetch with a shorter delay
      setTimeout(() => {
        if (isMountedRef.current) {
          debouncedFetchData(isMountedRef, setLoading, setMemories, setError, toast);
        }
      }, 300);
    }
    
    return () => {
      isMountedRef.current = false;
      controller.abort(); // Abort any in-flight fetch
      clearTimeout(failsafeTimeoutRef.current);
    };
  }, [debouncedFetchData, toast, loading]);
  
  // Function to get preview content (first 300-500 characters)
  const getPreviewContent = (content) => {
    if (!content) return 'No content available';
    
    const maxLength = 300;
    if (content.length <= maxLength) return content;
    
    return `${content.substring(0, maxLength)}...`;
  };
  
  // Function to render memory item
  const renderMemoryItem = (memory) => {
    const isExpanded = expandedItems[memory?.id] ?? false;
    
    return (
      <Card 
        key={memory?.id ?? Math.random()} 
        bg={colorMode === 'light' ? 'white' : 'gray.700'} 
        boxShadow="md" 
        borderRadius="lg"
        mb={4}
      >
        <CardBody>
          <HStack justifyContent="space-between" mb={2}>
            <Heading size="md">
              {memory?.title ?? 'Untitled Memory'}
            </Heading>
            <HStack>
              <Badge colorScheme={memory?.type === 'file' ? 'purple' : 'blue'}>
                {memory?.type === 'file' ? 'File' : 'Text'}
              </Badge>
              <Text fontSize="sm" color="gray.500">
                <Icon as={FiClock} mr={1} />
                {formatDate(memory?.timestamp ?? '')}
              </Text>
            </HStack>
          </HStack>
          
          {memory?.type === 'file' && (
            <HStack mb={2}>
              <Icon as={FiFileText} />
              <Text fontSize="sm" color="gray.500">
                {memory?.fileType?.toUpperCase() ?? 'Unknown'} - {memory?.fileSize ? `${(memory.fileSize / 1024).toFixed(2)} KB` : 'Unknown size'}
              </Text>
            </HStack>
          )}
          
          <Divider my={2} />
          
          <Box>
            <Text noOfLines={isExpanded ? undefined : 3}>
              {memory?.content ?? 'No content available'}
            </Text>
            
            <Button 
              variant="ghost" 
              size="sm" 
              rightIcon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
              onClick={() => toggleExpand(memory?.id)}
              mt={2}
            >
              {isExpanded ? 'Show Less' : 'Show More'}
            </Button>
          </Box>
        </CardBody>
      </Card>
    );
  };
  
  return (
    <Box p={4}>
      <HStack justifyContent="space-between" mb={6}>
        <Heading size="lg">Memory Browser</Heading>
        <Button 
          leftIcon={<FiRefreshCw />} 
          onClick={refreshMemories}
          isLoading={loading}
          loadingText="Refreshing..."
        >
          Refresh
        </Button>
      </HStack>
      
      {loading ? (
        <Flex justify="center" align="center" height="200px">
          <VStack spacing={4}>
            <Spinner size="xl" color="brand.500" thickness="4px" />
            {memories.length > 0 && (
              <Box textAlign="center">
                <Text>Loading latest data...</Text>
                <Badge colorScheme="yellow" mt={2}>Showing stale data</Badge>
                <Button size="sm" mt={3} onClick={refreshMemories}>
                  Retry
                </Button>
              </Box>
            )}
          </VStack>
        </Flex>
      ) : error ? (
        <Card bg={colorMode === 'light' ? 'red.50' : 'red.900'} p={4} borderRadius="md">
          <Text>{error}</Text>
        </Card>
      ) : memories?.length > 0 ? (
        <VStack spacing={4} align="stretch">
          {memories.map(memory => renderMemoryItem(memory))}
        </VStack>
      ) : (
        <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} p={8} borderRadius="md" textAlign="center">
          <Heading size="md" mb={2}>No Memories Found</Heading>
          <Text>Start by adding text or uploading files in the Memory Agent view.</Text>
        </Card>
      )}
    </Box>
  );
};

export default MemoryBrowser;
