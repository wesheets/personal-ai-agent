import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Icon, 
  Flex, 
  Spinner, 
  useColorModeValue,
  Tooltip,
  Progress,
  Badge,
  Divider,
  Button,
  CircularProgress,
  CircularProgressLabel
} from '@chakra-ui/react';
import { 
  FaRedo, 
  FaExclamationTriangle, 
  FaCheckCircle, 
  FaClock,
  FaCode,
  FaHistory,
  FaSync
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * RebuildStatusDisplay Component
 * 
 * Displays the status of system rebuilds and cognitive restructuring processes.
 * Connected to /api/rebuild/status endpoint for rebuild status data.
 */
const RebuildStatusDisplay = ({ projectId = 'promethios-core' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  
  // Fetch rebuild status data from API
  const { 
    data: rebuildData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/rebuild/status?projectId=${projectId}`, {}, {
    refreshInterval: 30000, // Refresh every 30 seconds
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'rebuilder',
      active_rebuild: {
        id: 'rb-20250422-001',
        status: 'in_progress',
        progress: 68,
        started_at: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
        estimated_completion: new Date(Date.now() + 900000).toISOString(), // 15 minutes from now
        triggered_by: 'system',
        type: 'cognitive_restructuring'
      },
      recent_rebuilds: [
        {
          id: 'rb-20250421-003',
          status: 'completed',
          progress: 100,
          started_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          completed_at: new Date(Date.now() - 82800000).toISOString(), // 23 hours ago
          triggered_by: 'operator',
          type: 'full_rebuild',
          success: true
        },
        {
          id: 'rb-20250421-002',
          status: 'failed',
          progress: 45,
          started_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
          failed_at: new Date(Date.now() - 170100000).toISOString(), // 1 day 23 hours ago
          triggered_by: 'system',
          type: 'belief_reconciliation',
          error: 'Contradiction detected in core beliefs'
        }
      ],
      rebuild_schedule: {
        next_scheduled: new Date(Date.now() + 86400000).toISOString(), // 1 day from now
        frequency: 'daily',
        types: ['belief_reconciliation', 'cognitive_restructuring']
      }
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'rebuilder',
      active_rebuild: data.active_rebuild || null,
      recent_rebuilds: Array.isArray(data.recent_rebuilds) ? data.recent_rebuilds : [],
      rebuild_schedule: data.rebuild_schedule || {}
    })
  });
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Format time difference
  const formatTimeDiff = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = Math.abs(date - now);
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);
      
      if (diffDays > 0) return `${diffDays}d ${diffHours % 24}h`;
      if (diffHours > 0) return `${diffHours}h ${diffMins % 60}m`;
      return `${diffMins}m`;
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'in_progress':
        return 'blue';
      case 'queued':
        return 'yellow';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get rebuild type display name
  const getRebuildTypeDisplay = (type) => {
    switch (type) {
      case 'full_rebuild':
        return 'Full System Rebuild';
      case 'cognitive_restructuring':
        return 'Cognitive Restructuring';
      case 'belief_reconciliation':
        return 'Belief Reconciliation';
      case 'memory_optimization':
        return 'Memory Optimization';
      default:
        return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
  };
  
  // Get rebuild type icon
  const getRebuildTypeIcon = (type) => {
    switch (type) {
      case 'full_rebuild':
        return FaRedo;
      case 'cognitive_restructuring':
        return FaCode;
      case 'belief_reconciliation':
        return FaBalanceScale;
      case 'memory_optimization':
        return FaMemory;
      default:
        return FaSync;
    }
  };
  
  // Handle manual rebuild trigger
  const handleTriggerRebuild = async () => {
    console.log('Trigger rebuild clicked');
    // In a real implementation, this would call an API to trigger a rebuild
  };
  
  return (
    <Box position="relative">
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px" zIndex={1}>
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px" zIndex={1}>
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        Rebuild Status
      </Text>
      
      {loading && !rebuildData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !rebuildData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading rebuild status: {error}</Text>
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {/* Active Rebuild Section */}
          {rebuildData?.active_rebuild ? (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Flex justify="space-between" align="center" mb={3}>
                <HStack>
                  <Icon 
                    as={getRebuildTypeIcon(rebuildData.active_rebuild.type)} 
                    color="blue.500" 
                  />
                  <Text fontWeight="bold">
                    {getRebuildTypeDisplay(rebuildData.active_rebuild.type)}
                  </Text>
                </HStack>
                <Badge colorScheme={getStatusColor(rebuildData.active_rebuild.status)}>
                  {rebuildData.active_rebuild.status.replace('_', ' ')}
                </Badge>
              </Flex>
              
              <Flex align="center" mb={3}>
                <CircularProgress 
                  value={rebuildData.active_rebuild.progress || 0} 
                  color="blue.500"
                  size="80px"
                  thickness="8px"
                >
                  <CircularProgressLabel>
                    {rebuildData.active_rebuild.progress || 0}%
                  </CircularProgressLabel>
                </CircularProgress>
                
                <Box ml={4}>
                  <HStack mb={1}>
                    <Icon as={FaClock} color="gray.500" />
                    <Text fontSize="sm">
                      Started: {formatTimeDiff(rebuildData.active_rebuild.started_at)} ago
                    </Text>
                  </HStack>
                  <HStack>
                    <Icon as={FaHistory} color="gray.500" />
                    <Text fontSize="sm">
                      ETA: {formatTimeDiff(rebuildData.active_rebuild.estimated_completion)}
                    </Text>
                  </HStack>
                </Box>
              </Flex>
              
              <Progress 
                value={rebuildData.active_rebuild.progress || 0} 
                colorScheme="blue"
                size="sm"
                borderRadius="md"
              />
              
              <Text fontSize="xs" color="gray.500" mt={2}>
                ID: {rebuildData.active_rebuild.id} • Triggered by: {rebuildData.active_rebuild.triggered_by}
              </Text>
            </Box>
          ) : (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Flex direction="column" align="center" justify="center" py={4}>
                <Icon as={FaCheckCircle} color="green.500" boxSize={10} mb={3} />
                <Text fontWeight="bold" mb={2}>No Active Rebuilds</Text>
                <Text fontSize="sm" color="gray.500" mb={4} textAlign="center">
                  System is stable and operating normally.
                </Text>
                <Button 
                  leftIcon={<Icon as={FaRedo} />} 
                  colorScheme="blue" 
                  size="sm"
                  onClick={handleTriggerRebuild}
                >
                  Trigger Manual Rebuild
                </Button>
              </Flex>
            </Box>
          )}
          
          {/* Recent Rebuilds Section */}
          {rebuildData?.recent_rebuilds?.length > 0 && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Recent Rebuilds</Text>
              <VStack spacing={2} align="stretch">
                {rebuildData.recent_rebuilds.map((rebuild, index) => (
                  <Box 
                    key={index} 
                    p={3} 
                    borderRadius="md" 
                    bg={useColorModeValue('white', 'gray.700')}
                    borderLeftWidth="4px"
                    borderLeftColor={getStatusColor(rebuild.status)}
                  >
                    <Flex justify="space-between" align="center" mb={1}>
                      <HStack>
                        <Icon 
                          as={getRebuildTypeIcon(rebuild.type)} 
                          color={getStatusColor(rebuild.status)} 
                        />
                        <Text fontWeight="medium">
                          {getRebuildTypeDisplay(rebuild.type)}
                        </Text>
                      </HStack>
                      <Badge colorScheme={getStatusColor(rebuild.status)}>
                        {rebuild.status}
                      </Badge>
                    </Flex>
                    
                    <Text fontSize="xs" color="gray.500">
                      {rebuild.status === 'completed' 
                        ? `Completed ${formatTimeDiff(rebuild.completed_at)} ago` 
                        : rebuild.status === 'failed'
                        ? `Failed ${formatTimeDiff(rebuild.failed_at)} ago`
                        : `Started ${formatTimeDiff(rebuild.started_at)} ago`}
                    </Text>
                    
                    {rebuild.error && (
                      <Text fontSize="xs" color="red.500" mt={1}>
                        Error: {rebuild.error}
                      </Text>
                    )}
                    
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      ID: {rebuild.id} • Triggered by: {rebuild.triggered_by}
                    </Text>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
          
          {/* Rebuild Schedule Section */}
          {rebuildData?.rebuild_schedule && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Rebuild Schedule</Text>
              <HStack mb={2}>
                <Icon as={FaClock} color="blue.500" />
                <Text>
                  Next scheduled: {formatTimestamp(rebuildData.rebuild_schedule.next_scheduled)}
                </Text>
              </HStack>
              <Text fontSize="sm" color="gray.500">
                Frequency: {rebuildData.rebuild_schedule.frequency || 'Not set'}
              </Text>
              {rebuildData.rebuild_schedule.types && (
                <Flex mt={2} flexWrap="wrap">
                  {rebuildData.rebuild_schedule.types.map((type, index) => (
                    <Badge 
                      key={index} 
                      colorScheme="blue" 
                      mr={2} 
                      mb={2}
                    >
                      {getRebuildTypeDisplay(type)}
                    </Badge>
                  ))}
                </Flex>
              )}
            </Box>
          )}
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Project: {rebuildData?.project_id || projectId}
      </Text>
    </Box>
  );
};

export default RebuildStatusDisplay;
