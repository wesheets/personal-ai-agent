import React, { useState, useEffect } from 'react';
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
  TabPanel
} from '@chakra-ui/react';
import { FiClock, FiTag, FiUser, FiFilter } from 'react-icons/fi';
import { useStatus } from '../context/StatusContext';

/**
 * MemoryViewer Component
 *
 * Enhanced with UX improvements:
 * - Toggle between raw and filtered memory
 * - Timestamps for entries
 * - Visual indicator for fallback state
 * - Agent ID/type tags
 */
const MemoryViewer = () => {
  const { colorMode } = useColorMode();
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('filtered'); // 'raw' or 'filtered'

  // Get memory fallback state from context
  const { memoryFallback } = useStatus();

  // Fetch memories
  useEffect(() => {
    let isMounted = true;

    const fetchMemories = async () => {
      try {
        setLoading(true);

        // Simulate API call - replace with actual API call
        const response = await fetch('/api/memory');

        if (!response.ok) {
          throw new Error(`Failed to fetch memories: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        if (isMounted) {
          setMemories(data);
          setError(null);
        }
      } catch (err) {
        console.error('Error fetching memories:', err);

        if (isMounted) {
          setError(err.message);

          // Fallback to mock data for demo
          setMemories([
            {
              id: 'mem-1',
              content: 'User requested information about AI agent architecture',
              timestamp: new Date().toISOString(),
              agent_id: 'hal9000',
              agent_type: 'system',
              tags: ['user-request', 'architecture']
            },
            {
              id: 'mem-2',
              content: 'Research completed on agent communication protocols',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              agent_id: 'ash-xenomorph',
              agent_type: 'persona',
              tags: ['research', 'protocols']
            },
            {
              id: 'mem-3',
              content: 'System update scheduled for next maintenance window',
              timestamp: new Date(Date.now() - 7200000).toISOString(),
              agent_id: 'system',
              agent_type: 'system',
              tags: ['maintenance', 'update']
            }
          ]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchMemories();

    return () => {
      isMounted = false;
    };
  }, []);

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

  // Filter memories based on view mode
  const filteredMemories =
    viewMode === 'raw'
      ? memories
      : memories.filter((mem) => {
          // Apply scoring/filtering logic here
          // For demo, just filter out items with 'maintenance' tag
          return !mem.tags || !mem.tags.includes('maintenance');
        });

  if (loading) {
    return (
      <Flex justify="center" align="center" height="200px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error && memories.length === 0) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="md" borderColor="red.300" bg="red.50">
        <Heading size="md" color="red.500" mb={2}>
          Error Loading Memories
        </Heading>
        <Text>{error}</Text>
      </Box>
    );
  }

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
          {memoryFallback.active && (
            <Tooltip label={memoryFallback.reason || 'Vector search disabled'}>
              <Badge colorScheme="yellow" variant="solid" px={2} py={1}>
                fallback: true
              </Badge>
            </Tooltip>
          )}

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

      {/* Memory entries */}
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>All Memories ({filteredMemories.length})</Tab>
          <Tab>System ({filteredMemories.filter((m) => m.agent_type === 'system').length})</Tab>
          <Tab>Persona ({filteredMemories.filter((m) => m.agent_type === 'persona').length})</Tab>
        </TabList>

        <TabPanels>
          <TabPanel p={0} pt={4}>
            <MemoryList
              memories={filteredMemories}
              formatTimestamp={formatTimestamp}
              getAgentColor={getAgentColor}
            />
          </TabPanel>

          <TabPanel p={0} pt={4}>
            <MemoryList
              memories={filteredMemories.filter((m) => m.agent_type === 'system')}
              formatTimestamp={formatTimestamp}
              getAgentColor={getAgentColor}
            />
          </TabPanel>

          <TabPanel p={0} pt={4}>
            <MemoryList
              memories={filteredMemories.filter((m) => m.agent_type === 'persona')}
              formatTimestamp={formatTimestamp}
              getAgentColor={getAgentColor}
            />
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* View mode indicator */}
      <Text fontSize="xs" textAlign="right" mt={2} color="gray.500">
        Viewing in {viewMode === 'raw' ? 'raw' : 'scored/filtered'} mode
        {viewMode === 'filtered' &&
          memories.length !== filteredMemories.length &&
          ` (${memories.length - filteredMemories.length} entries filtered)`}
      </Text>
    </Box>
  );
};

// Memory list component
const MemoryList = ({ memories, formatTimestamp, getAgentColor }) => {
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
      {memories.map((memory) => (
        <Box
          key={memory.id}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
        >
          {/* Memory content */}
          <Text mb={3}>{memory.content}</Text>

          <Divider mb={3} />

          {/* Memory metadata */}
          <Flex wrap="wrap" gap={2} justify="space-between">
            <HStack spacing={2}>
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
              {memory.tags &&
                memory.tags.map((tag) => (
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
