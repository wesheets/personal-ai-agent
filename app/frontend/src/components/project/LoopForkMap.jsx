import React, { useState, useEffect, useCallback } from 'react';
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
  Menu,
  MenuButton,
  MenuList,
  MenuItem
} from '@chakra-ui/react';
import { 
  FiGitBranch, 
  FiGitMerge, 
  FiGitCommit,
  FiRefreshCw,
  FiDownload,
  FiZoomIn,
  FiZoomOut,
  FiMaximize2,
  FiMinimize2,
  FiFilter,
  FiInfo,
  FiArrowRight,
  FiCheck,
  FiX,
  FiMoreVertical
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

// Custom node component for loop nodes
const LoopNode = ({ data }) => {
  const nodeBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  return (
    <Box
      padding={2}
      borderWidth="1px"
      borderRadius="md"
      borderColor={data.isMerged ? 'purple.400' : data.isSkipped ? 'gray.400' : data.isFork ? 'orange.400' : borderColor}
      bg={nodeBgColor}
      width="250px"
      boxShadow="sm"
    >
      <Flex justify="space-between" align="center" mb={1}>
        <HStack>
          <Badge colorScheme={data.agentColor}>{data.agent}</Badge>
          {data.isFork && <FiGitBranch color="orange" />}
          {data.isMerged && <FiGitMerge color="purple" />}
          {data.isSkipped && <FiX color="gray" />}
        </HStack>
        <Text fontSize="xs" color="gray.500">{data.relativeTime}</Text>
      </Flex>
      
      <Text fontWeight="medium" fontSize="sm" mb={1} noOfLines={2}>
        {data.summary}
      </Text>
      
      <HStack spacing={1} mt={1}>
        <Badge colorScheme={data.trustScoreColor}>
          Trust: {data.trustScore.toFixed(2)}
        </Badge>
        <Badge colorScheme={data.driftIndexColor}>
          Drift: {data.driftIndex.toFixed(2)}
        </Badge>
      </HStack>
      
      <Flex justify="space-between" align="center" mt={2}>
        <Text fontSize="xs" color="gray.500">
          #{data.loopId}
        </Text>
        
        {data.onSelect && (
          <IconButton
            icon={<FiArrowRight />}
            size="xs"
            variant="ghost"
            aria-label="View Loop Trace"
            onClick={(e) => {
              e.stopPropagation();
              data.onSelect(data.loopId);
            }}
          />
        )}
      </Flex>
    </Box>
  );
};

/**
 * LoopForkMap Component
 * 
 * A recursive tree/graph viewer that highlights where loops diverged,
 * shows which forks were explored, skipped, or merged, and tracks
 * drift score over branches.
 */
const LoopForkMap = ({ projectId, onLoopSelect }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [zoomLevel, setZoomLevel] = useState(0.8);
  const [showSkipped, setShowSkipped] = useState(true);
  const [showMerged, setShowMerged] = useState(true);
  const [layoutDirection, setLayoutDirection] = useState('TB'); // 'TB' (top-bottom) or 'LR' (left-right)
  
  const toast = useToast();
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const panelBgColor = useColorModeValue('gray.50', 'gray.800');
  
  // Fetch loop fork data
  const { 
    data: forkData, 
    error: forkError, 
    loading: forkLoading,
    refetch: refetchForkData
  } = useFetch(
    `/api/project/loop-forks?project_id=${projectId || ''}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: null
    }
  );
  
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
  
  // Truncate summary text
  const truncateSummary = (text, wordCount = 15) => {
    if (!text) return '';
    const words = text.split(' ');
    if (words.length <= wordCount) return text;
    return words.slice(0, wordCount).join(' ') + '...';
  };
  
  // Export fork map as JSON
  const exportForkMap = () => {
    if (!forkData) return;
    
    try {
      const dataStr = JSON.stringify(forkData, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
      
      const exportFileDefaultName = `loop-fork-map-${projectId || 'unknown'}-${new Date().toISOString().slice(0, 10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      toast({
        title: 'Fork map exported',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      console.error('Error exporting fork map:', err);
      toast({
        title: 'Export failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  };
  
  // Toggle layout direction
  const toggleLayoutDirection = () => {
    setLayoutDirection(prev => prev === 'TB' ? 'LR' : 'TB');
  };
  
  // Handle loop selection
  const handleLoopSelect = (loopId) => {
    if (onLoopSelect) {
      onLoopSelect(loopId);
    }
  };
  
  // Mock data for development/testing
  const mockForkData = {
    project_id: projectId || 'project-123',
    loops: [
      {
        loop_id: 'loop-001',
        timestamp: new Date(Date.now() - 86400000 * 7).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Initial project setup and requirements analysis for the cognitive system',
        trust_score: 0.95,
        drift_index: 0.05,
        fork_parent: null,
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-002',
        timestamp: new Date(Date.now() - 86400000 * 6).toISOString(),
        agent: 'SAGE',
        summary: 'Developing core memory architecture and schema definitions',
        trust_score: 0.92,
        drift_index: 0.08,
        fork_parent: 'loop-001',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-003',
        timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
        agent: 'SKEPTIC',
        summary: 'Reviewing memory architecture for potential failure modes and edge cases',
        trust_score: 0.85,
        drift_index: 0.15,
        fork_parent: 'loop-002',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-004',
        timestamp: new Date(Date.now() - 86400000 * 4).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Integrating memory system with cognitive loop execution framework',
        trust_score: 0.88,
        drift_index: 0.12,
        fork_parent: 'loop-003',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-005a',
        timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
        agent: 'SAGE',
        summary: 'Implementing natural language query capabilities for memory retrieval',
        trust_score: 0.78,
        drift_index: 0.22,
        fork_parent: 'loop-004',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-005b',
        timestamp: new Date(Date.now() - 86400000 * 3 + 3600000).toISOString(),
        agent: 'SAGE',
        summary: 'Exploring vector-based semantic search as alternative to natural language parsing',
        trust_score: 0.82,
        drift_index: 0.18,
        fork_parent: 'loop-004',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-005c',
        timestamp: new Date(Date.now() - 86400000 * 3 + 7200000).toISOString(),
        agent: 'SAGE',
        summary: 'Testing hybrid approach combining rule-based and neural methods',
        trust_score: 0.75,
        drift_index: 0.25,
        fork_parent: 'loop-004',
        is_skipped: true,
        is_merged: false
      },
      {
        loop_id: 'loop-006a',
        timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Merging natural language and vector-based approaches for hybrid memory query system',
        trust_score: 0.91,
        drift_index: 0.09,
        fork_parent: 'loop-005a',
        is_skipped: false,
        is_merged: true
      },
      {
        loop_id: 'loop-006b',
        timestamp: new Date(Date.now() - 86400000 * 2 + 3600000).toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Integrating vector-based search with existing memory retrieval system',
        trust_score: 0.89,
        drift_index: 0.11,
        fork_parent: 'loop-005b',
        is_skipped: false,
        is_merged: true
      },
      {
        loop_id: 'loop-007',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        agent: 'OPERATOR',
        summary: 'Testing memory query system with real-world scenarios and providing feedback',
        trust_score: 0.94,
        drift_index: 0.06,
        fork_parent: 'loop-006a',
        is_skipped: false,
        is_merged: false
      },
      {
        loop_id: 'loop-008',
        timestamp: new Date().toISOString(),
        agent: 'ORCHESTRATOR',
        summary: 'Finalizing memory system implementation and preparing for deployment',
        trust_score: 0.89,
        drift_index: 0.11,
        fork_parent: 'loop-007',
        is_skipped: false,
        is_merged: false
      }
    ]
  };
  
  // Use mock data if no real data is available
  const displayData = forkData || mockForkData;
  
  // Create graph data for ReactFlow
  const createGraphData = useCallback(() => {
    if (!displayData || !displayData.loops) return { nodes: [], edges: [] };
    
    const filteredLoops = displayData.loops.filter(loop => {
      if (!showSkipped && loop.is_skipped) return false;
      if (!showMerged && loop.is_merged) return false;
      return true;
    });
    
    // Create a map for quick lookup of loops by ID
    const loopMap = {};
    filteredLoops.forEach(loop => {
      loopMap[loop.loop_id] = loop;
    });
    
    // Create nodes and edges
    const nodes = [];
    const edges = [];
    
    // Calculate node positions
    const nodePositions = {};
    const levelMap = {};
    
    // First, determine the level of each node (depth in the tree)
    const calculateLevel = (loopId, level = 0) => {
      if (!loopMap[loopId]) return;
      
      // Update level if this is deeper
      if (!levelMap[loopId] || level > levelMap[loopId]) {
        levelMap[loopId] = level;
      }
      
      // Find children (loops that have this as fork_parent)
      filteredLoops.forEach(loop => {
        if (loop.fork_parent === loopId) {
          calculateLevel(loop.loop_id, level + 1);
        }
      });
    };
    
    // Start with root nodes (no fork_parent)
    filteredLoops.forEach(loop => {
      if (!loop.fork_parent) {
        calculateLevel(loop.loop_id);
      }
    });
    
    // Count nodes at each level for horizontal positioning
    const levelCounts = {};
    const levelPositions = {};
    
    Object.entries(levelMap).forEach(([loopId, level]) => {
      if (!levelCounts[level]) levelCounts[level] = 0;
      levelCounts[level]++;
    });
    
    Object.entries(levelMap).forEach(([loopId, level]) => {
      if (!levelPositions[level]) levelPositions[level] = 0;
      
      const horizontalSpacing = 300;
      const verticalSpacing = 200;
      
      if (layoutDirection === 'TB') {
        // Top to bottom layout
        nodePositions[loopId] = {
          x: (levelPositions[level] - (levelCounts[level] - 1) / 2) * horizontalSpacing,
          y: level * verticalSpacing
        };
      } else {
        // Left to right layout
        nodePositions[loopId] = {
          x: level * horizontalSpacing,
          y: (levelPositions[level] - (levelCounts[level] - 1) / 2) * verticalSpacing
        };
      }
      
      levelPositions[level]++;
    });
    
    // Create nodes
    filteredLoops.forEach(loop => {
      const position = nodePositions[loop.loop_id] || { x: 0, y: 0 };
      
      nodes.push({
        id: loop.loop_id,
        type: 'custom',
        position,
        data: {
          loopId: loop.loop_id,
          agent: loop.agent,
          agentColor: getAgentColor(loop.agent),
          summary: truncateSummary(loop.summary),
          trustScore: loop.trust_score,
          trustScoreColor: getTrustScoreColor(loop.trust_score),
          driftIndex: loop.drift_index,
          driftIndexColor: getDriftIndexColor(loop.drift_index),
          relativeTime: formatRelativeTime(loop.timestamp),
          isFork: !!loop.fork_parent,
          isMerged: loop.is_merged,
          isSkipped: loop.is_skipped,
          onSelect: handleLoopSelect
        }
      });
      
      // Create edge from parent to this node
      if (loop.fork_parent && loopMap[loop.fork_parent]) {
        edges.push({
          id: `${loop.fork_parent}-${loop.loop_id}`,
          source: loop.fork_parent,
          target: loop.loop_id,
          type: 'smoothstep',
          animated: loop.is_merged,
          style: { 
            stroke: loop.is_skipped ? '#A0AEC0' : loop.is_merged ? '#805AD5' : '#F6AD55',
            strokeWidth: loop.is_skipped ? 1 : 2,
            strokeDasharray: loop.is_skipped ? '5,5' : undefined
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: loop.is_skipped ? '#A0AEC0' : loop.is_merged ? '#805AD5' : '#F6AD55'
          }
        });
      }
    });
    
    return { nodes, edges };
  }, [displayData, showSkipped, showMerged, layoutDirection, handleLoopSelect]);
  
  // Update nodes and edges when data or filters change
  useEffect(() => {
    const { nodes: newNodes, edges: newEdges } = createGraphData();
    setNodes(newNodes);
    setEdges(newEdges);
  }, [createGraphData, setNodes, setEdges]);
  
  // Register custom node types
  const nodeTypes = {
    custom: LoopNode
  };
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">Loop Fork Map</Heading>
        
        <HStack spacing={2}>
          <Tooltip label="Refresh fork map">
            <IconButton
              icon={<FiRefreshCw />}
              size="sm"
              aria-label="Refresh fork map"
              onClick={() => refetchForkData()}
              isLoading={forkLoading}
            />
          </Tooltip>
          
          <Tooltip label="Export fork map">
            <IconButton
              icon={<FiDownload />}
              size="sm"
              aria-label="Export fork map"
              onClick={exportForkMap}
            />
          </Tooltip>
          
          <Tooltip label={layoutDirection === 'TB' ? 'Switch to horizontal' : 'Switch to vertical'}>
            <IconButton
              icon={layoutDirection === 'TB' ? <FiMaximize2 /> : <FiMinimize2 />}
              size="sm"
              aria-label="Toggle layout direction"
              onClick={toggleLayoutDirection}
            />
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Filters */}
      <Box mb={4} p={3} borderWidth="1px" borderRadius="md" bg={panelBgColor}>
        <Flex direction={{ base: 'column', md: 'row' }} gap={4}>
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="show-skipped" mb="0" fontSize="sm">
              Show Skipped:
            </FormLabel>
            <Switch
              id="show-skipped"
              isChecked={showSkipped}
              onChange={(e) => setShowSkipped(e.target.checked)}
            />
          </FormControl>
          
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="show-merged" mb="0" fontSize="sm">
              Show Merged:
            </FormLabel>
            <Switch
              id="show-merged"
              isChecked={showMerged}
              onChange={(e) => setShowMerged(e.target.checked)}
            />
          </FormControl>
        </Flex>
      </Box>
      
      {/* Fork map content */}
      <Box
        borderWidth="1px"
        borderRadius="md"
        borderColor={borderColor}
        bg={bgColor}
        height="calc(100vh - 250px)"
      >
        {forkLoading ? (
          <Flex justify="center" align="center" height="100%">
            <Spinner size="xl" thickness="4px" speed="0.65s" color="blue.500" />
          </Flex>
        ) : forkError ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" color="red.500" mb={2}>Error Loading Fork Map</Heading>
            <Text>{forkError.message || 'Failed to load loop fork map'}</Text>
            <Button mt={4} onClick={() => refetchForkData()}>
              Try Again
            </Button>
          </Flex>
        ) : nodes.length === 0 ? (
          <Flex direction="column" justify="center" align="center" height="100%" p={4}>
            <Heading size="md" mb={2}>No Loops Found</Heading>
            <Text>No loops match the current filters.</Text>
          </Flex>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            defaultZoom={zoomLevel}
            minZoom={0.2}
            maxZoom={2}
            attributionPosition="bottom-right"
          >
            <Controls />
            <MiniMap />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        )}
      </Box>
      
      {/* Legend */}
      <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg={panelBgColor}>
        <Heading size="xs" mb={2}>Legend</Heading>
        <Flex wrap="wrap" gap={4}>
          <HStack>
            <FiGitBranch color="orange" />
            <Text fontSize="sm">Fork</Text>
          </HStack>
          
          <HStack>
            <FiGitMerge color="purple" />
            <Text fontSize="sm">Merged</Text>
          </HStack>
          
          <HStack>
            <FiX color="gray" />
            <Text fontSize="sm">Skipped</Text>
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

export default LoopForkMap;
