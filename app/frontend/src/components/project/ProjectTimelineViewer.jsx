import React, { useState, useRef, useEffect } from 'react';
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
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  Select,
  Switch,
  FormControl,
  FormLabel
} from '@chakra-ui/react';
import { 
  FiClock, 
  FiUser, 
  FiTag, 
  FiMaximize2, 
  FiMinimize2,
  FiMoreVertical,
  FiDownload,
  FiShare2,
  FiZoomIn,
  FiZoomOut,
  FiRefreshCw,
  FiInfo,
  FiArrowRight,
  FiGitBranch,
  FiGitMerge,
  FiGitCommit,
  FiFilter,
  FiCalendar
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';

/**
 * ProjectTimelineViewer Component
 * 
 * A vertical or horizontal scrollable timeline showing the evolution of cognition,
 * with each node representing a loop and displaying agents involved, summary titles,
 * trust scores, and confidence/drift markers.
 */
const ProjectTimelineViewer = ({ projectId, onLoopSelect }) => {
  const [orientation, setOrientation] = useState('vertical'); // 'vertical' or 'horizontal'
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedLoop, setSelectedLoop] = useState(null);
  const [timeRange, setTimeRange] = useState('all'); // 'all', 'day', 'week', 'month'
  const [agentFilter, setAgentFilter] = useState('all');
  const [showForks, setShowForks] = useState(true);
  
  const toast = useToast();
  const containerRef = useRef(null);
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const nodeBgColor = useColorModeValue('gray.50', 'gray.600');
  const selectedNodeBgColor = useColorModeValue('blue.50', 'blue.900');
  const selectedNodeBorderColor = useColorModeValue('blue.500', 'blue.400');
  const connectorColor = useColorModeValue('gray.300', 'gray.500');
  const timelineBgColor = useColorModeValue('gray.100', 'gray.800');
  
  // Fetch project timeline data
  const { 
    data: timelineData, 
    error: timelineError, 
    loading: timelineLoading,
    refetch: refetchTimeline
  } = useFetch(
    `/api/project/timeline?project_id=${projectId || ''}&time_range=${timeRange}&agent=${agentFilter}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: null
    }
  );
  
  // Handle loop selection
  const handleLoopSelect = (loop) => {
    setSelectedLoop(loop);
    if (onLoopSelect) {
      onLoopSelect(loop.loop_id);
    }
  };
  
  // Zoom in/out
  const handleZoom = (direction) => {
    setZoomLevel(prev => {
      const newZoom = direction === 'in' ? prev + 0.25 : prev - 0.25;
      return Math.max(0.5, Math.min(2, newZoom));
    });
  };
  
  // Toggle orientation between vertical and horizontal
  const toggleOrientation = () => {
    setOrientation(prev => prev === 'vertical' ? 'horizontal' : 'vertical');
  };
  
  // Export timeline as JSON
  const exportTimeline = () => {
    if (!timelineData) return;
    
    try {
      const dataStr = JSON.stringify(timelineData, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
      
      const exportFileDefaultName = `project-timeline-${projectId || 'unknown'}-${new Date().toISOString().slice(0, 10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      toast({
        title: 'Timeline exported',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      console.error('Error exporting timeline:', err);
      toast({
        title: 'Export failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
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
  
  // Get trust score color
  const getTrustScoreColor = (score) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'teal';
    if (score >= 0.4) return 'yellow';
    if (score >= 0.2) return 'orange';
    return 'red';
  };
  
  // Get drift index color
  const getDriftIndexColor = (index) => {
    if (index <= 0.2) return 'green';
    if (index <= 0.4) return 'teal';
    if (index <= 0.6) return 'yellow';
    if (index <= 0.8) return 'orange';
    return 'red';
  };
  
  // Truncate summary text
  const truncateSummary = (text, wordCount = 15) => {
    if (!text) return '';
    const words = text.split(' ');
    if (words.length <= wordCount) return text;
    return words.slice(0, wordCount).join(' ') + '...';
  };
  
  // Mock data for development/testing
  const mockTimelineData = {
    project_id: projectId || 'project-123',
    loops: [
      {
        loop_id: 'loop-001',
        timestamp: new Date(Date.now() - 86400000 * 7).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Initial project setup and requirements analysis for the cognitive system',
        trust_score: 0.95,
        drift_index: 0.05,
        fork_parent: null
      },
      {
        loop_id: 'loop-002',
        timestamp: new Date(Date.now() - 86400000 * 6).toISOString(),
        agent: 'SAGE',
        summary: 'Developing core memory architecture and schema definitions',
        trust_score: 0.92,
        drift_index: 0.08,
        fork_parent: null
      },
      {
        loop_id: 'loop-003',
        timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
        agent: 'SKEPTIC',
        summary: 'Reviewing memory architecture for potential failure modes and edge cases',
        trust_score: 0.85,
        drift_index: 0.15,
        fork_parent: null
      },
      {
        loop_id: 'loop-004',
        timestamp: new Date(Date.now() - 86400000 * 4).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Integrating memory system with cognitive loop execution framework',
        trust_score: 0.88,
        drift_index: 0.12,
        fork_parent: null
      },
      {
        loop_id: 'loop-005a',
        timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
        agent: 'SAGE',
        summary: 'Implementing natural language query capabilities for memory retrieval',
        trust_score: 0.78,
        drift_index: 0.22,
        fork_parent: 'loop-004'
      },
      {
        loop_id: 'loop-005b',
        timestamp: new Date(Date.now() - 86400000 * 3 + 3600000).toISOString(),
        agent: 'SAGE',
        summary: 'Exploring vector-based semantic search as alternative to natural language parsing',
        trust_score: 0.82,
        drift_index: 0.18,
        fork_parent: 'loop-004'
      },
      {
        loop_id: 'loop-006',
        timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Merging natural language and vector-based approaches for hybrid memory query system',
        trust_score: 0.91,
        drift_index: 0.09,
        fork_parent: null
      },
      {
        loop_id: 'loop-007',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        agent: 'OPERATOR',
        summary: 'Testing memory query system with real-world scenarios and providing feedback',
        trust_score: 0.94,
        drift_index: 0.06,
        fork_parent: null
      },
      {
        loop_id: 'loop-008',
        timestamp: new Date().toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Finalizing memory system implementation and preparing for deployment',
        trust_score: 0.89,
        drift_index: 0.11,
        fork_parent: null
      }
    ]
  };
  
  // Use mock data if no real data is available
  const displayData = timelineData || mockTimelineData;
  
  // Filter loops based on current filters
  const filteredLoops = displayData.loops
    .filter(loop => {
      // Filter by agent if not 'all'
      if (agentFilter !== 'all' && loop.agent !== agentFilter) {
        return false;
      }
      
      // Filter out forks if showForks is false
      if (!showForks && loop.fork_parent) {
        return false;
      }
      
      // Filter by time range
      if (timeRange !== 'all') {
        const loopDate = new Date(loop.timestamp);
        const now = new Date();
        
        if (timeRange === 'day' && (now - loopDate > 86400000)) {
          return false;
        } else if (timeRange === 'week' && (now - loopDate > 86400000 * 7)) {
          return false;
        } else if (timeRange === 'month' && (now - loopDate > 86400000 * 30)) {
          return false;
        }
      }
      
      return true;
    })
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  
  // Render vertical timeline
  const renderVerticalTimeline = () => {
    return (
      <Box position="relative" pl={10} pr={4} py={4}>
        {/* Timeline line */}
        <Box
          position="absolute"
          left="20px"
          top="0"
          bottom="0"
          width="2px"
          bg={connectorColor}
        />
        
        {/* Timeline nodes */}
        <VStack spacing={4} align="stretch">
          {filteredLoops.map((loop, index) => {
            const isFork = !!loop.fork_parent;
            const isSelected = selectedLoop && selectedLoop.loop_id === loop.loop_id;
            
            return (
              <Box
                key={loop.loop_id}
                position="relative"
                borderWidth="1px"
                borderRadius="md"
                borderColor={isSelected ? selectedNodeBorderColor : isFork ? 'orange.300' : borderColor}
                bg={isSelected ? selectedNodeBgColor : nodeBgColor}
                p={3}
                ml={isFork ? 8 : 0}
                _hover={{
                  borderColor: 'blue.300',
                  boxShadow: 'sm'
                }}
                transition="all 0.2s"
                cursor="pointer"
                onClick={() => handleLoopSelect(loop)}
                transform={`scale(${zoomLevel})`}
                transformOrigin="left center"
              >
                {/* Timeline node marker */}
                <Box
                  position="absolute"
                  left="-16px"
                  top="50%"
                  transform="translateY(-50%)"
                  width="12px"
                  height="12px"
                  borderRadius="full"
                  bg={getAgentColor(loop.agent)}
                  borderWidth="2px"
                  borderColor="white"
                  zIndex="1"
                />
                
                {/* Fork connector */}
                {isFork && (
                  <Box
                    position="absolute"
                    left="-16px"
                    top="50%"
                    width="8px"
                    height="2px"
                    bg={connectorColor}
                  />
                )}
                
                {/* Fork indicator */}
                {isFork && (
                  <Box
                    position="absolute"
                    left="-24px"
                    top="50%"
                    transform="translateY(-50%)"
                    color="orange.500"
                  >
                    <FiGitBranch />
                  </Box>
                )}
                
                {/* Node header */}
                <Flex justify="space-between" mb={2}>
                  <HStack spacing={2}>
                    <Badge colorScheme={getAgentColor(loop.agent)}>
                      {loop.agent}
                    </Badge>
                    
                    <Badge colorScheme={getTrustScoreColor(loop.trust_score)}>
                      Trust: {loop.trust_score.toFixed(2)}
                    </Badge>
                    
                    <Badge colorScheme={getDriftIndexColor(loop.drift_index)}>
                      Drift: {loop.drift_index.toFixed(2)}
                    </Badge>
                  </HStack>
                  
                  <Text fontSize="xs" color="gray.500">
                    {formatRelativeTime(loop.timestamp)}
                  </Text>
                </Flex>
                
                {/* Node content */}
                <Text fontWeight="medium" mb={1}>
                  {truncateSummary(loop.summary)}
                </Text>
                
                <Flex justify="space-between" align="center" mt={2}>
                  <Text fontSize="xs" color="gray.500">
                    Loop #{loop.loop_id}
                  </Text>
                  
                  <HStack>
                    <Tooltip label="View Loop Trace">
                      <IconButton
                        icon={<FiArrowRight />}
                        size="xs"
                        variant="ghost"
                        aria-label="View Loop Trace"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLoopSelect(loop);
                        }}
                      />
                    </Tooltip>
                  </HStack>
                </Flex>
              </Box>
            );
          })}
        </VStack>
      </Box>
    );
  };
  
  // Render horizontal timeline
  const renderHorizontalTimeline = () => {
    return (
      <Box position="relative" pt={10} pb={4} overflowX="auto">
        {/* Timeline line */}
        <Box
          position="absolute"
          left="0"
          right="0"
          top="20px"
          height="2px"
          bg={connectorColor}
        />
        
        {/* Timeline nodes */}
        <Flex>
          {filteredLoops.map((loop, index) => {
            const isFork = !!loop.fork_parent;
            const isSelected = selectedLoop && selectedLoop.loop_id === loop.loop_id;
            
            return (
              <Box
                key={loop.loop_id}
                position="relative"
                borderWidth="1px"
                borderRadius="md"
                borderColor={isSelected ? selectedNodeBorderColor : isFork ? 'orange.300' : borderColor}
                bg={isSelected ? selectedNodeBgColor : nodeBgColor}
                p={3}
                mx={2}
                mt={isFork ? 8 : 0}
                minWidth="250px"
                maxWidth="250px"
                _hover={{
                  borderColor: 'blue.300',
                  boxShadow: 'sm'
                }}
                transition="all 0.2s"
                cursor="pointer"
                onClick={() => handleLoopSelect(loop)}
                transform={`scale(${zoomLevel})`}
                transformOrigin="center top"
              >
                {/* Timeline node marker */}
                <Box
                  position="absolute"
                  left="50%"
                  top="-16px"
                  transform="translateX(-50%)"
                  width="12px"
                  height="12px"
                  borderRadius="full"
                  bg={getAgentColor(loop.agent)}
                  borderWidth="2px"
                  borderColor="white"
                  zIndex="1"
                />
                
                {/* Fork connector */}
                {isFork && (
                  <Box
                    position="absolute"
                    left="50%"
                    top="-16px"
                    height="8px"
                    width="2px"
                    bg={connectorColor}
                  />
                )}
                
                {/* Fork indicator */}
                {isFork && (
                  <Box
                    position="absolute"
                    left="50%"
                    top="-24px"
                    transform="translateX(-50%)"
                    color="orange.500"
                  >
                    <FiGitBranch />
                  </Box>
                )}
                
                {/* Node header */}
                <Flex justify="space-between" mb={2}>
                  <Badge colorScheme={getAgentColor(loop.agent)}>
                    {loop.agent}
                  </Badge>
                  
                  <Text fontSize="xs" color="gray.500">
                    {formatRelativeTime(loop.timestamp)}
                  </Text>
                </Flex>
                
                {/* Node content */}
                <Text fontWeight="medium" mb={1} noOfLines={2}>
                  {truncateSummary(loop.summary, 10)}
                </Text>
                
                <HStack spacing={1} mt={2}>
                  <Badge colorScheme={getTrustScoreColor(loop.trust_score)}>
                    Trust: {loop.trust_score.toFixed(2)}
                  </Badge>
                  
                  <Badge colorScheme={getDriftIndexColor(loop.drift_index)}>
                    Drift: {loop.drift_index.toFixed(2)}
                  </Badge>
                </HStack>
                
                <Flex justify="space-between" align="center" mt={2}>
                  <Text fontSize="xs" color="gray.500">
                    #{loop.loop_id}
                  </Text>
                  
                  <Tooltip label="View Loop Trace">
                    <IconButton
                      icon={<FiArrowRight />}
                      size="xs"
                      variant="ghost"
                      aria-label="View Loop Trace"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLoopSelect(loop);
                      }}
                    />
                  </Tooltip>
                </Flex>
              </Box>
            );
          })}
        </Flex>
      </Box>
    );
  };
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">Project Timeline</Heading>
        
        <HStack spacing={2}>
          <Tooltip label="Refresh timeline">
            <IconButton
              icon={<FiRefreshCw />}
              size="sm"
              aria-label="Refresh timeline"
              onClick={() => refetchTimeline()}
              isLoading={timelineLoading}
            />
          </Tooltip>
          
          <Tooltip label="Export timeline">
            <IconButton
              icon={<FiDownload />}
              size="sm"
              aria-label="Export timeline"
              onClick={exportTimeline}
            />
          </Tooltip>
          
          <Tooltip label={orientation === 'vertical' ? 'Switch to horizontal' : 'Switch to vertical'}>
            <IconButton
              icon={orientation === 'vertical' ? <FiMaximize2 /> : <FiMinimize2 />}
              size="sm"
              aria-label="Toggle orientation"
              onClick={toggleOrientation}
            />
          </Tooltip>
          
          <Tooltip label="Zoom in">
            <IconButton
              icon={<FiZoomIn />}
              size="sm"
              aria-label="Zoom in"
              onClick={() => handleZoom('in')}
              isDisabled={zoomLevel >= 2}
            />
          </Tooltip>
          
          <Tooltip label="Zoom out">
            <IconButton
              icon={<FiZoomOut />}
              size="sm"
              aria-label="Zoom out"
              onClick={() => handleZoom('out')}
              isDisabled={zoomLevel <= 0.5}
            />
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Filters */}
      <Box mb={4} p={3} borderWidth="1px" borderRadius="md" bg={timelineBgColor}>
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
            <FormLabel htmlFor="show-forks" mb="0" fontSize="sm">
              Show Forks:
            </FormLabel>
            <Switch
              id="show-forks"
              isChecked={showForks}
              onChange={(e) => setShowForks(e.target.checked)}
            />
          </FormControl>
        </Flex>
      </Box>
      
      {/* Timeline content */}
      <Box
        ref={containerRef}
        borderWidth="1px"
        borderRadius="md"
        borderColor={borderColor}
        bg={bgColor}
        height="calc(100vh - 250px)"
        overflowY={orientation === 'vertical' ? 'auto' : 'hidden'}
        overflowX={orientation === 'horizontal' ? 'auto' : 'hidden'}
      >
        {timelineLoading ? (
          <Flex justify="center" align="center" height="100%">
            <Spinner size="xl" thickness="4px" speed="0.65s" color="blue.500" />
          </Flex>
        ) : timelineError ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" color="red.500" mb={2}>Error Loading Timeline</Heading>
            <Text>{timelineError.message || 'Failed to load project timeline'}</Text>
            <Button mt={4} onClick={() => refetchTimeline()}>
              Try Again
            </Button>
          </Flex>
        ) : filteredLoops.length === 0 ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" mb={2}>No Loops Found</Heading>
            <Text>No loops match the current filters.</Text>
          </Flex>
        ) : orientation === 'vertical' ? (
          renderVerticalTimeline()
        ) : (
          renderHorizontalTimeline()
        )}
      </Box>
      
      {/* Legend */}
      <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg={timelineBgColor}>
        <Heading size="xs" mb={2}>Legend</Heading>
        <Flex wrap="wrap" gap={4}>
          <HStack>
            <FiUser />
            <Text fontSize="sm">Agent Color</Text>
          </HStack>
          
          <HStack>
            <FiGitBranch color="orange" />
            <Text fontSize="sm">Fork</Text>
          </HStack>
          
          <HStack>
            <Badge colorScheme="green">Trust: 0.90+</Badge>
            <Text fontSize="sm">High Trust</Text>
          </HStack>
          
          <HStack>
            <Badge colorScheme="red">Drift: 0.80+</Badge>
            <Text fontSize="sm">High Drift</Text>
          </HStack>
        </Flex>
      </Box>
    </Box>
  );
};

export default ProjectTimelineViewer;
