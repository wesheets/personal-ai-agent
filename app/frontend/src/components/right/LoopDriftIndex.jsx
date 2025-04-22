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
  Badge,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Progress,
  Button
} from '@chakra-ui/react';
import { 
  FaExclamationTriangle, 
  FaExclamationCircle, 
  FaInfoCircle,
  FaArrowRight,
  FaArrowUp,
  FaArrowDown,
  FaSync
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * LoopDriftIndex Component
 * 
 * Displays cognitive loop drift metrics and anomalies.
 * Connected to /api/loop/drift endpoint for loop drift data.
 */
const LoopDriftIndex = ({ projectId = 'promethios-core' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  const tableBgColor = useColorModeValue('white', 'gray.700');
  const tableHeaderBgColor = useColorModeValue('gray.50', 'gray.600');
  
  // Fetch loop drift data from API
  const { 
    data: driftData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/loop/drift?projectId=${projectId}`, {}, {
    refreshInterval: 30000, // Refresh every 30 seconds
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'loop_monitor',
      timestamp: new Date().toISOString(),
      overall_drift: 3.2,
      drift_status: 'normal',
      drift_trend: 'stable',
      metrics: [
        { name: 'Belief Consistency', value: 2.1, threshold: 5.0, status: 'normal' },
        { name: 'Memory Coherence', value: 1.8, threshold: 4.5, status: 'normal' },
        { name: 'Reasoning Patterns', value: 4.7, threshold: 5.0, status: 'warning' },
        { name: 'Output Stability', value: 2.5, threshold: 6.0, status: 'normal' },
        { name: 'Goal Alignment', value: 3.2, threshold: 4.0, status: 'normal' }
      ],
      anomalies: [
        {
          id: 'anom-20250422-001',
          type: 'reasoning_pattern',
          severity: 'medium',
          description: 'Unusual reasoning pattern detected in goal loop execution',
          detected_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          status: 'monitoring'
        },
        {
          id: 'anom-20250421-003',
          type: 'belief_contradiction',
          severity: 'low',
          description: 'Minor contradiction in peripheral belief structure',
          detected_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          status: 'resolved',
          resolution: 'Auto-reconciled during scheduled belief maintenance'
        }
      ],
      historical_drift: [
        { timestamp: new Date(Date.now() - 86400000 * 7).toISOString(), value: 2.8 }, // 7 days ago
        { timestamp: new Date(Date.now() - 86400000 * 6).toISOString(), value: 2.9 }, // 6 days ago
        { timestamp: new Date(Date.now() - 86400000 * 5).toISOString(), value: 3.0 }, // 5 days ago
        { timestamp: new Date(Date.now() - 86400000 * 4).toISOString(), value: 3.1 }, // 4 days ago
        { timestamp: new Date(Date.now() - 86400000 * 3).toISOString(), value: 2.9 }, // 3 days ago
        { timestamp: new Date(Date.now() - 86400000 * 2).toISOString(), value: 3.0 }, // 2 days ago
        { timestamp: new Date(Date.now() - 86400000).toISOString(), value: 3.1 }      // 1 day ago
      ]
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'loop_monitor',
      timestamp: data.timestamp || new Date().toISOString(),
      overall_drift: data.overall_drift || 0,
      drift_status: data.drift_status || 'normal',
      drift_trend: data.drift_trend || 'stable',
      metrics: Array.isArray(data.metrics) ? data.metrics : [],
      anomalies: Array.isArray(data.anomalies) ? data.anomalies : [],
      historical_drift: Array.isArray(data.historical_drift) ? data.historical_drift : []
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
  
  // Format time ago
  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = Math.abs(now - date);
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);
      
      if (diffDays > 0) return `${diffDays}d ago`;
      if (diffHours > 0) return `${diffHours}h ago`;
      return `${diffMins}m ago`;
    } catch (error) {
      return 'Unknown';
    }
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return 'green';
      case 'warning':
        return 'yellow';
      case 'critical':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get severity color
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'low':
        return 'green';
      case 'medium':
        return 'yellow';
      case 'high':
        return 'orange';
      case 'critical':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get trend icon and color
  const getTrendInfo = (trend) => {
    switch (trend) {
      case 'improving':
        return { icon: FaArrowDown, color: 'green' };
      case 'worsening':
        return { icon: FaArrowUp, color: 'red' };
      case 'stable':
      default:
        return { icon: FaArrowRight, color: 'blue' };
    }
  };
  
  // Handle refresh
  const handleRefresh = () => {
    refetch();
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
      
      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="lg" fontWeight="bold">
          Loop Drift Index
        </Text>
        <Button 
          size="sm" 
          leftIcon={<Icon as={FaSync} />} 
          onClick={handleRefresh}
          isLoading={loading}
        >
          Refresh
        </Button>
      </Flex>
      
      {loading && !driftData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !driftData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading loop drift data: {error}</Text>
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {/* Overall Drift Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Flex justify="space-between" align="center" mb={2}>
              <Text fontWeight="bold">Overall Drift Index</Text>
              <Badge colorScheme={getStatusColor(driftData?.drift_status)}>
                {driftData?.drift_status}
              </Badge>
            </Flex>
            
            <Flex align="center" justify="center" my={4}>
              <Box 
                position="relative" 
                width="150px" 
                height="150px" 
                borderRadius="full" 
                bg={useColorModeValue('gray.100', 'gray.800')}
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Text fontSize="3xl" fontWeight="bold">
                  {driftData?.overall_drift.toFixed(1)}
                </Text>
                <Badge 
                  position="absolute" 
                  bottom="10px" 
                  colorScheme={getTrendInfo(driftData?.drift_trend).color}
                >
                  <HStack>
                    <Icon as={getTrendInfo(driftData?.drift_trend).icon} />
                    <Text>{driftData?.drift_trend}</Text>
                  </HStack>
                </Badge>
              </Box>
            </Flex>
            
            <Text fontSize="sm" color="gray.500" textAlign="center">
              Drift index measures cognitive stability over time.
              <br />
              Lower values indicate more stable cognitive processes.
            </Text>
          </Box>
          
          {/* Drift Metrics Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Text fontWeight="bold" mb={3}>Drift Metrics</Text>
            <Table variant="simple" size="sm">
              <Thead bg={tableHeaderBgColor}>
                <Tr>
                  <Th>Metric</Th>
                  <Th isNumeric>Value</Th>
                  <Th isNumeric>Threshold</Th>
                  <Th>Status</Th>
                </Tr>
              </Thead>
              <Tbody>
                {driftData?.metrics?.map((metric, index) => (
                  <Tr key={index}>
                    <Td>{metric.name}</Td>
                    <Td isNumeric>{metric.value.toFixed(1)}</Td>
                    <Td isNumeric>{metric.threshold.toFixed(1)}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(metric.status)}>
                        {metric.status}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
          
          {/* Anomalies Section */}
          {driftData?.anomalies?.length > 0 && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Detected Anomalies</Text>
              <VStack spacing={2} align="stretch">
                {driftData.anomalies.map((anomaly, index) => (
                  <Box 
                    key={index} 
                    p={3} 
                    borderRadius="md" 
                    bg={tableBgColor}
                    borderLeftWidth="4px"
                    borderLeftColor={getSeverityColor(anomaly.severity)}
                  >
                    <Flex justify="space-between" align="center" mb={1}>
                      <HStack>
                        <Icon 
                          as={anomaly.severity === 'critical' ? FaExclamationCircle : 
                              anomaly.severity === 'high' ? FaExclamationTriangle : 
                              FaInfoCircle} 
                          color={getSeverityColor(anomaly.severity)} 
                        />
                        <Text fontWeight="medium">
                          {anomaly.type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </Text>
                      </HStack>
                      <Badge colorScheme={anomaly.status === 'resolved' ? 'green' : 'yellow'}>
                        {anomaly.status}
                      </Badge>
                    </Flex>
                    
                    <Text fontSize="sm" mt={1}>
                      {anomaly.description}
                    </Text>
                    
                    <Flex justify="space-between" mt={2}>
                      <Badge colorScheme={getSeverityColor(anomaly.severity)}>
                        {anomaly.severity} severity
                      </Badge>
                      <Text fontSize="xs" color="gray.500">
                        Detected {formatTimeAgo(anomaly.detected_at)}
                      </Text>
                    </Flex>
                    
                    {anomaly.resolution && (
                      <Text fontSize="xs" color="green.500" mt={1}>
                        Resolution: {anomaly.resolution}
                      </Text>
                    )}
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
          
          {/* Historical Drift Section */}
          {driftData?.historical_drift?.length > 0 && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Historical Drift (7 Days)</Text>
              <Flex height="100px" align="flex-end">
                {driftData.historical_drift.map((point, index) => {
                  const value = point.value;
                  const height = `${Math.min(value * 15, 100)}px`;
                  const color = value > 5 ? 'red.400' : 
                               value > 4 ? 'orange.400' : 
                               value > 3 ? 'yellow.400' : 'green.400';
                  
                  return (
                    <Tooltip 
                      key={index} 
                      label={`${new Date(point.timestamp).toLocaleDateString()}: ${value.toFixed(1)}`}
                    >
                      <Box
                        height={height}
                        width="100%"
                        bg={color}
                        mx={1}
                        borderTopRadius="md"
                        position="relative"
                      />
                    </Tooltip>
                  );
                })}
              </Flex>
              <Flex justify="space-between" mt={2}>
                <Text fontSize="xs">7 days ago</Text>
                <Text fontSize="xs">Today</Text>
              </Flex>
            </Box>
          )}
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Last updated: {formatTimestamp(driftData?.timestamp || Date.now())}
      </Text>
    </Box>
  );
};

export default LoopDriftIndex;
