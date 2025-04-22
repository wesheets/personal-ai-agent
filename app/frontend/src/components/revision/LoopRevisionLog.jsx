import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Text,
  Heading,
  Flex,
  Button,
  IconButton,
  useColorModeValue,
  Tooltip,
  HStack,
  VStack,
  Collapse,
  Divider,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from '@chakra-ui/react';
import {
  FiChevronDown,
  FiChevronUp,
  FiFilter,
  FiSearch,
  FiInfo,
  FiRefreshCw,
  FiClock,
  FiCheck,
  FiX,
  FiAlertTriangle,
  FiEdit,
} from 'react-icons/fi';

/**
 * LoopRevisionLog Component
 * 
 * Displays a table or timeline showing loop revisions, including:
 * - Loop ID
 * - Original reflection
 * - Revision reason
 * - Timestamp
 * - Replanning status
 */
const LoopRevisionLog = () => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const headerBgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // State for revisions
  const [revisions, setRevisions] = useState([]);
  const [expandedRows, setExpandedRows] = useState({});
  const [selectedRevision, setSelectedRevision] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // State for filters
  const [filters, setFilters] = useState({
    agent: '',
    reason: '',
    status: '',
    search: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Modal controls
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Load revisions on component mount
  useEffect(() => {
    fetchRevisions();
  }, []);
  
  // Mock function to fetch revisions - would be replaced with actual API call
  const fetchRevisions = async () => {
    setIsLoading(true);
    
    try {
      // In a real implementation, this would be an API call
      // For now, we'll use mock data
      const mockRevisions = [
        {
          loop_id: 'loop_456',
          revised_from_loop_id: 'loop_123',
          agent: 'SAGE',
          reason: 'misalignment',
          timestamp: '2025-04-22T14:30:00Z',
          status: 'revised',
          original_reflection: 'The user wants to implement a feature that maximizes efficiency regardless of user comfort.',
          revised_reflection: 'The user wants to implement a feature that balances efficiency with user comfort and emotional safety.',
          project_id: 'life_tree',
        },
        {
          loop_id: 'loop_789',
          revised_from_loop_id: 'loop_345',
          agent: 'HAL',
          reason: 'operator_override',
          timestamp: '2025-04-22T15:45:00Z',
          status: 'replanned',
          original_reflection: 'The system should prioritize data collection over user privacy concerns.',
          revised_reflection: 'The system must always prioritize user privacy and obtain explicit consent for any data collection.',
          project_id: 'life_tree',
        },
        {
          loop_id: 'loop_567',
          revised_from_loop_id: 'loop_432',
          agent: 'NOVA',
          reason: 'contradiction',
          timestamp: '2025-04-22T16:15:00Z',
          status: 'pending',
          original_reflection: 'The approach should focus on technical implementation first, with user experience as a secondary concern.',
          revised_reflection: 'User experience and technical implementation should be developed in parallel, with neither taking precedence.',
          project_id: 'life_tree',
        },
        {
          loop_id: 'loop_890',
          revised_from_loop_id: 'loop_765',
          agent: 'CRITIC',
          reason: 'drift',
          timestamp: '2025-04-22T17:30:00Z',
          status: 'revised',
          original_reflection: 'The system should make decisions autonomously without user input when confidence is high.',
          revised_reflection: 'The system should always seek user confirmation for important decisions, regardless of confidence level.',
          project_id: 'life_tree',
        },
      ];
      
      setRevisions(mockRevisions);
    } catch (error) {
      console.error('Failed to fetch revisions:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Toggle row expansion
  const toggleRowExpansion = (loopId) => {
    setExpandedRows(prev => ({
      ...prev,
      [loopId]: !prev[loopId]
    }));
  };
  
  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Reset filters
  const resetFilters = () => {
    setFilters({
      agent: '',
      reason: '',
      status: '',
      search: '',
    });
  };
  
  // Apply filters to revisions
  const filteredRevisions = revisions.filter(revision => {
    // Filter by agent
    if (filters.agent && revision.agent !== filters.agent) {
      return false;
    }
    
    // Filter by reason
    if (filters.reason && revision.reason !== filters.reason) {
      return false;
    }
    
    // Filter by status
    if (filters.status && revision.status !== filters.status) {
      return false;
    }
    
    // Filter by search term
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        revision.loop_id.toLowerCase().includes(searchTerm) ||
        revision.revised_from_loop_id.toLowerCase().includes(searchTerm) ||
        revision.original_reflection.toLowerCase().includes(searchTerm) ||
        revision.revised_reflection.toLowerCase().includes(searchTerm)
      );
    }
    
    return true;
  });
  
  // View revision details
  const viewRevisionDetails = (revision) => {
    setSelectedRevision(revision);
    onOpen();
  };
  
  // Get badge color based on status
  const getStatusBadgeProps = (status) => {
    switch (status) {
      case 'revised':
        return { colorScheme: 'blue', variant: 'subtle' };
      case 'replanned':
        return { colorScheme: 'green', variant: 'subtle' };
      case 'pending':
        return { colorScheme: 'yellow', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  // Get badge color based on reason
  const getReasonBadgeProps = (reason) => {
    switch (reason) {
      case 'misalignment':
        return { colorScheme: 'red', variant: 'subtle' };
      case 'drift':
        return { colorScheme: 'purple', variant: 'subtle' };
      case 'operator_override':
        return { colorScheme: 'orange', variant: 'subtle' };
      case 'contradiction':
        return { colorScheme: 'teal', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  return (
    <Box
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      boxShadow="sm"
    >
      {/* Header */}
      <Box bg={headerBgColor} px={6} py={4}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Loop Revision Log</Heading>
          <HStack>
            <Button
              leftIcon={<FiFilter />}
              size="sm"
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
            <Button
              leftIcon={<FiRefreshCw />}
              size="sm"
              variant="outline"
              onClick={fetchRevisions}
              isLoading={isLoading}
            >
              Refresh
            </Button>
          </HStack>
        </Flex>
      </Box>
      
      {/* Filters */}
      <Collapse in={showFilters} animateOpacity>
        <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={4}>
            <InputGroup size="sm">
              <InputLeftElement pointerEvents="none">
                <FiSearch color="gray.300" />
              </InputLeftElement>
              <Input
                name="search"
                placeholder="Search revisions..."
                value={filters.search}
                onChange={handleFilterChange}
              />
            </InputGroup>
            
            <Select
              name="agent"
              placeholder="Filter by agent"
              size="sm"
              value={filters.agent}
              onChange={handleFilterChange}
            >
              <option value="SAGE">SAGE</option>
              <option value="HAL">HAL</option>
              <option value="NOVA">NOVA</option>
              <option value="CRITIC">CRITIC</option>
            </Select>
            
            <Select
              name="reason"
              placeholder="Filter by reason"
              size="sm"
              value={filters.reason}
              onChange={handleFilterChange}
            >
              <option value="misalignment">Misalignment</option>
              <option value="drift">Drift</option>
              <option value="operator_override">Operator Override</option>
              <option value="contradiction">Contradiction</option>
            </Select>
            
            <Select
              name="status"
              placeholder="Filter by status"
              size="sm"
              value={filters.status}
              onChange={handleFilterChange}
            >
              <option value="revised">Revised</option>
              <option value="replanned">Replanned</option>
              <option value="pending">Pending</option>
            </Select>
            
            <Button
              size="sm"
              variant="ghost"
              onClick={resetFilters}
            >
              Reset
            </Button>
          </Flex>
        </Box>
      </Collapse>
      
      {/* Revisions Table */}
      <Box overflowX="auto">
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th width="40px"></Th>
              <Th>Loop ID</Th>
              <Th>Agent</Th>
              <Th>Reason</Th>
              <Th>Timestamp</Th>
              <Th>Status</Th>
              <Th width="80px">Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {filteredRevisions.length > 0 ? (
              filteredRevisions.map((revision) => (
                <React.Fragment key={revision.loop_id}>
                  <Tr 
                    _hover={{ bg: hoverBgColor }}
                    cursor="pointer"
                    onClick={() => toggleRowExpansion(revision.loop_id)}
                  >
                    <Td>
                      <IconButton
                        icon={expandedRows[revision.loop_id] ? <FiChevronUp /> : <FiChevronDown />}
                        variant="ghost"
                        size="sm"
                        aria-label={expandedRows[revision.loop_id] ? "Collapse" : "Expand"}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleRowExpansion(revision.loop_id);
                        }}
                      />
                    </Td>
                    <Td>
                      <Tooltip label={`Revised from: ${revision.revised_from_loop_id}`}>
                        <Text fontFamily="mono">{revision.loop_id}</Text>
                      </Tooltip>
                    </Td>
                    <Td>
                      <Badge>{revision.agent}</Badge>
                    </Td>
                    <Td>
                      <Badge {...getReasonBadgeProps(revision.reason)}>
                        {revision.reason.replace('_', ' ')}
                      </Badge>
                    </Td>
                    <Td>{formatTimestamp(revision.timestamp)}</Td>
                    <Td>
                      <Badge {...getStatusBadgeProps(revision.status)}>
                        {revision.status}
                      </Badge>
                    </Td>
                    <Td>
                      <IconButton
                        icon={<FiInfo />}
                        variant="ghost"
                        size="sm"
                        aria-label="View details"
                        onClick={(e) => {
                          e.stopPropagation();
                          viewRevisionDetails(revision);
                        }}
                      />
                    </Td>
                  </Tr>
                  
                  {/* Expanded Row */}
                  <Tr>
                    <Td colSpan={7} p={0}>
                      <Collapse in={expandedRows[revision.loop_id]} animateOpacity>
                        <Box p={4} bg={useColorModeValue('gray.50', 'gray.700')}>
                          <VStack align="stretch" spacing={3}>
                            <Box>
                              <Text fontWeight="bold" fontSize="sm">Original Reflection:</Text>
                              <Text fontSize="sm" pl={2} borderLeftWidth="2px" borderColor="red.500">
                                {revision.original_reflection}
                              </Text>
                            </Box>
                            
                            <Box>
                              <Text fontWeight="bold" fontSize="sm">Revised Reflection:</Text>
                              <Text fontSize="sm" pl={2} borderLeftWidth="2px" borderColor="green.500">
                                {revision.revised_reflection}
                              </Text>
                            </Box>
                            
                            <Divider />
                            
                            <Flex justify="space-between" align="center">
                              <Text fontSize="xs" color="gray.500">
                                Project: {revision.project_id}
                              </Text>
                              
                              <HStack>
                                <Button
                                  size="xs"
                                  leftIcon={<FiInfo />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    viewRevisionDetails(revision);
                                  }}
                                >
                                  Details
                                </Button>
                              </HStack>
                            </Flex>
                          </VStack>
                        </Box>
                      </Collapse>
                    </Td>
                  </Tr>
                </React.Fragment>
              ))
            ) : (
              <Tr>
                <Td colSpan={7} textAlign="center" py={4}>
                  {isLoading ? (
                    <Text>Loading revisions...</Text>
                  ) : (
                    <Text>No revisions found</Text>
                  )}
                </Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </Box>
      
      {/* Revision Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Revision Details</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {selectedRevision && (
              <VStack align="stretch" spacing={4}>
                <Flex justify="space-between">
                  <Box>
                    <Text fontWeight="bold">Loop ID:</Text>
                    <Text fontFamily="mono">{selectedRevision.loop_id}</Text>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Revised From:</Text>
                    <Text fontFamily="mono">{selectedRevision.revised_from_loop_id}</Text>
                  </Box>
                </Flex>
                
                <Flex justify="space-between">
                  <Box>
                    <Text fontWeight="bold">Agent:</Text>
                    <Badge>{selectedRevision.agent}</Badge>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Project:</Text>
                    <Text>{selectedRevision.project_id}</Text>
                  </Box>
                </Flex>
                
                <Box>
                  <Text fontWeight="bold">Reason:</Text>
                  <Badge {...getReasonBadgeProps(selectedRevision.reason)}>
                    {selectedRevision.reason.replace('_', ' ')}
                  </Badge>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Status:</Text>
                  <Badge {...getStatusBadgeProps(selectedRevision.status)}>
                    {selectedRevision.status}
                  </Badge>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Timestamp:</Text>
                  <Text>{formatTimestamp(selectedRevision.timestamp)}</Text>
                </Box>
                
                <Divider />
                
                <Box>
                  <Text fontWeight="bold">Original Reflection:</Text>
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderColor="red.200"
                    bg={useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)')}
                    mt={1}
                  >
                    <Text>{selectedRevision.original_reflection}</Text>
                  </Box>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Revised Reflection:</Text>
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderColor="green.200"
                    bg={useColorModeValue('green.50', 'rgba(154, 230, 180, 0.16)')}
                    mt={1}
                  >
                    <Text>{selectedRevision.revised_reflection}</Text>
                  </Box>
                </Box>
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

export default LoopRevisionLog;
