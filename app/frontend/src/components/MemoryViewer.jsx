import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Heading,
  useColorMode,
  Divider,
  Button,
  Flex,
  Spinner,
  Switch,
  FormControl,
  FormLabel,
  Tooltip,
  Icon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Alert,
  AlertIcon,
  useToast
} from '@chakra-ui/react';
import { FiClock, FiTag, FiUser, FiFilter, FiSearch, FiRefreshCw } from 'react-icons/fi';
import { useStatus } from '../context/StatusContext';

/**
 * MemoryViewer Component
 * 
 * Enhanced with UX improvements and API integration:
 * - Connected to /api/memory/read endpoint
 * - Toggle between raw and filtered memory
 * - Search and filter capabilities
 * - Timestamps for entries
 * - Visual indicator for fallback state
 * - Agent ID/type tags
 * - Refresh functionality
 */
const MemoryViewer = () => {
  const { colorMode } = useColorMode();
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('filtered'); // 'raw' or 'filtered'
  const [searchQuery, setSearchQuery] = useState('');
  const [memoryType, setMemoryType] = useState('all'); // 'all', 'episodic', 'semantic', 'procedural'
  const [refreshKey, setRefreshKey] = useState(0);
  const toast = useToast();
  
  // Get memory fallback state from context
  const { memoryFallback } = useStatus();
  
  // Fetch memories from API
  const fetchMemories = useCallback(async () => {
    try {
      setLoading(true);
      
      // Build query parameters
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (memoryType !== 'all') params.append('type', memoryType);
      
      // Make API request to the specified endpoint
      const response = await fetch(`/api/memory/read?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch memories: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Transform API response to expected format if needed
      const formattedData = Array.isArray(data.memories) 
        ? data.memories.map(mem => ({
            id: mem.id || mem.memory_id || `mem-${Math.random().toString(36).substr(2, 9)}`,
            content: mem.content || mem.text || mem.value || '',
            timestamp: mem.timestamp || mem.created_at || new Date().toISOString(),
            agent_id: mem.agent_id || mem.source || 'system',
            agent_type: mem.agent_type || (mem.source === 'system' ? 'system' : 'persona'),
            tags: mem.tags || [],
            type: mem.type || 'episodic',
            relevance: mem.relevance || mem.score || 1.0
          }))
        : [];
      
      setMemories(formattedData);
      setError(null);
      
      // Show success toast on manual refresh
      if (refreshKey > 0) {
        toast({
          title: "Memories refreshed",
          description: `Loaded ${formattedData.length} memory entries`,
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (err) {
      console.error('Error fetching memories:', err);
      setError(err.message);
      
      // Show error toast on manual refresh
      if (refreshKey > 0) {
        toast({
          title: "Failed to refresh memories",
          description: err.message,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
      
      // Fallback to mock data for demo
      setMemories([
        {
          id: 'mem-1',
          content: 'User requested information about AI agent architecture',
          timestamp: new Date().toISOString(),
          agent_id: 'hal9000',
          agent_type: 'system',
          tags: ['user-request', 'architecture'],
          type: 'episodic',
          relevance: 0.95
        },
        {
          id: 'mem-2',
          content: 'Research completed on agent communication protocols',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          agent_id: 'ash-xenomorph',
          agent_type: 'persona',
          tags: ['research', 'protocols'],
          type: 'semantic',
          relevance: 0.87
        },
        {
          id: 'mem-3',
          content: 'System update scheduled for next maintenance window',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          agent_id: 'system',
          agent_type: 'system',
          tags: ['maintenance', 'update'],
          type: 'procedural',
          relevance: 0.72
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, memoryType, refreshKey, toast]);
  
  // Fetch memories on component mount and when dependencies change
  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);
  
  // Handle manual refresh
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
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
  
  // Get memory type color
  const getMemoryTypeColor = (type) => {
    switch (type) {
      case 'episodic':
        return 'green';
      case 'semantic':
        return 'orange';
      case 'procedural':
        return 'cyan';
      default:
        return 'gray';
    }
  };
  
  // Filter memories based on view mode and search query
  const filteredMemories = memories
    .filter(mem => {
      // Apply view mode filter
      if (viewMode === 'raw') return true;
      
      // For filtered mode, apply relevance threshold
      return mem.relevance >= 0.75;
    })
    .filter(mem => {
      // Apply search query if present
      if (!searchQuery) return true;
      
      const query = searchQuery.toLowerCase();
      return (
        (mem.content && mem.content.toLowerCase().includes(query)) ||
        (mem.agent_id && mem.agent_id.toLowerCase().includes(query)) ||
        (mem.tags && mem.tags.some(tag => tag.toLowerCase().includes(query)))
      );
    });
  
  return (
    <Box>
      {/* Header with controls */}
      <Flex 
        justify="space-between" 
        align="center" 
        mb={4} 
        pb={2} 
        borderBottomWidth="1px" 
        borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
      >
        <Heading size="md">Memory Viewer</Heading>
        
        <HStack spacing={4}>
          {/* Fallback state indicator */}
          {memoryFallback && memoryFallback.active && (
            <Tooltip label={memoryFallback.reason || 'Vector search disabled'}>
              <Badge colorScheme="yellow" variant="solid" px={2} py={1}>
                fallback: true
              </Badge>
            </Tooltip>
          )}
          
          {/* Refresh button */}
          <Tooltip label="Refresh memories">
            <Button
              size="sm"
              leftIcon={<FiRefreshCw />}
              onClick={handleRefresh}
              isLoading={loading && refreshKey > 0}
              loadingText="Refreshing"
            >
              Refresh
            </Button>
          </Tooltip>
          
          {/* View mode toggle */}
          <FormControl display="flex" alignItems="center" width="auto">
            <FormLabel htmlFor="view-mode" mb="0" mr={2} fontSize="sm">
              Show Raw Memory
            </FormLabel>
            <Switch
              id="view-mode"
              isChecked={viewMode === 'raw'}
              onChange={(e) => setViewMode(e.target.checked ? 'raw' : 'filtered')}
              colorScheme="purple"
            />
          </FormControl>
        </HStack>
      </Flex>
      
      {/* Search and filter controls */}
      <Flex mb={4} gap={4} wrap={{ base: "wrap", md: "nowrap" }}>
        <InputGroup>
          <InputLeftElement pointerEvents="none">
            <Icon as={FiSearch} color="gray.400" />
          </InputLeftElement>
          <Input
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </InputGroup>
        
        <Select
          value={memoryType}
          onChange={(e) => setMemoryType(e.target.value)}
          width={{ base: "full", md: "200px" }}
        >
          <option value="all">All Types</option>
          <option value="episodic">Episodic</option>
          <option value="semantic">Semantic</option>
          <option value="procedural">Procedural</option>
        </Select>
      </Flex>
      
      {/* Error display */}
      {error && (
        <Alert status="error" mb={4} borderRadius="md">
          <AlertIcon />
          {error}
        </Alert>
      )}
      
      {/* Loading state */}
      {loading && refreshKey === 0 && (
        <Flex justify="center" align="center" height="200px">
          <Spinner size="xl" />
        </Flex>
      )}
      
      {/* Memory entries */}
      {!loading && (
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>All Memories ({filteredMemories.length})</Tab>
            <Tab>System ({filteredMemories.filter(m => m.agent_type === 'system').length})</Tab>
            <Tab>Persona ({filteredMemories.filter(m => m.agent_type === 'persona').length})</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel p={0} pt={4}>
              <MemoryList 
                memories={filteredMemories} 
                formatTimestamp={formatTimestamp} 
                getAgentColor={getAgentColor} 
                getMemoryTypeColor={getMemoryTypeColor}
              />
            </TabPanel>
            
            <TabPanel p={0} pt={4}>
              <MemoryList 
                memories={filteredMemories.filter(m => m.agent_type === 'system')} 
                formatTimestamp={formatTimestamp} 
                getAgentColor={getAgentColor} 
                getMemoryTypeColor={getMemoryTypeColor}
              />
            </TabPanel>
            
            <TabPanel p={0} pt={4}>
              <MemoryList 
                memories={filteredMemories.filter(m => m.agent_type === 'persona')} 
                formatTimestamp={formatTimestamp} 
                getAgentColor={getAgentColor} 
                getMemoryTypeColor={getMemoryTypeColor}
              />
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}
      
      {/* View mode indicator */}
      <Text fontSize="xs" textAlign="right" mt={2} color="gray.500">
        Viewing in {viewMode === 'raw' ? 'raw' : 'scored/filtered'} mode
        {viewMode === 'filtered' && memories.length !== filteredMemories.length && 
          ` (${memories.length - filteredMemories.length} entries filtered)`
        }
      </Text>
    </Box>
  );
};

// Memory list component
const MemoryList = ({ memories, formatTimestamp, getAgentColor, getMemoryTypeColor }) => {
  const { colorMode } = useColorMode();
  
  if (memories.length === 0) {
    return (
      <Box p={4} textAlign="center" color="gray.500">
        No memory entries found
      </Box>
    );
  }
  
  return (
    <VStack spacing={4} align="stretch">
      {memories.map(memory => (
        <Box 
          key={memory.id} 
          p={4} 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
          position="relative"
          _hover={{
            boxShadow: "md",
            borderColor: colorMode === 'light' ? 'blue.200' : 'blue.500',
          }}
          transition="all 0.2s"
        >
          {/* Relevance indicator */}
          {memory.relevance && (
            <Tooltip label={`Relevance: ${(memory.relevance * 100).toFixed(0)}%`}>
              <Box 
                position="absolute" 
                top={0} 
                right={0} 
                width="8px" 
                height="100%" 
                bg={`${memory.relevance > 0.9 ? 'green' : memory.relevance > 0.7 ? 'yellow' : 'red'}.${memory.relevance > 0.8 ? '500' : '400'}`}
                borderTopRightRadius="md"
                borderBottomRightRadius="md"
                opacity={0.7}
              />
            </Tooltip>
          )}
          
          {/* Memory content */}
          <Text mb={3}>{memory.content}</Text>
          
          <Divider mb={3} />
          
          {/* Memory metadata */}
          <Flex wrap="wrap" gap={2} justify="space-between">
            <HStack spacing={2} flexWrap="wrap">
              {/* Memory type */}
              {memory.type && (
                <Badge colorScheme={getMemoryTypeColor(memory.type)}>
                  {memory.type}
                </Badge>
              )}
              
              {/* Agent ID/type tag */}
              {memory.agent_id && (
                <Badge colorScheme={getAgentColor(memory.agent_type)}>
                  <HStack spacing={1}>
                    <Icon as={FiUser} boxSize={3} />
                    <Text>{memory.agent_id}</Text>
                  </HStack>
                </Badge>
              )}
              
              {/* Tags */}
              {memory.tags && memory.tags.map(tag => (
                <Badge key={tag} colorScheme="green" variant="outline">
                  <HStack spacing={1}>
                    <Icon as={FiTag} boxSize={3} />
                    <Text>{tag}</Text>
                  </HStack>
                </Badge>
              ))}
            </HStack>
            
            {/* Timestamp */}
            {memory.timestamp && (
              <Badge variant="subtle" colorScheme="gray">
                <HStack spacing={1}>
                  <Icon as={FiClock} boxSize={3} />
                  <Text>{formatTimestamp(memory.timestamp)}</Text>
                </HStack>
              </Badge>
            )}
          </Flex>
        </Box>
      ))}
    </VStack>
  );
};

export default MemoryViewer;
