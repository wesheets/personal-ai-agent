import React, { useState, useEffect, useRef } from 'react';
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
  Collapse,
  Divider,
  Tooltip,
  Heading,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiChevronDown, 
  FiChevronRight, 
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
  FiInfo
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';
import ReflectionHistoryPanel from './ReflectionHistoryPanel';

/**
 * LoopTraceViewer Component
 * 
 * A visual tree or timeline showing the progression of loops,
 * including agent delegations, summaries, and reflections.
 */
const LoopTraceViewer = ({ loopId, projectId }) => {
  const [expandedNodes, setExpandedNodes] = useState({});
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [viewMode, setViewMode] = useState('tree'); // 'tree' or 'timeline'
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const containerRef = useRef(null);
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const nodeBgColor = useColorModeValue('gray.50', 'gray.600');
  const selectedNodeBgColor = useColorModeValue('blue.50', 'blue.900');
  const selectedNodeBorderColor = useColorModeValue('blue.500', 'blue.400');
  const connectorColor = useColorModeValue('gray.300', 'gray.500');
  
  // Fetch loop trace data
  const { 
    data: loopTrace, 
    error: loopError, 
    loading: loopLoading,
    refetch: refetchLoopTrace
  } = useFetch(
    `/api/loop/trace?${loopId ? `loop_id=${loopId}` : `project_id=${projectId || ''}`}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: null,
      transformResponse: (data) => {
        // Process the loop trace data if needed
        return data;
      }
    }
  );
  
  // Toggle node expansion
  const toggleNode = (nodeId) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodeId]: !prev[nodeId]
    }));
  };
  
  // Select a node to view details
  const selectNode = (node) => {
    setSelectedNode(node);
    onOpen();
  };
  
  // Zoom in/out
  const handleZoom = (direction) => {
    setZoomLevel(prev => {
      const newZoom = direction === 'in' ? prev + 0.25 : prev - 0.25;
      return Math.max(0.5, Math.min(2, newZoom));
    });
  };
  
  // Toggle view mode between tree and timeline
  const toggleViewMode = () => {
    setViewMode(prev => prev === 'tree' ? 'timeline' : 'tree');
  };
  
  // Export loop trace as JSON
  const exportLoopTrace = () => {
    if (!loopTrace) return;
    
    try {
      const dataStr = JSON.stringify(loopTrace, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
      
      const exportFileDefaultName = `loop-trace-${loopId || 'project'}-${new Date().toISOString().slice(0, 10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      toast({
        title: 'Loop trace exported',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      console.error('Error exporting loop trace:', err);
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
  
  // Get node type color
  const getNodeTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'reflection':
        return 'blue';
      case 'plan':
        return 'green';
      case 'summary':
        return 'purple';
      case 'delegation':
        return 'orange';
      case 'execution':
        return 'cyan';
      default:
        return 'gray';
    }
  };
  
  // Mock data for development/testing
  const mockLoopTrace = {
    loop_id: loopId || 'loop-123',
    project_id: projectId || 'project-456',
    start_time: new Date(Date.now() - 3600000).toISOString(),
    end_time: new Date().toISOString(),
    status: 'completed',
    root: {
      id: 'node-1',
      type: 'plan',
      agent: 'ORCHESTRATOR',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      content: 'Initial plan for implementing the Memory Query Console and Reflection Trace Viewer',
      children: [
        {
          id: 'node-2',
          type: 'delegation',
          agent: 'ORCHESTRATOR',
          timestamp: new Date(Date.now() - 3500000).toISOString(),
          content: 'Delegating memory query implementation to SAGE',
          target_agent: 'SAGE',
          children: [
            {
              id: 'node-3',
              type: 'plan',
              agent: 'SAGE',
              timestamp: new Date(Date.now() - 3400000).toISOString(),
              content: 'Planning approach for natural language memory query system',
              children: [
                {
                  id: 'node-4',
                  type: 'execution',
                  agent: 'SAGE',
                  timestamp: new Date(Date.now() - 3300000).toISOString(),
                  content: 'Implementing memory query parser and retrieval system',
                  children: []
                },
                {
                  id: 'node-5',
                  type: 'reflection',
                  agent: 'SAGE',
                  timestamp: new Date(Date.now() - 3200000).toISOString(),
                  content: 'The current implementation may not handle complex queries efficiently. Consider adding vector-based semantic search capabilities.',
                  children: []
                }
              ]
            },
            {
              id: 'node-6',
              type: 'summary',
              agent: 'SAGE',
              timestamp: new Date(Date.now() - 3100000).toISOString(),
              content: 'Completed memory query implementation with basic natural language parsing and schema-based filtering.',
              children: []
            }
          ]
        },
        {
          id: 'node-7',
          type: 'delegation',
          agent: 'ORCHESTRATOR',
          timestamp: new Date(Date.now() - 3000000).toISOString(),
          content: 'Delegating loop trace visualization to SKEPTIC for review',
          target_agent: 'SKEPTIC',
          children: [
            {
              id: 'node-8',
              type: 'reflection',
              agent: 'SKEPTIC',
              timestamp: new Date(Date.now() - 2900000).toISOString(),
              content: 'The proposed visualization approach may not scale well for deeply nested loops. Consider implementing collapsible nodes and pagination.',
              children: []
            }
          ]
        },
        {
          id: 'node-9',
          type: 'summary',
          agent: 'ORCHESTRATOR',
          timestamp: new Date(Date.now() - 2800000).toISOString(),
          content: 'Integration of Memory Query Console and Loop Trace Viewer completed with improvements based on SKEPTIC feedback.',
          children: []
        }
      ]
    }
  };
  
  // Use mock data if no real data is available
  const displayData = loopTrace || mockLoopTrace;
  
  // Render a node in the tree view
  const renderTreeNode = (node, level = 0) => {
    if (!node) return null;
    
    const isExpanded = expandedNodes[node.id] !== false; // Default to expanded
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedNode && selectedNode.id === node.id;
    
    return (
      <Box key={node.id} ml={level > 0 ? 6 : 0} position="relative">
        {/* Connector lines */}
        {level > 0 && (
          <>
            <Box
              position="absolute"
              left="-24px"
              top="0"
              bottom="0"
              width="24px"
              height="16px"
              borderLeft="2px solid"
              borderBottom="2px solid"
              borderColor={connectorColor}
            />
          </>
        )}
        
        {/* Node */}
        <Box
          mb={3}
          borderWidth="1px"
          borderRadius="md"
          borderColor={isSelected ? selectedNodeBorderColor : borderColor}
          bg={isSelected ? selectedNodeBgColor : nodeBgColor}
          overflow="hidden"
          transition="all 0.2s"
          _hover={{
            borderColor: 'blue.300',
            boxShadow: 'sm'
          }}
        >
          {/* Node header */}
          <Flex
            p={3}
            align="center"
            justify="space-between"
            borderBottomWidth={isExpanded && hasChildren ? "1px" : "0"}
            borderColor={borderColor}
            cursor="pointer"
            onClick={() => hasChildren && toggleNode(node.id)}
          >
            <HStack spacing={2}>
              {hasChildren && (
                <Box color="gray.500">
                  {isExpanded ? <FiChevronDown /> : <FiChevronRight />}
                </Box>
              )}
              
              <Badge colorScheme={getAgentColor(node.agent)}>
                {node.agent}
              </Badge>
              
              <Badge colorScheme={getNodeTypeColor(node.type)}>
                {node.type}
              </Badge>
              
              {node.target_agent && (
                <Badge variant="outline" colorScheme={getAgentColor(node.target_agent)}>
                  → {node.target_agent}
                </Badge>
              )}
            </HStack>
            
            <HStack spacing={2}>
              <Text fontSize="xs" color="gray.500">
                {formatTimestamp(node.timestamp)}
              </Text>
              
              <Menu>
                <MenuButton
                  as={IconButton}
                  icon={<FiMoreVertical />}
                  variant="ghost"
                  size="xs"
                  aria-label="More options"
                  onClick={(e) => e.stopPropagation()}
                />
                <MenuList>
                  <MenuItem onClick={() => selectNode(node)}>View Details</MenuItem>
                  {node.type === 'reflection' && (
                    <MenuItem onClick={() => selectNode(node)}>View Reflection History</MenuItem>
                  )}
                  <MenuItem onClick={() => navigator.clipboard.writeText(node.content)}>Copy Content</MenuItem>
                </MenuList>
              </Menu>
            </HStack>
          </Flex>
          
          {/* Node content */}
          <Collapse in={isExpanded} animateOpacity>
            <Box p={3}>
              <Text noOfLines={3}>{node.content}</Text>
              
              {/* View more button */}
              {node.content && node.content.length > 150 && (
                <Button
                  size="xs"
                  variant="link"
                  mt={1}
                  onClick={() => selectNode(node)}
                >
                  View more
                </Button>
              )}
            </Box>
          </Collapse>
        </Box>
        
        {/* Children */}
        <Collapse in={isExpanded} animateOpacity>
          {hasChildren && node.children.map(child => renderTreeNode(child, level + 1))}
        </Collapse>
      </Box>
    );
  };
  
  // Render timeline view
  const renderTimeline = () => {
    // Flatten the tree into a chronological list
    const flattenTree = (node, result = []) => {
      if (!node) return result;
      
      result.push(node);
      
      if (node.children && node.children.length > 0) {
        node.children.forEach(child => flattenTree(child, result));
      }
      
      return result;
    };
    
    const timelineNodes = flattenTree(displayData.root).sort((a, b) => {
      return new Date(a.timestamp) - new Date(b.timestamp);
    });
    
    return (
      <Box position="relative">
        {/* Timeline line */}
        <Box
          position="absolute"
          left="16px"
          top="0"
          bottom="0"
          width="2px"
          bg={connectorColor}
        />
        
        {/* Timeline nodes */}
        <VStack spacing={4} align="stretch" ml={10}>
          {timelineNodes.map(node => (
            <Box
              key={node.id}
              position="relative"
              borderWidth="1px"
              borderRadius="md"
              borderColor={selectedNode && selectedNode.id === node.id ? selectedNodeBorderColor : borderColor}
              bg={selectedNode && selectedNode.id === node.id ? selectedNodeBgColor : nodeBgColor}
              p={3}
              _hover={{
                borderColor: 'blue.300',
                boxShadow: 'sm'
              }}
              transition="all 0.2s"
            >
              {/* Timeline node marker */}
              <Box
                position="absolute"
                left="-22px"
                top="50%"
                transform="translateY(-50%)"
                width="12px"
                height="12px"
                borderRadius="full"
                bg={getAgentColor(node.agent)}
                borderWidth="2px"
                borderColor="white"
                zIndex="1"
              />
              
              {/* Timeline connector */}
              <Box
                position="absolute"
                left="-16px"
                top="50%"
                width="16px"
                height="2px"
                bg={connectorColor}
              />
              
              {/* Node content */}
              <Flex justify="space-between" mb={2}>
                <HStack spacing={2}>
                  <Badge colorScheme={getAgentColor(node.agent)}>
                    {node.agent}
                  </Badge>
                  
                  <Badge colorScheme={getNodeTypeColor(node.type)}>
                    {node.type}
                  </Badge>
                  
                  {node.target_agent && (
                    <Badge variant="outline" colorScheme={getAgentColor(node.target_agent)}>
                      → {node.target_agent}
                    </Badge>
                  )}
                </HStack>
                
                <HStack spacing={2}>
                  <Text fontSize="xs" color="gray.500">
                    {formatTimestamp(node.timestamp)}
                  </Text>
                  
                  <IconButton
                    icon={<FiInfo />}
                    variant="ghost"
                    size="xs"
                    aria-label="View details"
                    onClick={() => selectNode(node)}
                  />
                </HStack>
              </Flex>
              
              <Text noOfLines={2}>{node.content}</Text>
            </Box>
          ))}
        </VStack>
      </Box>
    );
  };
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">
          Loop Trace {loopId ? `#${loopId}` : 'Viewer'}
        </Heading>
        
        <HStack spacing={2}>
          <Tooltip label="Refresh">
            <IconButton
              icon={<FiRefreshCw />}
              size="sm"
              variant="ghost"
              aria-label="Refresh"
              onClick={refetchLoopTrace}
              isLoading={loopLoading}
            />
          </Tooltip>
          
          <Tooltip label="Zoom In">
            <IconButton
              icon={<FiZoomIn />}
              size="sm"
              variant="ghost"
              aria-label="Zoom in"
              onClick={() => handleZoom('in')}
              isDisabled={zoomLevel >= 2}
            />
          </Tooltip>
          
          <Tooltip label="Zoom Out">
            <IconButton
              icon={<FiZoomOut />}
              size="sm"
              variant="ghost"
              aria-label="Zoom out"
              onClick={() => handleZoom('out')}
              isDisabled={zoomLevel <= 0.5}
            />
          </Tooltip>
          
          <Tooltip label={viewMode === 'tree' ? 'Switch to Timeline View' : 'Switch to Tree View'}>
            <IconButton
              icon={viewMode === 'tree' ? <FiMaximize2 /> : <FiMinimize2 />}
              size="sm"
              variant="ghost"
              aria-label="Toggle view mode"
              onClick={toggleViewMode}
            />
          </Tooltip>
          
          <Tooltip label="Export Loop Trace">
            <IconButton
              icon={<FiDownload />}
              size="sm"
              variant="ghost"
              aria-label="Export"
              onClick={exportLoopTrace}
              isDisabled={!displayData}
            />
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Loop info */}
      {displayData && (
        <Box
          p={3}
          mb={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          bg={bgColor}
        >
          <Flex wrap="wrap" gap={2} justify="space-between">
            <HStack spacing={3}>
              <VStack align="flex-start" spacing={0}>
                <Text fontSize="xs" color="gray.500">Loop ID</Text>
                <Text fontWeight="medium">{displayData.loop_id}</Text>
              </VStack>
              
              <VStack align="flex-start" spacing={0}>
                <Text fontSize="xs" color="gray.500">Project</Text>
                <Text fontWeight="medium">{displayData.project_id}</Text>
              </VStack>
              
              <VStack align="flex-start" spacing={0}>
                <Text fontSize="xs" color="gray.500">Status</Text>
                <Badge colorScheme={displayData.status === 'completed' ? 'green' : 'blue'}>
                  {displayData.status}
                </Badge>
              </VStack>
            </HStack>
            
            <HStack spacing={3}>
              <VStack align="flex-start" spacing={0}>
                <Text fontSize="xs" color="gray.500">Started</Text>
                <Text fontSize="sm">{formatTimestamp(displayData.start_time)}</Text>
              </VStack>
              
              <VStack align="flex-start" spacing={0}>
                <Text fontSize="xs" color="gray.500">Ended</Text>
                <Text fontSize="sm">{formatTimestamp(displayData.end_time)}</Text>
              </VStack>
            </HStack>
          </Flex>
        </Box>
      )}
      
      {/* Loading state */}
      {loopLoading && (
        <Flex justify="center" align="center" height="300px">
          <Spinner size="xl" />
        </Flex>
      )}
      
      {/* Error state */}
      {loopError && (
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor="red.300"
          bg="red.50"
          color="red.800"
        >
          <Heading size="sm" mb={2}>Error Loading Loop Trace</Heading>
          <Text>{loopError}</Text>
        </Box>
      )}
      
      {/* Loop trace visualization */}
      {!loopLoading && displayData && (
        <Box
          ref={containerRef}
          overflowX="auto"
          overflowY="auto"
          maxH="600px"
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          bg={bgColor}
          transform={`scale(${zoomLevel})`}
          transformOrigin="top left"
          transition="transform 0.2s"
        >
          {viewMode === 'tree' ? renderTreeNode(displayData.root) : renderTimeline()}
        </Box>
      )}
      
      {/* Node details drawer */}
      <Drawer isOpen={isOpen} placement="right" onClose={onClose} size="md">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>
            <HStack spacing={2}>
              {selectedNode && (
                <>
                  <Badge colorScheme={getAgentColor(selectedNode.agent)}>
                    {selectedNode.agent}
                  </Badge>
                  
                  <Badge colorScheme={getNodeTypeColor(selectedNode.type)}>
                    {selectedNode.type}
                  </Badge>
                </>
              )}
            </HStack>
          </DrawerHeader>
          
          <DrawerBody>
            {selectedNode && (
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="medium" mb={1}>Timestamp</Text>
                  <Text>{formatTimestamp(selectedNode.timestamp)}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="medium" mb={1}>Content</Text>
                  <Box
                    p={3}
                    borderWidth="1px"
                    borderRadius="md"
                    borderColor={borderColor}
                    bg={nodeBgColor}
                  >
                    <Text whiteSpace="pre-wrap">{selectedNode.content}</Text>
                  </Box>
                </Box>
                
                {selectedNode.target_agent && (
                  <Box>
                    <Text fontWeight="medium" mb={1}>Delegated To</Text>
                    <Badge colorScheme={getAgentColor(selectedNode.target_agent)}>
                      {selectedNode.target_agent}
                    </Badge>
                  </Box>
                )}
                
                {selectedNode.type === 'reflection' && (
                  <Box>
                    <Divider my={4} />
                    <Heading size="sm" mb={4}>Reflection History</Heading>
                    <ReflectionHistoryPanel 
                      loopId={displayData.loop_id} 
                      nodeId={selectedNode.id}
                      inDrawer={true}
                    />
                  </Box>
                )}
              </VStack>
            )}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default LoopTraceViewer;
