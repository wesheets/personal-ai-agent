import React, { useState, useEffect } from 'react';
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
  
  // Function to refresh memories
  const refreshMemories = async () => {
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
  
  // Fetch memories on component mount
  useEffect(() => {
    refreshMemories();
  }, []);
  
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
          <Spinner size="xl" color="brand.500" thickness="4px" />
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
