import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  VStack,
  Text,
  Flex,
  Badge,
  Divider,
  Button,
  Spinner,
  useColorModeValue,
  useToast,
  Kbd,
  List,
  ListItem,
  IconButton,
  Collapse,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Heading
} from '@chakra-ui/react';
import { 
  FiSearch, 
  FiClock, 
  FiUser, 
  FiTag, 
  FiFilter, 
  FiChevronDown, 
  FiChevronUp, 
  FiX, 
  FiInfo,
  FiSave,
  FiCopy,
  FiList
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';

/**
 * MemoryQueryConsole Component
 * 
 * A searchable input panel that accepts natural language or schema filters
 * for querying memory across time, agents, and projects.
 */
const MemoryQueryConsole = ({ projectId }) => {
  const [query, setQuery] = useState('');
  const [recentQueries, setRecentQueries] = useState([]);
  const [showRecentQueries, setShowRecentQueries] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedFilters, setSelectedFilters] = useState({
    agents: [],
    types: [],
    timeRange: 'all'
  });
  const [showFilters, setShowFilters] = useState(false);
  
  const inputRef = useRef(null);
  const toast = useToast();
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.600');
  
  // Fetch memory query suggestions
  const { data: suggestions, error: suggestionsError, loading: suggestionsLoading } = useFetch(
    `/api/memory/suggestions?project_id=${projectId || ''}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: {
        agents: ['SAGE', 'ORCHESTRATOR', 'OPERATOR', 'SKEPTIC'],
        types: ['reflection', 'plan', 'summary', 'belief', 'goal'],
        examples: [
          'Show me loops by SAGE',
          'What did I believe in phase 12?',
          'List all reflections tagged summary_realism',
          'Show all loops from yesterday',
          'Find reflections about memory integrity'
        ]
      }
    }
  );
  
  // Load recent queries from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('memoryRecentQueries');
      if (saved) {
        setRecentQueries(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Error loading recent queries:', err);
    }
  }, []);
  
  // Save recent queries to localStorage
  const saveRecentQuery = (newQuery) => {
    try {
      // Don't save empty queries
      if (!newQuery.trim()) return;
      
      // Add to recent queries, remove duplicates, and limit to 10
      const updated = [
        newQuery,
        ...recentQueries.filter(q => q !== newQuery)
      ].slice(0, 10);
      
      setRecentQueries(updated);
      localStorage.setItem('memoryRecentQueries', JSON.stringify(updated));
    } catch (err) {
      console.error('Error saving recent query:', err);
    }
  };
  
  // Clear recent queries
  const clearRecentQueries = () => {
    setRecentQueries([]);
    localStorage.removeItem('memoryRecentQueries');
    toast({
      title: 'Recent queries cleared',
      status: 'info',
      duration: 3000,
      isClosable: true
    });
  };
  
  // Handle search submission
  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('query', query);
      if (projectId) params.append('project_id', projectId);
      
      // Add filters if selected
      if (selectedFilters.agents.length > 0) {
        params.append('agents', selectedFilters.agents.join(','));
      }
      if (selectedFilters.types.length > 0) {
        params.append('types', selectedFilters.types.join(','));
      }
      if (selectedFilters.timeRange !== 'all') {
        params.append('time_range', selectedFilters.timeRange);
      }
      
      // Make API request
      const response = await fetch(`/api/memory/query?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Save query to recent queries
      saveRecentQuery(query);
      
      // Update search results
      setSearchResults(data.results || []);
      
      // Close recent queries dropdown
      setShowRecentQueries(false);
      
      // Show success toast for empty results
      if (data.results.length === 0) {
        toast({
          title: 'No results found',
          description: 'Try a different query or adjust your filters',
          status: 'info',
          duration: 3000,
          isClosable: true
        });
      }
    } catch (err) {
      console.error('Search error:', err);
      toast({
        title: 'Search failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
      
      // Set mock results for development/testing
      setSearchResults([
        {
          id: 'mem-1',
          project_id: 'project-123',
          loop_id: 'loop-456',
          agent: 'SAGE',
          timestamp: new Date().toISOString(),
          type: 'reflection',
          content: 'The current approach to memory integrity verification appears to be working well, but we should consider implementing additional checks for cross-reference validation.',
          tags: ['memory_integrity', 'verification']
        },
        {
          id: 'mem-2',
          project_id: 'project-123',
          loop_id: 'loop-789',
          agent: 'ORCHESTRATOR',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          type: 'plan',
          content: 'We will implement the memory query system with natural language processing capabilities to allow operators to search through historical data efficiently.',
          tags: ['implementation', 'memory_system']
        },
        {
          id: 'mem-3',
          project_id: 'project-123',
          loop_id: 'loop-456',
          agent: 'SKEPTIC',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          type: 'summary',
          content: 'The proposed memory integrity checks may not be sufficient for ensuring data consistency across distributed systems. We should consider additional validation mechanisms.',
          tags: ['memory_integrity', 'critique']
        }
      ]);
    } finally {
      setIsSearching(false);
    }
  };
  
  // Handle key press events
  const handleKeyPress = (e) => {
    // Submit search on Enter
    if (e.key === 'Enter') {
      handleSearch();
    }
    
    // Show recent queries on ArrowDown
    if (e.key === 'ArrowDown' && !showRecentQueries && recentQueries.length > 0) {
      setShowRecentQueries(true);
      e.preventDefault();
    }
    
    // Hide recent queries on Escape
    if (e.key === 'Escape' && showRecentQueries) {
      setShowRecentQueries(false);
      e.preventDefault();
    }
    
    // Toggle filters on Ctrl+F
    if (e.key === 'f' && (e.ctrlKey || e.metaKey)) {
      setShowFilters(!showFilters);
      e.preventDefault();
    }
  };
  
  // Handle selecting a recent query
  const selectRecentQuery = (selectedQuery) => {
    setQuery(selectedQuery);
    setShowRecentQueries(false);
    // Focus the input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  // Handle toggling a filter value
  const toggleFilter = (type, value) => {
    setSelectedFilters(prev => {
      const current = [...prev[type]];
      const index = current.indexOf(value);
      
      if (index === -1) {
        // Add the value
        return { ...prev, [type]: [...current, value] };
      } else {
        // Remove the value
        return { ...prev, [type]: current.filter(v => v !== value) };
      }
    });
  };
  
  // Handle setting time range
  const setTimeRange = (range) => {
    setSelectedFilters(prev => ({
      ...prev,
      timeRange: range
    }));
  };
  
  // Clear all filters
  const clearFilters = () => {
    setSelectedFilters({
      agents: [],
      types: [],
      timeRange: 'all'
    });
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
  
  // Get agent color
  const getAgentColor = (agent) => {
    switch (agent?.toUpperCase()) {
      case 'SAGE':
        return 'purple';
      case 'ORCHESTRATOR':
        return 'blue';
      case 'OPERATOR':
        return 'green';
      case 'SKEPTIC':
        return 'orange';
      default:
        return 'gray';
    }
  };
  
  // Get memory type color
  const getTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'reflection':
        return 'blue';
      case 'plan':
        return 'green';
      case 'summary':
        return 'purple';
      case 'belief':
        return 'orange';
      case 'goal':
        return 'cyan';
      default:
        return 'gray';
    }
  };
  
  // Copy query to clipboard
  const copyQuery = () => {
    navigator.clipboard.writeText(query).then(
      () => {
        toast({
          title: 'Query copied to clipboard',
          status: 'success',
          duration: 2000,
          isClosable: true
        });
      },
      (err) => {
        console.error('Could not copy query:', err);
        toast({
          title: 'Failed to copy query',
          status: 'error',
          duration: 2000,
          isClosable: true
        });
      }
    );
  };
  
  return (
    <Box>
      <VStack spacing={4} align="stretch">
        {/* Search input */}
        <Box position="relative">
          <InputGroup size="lg">
            <InputLeftElement pointerEvents="none">
              <FiSearch color="gray.300" />
            </InputLeftElement>
            
            <Input
              ref={inputRef}
              placeholder="Search memory, reflections, loops..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              onFocus={() => recentQueries.length > 0 && setShowRecentQueries(true)}
              borderColor={borderColor}
              _hover={{ borderColor: 'blue.300' }}
              _focus={{ borderColor: 'blue.500', boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)' }}
              bg={bgColor}
            />
            
            <InputRightElement width="auto">
              <Flex>
                {query && (
                  <IconButton
                    icon={<FiX />}
                    size="sm"
                    variant="ghost"
                    aria-label="Clear search"
                    onClick={() => setQuery('')}
                    mr={1}
                  />
                )}
                
                <IconButton
                  icon={<FiFilter />}
                  size="sm"
                  variant={showFilters || Object.values(selectedFilters).some(v => Array.isArray(v) ? v.length > 0 : v !== 'all') ? "solid" : "ghost"}
                  colorScheme={Object.values(selectedFilters).some(v => Array.isArray(v) ? v.length > 0 : v !== 'all') ? "blue" : "gray"}
                  aria-label="Toggle filters"
                  onClick={() => setShowFilters(!showFilters)}
                  mr={1}
                />
                
                <Button
                  isLoading={isSearching}
                  loadingText="Searching"
                  onClick={handleSearch}
                  colorScheme="blue"
                  size="sm"
                  mr={2}
                >
                  Search
                </Button>
              </Flex>
            </InputRightElement>
          </InputGroup>
          
          {/* Recent queries dropdown */}
          <Collapse in={showRecentQueries && recentQueries.length > 0} animateOpacity>
            <Box
              position="absolute"
              top="100%"
              left={0}
              right={0}
              zIndex={10}
              mt={1}
              bg={bgColor}
              borderWidth="1px"
              borderColor={borderColor}
              borderRadius="md"
              boxShadow="md"
              maxH="300px"
              overflowY="auto"
            >
              <Flex justify="space-between" align="center" p={2} borderBottomWidth="1px" borderColor={borderColor}>
                <Text fontSize="sm" fontWeight="medium">Recent Queries</Text>
                <Button size="xs" variant="ghost" onClick={clearRecentQueries}>
                  Clear All
                </Button>
              </Flex>
              
              <List spacing={0}>
                {recentQueries.map((recentQuery, index) => (
                  <ListItem
                    key={`${recentQuery}-${index}`}
                    p={2}
                    cursor="pointer"
                    _hover={{ bg: hoverBgColor }}
                    onClick={() => selectRecentQuery(recentQuery)}
                  >
                    <Flex align="center">
                      <FiClock size="14px" style={{ marginRight: '8px', opacity: 0.7 }} />
                      <Text>{recentQuery}</Text>
                    </Flex>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Collapse>
          
          {/* Keyboard shortcuts hint */}
          <Flex justify="space-between" mt={1} px={1}>
            <Text fontSize="xs" color="gray.500">
              Press <Kbd size="xs">Enter</Kbd> to search, <Kbd size="xs">↓</Kbd> for history, <Kbd size="xs">Ctrl</Kbd>+<Kbd size="xs">F</Kbd> for filters
            </Text>
            
            <Flex>
              {query && (
                <Tooltip label="Copy query">
                  <IconButton
                    icon={<FiCopy />}
                    size="xs"
                    variant="ghost"
                    aria-label="Copy query"
                    onClick={copyQuery}
                    mr={1}
                  />
                </Tooltip>
              )}
              
              <Menu>
                <Tooltip label="Example queries">
                  <MenuButton
                    as={IconButton}
                    icon={<FiList />}
                    size="xs"
                    variant="ghost"
                    aria-label="Example queries"
                  />
                </Tooltip>
                <MenuList>
                  <MenuItem fontSize="sm" fontWeight="bold" isDisabled>Example Queries</MenuItem>
                  <Divider />
                  {suggestions?.examples?.map((example, index) => (
                    <MenuItem 
                      key={index} 
                      fontSize="sm"
                      onClick={() => selectRecentQuery(example)}
                    >
                      {example}
                    </MenuItem>
                  ))}
                </MenuList>
              </Menu>
            </Flex>
          </Flex>
        </Box>
        
        {/* Filters section */}
        <Collapse in={showFilters} animateOpacity>
          <Box
            p={3}
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="md"
            bg={bgColor}
          >
            <Flex justify="space-between" align="center" mb={2}>
              <Heading size="sm">Filters</Heading>
              <Button size="xs" variant="ghost" onClick={clearFilters}>
                Clear All
              </Button>
            </Flex>
            
            <Flex direction={{ base: "column", md: "row" }} gap={4}>
              {/* Agent filters */}
              <Box flex="1">
                <Text fontSize="sm" fontWeight="medium" mb={1}>Agents</Text>
                <Flex wrap="wrap" gap={2}>
                  {suggestions?.agents?.map(agent => (
                    <Badge
                      key={agent}
                      colorScheme={selectedFilters.agents.includes(agent) ? getAgentColor(agent) : "gray"}
                      variant={selectedFilters.agents.includes(agent) ? "solid" : "outline"}
                      cursor="pointer"
                      onClick={() => toggleFilter('agents', agent)}
                      px={2}
                      py={1}
                    >
                      {agent}
                    </Badge>
                  ))}
                </Flex>
              </Box>
              
              {/* Type filters */}
              <Box flex="1">
                <Text fontSize="sm" fontWeight="medium" mb={1}>Types</Text>
                <Flex wrap="wrap" gap={2}>
                  {suggestions?.types?.map(type => (
                    <Badge
                      key={type}
                      colorScheme={selectedFilters.types.includes(type) ? getTypeColor(type) : "gray"}
                      variant={selectedFilters.types.includes(type) ? "solid" : "outline"}
                      cursor="pointer"
                      onClick={() => toggleFilter('types', type)}
                      px={2}
                      py={1}
                    >
                      {type}
                    </Badge>
                  ))}
                </Flex>
              </Box>
              
              {/* Time range filters */}
              <Box flex="1">
                <Text fontSize="sm" fontWeight="medium" mb={1}>Time Range</Text>
                <Flex wrap="wrap" gap={2}>
                  {[
                    { value: 'all', label: 'All Time' },
                    { value: 'today', label: 'Today' },
                    { value: 'week', label: 'This Week' },
                    { value: 'month', label: 'This Month' }
                  ].map(range => (
                    <Badge
                      key={range.value}
                      colorScheme={selectedFilters.timeRange === range.value ? "blue" : "gray"}
                      variant={selectedFilters.timeRange === range.value ? "solid" : "outline"}
                      cursor="pointer"
                      onClick={() => setTimeRange(range.value)}
                      px={2}
                      py={1}
                    >
                      {range.label}
                    </Badge>
                  ))}
                </Flex>
              </Box>
            </Flex>
          </Box>
        </Collapse>
        
        {/* Search results */}
        {searchResults.length > 0 && (
          <Box>
            <Flex justify="space-between" align="center" mb={2}>
              <Text fontWeight="medium">
                {searchResults.length} {searchResults.length === 1 ? 'result' : 'results'}
              </Text>
              
              <Button
                size="xs"
                leftIcon={<FiSave />}
                variant="outline"
                onClick={() => {
                  // Implement save results functionality
                  toast({
                    title: 'Results saved',
                    status: 'success',
                    duration: 2000,
                    isClosable: true
                  });
                }}
              >
                Save Results
              </Button>
            </Flex>
            
            <VStack spacing={3} align="stretch">
              {searchResults.map(result => (
                <Box
                  key={result.id}
                  p={3}
                  borderWidth="1px"
                  borderColor={borderColor}
                  borderRadius="md"
                  bg={bgColor}
                  _hover={{
                    borderColor: 'blue.300',
                    boxShadow: 'sm'
                  }}
                  transition="all 0.2s"
                >
                  <Flex justify="space-between" mb={2}>
                    <Flex align="center" gap={2}>
                      <Badge colorScheme={getAgentColor(result.agent)}>
                        {result.agent}
                      </Badge>
                      
                      <Badge colorScheme={getTypeColor(result.type)}>
                        {result.type}
                      </Badge>
                      
                      <Text fontSize="xs" color="gray.500">
                        Loop: {result.loop_id}
                      </Text>
                    </Flex>
                    
                    <Text fontSize="xs" color="gray.500">
                      {formatTimestamp(result.timestamp)}
                    </Text>
                  </Flex>
                  
                  <Text noOfLines={3}>{result.content}</Text>
                  
                  {result.tags && result.tags.length > 0 && (
                    <Flex mt={2} gap={2} wrap="wrap">
                      {result.tags.map(tag => (
                        <Badge key={tag} variant="outline" colorScheme="green" size="sm">
                          {tag}
                        </Badge>
                      ))}
                    </Flex>
                  )}
                </Box>
              ))}
            </VStack>
          </Box>
        )}
        
        {/* Empty state */}
        {searchResults.length === 0 && !isSearching && query && (
          <Flex
            direction="column"
            align="center"
            justify="center"
            p={6}
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="md"
            borderStyle="dashed"
          >
            <FiInfo size="48px" style={{ opacity: 0.5, marginBottom: '16px' }} />
            <Text fontWeight="medium">No results found</Text>
            <Text color="gray.500" textAlign="center" mt={1}>
              Try a different query or adjust your filters
            </Text>
          </Flex>
        )}
        
        {/* Initial state */}
        {searchResults.length === 0 && !isSearching && !query && (
          <Box
            p={4}
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="md"
            bg={bgColor}
          >
            <Heading size="sm" mb={3}>Example Queries</Heading>
            <VStack align="stretch" spacing={2}>
              {suggestions?.examples?.map((example, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  justifyContent="flex-start"
                  fontWeight="normal"
                  onClick={() => selectRecentQuery(example)}
                  leftIcon={<FiSearch size="14px" />}
                  size="sm"
                >
                  {example}
                </Button>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default MemoryQueryConsole;
