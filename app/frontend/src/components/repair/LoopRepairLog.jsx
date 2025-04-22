import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Badge,
  Button,
  Flex,
  Divider,
  useColorModeValue,
  Icon,
  Tooltip,
  Spinner,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Alert,
  AlertIcon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  InputGroup,
  Input,
  InputLeftElement,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton
} from '@chakra-ui/react';
import { 
  FiAlertTriangle, 
  FiRefreshCw, 
  FiCpu, 
  FiArrowRight,
  FiFilter,
  FiCalendar,
  FiCheck,
  FiX,
  FiChevronDown,
  FiSearch,
  FiInfo,
  FiClock
} from 'react-icons/fi';
import { useAutoRouter } from '../../logic/AutoRerouter';

/**
 * LoopRepairLog Component
 * 
 * Shows history of:
 * - Failed loops
 * - Chosen repair paths
 * - Outcome of rerouted plans
 */
const LoopRepairLog = () => {
  const [repairHistory, setRepairHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState('week');
  const [agentFilter, setAgentFilter] = useState('all');
  const [repairTypeFilter, setRepairTypeFilter] = useState('all');
  const [outcomeFilter, setOutcomeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('timeline'); // 'timeline' or 'table'
  const [selectedRepair, setSelectedRepair] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Get auto-router context if available
  const autoRouter = useAutoRouter ? useAutoRouter() : null;
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headingColor = useColorModeValue('gray.700', 'white');
  const timelineBgColor = useColorModeValue('gray.50', 'gray.800');

  // Fetch repair history
  useEffect(() => {
    const fetchRepairHistory = async () => {
      try {
        setLoading(true);
        
        // Build query parameters
        const params = new URLSearchParams();
        if (timeFilter !== 'all') params.append('time_range', timeFilter);
        if (agentFilter !== 'all') params.append('agent', agentFilter);
        if (repairTypeFilter !== 'all') params.append('repair_type', repairTypeFilter);
        if (outcomeFilter !== 'all') params.append('outcome', outcomeFilter);
        if (searchQuery) params.append('query', searchQuery);
        
        // Make API request
        const response = await fetch(`/api/loop/repairs?${params.toString()}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch repair history: ${response.status}`);
        }
        
        const data = await response.json();
        setRepairHistory(data.repairs || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching repair history:', err);
        setError(err.message);
        
        // Fallback to mock data for development
        if (process.env.NODE_ENV === 'development') {
          setRepairHistory(generateMockRepairHistory());
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchRepairHistory();
    
    // Set up polling for real-time updates (every 30 seconds)
    const intervalId = setInterval(fetchRepairHistory, 30000);
    
    return () => clearInterval(intervalId);
  }, [timeFilter, agentFilter, repairTypeFilter, outcomeFilter, searchQuery]);

  // Handle refresh click
  const handleRefresh = () => {
    setLoading(true);
    // This will trigger the useEffect to refetch data
    setTimeout(() => setLoading(false), 500);
  };

  // Handle repair details click
  const handleRepairDetailsClick = (repair) => {
    setSelectedRepair(repair);
    onOpen();
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

  // Get color for repair type
  const getRepairTypeColor = (type) => {
    switch (type) {
      case 'replan':
        return 'blue';
      case 'agent_switch':
        return 'purple';
      case 'reflect':
        return 'teal';
      case 'flag':
        return 'orange';
      default:
        return 'gray';
    }
  };

  // Get color for outcome
  const getOutcomeColor = (outcome) => {
    switch (outcome) {
      case 'success':
        return 'green';
      case 'partial':
        return 'yellow';
      case 'failure':
        return 'red';
      case 'pending':
        return 'blue';
      default:
        return 'gray';
    }
  };

  // Get icon for repair type
  const getRepairTypeIcon = (type) => {
    switch (type) {
      case 'replan':
        return FiRefreshCw;
      case 'agent_switch':
        return FiCpu;
      case 'reflect':
        return FiArrowRight;
      case 'flag':
        return FiAlertTriangle;
      default:
        return FiInfo;
    }
  };

  // Get icon for outcome
  const getOutcomeIcon = (outcome) => {
    switch (outcome) {
      case 'success':
        return FiCheck;
      case 'failure':
        return FiX;
      case 'pending':
        return FiClock;
      default:
        return FiInfo;
    }
  };

  // Filter repair history based on selected filters
  const filteredRepairHistory = useMemo(() => {
    return repairHistory.filter(repair => {
      // Apply time filter
      if (timeFilter !== 'all') {
        const repairDate = new Date(repair.timestamp);
        const now = new Date();
        
        switch (timeFilter) {
          case 'hour':
            if (now - repairDate > 60 * 60 * 1000) return false;
            break;
          case 'day':
            if (now - repairDate > 24 * 60 * 60 * 1000) return false;
            break;
          case 'week':
            if (now - repairDate > 7 * 24 * 60 * 60 * 1000) return false;
            break;
          default:
            break;
        }
      }
      
      // Apply agent filter
      if (agentFilter !== 'all' && repair.original_agent !== agentFilter && repair.fallback_agent !== agentFilter) {
        return false;
      }
      
      // Apply repair type filter
      if (repairTypeFilter !== 'all' && repair.repair_type !== repairTypeFilter) {
        return false;
      }
      
      // Apply outcome filter
      if (outcomeFilter !== 'all' && repair.outcome !== outcomeFilter) {
        return false;
      }
      
      // Apply search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          (repair.loop_id && repair.loop_id.toLowerCase().includes(query)) ||
          (repair.original_agent && repair.original_agent.toLowerCase().includes(query)) ||
          (repair.fallback_agent && repair.fallback_agent.toLowerCase().includes(query)) ||
          (repair.reason && repair.reason.toLowerCase().includes(query))
        );
      }
      
      return true;
    });
  }, [repairHistory, timeFilter, agentFilter, repairTypeFilter, outcomeFilter, searchQuery]);

  // If loading, show spinner
  if (loading && repairHistory.length === 0) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="md" borderColor={borderColor} bg={bgColor}>
        <Flex justify="center" align="center" py={4}>
          <Spinner size="xl" />
          <Text ml={3}>Loading repair history...</Text>
        </Flex>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md" color={headingColor}>Loop Repair Log</Heading>
        
        <HStack>
          {/* View mode toggle */}
          <Tabs size="sm" variant="soft-rounded" colorScheme="blue" value={viewMode} onChange={(index) => setViewMode(index === 0 ? 'timeline' : 'table')}>
            <TabList>
              <Tab>Timeline</Tab>
              <Tab>Table</Tab>
            </TabList>
          </Tabs>
          
          {/* Refresh button */}
          <Tooltip label="Refresh repair history">
            <Button
              size="sm"
              leftIcon={<Icon as={FiRefreshCw} />}
              onClick={handleRefresh}
              isLoading={loading}
            >
              Refresh
            </Button>
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Filters */}
      <Box mb={4} p={3} borderWidth="1px" borderRadius="md" borderColor={borderColor} bg={timelineBgColor}>
        <Flex wrap="wrap" gap={3} align="center">
          <InputGroup maxW="250px">
            <InputLeftElement pointerEvents="none">
              <Icon as={FiSearch} color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Search repairs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="sm"
            />
          </InputGroup>
          
          <Select
            size="sm"
            maxW="150px"
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            leftIcon={<FiCalendar />}
          >
            <option value="all">All Time</option>
            <option value="hour">Past Hour</option>
            <option value="day">Past Day</option>
            <option value="week">Past Week</option>
          </Select>
          
          <Select
            size="sm"
            maxW="150px"
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
          >
            <option value="all">All Agents</option>
            <option value="ASH">ASH</option>
            <option value="SAGE">SAGE</option>
            <option value="NOVA">NOVA</option>
            <option value="SKEPTIC">SKEPTIC</option>
          </Select>
          
          <Select
            size="sm"
            maxW="150px"
            value={repairTypeFilter}
            onChange={(e) => setRepairTypeFilter(e.target.value)}
          >
            <option value="all">All Repairs</option>
            <option value="replan">Replan</option>
            <option value="agent_switch">Agent Switch</option>
            <option value="reflect">Reflect</option>
            <option value="flag">Flag</option>
          </Select>
          
          <Select
            size="sm"
            maxW="150px"
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
          >
            <option value="all">All Outcomes</option>
            <option value="success">Success</option>
            <option value="partial">Partial</option>
            <option value="failure">Failure</option>
            <option value="pending">Pending</option>
          </Select>
        </Flex>
      </Box>
      
      {/* Error display */}
      {error && (
        <Alert status="error" mb={4} borderRadius="md">
          <AlertIcon />
          {error}
        </Alert>
      )}
      
      {/* No results */}
      {filteredRepairHistory.length === 0 && !loading && (
        <Box p={6} textAlign="center" borderWidth="1px" borderRadius="md" borderColor={borderColor} bg={bgColor}>
          <Icon as={FiInfo} boxSize={10} color="gray.400" mb={3} />
          <Text fontSize="lg" fontWeight="medium">No repair history found</Text>
          <Text color="gray.500">Try adjusting your filters or check back later</Text>
        </Box>
      )}
      
      {/* Timeline View */}
      {viewMode === 'timeline' && filteredRepairHistory.length > 0 && (
        <Box 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor={borderColor} 
          bg={bgColor}
          p={4}
          position="relative"
          overflow="hidden"
        >
          {/* Timeline line */}
          <Box 
            position="absolute"
            left="30px"
            top="0"
            bottom="0"
            width="2px"
            bg="blue.500"
            zIndex={1}
          />
          
          <VStack spacing={0} align="stretch">
            {filteredRepairHistory.map((repair, index) => (
              <Box 
                key={repair.id || `repair-${index}`}
                position="relative"
                pl="60px"
                py={4}
                _hover={{ bg: timelineBgColor }}
                transition="background 0.2s"
                cursor="pointer"
                onClick={() => handleRepairDetailsClick(repair)}
              >
                {/* Timeline node */}
                <Box 
                  position="absolute"
                  left="26px"
                  top="50%"
                  transform="translateY(-50%)"
                  width="10px"
                  height="10px"
                  borderRadius="full"
                  bg={getOutcomeColor(repair.outcome)}
                  zIndex={2}
                />
                
                {/* Repair content */}
                <Box>
                  <Flex justify="space-between" align="center" mb={1}>
                    <HStack>
                      <Badge colorScheme={getRepairTypeColor(repair.repair_type)}>
                        <HStack spacing={1}>
                          <Icon as={getRepairTypeIcon(repair.repair_type)} />
                          <Text>{repair.repair_type === 'agent_switch' ? 'Agent Switch' : 
                                 repair.repair_type === 'replan' ? 'Replan' :
                                 repair.repair_type === 'reflect' ? 'Reflect' :
                                 repair.repair_type === 'flag' ? 'Flagged' :
                                 repair.repair_type}</Text>
                        </HStack>
                      </Badge>
                      
                      <Badge colorScheme={getOutcomeColor(repair.outcome)}>
                        <HStack spacing={1}>
                          <Icon as={getOutcomeIcon(repair.outcome)} />
                          <Text>{repair.outcome}</Text>
                        </HStack>
                      </Badge>
                    </HStack>
                    
                    <Text fontSize="sm" color="gray.500">
                      {formatTimestamp(repair.timestamp)}
                    </Text>
                  </Flex>
                  
                  <Text fontWeight="medium" mb={1}>
                    Loop: {repair.loop_id}
                  </Text>
                  
                  <HStack spacing={2} wrap="wrap" mb={1}>
                    {repair.original_agent && (
                      <Badge colorScheme="red" variant="outline">
                        From: {repair.original_agent}
                      </Badge>
                    )}
                    
                    {repair.fallback_agent && (
                      <Badge colorScheme="green" variant="outline">
                        To: {repair.fallback_agent}
                      </Badge>
                    )}
                  </HStack>
                  
                  <Text fontSize="sm" color="gray.600" noOfLines={2}>
                    {repair.reason || 'No reason provided'}
                  </Text>
                </Box>
                
                {index < filteredRepairHistory.length - 1 && (
                  <Divider mt={4} />
                )}
              </Box>
            ))}
          </VStack>
        </Box>
      )}
      
      {/* Table View */}
      {viewMode === 'table' && filteredRepairHistory.length > 0 && (
        <Box 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor={borderColor} 
          bg={bgColor}
          overflow="hidden"
        >
          <Box overflowX="auto">
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Timestamp</Th>
                  <Th>Loop ID</Th>
                  <Th>Repair Type</Th>
                  <Th>Original Agent</Th>
                  <Th>Fallback Agent</Th>
                  <Th>Outcome</Th>
                  <Th>Reason</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredRepairHistory.map((repair, index) => (
                  <Tr 
                    key={repair.id || `repair-${index}`}
                    _hover={{ bg: timelineBgColor }}
                    cursor="pointer"
                  >
                    <Td>{formatTimestamp(repair.timestamp)}</Td>
                    <Td fontWeight="medium">{repair.loop_id}</Td>
                    <Td>
                      <Badge colorScheme={getRepairTypeColor(repair.repair_type)}>
                        {repair.repair_type === 'agent_switch' ? 'Agent Switch' : 
                         repair.repair_type === 'replan' ? 'Replan' :
                         repair.repair_type === 'reflect' ? 'Reflect' :
                         repair.repair_type === 'flag' ? 'Flagged' :
                         repair.repair_type}
                      </Badge>
                    </Td>
                    <Td>{repair.original_agent}</Td>
                    <Td>{repair.fallback_agent}</Td>
                    <Td>
                      <Badge colorScheme={getOutcomeColor(repair.outcome)}>
                        {repair.outcome}
                      </Badge>
                    </Td>
                    <Td noOfLines={1} maxW="200px">{repair.reason || 'No reason provided'}</Td>
                    <Td>
                      <Button
                        size="xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRepairDetailsClick(repair);
                        }}
                      >
                        Details
                      </Button>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        </Box>
      )}
      
      {/* Stats summary */}
      {filteredRepairHistory.length > 0 && (
        <Flex justify="space-between" mt={2} fontSize="sm" color="gray.500">
          <Text>
            Showing {filteredRepairHistory.length} {filteredRepairHistory.length === 1 ? 'repair' : 'repairs'}
            {repairHistory.length !== filteredRepairHistory.length && ` (filtered from ${repairHistory.length})`}
          </Text>
          
          <HStack spacing={4}>
            <HStack>
              <Badge colorScheme="green" variant="outline">
                Success: {filteredRepairHistory.filter(r => r.outcome === 'success').length}
              </Badge>
            </HStack>
            
            <HStack>
              <Badge colorScheme="yellow" variant="outline">
                Partial: {filteredRepairHistory.filter(r => r.outcome === 'partial').length}
              </Badge>
            </HStack>
            
            <HStack>
              <Badge colorScheme="red" variant="outline">
                Failure: {filteredRepairHistory.filter(r => r.outcome === 'failure').length}
              </Badge>
            </HStack>
            
            <HStack>
              <Badge colorScheme="blue" variant="outline">
                Pending: {filteredRepairHistory.filter(r => r.outcome === 'pending').length}
              </Badge>
            </HStack>
          </HStack>
        </Flex>
      )}
      
      {/* Repair details modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Repair Details
            {selectedRepair && (
              <Badge ml={2} colorScheme={getRepairTypeColor(selectedRepair.repair_type)}>
                {selectedRepair.repair_type === 'agent_switch' ? 'Agent Switch' : 
                 selectedRepair.repair_type === 'replan' ? 'Replan' :
                 selectedRepair.repair_type === 'reflect' ? 'Reflect' :
                 selectedRepair.repair_type === 'flag' ? 'Flagged' :
                 selectedRepair.repair_type}
              </Badge>
            )}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedRepair && (
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Heading size="sm" mb={2}>Loop Information</Heading>
                  <Table size="sm" variant="simple">
                    <Tbody>
                      <Tr>
                        <Td fontWeight="bold">Loop ID</Td>
                        <Td>{selectedRepair.loop_id}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="bold">Timestamp</Td>
                        <Td>{formatTimestamp(selectedRepair.timestamp)}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="bold">Original Agent</Td>
                        <Td>{selectedRepair.original_agent}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="bold">Fallback Agent</Td>
                        <Td>{selectedRepair.fallback_agent}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="bold">Outcome</Td>
                        <Td>
                          <Badge colorScheme={getOutcomeColor(selectedRepair.outcome)}>
                            {selectedRepair.outcome}
                          </Badge>
                        </Td>
                      </Tr>
                    </Tbody>
                  </Table>
                </Box>
                
                <Box>
                  <Heading size="sm" mb={2}>Repair Reason</Heading>
                  <Text>{selectedRepair.reason || 'No reason provided'}</Text>
                </Box>
                
                {selectedRepair.metrics_before && (
                  <Box>
                    <Heading size="sm" mb={2}>Metrics Before Repair</Heading>
                    <Table size="sm" variant="simple">
                      <Tbody>
                        {selectedRepair.metrics_before.realism_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Realism Score</Td>
                            <Td>{(selectedRepair.metrics_before.realism_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                        {selectedRepair.metrics_before.drift_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Drift Score</Td>
                            <Td>{(selectedRepair.metrics_before.drift_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                        {selectedRepair.metrics_before.trust_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Trust Score</Td>
                            <Td>{(selectedRepair.metrics_before.trust_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                      </Tbody>
                    </Table>
                  </Box>
                )}
                
                {selectedRepair.metrics_after && (
                  <Box>
                    <Heading size="sm" mb={2}>Metrics After Repair</Heading>
                    <Table size="sm" variant="simple">
                      <Tbody>
                        {selectedRepair.metrics_after.realism_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Realism Score</Td>
                            <Td>{(selectedRepair.metrics_after.realism_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                        {selectedRepair.metrics_after.drift_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Drift Score</Td>
                            <Td>{(selectedRepair.metrics_after.drift_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                        {selectedRepair.metrics_after.trust_score !== undefined && (
                          <Tr>
                            <Td fontWeight="bold">Trust Score</Td>
                            <Td>{(selectedRepair.metrics_after.trust_score * 100).toFixed(1)}%</Td>
                          </Tr>
                        )}
                      </Tbody>
                    </Table>
                  </Box>
                )}
                
                {selectedRepair.notes && (
                  <Box>
                    <Heading size="sm" mb={2}>Notes</Heading>
                    <Text>{selectedRepair.notes}</Text>
                  </Box>
                )}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

// Generate mock repair history for development
const generateMockRepairHistory = () => {
  const repairTypes = ['replan', 'agent_switch', 'reflect', 'flag'];
  const outcomes = ['success', 'partial', 'failure', 'pending'];
  const agents = ['ASH', 'SAGE', 'NOVA', 'SKEPTIC'];
  
  const mockHistory = [];
  
  for (let i = 0; i < 20; i++) {
    const repairType = repairTypes[Math.floor(Math.random() * repairTypes.length)];
    const outcome = outcomes[Math.floor(Math.random() * outcomes.length)];
    const originalAgent = agents[Math.floor(Math.random() * agents.length)];
    let fallbackAgent;
    
    do {
      fallbackAgent = agents[Math.floor(Math.random() * agents.length)];
    } while (fallbackAgent === originalAgent);
    
    const timestamp = new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000));
    
    mockHistory.push({
      id: `repair-${i}`,
      loop_id: `loop-${1000 + i}`,
      repair_type: repairType,
      original_agent: originalAgent,
      fallback_agent: repairType === 'agent_switch' ? fallbackAgent : null,
      outcome: outcome,
      timestamp: timestamp.toISOString(),
      reason: getRandomReason(repairType, originalAgent),
      metrics_before: {
        realism_score: Math.random() * 0.5,
        drift_score: 0.7 + Math.random() * 0.3,
        trust_score: Math.random() * 0.5
      },
      metrics_after: outcome !== 'failure' ? {
        realism_score: 0.5 + Math.random() * 0.5,
        drift_score: Math.random() * 0.5,
        trust_score: 0.5 + Math.random() * 0.5
      } : null
    });
  }
  
  // Sort by timestamp (most recent first)
  return mockHistory.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
};

// Get random reason for mock data
const getRandomReason = (repairType, agent) => {
  const reasons = {
    replan: [
      `Loop execution failed due to inconsistent output format`,
      `${agent} agent produced incomplete plan`,
      `Output schema validation failed`
    ],
    agent_switch: [
      `${agent} agent has multiple consecutive failures`,
      `Trust delta dropped below threshold (-0.62)`,
      `Drift score exceeded threshold (0.83)`
    ],
    reflect: [
      `Additional reflection needed on contradictory outputs`,
      `Logical inconsistency detected in reasoning`,
      `Reflection required to resolve ambiguity`
    ],
    flag: [
      `Critical failure in core reasoning`,
      `Potential safety concern in output`,
      `Operator review required for unusual pattern`
    ]
  };
  
  const typeReasons = reasons[repairType] || reasons.replan;
  return typeReasons[Math.floor(Math.random() * typeReasons.length)];
};

export default LoopRepairLog;
