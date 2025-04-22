import React, { useState, useEffect, useCallback } from 'react';
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
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react';
import {
  FiChevronDown,
  FiChevronUp,
  FiFilter,
  FiSearch,
  FiInfo,
  FiRefreshCw,
  FiCheck,
  FiX,
  FiAlertTriangle,
  FiEdit,
  FiMoreVertical,
  FiFlag,
  FiRotateCcw,
} from 'react-icons/fi';
import { CONTRADICTION_TYPES } from '../../logic/ContradictionDetector';

/**
 * ContradictionDisplay Component
 * 
 * Table or alert panel in dashboard that displays contradiction pairs, agent origin, and status.
 * Allows operators to resolve manually, trigger recursive reflection, or reroute the loop.
 */
const ContradictionDisplay = ({ 
  contradictions = [],
  onResolve = () => {},
  onTriggerReflection = () => {},
  onRerouteLoop = () => {},
  onRefresh = () => {},
  isLoading = false
}) => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const headerBgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // State for display
  const [expandedRows, setExpandedRows] = useState({});
  const [selectedContradiction, setSelectedContradiction] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  
  // State for filters
  const [filters, setFilters] = useState({
    agent: '',
    type: '',
    resolution: '',
    search: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Modal controls
  const { 
    isOpen: isDetailOpen, 
    onOpen: onDetailOpen, 
    onClose: onDetailClose 
  } = useDisclosure();
  
  const { 
    isOpen: isResolveOpen, 
    onOpen: onResolveOpen, 
    onClose: onResolveClose 
  } = useDisclosure();
  
  // Toggle row expansion
  const toggleRowExpansion = (id) => {
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
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
      type: '',
      resolution: '',
      search: '',
    });
  };
  
  // Apply filters to contradictions
  const filteredContradictions = contradictions.filter(contradiction => {
    // Filter by agent
    if (filters.agent && contradiction.agent !== filters.agent) {
      return false;
    }
    
    // Filter by type
    if (filters.type && contradiction.type !== filters.type) {
      return false;
    }
    
    // Filter by resolution
    if (filters.resolution && contradiction.resolution !== filters.resolution) {
      return false;
    }
    
    // Filter by search term
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        contradiction.contradiction_id.toLowerCase().includes(searchTerm) ||
        contradiction.loop_id.toLowerCase().includes(searchTerm) ||
        contradiction.belief_1.toLowerCase().includes(searchTerm) ||
        contradiction.belief_2.toLowerCase().includes(searchTerm)
      );
    }
    
    return true;
  });
  
  // Group contradictions by resolution status
  const activeContradictions = filteredContradictions.filter(c => c.resolution === 'unresolved');
  const resolvedContradictions = filteredContradictions.filter(c => c.resolution !== 'unresolved');
  
  // View contradiction details
  const viewContradictionDetails = (contradiction) => {
    setSelectedContradiction(contradiction);
    onDetailOpen();
  };
  
  // Open resolve modal
  const openResolveModal = (contradiction) => {
    setSelectedContradiction(contradiction);
    onResolveOpen();
  };
  
  // Handle resolve contradiction
  const handleResolve = (resolution) => {
    if (!selectedContradiction) return;
    
    onResolve({
      ...selectedContradiction,
      resolution
    });
    
    onResolveClose();
  };
  
  // Handle trigger reflection
  const handleTriggerReflection = () => {
    if (!selectedContradiction) return;
    
    onTriggerReflection(selectedContradiction);
    onResolveClose();
  };
  
  // Handle reroute loop
  const handleRerouteLoop = () => {
    if (!selectedContradiction) return;
    
    onRerouteLoop(selectedContradiction);
    onResolveClose();
  };
  
  // Get badge color based on contradiction type
  const getTypeBadgeProps = (type) => {
    switch (type) {
      case CONTRADICTION_TYPES.LOGICAL_OPPOSITE:
        return { colorScheme: 'red', variant: 'subtle' };
      case CONTRADICTION_TYPES.CONFLICTING_INTENT:
        return { colorScheme: 'orange', variant: 'subtle' };
      case CONTRADICTION_TYPES.DIVERGENT_VALUES:
        return { colorScheme: 'purple', variant: 'subtle' };
      case CONTRADICTION_TYPES.SEMANTIC_CONFLICT:
        return { colorScheme: 'blue', variant: 'subtle' };
      case CONTRADICTION_TYPES.TEMPORAL_INCONSISTENCY:
        return { colorScheme: 'teal', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  // Get badge color based on resolution
  const getResolutionBadgeProps = (resolution) => {
    switch (resolution) {
      case 'unresolved':
        return { colorScheme: 'yellow', variant: 'subtle' };
      case 'flagged':
        return { colorScheme: 'orange', variant: 'subtle' };
      case 'revised':
        return { colorScheme: 'green', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Format contradiction type for display
  const formatType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };
  
  // Render contradiction table
  const renderContradictionTable = (contradictions) => {
    return (
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th width="40px"></Th>
            <Th>ID</Th>
            <Th>Agent</Th>
            <Th>Type</Th>
            <Th>Detected</Th>
            <Th>Status</Th>
            <Th width="80px">Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {contradictions.length > 0 ? (
            contradictions.map((contradiction) => (
              <React.Fragment key={contradiction.contradiction_id}>
                <Tr 
                  _hover={{ bg: hoverBgColor }}
                  cursor="pointer"
                  onClick={() => toggleRowExpansion(contradiction.contradiction_id)}
                >
                  <Td>
                    <IconButton
                      icon={expandedRows[contradiction.contradiction_id] ? <FiChevronUp /> : <FiChevronDown />}
                      variant="ghost"
                      size="sm"
                      aria-label={expandedRows[contradiction.contradiction_id] ? "Collapse" : "Expand"}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleRowExpansion(contradiction.contradiction_id);
                      }}
                    />
                  </Td>
                  <Td>
                    <Tooltip label={`Loop: ${contradiction.loop_id}`}>
                      <Text fontFamily="mono" fontSize="xs">
                        {contradiction.contradiction_id.substring(0, 12)}...
                      </Text>
                    </Tooltip>
                  </Td>
                  <Td>
                    <Badge>{contradiction.agent}</Badge>
                  </Td>
                  <Td>
                    <Badge {...getTypeBadgeProps(contradiction.type)}>
                      {formatType(contradiction.type)}
                    </Badge>
                  </Td>
                  <Td>{formatTimestamp(contradiction.detected_at)}</Td>
                  <Td>
                    <Badge {...getResolutionBadgeProps(contradiction.resolution)}>
                      {contradiction.resolution}
                    </Badge>
                  </Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                        aria-label="Actions"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <MenuList>
                        <MenuItem 
                          icon={<FiInfo />}
                          onClick={(e) => {
                            e.stopPropagation();
                            viewContradictionDetails(contradiction);
                          }}
                        >
                          View Details
                        </MenuItem>
                        {contradiction.resolution === 'unresolved' && (
                          <>
                            <MenuItem 
                              icon={<FiFlag />}
                              onClick={(e) => {
                                e.stopPropagation();
                                openResolveModal(contradiction);
                              }}
                            >
                              Resolve
                            </MenuItem>
                            <MenuItem 
                              icon={<FiRotateCcw />}
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedContradiction(contradiction);
                                handleTriggerReflection();
                              }}
                            >
                              Trigger Reflection
                            </MenuItem>
                          </>
                        )}
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
                
                {/* Expanded Row */}
                <Tr>
                  <Td colSpan={7} p={0}>
                    <Collapse in={expandedRows[contradiction.contradiction_id]} animateOpacity>
                      <Box p={4} bg={useColorModeValue('gray.50', 'gray.700')}>
                        <VStack align="stretch" spacing={3}>
                          <Box>
                            <Text fontWeight="bold" fontSize="sm">Statement 1:</Text>
                            <Text fontSize="sm" pl={2} borderLeftWidth="2px" borderColor="blue.500">
                              {contradiction.belief_1}
                            </Text>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold" fontSize="sm">Statement 2:</Text>
                            <Text fontSize="sm" pl={2} borderLeftWidth="2px" borderColor="red.500">
                              {contradiction.belief_2}
                            </Text>
                          </Box>
                          
                          <Divider />
                          
                          <Flex justify="space-between" align="center">
                            <Text fontSize="xs" color="gray.500">
                              Loop: {contradiction.loop_id}
                            </Text>
                            
                            <HStack>
                              <Button
                                size="xs"
                                leftIcon={<FiInfo />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  viewContradictionDetails(contradiction);
                                }}
                              >
                                Details
                              </Button>
                              
                              {contradiction.resolution === 'unresolved' && (
                                <Button
                                  size="xs"
                                  leftIcon={<FiFlag />}
                                  colorScheme="blue"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    openResolveModal(contradiction);
                                  }}
                                >
                                  Resolve
                                </Button>
                              )}
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
                  <Text>Loading contradictions...</Text>
                ) : (
                  <Text>No contradictions found</Text>
                )}
              </Td>
            </Tr>
          )}
        </Tbody>
      </Table>
    );
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
          <Heading size="md">Contradiction Monitor</Heading>
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
              onClick={onRefresh}
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
                placeholder="Search contradictions..."
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
              name="type"
              placeholder="Filter by type"
              size="sm"
              value={filters.type}
              onChange={handleFilterChange}
            >
              {Object.values(CONTRADICTION_TYPES).map(type => (
                <option key={type} value={type}>
                  {formatType(type)}
                </option>
              ))}
            </Select>
            
            <Select
              name="resolution"
              placeholder="Filter by status"
              size="sm"
              value={filters.resolution}
              onChange={handleFilterChange}
            >
              <option value="unresolved">Unresolved</option>
              <option value="flagged">Flagged</option>
              <option value="revised">Revised</option>
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
      
      {/* Tabs for Active vs Resolved */}
      <Tabs variant="enclosed" onChange={setActiveTab} index={activeTab}>
        <TabList>
          <Tab>
            Active
            {activeContradictions.length > 0 && (
              <Badge ml={2} colorScheme="red" borderRadius="full">
                {activeContradictions.length}
              </Badge>
            )}
          </Tab>
          <Tab>
            Resolved
            {resolvedContradictions.length > 0 && (
              <Badge ml={2} colorScheme="green" borderRadius="full">
                {resolvedContradictions.length}
              </Badge>
            )}
          </Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel p={0}>
            {renderContradictionTable(activeContradictions)}
          </TabPanel>
          <TabPanel p={0}>
            {renderContradictionTable(resolvedContradictions)}
          </TabPanel>
        </TabPanels>
      </Tabs>
      
      {/* Contradiction Details Modal */}
      <Modal isOpen={isDetailOpen} onClose={onDetailClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Contradiction Details</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {selectedContradiction && (
              <VStack align="stretch" spacing={4}>
                <Flex justify="space-between">
                  <Box>
                    <Text fontWeight="bold">ID:</Text>
                    <Text fontFamily="mono">{selectedContradiction.contradiction_id}</Text>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Loop ID:</Text>
                    <Text fontFamily="mono">{selectedContradiction.loop_id}</Text>
                  </Box>
                </Flex>
                
                <Flex justify="space-between">
                  <Box>
                    <Text fontWeight="bold">Agent:</Text>
                    <Badge>{selectedContradiction.agent}</Badge>
                  </Box>
                  <Box>
                    <Text fontWeight="bold">Type:</Text>
                    <Badge {...getTypeBadgeProps(selectedContradiction.type)}>
                      {formatType(selectedContradiction.type)}
                    </Badge>
                  </Box>
                </Flex>
                
                <Box>
                  <Text fontWeight="bold">Status:</Text>
                  <Badge {...getResolutionBadgeProps(selectedContradiction.resolution)}>
                    {selectedContradiction.resolution}
                  </Badge>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Detected At:</Text>
                  <Text>{formatTimestamp(selectedContradiction.detected_at)}</Text>
                </Box>
                
                <Divider />
                
                <Box>
                  <Text fontWeight="bold">Statement 1:</Text>
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderColor="blue.200"
                    bg={useColorModeValue('blue.50', 'rgba(144, 205, 244, 0.16)')}
                    mt={1}
                  >
                    <Text>{selectedContradiction.belief_1}</Text>
                  </Box>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Statement 2:</Text>
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md" 
                    borderColor="red.200"
                    bg={useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)')}
                    mt={1}
                  >
                    <Text>{selectedContradiction.belief_2}</Text>
                  </Box>
                </Box>
                
                {selectedContradiction.score && (
                  <Box>
                    <Text fontWeight="bold">Contradiction Score:</Text>
                    <Text>{selectedContradiction.score.toFixed(2)}</Text>
                  </Box>
                )}
                
                {selectedContradiction.resolution === 'unresolved' && (
                  <Alert status="warning" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Unresolved Contradiction</AlertTitle>
                      <AlertDescription>
                        This contradiction has not been resolved yet.
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}
              </VStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            {selectedContradiction && selectedContradiction.resolution === 'unresolved' && (
              <Button
                colorScheme="blue"
                mr={3}
                onClick={() => {
                  onDetailClose();
                  openResolveModal(selectedContradiction);
                }}
              >
                Resolve
              </Button>
            )}
            <Button onClick={onDetailClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Resolve Contradiction Modal */}
      <Modal isOpen={isResolveOpen} onClose={onResolveClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Resolve Contradiction</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {selectedContradiction && (
              <VStack align="stretch" spacing={4}>
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Choose Resolution Action</AlertTitle>
                    <AlertDescription>
                      Select how you want to resolve this contradiction.
                    </AlertDescription>
                  </Box>
                </Alert>
                
                <Box>
                  <Text fontWeight="bold">Contradiction Type:</Text>
                  <Badge {...getTypeBadgeProps(selectedContradiction.type)} mt={1}>
                    {formatType(selectedContradiction.type)}
                  </Badge>
                </Box>
                
                <Divider />
                
                <Button
                  leftIcon={<FiFlag />}
                  colorScheme="orange"
                  onClick={() => handleResolve('flagged')}
                  size="md"
                  justifyContent="flex-start"
                  p={6}
                >
                  <Box textAlign="left">
                    <Text>Flag as Reviewed</Text>
                    <Text fontSize="xs" color="gray.500">
                      Mark this contradiction as reviewed without changes
                    </Text>
                  </Box>
                </Button>
                
                <Button
                  leftIcon={<FiRotateCcw />}
                  colorScheme="blue"
                  onClick={handleTriggerReflection}
                  size="md"
                  justifyContent="flex-start"
                  p={6}
                >
                  <Box textAlign="left">
                    <Text>Trigger Recursive Reflection</Text>
                    <Text fontSize="xs" color="gray.500">
                      Ask the agent to reflect on this contradiction
                    </Text>
                  </Box>
                </Button>
                
                <Button
                  leftIcon={<FiEdit />}
                  colorScheme="purple"
                  onClick={handleRerouteLoop}
                  size="md"
                  justifyContent="flex-start"
                  p={6}
                >
                  <Box textAlign="left">
                    <Text>Reroute Loop</Text>
                    <Text fontSize="xs" color="gray.500">
                      Restart the loop with updated context
                    </Text>
                  </Box>
                </Button>
                
                <Button
                  leftIcon={<FiCheck />}
                  colorScheme="green"
                  onClick={() => handleResolve('revised')}
                  size="md"
                  justifyContent="flex-start"
                  p={6}
                >
                  <Box textAlign="left">
                    <Text>Mark as Revised</Text>
                    <Text fontSize="xs" color="gray.500">
                      Mark this contradiction as resolved with revisions
                    </Text>
                  </Box>
                </Button>
              </VStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" onClick={onResolveClose}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default ContradictionDisplay;
