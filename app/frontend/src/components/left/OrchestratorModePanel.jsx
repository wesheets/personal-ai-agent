import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  ButtonGroup, 
  Icon, 
  Tooltip,
  useColorModeValue,
  Badge,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { FaBolt, FaBalanceScale, FaSearch, FaFlask, FaExclamationTriangle } from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * OrchestratorModePanel Component
 * 
 * Controls the orchestration mode of the Promethios system.
 * Connected to /api/system/orchestrator endpoint for mode data and control.
 */
const OrchestratorModePanel = () => {
  const [activeMode, setActiveMode] = useState('BALANCED');
  const [isChanging, setIsChanging] = useState(false);
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const toast = useToast();
  
  const modes = [
    { 
      id: 'FAST', 
      name: 'Fast', 
      icon: FaBolt, 
      color: 'green',
      description: 'Quick execution with minimal reflection and validation'
    },
    { 
      id: 'BALANCED', 
      name: 'Balanced', 
      icon: FaBalanceScale, 
      color: 'blue',
      description: 'Standard execution with normal reflection and validation'
    },
    { 
      id: 'THOROUGH', 
      name: 'Thorough', 
      icon: FaSearch, 
      color: 'purple',
      description: 'Comprehensive execution with extensive reflection and validation'
    },
    { 
      id: 'RESEARCH', 
      name: 'Research', 
      icon: FaFlask, 
      color: 'orange',
      description: 'Deep exploration mode with maximum reflection and validation'
    }
  ];
  
  // Fetch orchestrator mode from API
  const { 
    data: orchestratorData, 
    error, 
    loading, 
    refetch 
  } = useFetch('/api/system/orchestrator', {}, {
    refreshInterval: 15000, // Refresh every 15 seconds
    initialData: {
      mode: 'BALANCED',
      lastChanged: new Date().toISOString(),
      activeLoops: 0,
      stability: 0.95
    },
    transformResponse: (data) => ({
      mode: data.mode || 'BALANCED',
      lastChanged: data.lastChanged || new Date().toISOString(),
      activeLoops: data.activeLoops || 0,
      stability: data.stability || 0.95
    })
  });
  
  // Update active mode when data is loaded
  useEffect(() => {
    if (orchestratorData && orchestratorData.mode) {
      setActiveMode(orchestratorData.mode);
    }
  }, [orchestratorData]);
  
  const handleModeChange = async (mode) => {
    if (mode === activeMode) return;
    
    setIsChanging(true);
    
    try {
      // Call API to update orchestrator mode
      const response = await fetch('/api/system/orchestrator/set-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to set mode: ${response.status}`);
      }
      
      setActiveMode(mode);
      
      toast({
        title: "Orchestrator mode updated",
        description: `Switched to ${mode} mode`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      // Refresh data after mode change
      refetch();
    } catch (err) {
      console.error(`Error setting mode to ${mode}:`, err);
      
      toast({
        title: "Failed to change mode",
        description: err.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsChanging(false);
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Unknown';
    }
  };
  
  return (
    <Box 
      p={4} 
      borderRadius="md" 
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
      position="relative"
    >
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px">
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px">
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Flex justifyContent="space-between" alignItems="center" mb={3}>
        <Heading size="sm">Orchestrator Mode</Heading>
        <Badge colorScheme={modes.find(m => m.id === activeMode)?.color || 'blue'}>
          {activeMode}
        </Badge>
      </Flex>
      
      <ButtonGroup size="sm" isAttached variant="outline" width="100%" mb={3}>
        {modes.map(mode => (
          <Tooltip key={mode.id} label={mode.description} placement="top">
            <Button
              flex={1}
              leftIcon={<Icon as={mode.icon} />}
              colorScheme={mode.id === activeMode ? mode.color : 'gray'}
              variant={mode.id === activeMode ? 'solid' : 'outline'}
              onClick={() => handleModeChange(mode.id)}
              isLoading={isChanging && mode.id !== activeMode}
              loadingText=""
              isDisabled={isChanging}
            >
              <Text fontSize="xs" display={{ base: 'none', md: 'block' }}>
                {mode.name}
              </Text>
            </Button>
          </Tooltip>
        ))}
      </ButtonGroup>
      
      <Text fontSize="xs" color={textColor}>
        {modes.find(m => m.id === activeMode)?.description}
      </Text>
      
      {orchestratorData && (
        <Flex mt={2} justifyContent="space-between" fontSize="xs" color="gray.500">
          <Text>Active loops: {orchestratorData.activeLoops}</Text>
          <Text>
            Last changed: {formatTimestamp(orchestratorData.lastChanged)}
          </Text>
        </Flex>
      )}
    </Box>
  );
};

export default OrchestratorModePanel;
