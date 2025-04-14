import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Switch,
  FormControl,
  FormLabel,
  useColorMode,
  Divider,
  Heading,
  Button,
  Tooltip,
  Icon
} from '@chakra-ui/react';
import { FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';
import { useStatus } from '../context/StatusContext';

/**
 * MemoryWarningHandler Component
 * 
 * Displays memory fallback state and warnings
 * Integrated with the global StatusContext
 */
const MemoryWarningHandler = () => {
  const { colorMode } = useColorMode();
  const [showFallbackAlerts, setShowFallbackAlerts] = useState(true);
  
  // Get status from context
  const { 
    memoryFallback, 
    setMemoryFallbackState 
  } = useStatus();
  
  // Simulate fallback for testing
  const simulateFallback = () => {
    setMemoryFallbackState(true, 'OpenAI API quota exceeded');
  };
  
  // Clear fallback state
  const clearFallback = () => {
    setMemoryFallbackState(false);
  };
  
  // If not in fallback state and alerts are enabled, don't render anything
  if (!memoryFallback.active && !showFallbackAlerts) return null;
  
  return (
    <Box
      p={4}
      borderWidth="1px"
      borderRadius="md"
      borderColor={memoryFallback.active ? "yellow.300" : "gray.200"}
      bg={memoryFallback.active ? (colorMode === 'light' ? 'yellow.50' : 'yellow.900') : 'transparent'}
      mb={4}
    >
      <VStack spacing={3} align="stretch">
        <HStack justifyContent="space-between">
          <HStack>
            {memoryFallback.active && <Icon as={FiAlertTriangle} color="yellow.500" />}
            <Heading size="sm">Memory System Status</Heading>
          </HStack>
          
          <FormControl display="flex" alignItems="center" width="auto">
            <FormLabel htmlFor="fallback-alerts" mb="0" mr={2} fontSize="sm">
              Show Alerts
            </FormLabel>
            <Switch
              id="fallback-alerts"
              isChecked={showFallbackAlerts}
              onChange={(e) => setShowFallbackAlerts(e.target.checked)}
              colorScheme="blue"
            />
          </FormControl>
        </HStack>
        
        <Divider />
        
        <HStack justifyContent="space-between">
          <Text fontSize="sm">Fallback State:</Text>
          <Badge colorScheme={memoryFallback.active ? "yellow" : "green"}>
            {memoryFallback.active ? "ACTIVE" : "INACTIVE"}
          </Badge>
        </HStack>
        
        {memoryFallback.active && (
          <>
            <HStack justifyContent="space-between">
              <Text fontSize="sm">Reason:</Text>
              <Text fontSize="sm" fontWeight="medium">{memoryFallback.reason || "Unknown"}</Text>
            </HStack>
            
            <HStack justifyContent="space-between">
              <Text fontSize="sm">Since:</Text>
              <Text fontSize="sm">
                {memoryFallback.timestamp ? new Date(memoryFallback.timestamp).toLocaleTimeString() : "Unknown"}
              </Text>
            </HStack>
            
            <Text fontSize="sm" color={colorMode === 'light' ? 'yellow.700' : 'yellow.200'}>
              Memory system is operating in fallback mode. Vector search is disabled.
            </Text>
            
            <Button size="sm" colorScheme="yellow" onClick={clearFallback}>
              Clear Fallback State
            </Button>
          </>
        )}
        
        {!memoryFallback.active && (
          <>
            <Text fontSize="sm" color={colorMode === 'light' ? 'green.700' : 'green.200'}>
              Memory system is operating normally with vector search enabled.
            </Text>
            
            <Tooltip label="For testing only">
              <Button 
                size="sm" 
                variant="outline" 
                colorScheme="yellow" 
                leftIcon={<FiRefreshCw />}
                onClick={simulateFallback}
              >
                Simulate Fallback
              </Button>
            </Tooltip>
          </>
        )}
      </VStack>
    </Box>
  );
};

export default MemoryWarningHandler;
