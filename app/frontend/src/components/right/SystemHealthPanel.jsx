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
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  CircularProgress,
  CircularProgressLabel
} from '@chakra-ui/react';
import { 
  FaServer, 
  FaMemory, 
  FaMicrochip, 
  FaNetworkWired, 
  FaExclamationTriangle,
  FaCheckCircle,
  FaExclamationCircle,
  FaInfoCircle
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * SystemHealthPanel Component
 * 
 * Displays system health metrics including CPU, memory, network, and service status.
 * Connected to /api/system/health endpoint for real-time system metrics.
 */
const SystemHealthPanel = ({ projectId = 'promethios-core' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  
  // Fetch system health data from API
  const { 
    data: healthData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/system/health?projectId=${projectId}`, {}, {
    refreshInterval: 15000, // Refresh every 15 seconds
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'system_monitor',
      timestamp: new Date().toISOString(),
      resources: {
        cpu: {
          usage: 42,
          temperature: 65,
          cores: 8,
          load: [2.1, 1.8, 1.5]
        },
        memory: {
          total: 16384,
          used: 8192,
          usage: 50,
          swap_usage: 15
        },
        disk: {
          total: 512000,
          used: 256000,
          usage: 50
        },
        network: {
          rx_rate: 1.2,
          tx_rate: 0.8,
          connections: 24
        }
      },
      services: [
        { name: 'API Server', status: 'healthy', uptime: 86400 },
        { name: 'Database', status: 'healthy', uptime: 172800 },
        { name: 'Loop Engine', status: 'healthy', uptime: 43200 },
        { name: 'Memory Service', status: 'degraded', uptime: 21600 },
        { name: 'Agent Runner', status: 'healthy', uptime: 64800 }
      ],
      alerts: [
        { level: 'warning', message: 'Memory service performance degraded', timestamp: new Date().toISOString() }
      ]
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'system_monitor',
      timestamp: data.timestamp || new Date().toISOString(),
      resources: data.resources || {},
      services: Array.isArray(data.services) ? data.services : [],
      alerts: Array.isArray(data.alerts) ? data.alerts : []
    })
  });
  
  // Format uptime
  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'green';
      case 'degraded':
        return 'yellow';
      case 'critical':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get alert icon
  const getAlertIcon = (level) => {
    switch (level) {
      case 'critical':
        return FaExclamationCircle;
      case 'warning':
        return FaExclamationTriangle;
      case 'info':
        return FaInfoCircle;
      default:
        return FaInfoCircle;
    }
  };
  
  // Format bytes
  const formatBytes = (bytes, decimals = 1) => {
    if (!bytes) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
  };
  
  // Get progress color based on usage percentage
  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'red';
    if (percentage >= 70) return 'yellow';
    return 'green';
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
        System Health
      </Text>
      
      {loading && !healthData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !healthData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading system health data: {error}</Text>
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {/* Resource Usage Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Text fontWeight="bold" mb={3}>Resource Usage</Text>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              {/* CPU Usage */}
              <Stat>
                <StatLabel>
                  <HStack>
                    <Icon as={FaMicrochip} />
                    <Text>CPU</Text>
                  </HStack>
                </StatLabel>
                <Flex align="center">
                  <CircularProgress 
                    value={healthData?.resources?.cpu?.usage || 0} 
                    color={getUsageColor(healthData?.resources?.cpu?.usage || 0)}
                    size="60px"
                    thickness="8px"
                  >
                    <CircularProgressLabel>
                      {healthData?.resources?.cpu?.usage || 0}%
                    </CircularProgressLabel>
                  </CircularProgress>
                  <Box ml={4}>
                    <Text fontSize="sm">
                      {healthData?.resources?.cpu?.cores || 0} Cores
                    </Text>
                    <Text fontSize="sm">
                      {healthData?.resources?.cpu?.temperature || 0}°C
                    </Text>
                  </Box>
                </Flex>
              </Stat>
              
              {/* Memory Usage */}
              <Stat>
                <StatLabel>
                  <HStack>
                    <Icon as={FaMemory} />
                    <Text>Memory</Text>
                  </HStack>
                </StatLabel>
                <StatNumber>
                  {formatBytes(healthData?.resources?.memory?.used || 0)} / {formatBytes(healthData?.resources?.memory?.total || 0)}
                </StatNumber>
                <Progress 
                  value={healthData?.resources?.memory?.usage || 0} 
                  colorScheme={getUsageColor(healthData?.resources?.memory?.usage || 0)}
                  size="sm"
                  mt={1}
                />
                <StatHelpText>
                  Swap: {healthData?.resources?.memory?.swap_usage || 0}% used
                </StatHelpText>
              </Stat>
              
              {/* Disk Usage */}
              <Stat>
                <StatLabel>Disk</StatLabel>
                <StatNumber>
                  {formatBytes(healthData?.resources?.disk?.used || 0)} / {formatBytes(healthData?.resources?.disk?.total || 0)}
                </StatNumber>
                <Progress 
                  value={healthData?.resources?.disk?.usage || 0} 
                  colorScheme={getUsageColor(healthData?.resources?.disk?.usage || 0)}
                  size="sm"
                  mt={1}
                />
              </Stat>
              
              {/* Network Usage */}
              <Stat>
                <StatLabel>
                  <HStack>
                    <Icon as={FaNetworkWired} />
                    <Text>Network</Text>
                  </HStack>
                </StatLabel>
                <StatNumber>
                  {healthData?.resources?.network?.connections || 0} Connections
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="down" />
                  {healthData?.resources?.network?.rx_rate || 0} MB/s
                  <StatArrow type="up" ml={2} />
                  {healthData?.resources?.network?.tx_rate || 0} MB/s
                </StatHelpText>
              </Stat>
            </SimpleGrid>
          </Box>
          
          {/* Services Status Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Text fontWeight="bold" mb={3}>Services Status</Text>
            <VStack spacing={2} align="stretch">
              {healthData?.services?.map((service, index) => (
                <Flex 
                  key={index} 
                  justify="space-between" 
                  align="center" 
                  p={2} 
                  borderRadius="md" 
                  bg={useColorModeValue('white', 'gray.700')}
                >
                  <HStack>
                    <Icon 
                      as={service.status === 'healthy' ? FaCheckCircle : FaExclamationTriangle} 
                      color={getStatusColor(service.status)} 
                    />
                    <Text>{service.name}</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme={getStatusColor(service.status)}>
                      {service.status}
                    </Badge>
                    <Text fontSize="sm" color="gray.500">
                      {formatUptime(service.uptime)}
                    </Text>
                  </HStack>
                </Flex>
              ))}
            </VStack>
          </Box>
          
          {/* Alerts Section */}
          {healthData?.alerts?.length > 0 && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Alerts</Text>
              <VStack spacing={2} align="stretch">
                {healthData.alerts.map((alert, index) => (
                  <Flex 
                    key={index} 
                    p={2} 
                    borderRadius="md" 
                    bg={useColorModeValue('white', 'gray.700')}
                    borderLeftWidth="4px"
                    borderLeftColor={getStatusColor(alert.level)}
                  >
                    <Icon 
                      as={getAlertIcon(alert.level)} 
                      color={getStatusColor(alert.level)} 
                      mr={2}
                    />
                    <Box>
                      <Text>{alert.message}</Text>
                      <Text fontSize="xs" color="gray.500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </Text>
                    </Box>
                  </Flex>
                ))}
              </VStack>
            </Box>
          )}
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Last updated: {new Date(healthData?.timestamp || Date.now()).toLocaleString()}
      </Text>
    </Box>
  );
};

export default SystemHealthPanel;
