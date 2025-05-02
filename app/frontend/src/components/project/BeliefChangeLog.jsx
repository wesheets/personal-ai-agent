import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Flex,
  Spinner,
  useColorModeValue,
  Button,
  IconButton,
  Divider,
  Tooltip,
  Heading,
  useToast,
  Select,
  Switch,
  FormControl,
  FormLabel,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Code,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
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
  FiClock, 
  FiUser, 
  FiTag, 
  FiRefreshCw,
  FiDownload,
  FiFilter,
  FiInfo,
  FiEdit,
  FiPlus,
  FiMinus,
  FiArrowRight,
  FiArrowLeft,
  FiRotateCcw
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactDiffViewer from 'react-diff-viewer';

/**
 * BeliefChangeLog Component
 * 
 * Shows belief version diffs over time with information about
 * authoring agents and change types.
 */
const BeliefChangeLog = ({ projectId }) => {
  const [selectedBelief, setSelectedBelief] = useState(null);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [timeRange, setTimeRange] = useState('all'); // 'all', 'day', 'week', 'month'
  const [agentFilter, setAgentFilter] = useState('all');
  const [changeTypeFilter, setChangeTypeFilter] = useState('all'); // 'all', 'modified', 'added', 'deprecated'
  const [showDiff, setShowDiff] = useState(true);
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const panelBgColor = useColorModeValue('gray.50', 'gray.800');
  const diffBgColor = useColorModeValue('gray.50', 'gray.600');
  const addedColor = useColorModeValue('green.500', 'green.300');
  const removedColor = useColorModeValue('red.500', 'red.300');
  
  // Fetch belief change data
  const { 
    data: beliefData, 
    error: beliefError, 
    loading: beliefLoading,
    refetch: refetchBeliefData
  } = useFetch(
    `/api/project/belief-changes?project_id=${projectId || ''}&time_range=${timeRange}&agent=${agentFilter}&change_type=${changeTypeFilter}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: null
    }
  );
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Format relative time
  const formatRelativeTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      
      if (diffDay > 0) {
        return `${diffDay}d ago`;
      } else if (diffHour > 0) {
        return `${diffHour}h ago`;
      } else if (diffMin > 0) {
        return `${diffMin}m ago`;
      } else {
        return 'Just now';
      }
    } catch (error) {
      return 'Unknown';
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
  
  // Get change type color
  const getChangeTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'modified':
        return 'blue';
      case 'added':
        return 'green';
      case 'deprecated':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Export belief changes as JSON
  const exportBeliefChanges = () => {
    if (!beliefData) return;
    
    try {
      const dataStr = JSON.stringify(beliefData, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
      
      const exportFileDefaultName = `belief-changes-${projectId || 'unknown'}-${new Date().toISOString().slice(0, 10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      toast({
        title: 'Belief changes exported',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      console.error('Error exporting belief changes:', err);
      toast({
        title: 'Export failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  };
  
  // Handle belief selection
  const handleBeliefSelect = (belief) => {
    setSelectedBelief(belief);
    
    // Find all versions of this belief
    if (beliefData && beliefData.beliefs) {
      const versions = beliefData.beliefs.filter(b => b.belief_id === belief.belief_id);
      setSelectedVersions(versions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
    }
    
    onOpen();
  };
  
  // Handle belief rollback
  const handleRollback = (version) => {
    // In a real implementation, this would call an API to roll back to this version
    toast({
      title: 'Rollback initiated',
      description: `Rolling back belief ${version.belief_id} to version from ${formatTimestamp(version.timestamp)}`,
      status: 'info',
      duration: 3000,
      isClosable: true
    });
  };
  
  // Mock data for development/testing
  const mockBeliefData = {
    project_id: projectId || 'project-123',
    beliefs: [
      {
        belief_id: 'belief-001',
        timestamp: new Date(Date.now() - 86400000 * 7).toISOString(),
        agent: 'SAGE',
        change_type: 'added',
        content: 'Memory systems must maintain integrity across distributed nodes to ensure cognitive continuity.',
        version: 1
      },
      {
        belief_id: 'belief-001',
        timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
        agent: 'SKEPTIC',
        change_type: 'modified',
        content: 'Memory systems must maintain integrity across distributed nodes to ensure cognitive continuity, with regular validation checks to prevent drift.',
        version: 2
      },
      {
        belief_id: 'belief-001',
        timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
        agent: 'ORCHESTRATOR',
        change_type: 'modified',
        content: 'Memory systems must maintain integrity across distributed nodes to ensure cognitive continuity, with regular validation checks to prevent drift and reconciliation protocols to resolve conflicts.',
        version: 3
      },
      {
        belief_id: 'belief-002',
        timestamp: new Date(Date.now() - 86400000 * 6).toISOString(),
        agent: 'ORCHESTRATOR',
        change_type: 'added',
        content: 'Natural language queries should be parsed into structured representations before execution.',
        version: 1
      },
      {
        belief_id: 'belief-002',
        timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
        agent: 'SAGE',
        change_type: 'modified',
        content: 'Natural language queries should be parsed into structured representations before execution, with fallback to vector similarity search when parsing fails.',
        version: 2
      },
      {
        belief_id: 'belief-003',
        timestamp: new Date(Date.now() - 86400000 * 4).toISOString(),
        agent: 'SKEPTIC',
        change_type: 'added',
        content: 'All cognitive operations must be traceable and explainable to maintain operator trust.',
        version: 1
      },
      {
        belief_id: 'belief-004',
        timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
        agent: 'OPERATOR',
        change_type: 'added',
        content: 'System should prioritize response time over exhaustive search when under high load.',
        version: 1
      },
      {
        belief_id: 'belief-004',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        agent: 'SKEPTIC',
        change_type: 'deprecated',
        content: 'System should prioritize response time over exhaustive search when under high load.',
        version: 2
      },
      {
        belief_id: 'belief-005',
        timestamp: new Date().toISOString(),
        agent: 'SAGE',
        change_type: 'added',
        content: 'Cognitive loops should be self-monitoring and capable of detecting their own failure modes.',
        version: 1
      }
    ]
  };
  
  // Use mock data if no real data is available
  const displayData = beliefData || mockBeliefData;
  
  // Filter beliefs based on current filters
  const filteredBeliefs = displayData.beliefs
    .filter(belief => {
      // Filter by agent if not 'all'
      if (agentFilter !== 'all' && belief.agent !== agentFilter) {
        return false;
      }
      
      // Filter by change type if not 'all'
      if (changeTypeFilter !== 'all' && belief.change_type !== changeTypeFilter) {
        return false;
      }
      
      // Filter by time range
      if (timeRange !== 'all') {
        const beliefDate = new Date(belief.timestamp);
        const now = new Date();
        
        if (timeRange === 'day' && (now - beliefDate > 86400000)) {
          return false;
        } else if (timeRange === 'week' && (now - beliefDate > 86400000 * 7)) {
          return false;
        } else if (timeRange === 'month' && (now - beliefDate > 86400000 * 30)) {
          return false;
        }
      }
      
      return true;
    })
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  // Group beliefs by ID for the accordion view
  const groupedBeliefs = filteredBeliefs.reduce((acc, belief) => {
    if (!acc[belief.belief_id]) {
      acc[belief.belief_id] = [];
    }
    acc[belief.belief_id].push(belief);
    return acc;
  }, {});
  
  // Sort belief groups by most recent update
  const sortedBeliefGroups = Object.entries(groupedBeliefs)
    .map(([beliefId, versions]) => ({
      beliefId,
      versions: versions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    }))
    .sort((a, b) => {
      const aLatest = a.versions[0];
      const bLatest = b.versions[0];
      return new Date(bLatest.timestamp) - new Date(aLatest.timestamp);
    });
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">Belief Change Log</Heading>
        
        <HStack spacing={2}>
          <Tooltip label="Refresh belief changes">
            <IconButton
              icon={<FiRefreshCw />}
              size="sm"
              aria-label="Refresh belief changes"
              onClick={() => refetchBeliefData()}
              isLoading={beliefLoading}
            />
          </Tooltip>
          
          <Tooltip label="Export belief changes">
            <IconButton
              icon={<FiDownload />}
              size="sm"
              aria-label="Export belief changes"
              onClick={exportBeliefChanges}
            />
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Filters */}
      <Box mb={4} p={3} borderWidth="1px" borderRadius="md" bg={panelBgColor}>
        <Flex direction={{ base: 'column', md: 'row' }} gap={4}>
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="time-range" mb="0" fontSize="sm">
              Time Range:
            </FormLabel>
            <Select
              id="time-range"
              size="sm"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              width="auto"
            >
              <option value="all">All Time</option>
              <option value="day">Last 24 Hours</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
            </Select>
          </FormControl>
          
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="agent-filter" mb="0" fontSize="sm">
              Agent:
            </FormLabel>
            <Select
              id="agent-filter"
              size="sm"
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              width="auto"
            >
              <option value="all">All Agents</option>
              <option value="ORCHESTRATOR">Orchestrator</option>
              <option value="SAGE">Sage</option>
              <option value="SKEPTIC">Skeptic</option>
              <option value="OPERATOR">Operator</option>
            </Select>
          </FormControl>
          
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="change-type" mb="0" fontSize="sm">
              Change Type:
            </FormLabel>
            <Select
              id="change-type"
              size="sm"
              value={changeTypeFilter}
              onChange={(e) => setChangeTypeFilter(e.target.value)}
              width="auto"
            >
              <option value="all">All Types</option>
              <option value="added">Added</option>
              <option value="modified">Modified</option>
              <option value="deprecated">Deprecated</option>
            </Select>
          </FormControl>
        </Flex>
      </Box>
      
      {/* Belief change log content */}
      <Box
        borderWidth="1px"
        borderRadius="md"
        borderColor={borderColor}
        bg={bgColor}
        height="calc(100vh - 250px)"
        overflowY="auto"
      >
        {beliefLoading ? (
          <Flex justify="center" align="center" height="100%">
            <Spinner size="xl" thickness="4px" speed="0.65s" color="blue.500" />
          </Flex>
        ) : beliefError ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" color="red.500" mb={2}>Error Loading Belief Changes</Heading>
            <Text>{beliefError.message || 'Failed to load belief changes'}</Text>
            <Button mt={4} onClick={() => refetchBeliefData()}>
              Try Again
            </Button>
          </Flex>
        ) : filteredBeliefs.length === 0 ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" mb={2}>No Belief Changes Found</Heading>
            <Text>No belief changes match the current filters.</Text>
          </Flex>
        ) : (
          <Accordion allowMultiple defaultIndex={[0]} p={2}>
            {sortedBeliefGroups.map(({ beliefId, versions }) => {
              const latestVersion = versions[0];
              const isDeprecated = latestVersion.change_type === 'deprecated';
              
              return (
                <AccordionItem 
                  key={beliefId}
                  mb={2}
                  borderWidth="1px"
                  borderRadius="md"
                  borderColor={isDeprecated ? 'red.300' : borderColor}
                  bg={isDeprecated ? 'red.50' : bgColor}
                  _dark={{
                    bg: isDeprecated ? 'red.900' : bgColor
                  }}
                >
                  <h2>
                    <AccordionButton py={3}>
                      <Box flex="1" textAlign="left">
                        <Flex align="center" wrap="wrap" gap={2}>
                          <Text fontWeight="bold" mr={2}>
                            {beliefId}
                          </Text>
                          
                          <Badge colorScheme={getChangeTypeColor(latestVersion.change_type)}>
                            {latestVersion.change_type}
                          </Badge>
                          
                          <Badge colorScheme={getAgentColor(latestVersion.agent)}>
                            {latestVersion.agent}
                          </Badge>
                          
                          <Text fontSize="sm" color="gray.500">
                            {formatRelativeTime(latestVersion.timestamp)}
                          </Text>
                          
                          {isDeprecated && (
                            <Badge colorScheme="red">Deprecated</Badge>
                          )}
                        </Flex>
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="stretch" spacing={4}>
                      {/* Latest version content */}
                      <Box>
                        <Text fontWeight="medium" mb={2}>Current Version:</Text>
                        <Box
                          p={3}
                          borderWidth="1px"
                          borderRadius="md"
                          borderColor={borderColor}
                          bg={diffBgColor}
                        >
                          <Text>{latestVersion.content}</Text>
                        </Box>
                      </Box>
                      
                      {/* Version history */}
                      {versions.length > 1 && (
                        <Box>
                          <Text fontWeight="medium" mb={2}>Version History:</Text>
                          <VStack align="stretch" spacing={2}>
                            {versions.map((version, index) => (
                              <Flex
                                key={`${version.belief_id}-${version.version}`}
                                p={2}
                                borderWidth="1px"
                                borderRadius="md"
                                borderColor={borderColor}
                                justify="space-between"
                                align="center"
                              >
                                <HStack>
                                  <Badge>v{version.version}</Badge>
                                  <Badge colorScheme={getChangeTypeColor(version.change_type)}>
                                    {version.change_type}
                                  </Badge>
                                  <Badge colorScheme={getAgentColor(version.agent)}>
                                    {version.agent}
                                  </Badge>
                                  <Text fontSize="sm">
                                    {formatTimestamp(version.timestamp)}
                                  </Text>
                                </HStack>
                                
                                <HStack>
                                  <Tooltip label="View Details">
                                    <IconButton
                                      icon={<FiInfo />}
                                      size="sm"
                                      variant="ghost"
                                      aria-label="View details"
                                      onClick={() => handleBeliefSelect(version)}
                                    />
                                  </Tooltip>
                                  
                                  {index > 0 && (
                                    <Tooltip label="Rollback to this version">
                                      <IconButton
                                        icon={<FiRotateCcw />}
                                        size="sm"
                                        variant="ghost"
                                        aria-label="Rollback to this version"
                                        onClick={() => handleRollback(version)}
                                      />
                                    </Tooltip>
                                  )}
                                </HStack>
                              </Flex>
                            ))}
                          </VStack>
                        </Box>
                      )}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              );
            })}
          </Accordion>
        )}
      </Box>
      
      {/* Version details modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Belief Version Details
            {selectedBelief && (
              <Flex mt={1} wrap="wrap" gap={2}>
                <Badge>{selectedBelief.belief_id}</Badge>
                <Badge>v{selectedBelief.version}</Badge>
                <Badge colorScheme={getChangeTypeColor(selectedBelief?.change_type)}>
                  {selectedBelief?.change_type}
                </Badge>
              </Flex>
            )}
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {selectedBelief && (
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="medium" mb={2}>Metadata:</Text>
                  <HStack wrap="wrap" spacing={2}>
                    <Badge colorScheme={getAgentColor(selectedBelief.agent)}>
                      {selectedBelief.agent}
                    </Badge>
                    <Text fontSize="sm">
                      {formatTimestamp(selectedBelief.timestamp)}
                    </Text>
                  </HStack>
                </Box>
                
                <Box>
                  <Text fontWeight="medium" mb={2}>Content:</Text>
                  <Box
                    p={3}
                    borderWidth="1px"
                    borderRadius="md"
                    borderColor={borderColor}
                    bg={diffBgColor}
                  >
                    <Text>{selectedBelief.content}</Text>
                  </Box>
                </Box>
                
                {/* Diff view if this is not the first version */}
                {selectedVersions.length > 1 && selectedBelief.version > 1 && (
                  <Box>
                    <Flex justify="space-between" align="center" mb={2}>
                      <Text fontWeight="medium">Changes from Previous Version:</Text>
                      <Switch
                        isChecked={showDiff}
                        onChange={(e) => setShowDiff(e.target.checked)}
                        size="sm"
                      />
                    </Flex>
                    
                    {showDiff ? (
                      <Box
                        borderWidth="1px"
                        borderRadius="md"
                        borderColor={borderColor}
                        overflow="hidden"
                      >
                        <ReactDiffViewer
                          oldValue={selectedVersions.find(v => v.version === selectedBelief.version - 1)?.content || ''}
                          newValue={selectedBelief.content}
                          splitView={false}
                          disableWordDiff={false}
                          showDiffOnly={false}
                          styles={{
                            contentText: {
                              fontSize: '14px',
                            },
                          }}
                        />
                      </Box>
                    ) : (
                      <Box
                        p={3}
                        borderWidth="1px"
                        borderRadius="md"
                        borderColor={borderColor}
                        bg={diffBgColor}
                      >
                        <Text>Previous version:</Text>
                        <Text mt={2}>{selectedVersions.find(v => v.version === selectedBelief.version - 1)?.content || ''}</Text>
                      </Box>
                    )}
                  </Box>
                )}
                
                {/* Version navigation */}
                {selectedVersions.length > 1 && (
                  <Flex justify="space-between" mt={2}>
                    <Button
                      leftIcon={<FiArrowLeft />}
                      size="sm"
                      isDisabled={selectedBelief.version === 1}
                      onClick={() => {
                        const prevVersion = selectedVersions.find(v => v.version === selectedBelief.version - 1);
                        if (prevVersion) setSelectedBelief(prevVersion);
                      }}
                    >
                      Previous Version
                    </Button>
                    
                    <Button
                      rightIcon={<FiArrowRight />}
                      size="sm"
                      isDisabled={selectedBelief.version === Math.max(...selectedVersions.map(v => v.version))}
                      onClick={() => {
                        const nextVersion = selectedVersions.find(v => v.version === selectedBelief.version + 1);
                        if (nextVersion) setSelectedBelief(nextVersion);
                      }}
                    >
                      Next Version
                    </Button>
                  </Flex>
                )}
              </VStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            {selectedBelief && selectedBelief.version > 1 && (
              <Button
                leftIcon={<FiRotateCcw />}
                colorScheme="blue"
                mr={3}
                onClick={() => {
                  handleRollback(selectedBelief);
                  onClose();
                }}
              >
                Rollback to this Version
              </Button>
            )}
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Legend */}
      <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg={panelBgColor}>
        <Heading size="xs" mb={2}>Legend</Heading>
        <Flex wrap="wrap" gap={4}>
          <HStack>
            <Badge colorScheme="green">Added</Badge>
            <Text fontSize="sm">New belief</Text>
          </HStack>
          
          <HStack>
            <Badge colorScheme="blue">Modified</Badge>
            <Text fontSize="sm">Updated belief</Text>
          </HStack>
          
          <HStack>
            <Badge colorScheme="red">Deprecated</Badge>
            <Text fontSize="sm">Removed belief</Text>
          </HStack>
          
          <HStack>
            <FiRotateCcw />
            <Text fontSize="sm">Rollback option</Text>
          </HStack>
        </Flex>
      </Box>
    </Box>
  );
};

export default BeliefChangeLog;
