import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  Badge,
  useColorMode,
  Fade,
  HStack,
  Icon,
  Tooltip,
  VStack,
  Flex,
  CloseButton,
  Collapse,
  Button,
  Divider
} from '@chakra-ui/react';
import { FiCheckCircle, FiAlertTriangle, FiAlertCircle, FiInfo, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import { useStatus, STATUS_TYPES } from '../context/StatusContext';

/**
 * StatusOverlay Component
 * 
 * A globally accessible component that displays system status information
 * Shows warnings, errors, and health status from various parts of the system
 */
const StatusOverlay = () => {
  const { colorMode } = useColorMode();
  const [expanded, setExpanded] = useState(false);
  const [currentPingIndex, setCurrentPingIndex] = useState(0);
  
  // Get status from context
  const {
    systemStatus,
    warnings,
    memoryFallback,
    controlMode,
    delegateStatus,
    agentHealthPings,
    overlayVisible,
    toggleOverlay,
    removeWarning
  } = useStatus();
  
  // Rotate through agent health pings
  useEffect(() => {
    if (!agentHealthPings || agentHealthPings.length === 0) return;
    
    const interval = setInterval(() => {
      setCurrentPingIndex(prev => (prev + 1) % agentHealthPings.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [agentHealthPings]);
  
  // Don't render anything if not visible
  if (!overlayVisible && warnings.length === 0 && systemStatus.type === STATUS_TYPES.STABLE) return null;
  
  // Determine styling based on status
  const getBgColor = () => {
    switch (systemStatus.type) {
      case STATUS_TYPES.STABLE:
        return colorMode === 'light' ? 'green.50' : 'green.900';
      case STATUS_TYPES.UNAVAILABLE:
        return colorMode === 'light' ? 'red.50' : 'red.900';
      case STATUS_TYPES.DEGRADED:
        return colorMode === 'light' ? 'yellow.50' : 'yellow.900';
      default:
        return colorMode === 'light' ? 'blue.50' : 'blue.900';
    }
  };
  
  const getBorderColor = () => {
    switch (systemStatus.type) {
      case STATUS_TYPES.STABLE:
        return colorMode === 'light' ? 'green.200' : 'green.700';
      case STATUS_TYPES.UNAVAILABLE:
        return colorMode === 'light' ? 'red.200' : 'red.700';
      case STATUS_TYPES.DEGRADED:
        return colorMode === 'light' ? 'yellow.200' : 'yellow.700';
      default:
        return colorMode === 'light' ? 'blue.200' : 'blue.700';
    }
  };
  
  const getIcon = () => {
    switch (systemStatus.type) {
      case STATUS_TYPES.STABLE:
        return FiCheckCircle;
      case STATUS_TYPES.UNAVAILABLE:
        return FiAlertCircle;
      case STATUS_TYPES.DEGRADED:
        return FiAlertTriangle;
      default:
        return FiInfo;
    }
  };
  
  const getStatusText = () => {
    switch (systemStatus.type) {
      case STATUS_TYPES.STABLE:
        return '🟢 Stable';
      case STATUS_TYPES.UNAVAILABLE:
        return '🔴 Unavailable';
      case STATUS_TYPES.DEGRADED:
        return '🟡 Degraded';
      default:
        return 'System Status';
    }
  };
  
  const getStatusColor = () => {
    switch (systemStatus.type) {
      case STATUS_TYPES.STABLE:
        return 'green';
      case STATUS_TYPES.UNAVAILABLE:
        return 'red';
      case STATUS_TYPES.DEGRADED:
        return 'yellow';
      default:
        return 'blue';
    }
  };
  
  // Get current agent health ping
  const currentPing = agentHealthPings.length > 0 ? agentHealthPings[currentPingIndex] : null;
  
  return (
    <Fade in={true}>
      <Box
        position="fixed"
        bottom="20px"
        right="20px"
        zIndex={9999}
        borderRadius="md"
        bg={getBgColor()}
        borderWidth="1px"
        borderColor={getBorderColor()}
        boxShadow="md"
        maxW="400px"
        overflow="hidden"
      >
        {/* Header */}
        <Flex 
          p={3} 
          justifyContent="space-between" 
          alignItems="center"
          borderBottomWidth={expanded ? "1px" : "0"}
          borderBottomColor={getBorderColor()}
        >
          <HStack spacing={2} align="center">
            <Icon as={getIcon()} />
            <Badge colorScheme={getStatusColor()}>
              {getStatusText()}
            </Badge>
            <Text fontSize="sm">{systemStatus.message}</Text>
          </HStack>
          
          <HStack>
            <Button 
              size="xs" 
              variant="ghost" 
              onClick={() => setExpanded(!expanded)}
              aria-label={expanded ? "Collapse" : "Expand"}
            >
              <Icon as={expanded ? FiChevronUp : FiChevronDown} />
            </Button>
            <CloseButton size="sm" onClick={toggleOverlay} />
          </HStack>
        </Flex>
        
        {/* Expanded content */}
        <Collapse in={expanded} animateOpacity>
          <Box p={3}>
            {/* Memory fallback status */}
            {memoryFallback.active && (
              <Box mb={3} p={2} bg={colorMode === 'light' ? 'yellow.100' : 'yellow.800'} borderRadius="md">
                <HStack>
                  <Icon as={FiAlertTriangle} color="yellow.500" />
                  <Text fontSize="sm" fontWeight="medium">Memory Fallback Active</Text>
                </HStack>
                {memoryFallback.reason && (
                  <Text fontSize="xs" mt={1}>{memoryFallback.reason}</Text>
                )}
              </Box>
            )}
            
            {/* Control mode status */}
            {controlMode.loadError && (
              <Box mb={3} p={2} bg={colorMode === 'light' ? 'red.100' : 'red.800'} borderRadius="md">
                <HStack>
                  <Icon as={FiAlertCircle} color="red.500" />
                  <Text fontSize="sm" fontWeight="medium">Control Mode Load Failure</Text>
                </HStack>
                {controlMode.errorMessage && (
                  <Text fontSize="xs" mt={1}>{controlMode.errorMessage}</Text>
                )}
              </Box>
            )}
            
            {/* Delegate endpoint errors */}
            {delegateStatus.errors.length > 0 && (
              <Box mb={3} p={2} bg={colorMode === 'light' ? 'red.100' : 'red.800'} borderRadius="md">
                <HStack>
                  <Icon as={FiAlertCircle} color="red.500" />
                  <Text fontSize="sm" fontWeight="medium">Delegate Endpoint Errors</Text>
                </HStack>
                <Text fontSize="xs" mt={1}>
                  {delegateStatus.errors[0].message}
                  {delegateStatus.errors.length > 1 && ` (+${delegateStatus.errors.length - 1} more)`}
                </Text>
              </Box>
            )}
            
            {/* Warnings */}
            {warnings.length > 0 && (
              <Box mb={3}>
                <Text fontSize="sm" fontWeight="medium" mb={1}>Warnings</Text>
                <VStack spacing={2} align="stretch">
                  {warnings.slice(0, 3).map(warning => (
                    <Box 
                      key={warning.id} 
                      p={2} 
                      bg={colorMode === 'light' ? 'yellow.100' : 'yellow.800'} 
                      borderRadius="md"
                      position="relative"
                    >
                      <CloseButton 
                        size="xs" 
                        position="absolute" 
                        top={1} 
                        right={1} 
                        onClick={() => removeWarning(warning.id)} 
                      />
                      <Text fontSize="xs" fontWeight="medium">{warning.title}</Text>
                      <Text fontSize="xs">{warning.message}</Text>
                    </Box>
                  ))}
                  {warnings.length > 3 && (
                    <Text fontSize="xs" textAlign="center">
                      +{warnings.length - 3} more warnings
                    </Text>
                  )}
                </VStack>
              </Box>
            )}
            
            {/* Agent health pings */}
            {currentPing && (
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={1}>Agent Health</Text>
                <HStack spacing={2} p={2} bg={colorMode === 'light' ? 'blue.50' : 'blue.800'} borderRadius="md">
                  <Badge colorScheme={
                    currentPing.status === 'active' ? 'green' :
                    currentPing.status === 'degraded' ? 'yellow' : 'red'
                  }>
                    {currentPing.status === 'active' ? '🟢' : 
                     currentPing.status === 'degraded' ? '🟡' : '🔴'}
                  </Badge>
                  <Text fontSize="xs">{currentPing.name || currentPing.id}</Text>
                  <Text fontSize="xs" color="gray.500" ml="auto">
                    {new Date(currentPing.lastPing).toLocaleTimeString()}
                  </Text>
                </HStack>
                {agentHealthPings.length > 1 && (
                  <Text fontSize="xs" textAlign="center" mt={1}>
                    Showing 1 of {agentHealthPings.length} agents
                  </Text>
                )}
              </Box>
            )}
          </Box>
        </Collapse>
      </Box>
    </Fade>
  );
};

export default StatusOverlay;
