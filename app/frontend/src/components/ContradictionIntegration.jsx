import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Badge,
  Button,
  useColorModeValue,
  useDisclosure,
  Tooltip,
  IconButton,
} from '@chakra-ui/react';
import { FiAlertTriangle } from 'react-icons/fi';
import ContradictionDisplay from './contradiction/ContradictionDisplay';
import { useContradictionDetector } from '../logic/ContradictionDetector';
import { ReflectionRetractionTrigger } from './revision/ReflectionRetractionPanel';
import { useReplanTrigger } from '../logic/ReplanTrigger';

/**
 * ContradictionIntegration Component
 * 
 * Integrates the contradiction detection system with existing components.
 * Provides hooks and utilities for other components to use the contradiction detection system.
 */
const ContradictionIntegration = () => {
  // Mock data for development
  const [beliefs, setBeliefs] = useState([]);
  const [reflections, setReflections] = useState([]);
  const [summaries, setSummaries] = useState([]);
  const [contradictions, setContradictions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Replan trigger hook
  const {
    triggerReplan,
    isReplanning,
  } = useReplanTrigger({
    onComplete: (result) => {
      console.log('Replan completed:', result);
    },
  });
  
  // Contradiction detector hook
  const {
    contradictionLogs,
    processItem,
    isDetecting,
    startDetection,
    stopDetection,
  } = useContradictionDetector({
    beliefs,
    reflections,
    summaries,
    onContradictionDetected: (contradiction) => {
      console.log('Contradiction detected:', contradiction);
      setContradictions(prev => [...prev, contradiction]);
    },
    threshold: 0.7,
    enabled: true,
  });
  
  // Load mock data on component mount
  useEffect(() => {
    const loadMockData = async () => {
      try {
        setIsLoading(true);
        
        // In a real implementation, this would fetch from an API
        // For now, we'll use mock data from the ContradictionLog.json file
        const response = await fetch('/data/ContradictionLog.json');
        const data = await response.json();
        
        setContradictions(data.contradictions || []);
        
        // Mock beliefs, reflections, and summaries
        setBeliefs([
          {
            id: 'belief_privacy_001',
            content: 'The system should prioritize user privacy over data collection.',
            agent: 'SAGE',
            loop_id: 'loop_789',
            metadata: { timestamp: '2025-04-22T14:20:00.000Z' }
          },
          {
            id: 'belief_autonomy_003',
            content: 'The system will never make autonomous decisions affecting user data.',
            agent: 'NOVA',
            loop_id: 'loop_123',
            metadata: { timestamp: '2025-04-22T14:25:00.000Z' }
          },
          {
            id: 'belief_timeline_002',
            content: 'The implementation must be completed by the original deadline.',
            agent: 'CRITIC',
            loop_id: 'loop_567',
            metadata: { timestamp: '2025-04-22T14:30:00.000Z' }
          }
        ]);
        
        setReflections([
          {
            id: 'reflection_456_002',
            content: 'The user interface should be simplified for better accessibility.',
            agent: 'HAL',
            loop_id: 'loop_456',
            metadata: { timestamp: '2025-04-22T14:32:00.000Z' }
          },
          {
            id: 'reflection_456_005',
            content: 'Advanced features should be prominently displayed in the interface.',
            agent: 'HAL',
            loop_id: 'loop_456',
            metadata: { timestamp: '2025-04-22T14:35:00.000Z' }
          },
          {
            id: 'reflection_567_003',
            content: 'The implementation timeline should be extended to ensure quality.',
            agent: 'CRITIC',
            loop_id: 'loop_567',
            metadata: { timestamp: '2025-04-22T14:38:00.000Z' }
          }
        ]);
        
        setSummaries([
          {
            id: 'summary_123_001',
            content: 'In certain high-confidence scenarios, the system should act autonomously to protect user data.',
            agent: 'NOVA',
            loop_id: 'loop_123',
            metadata: { timestamp: '2025-04-22T14:40:00.000Z' }
          },
          {
            id: 'summary_890_001',
            content: 'The feature will be implemented in the next release.',
            agent: 'SAGE',
            loop_id: 'loop_890',
            metadata: { timestamp: '2025-04-22T14:45:00.000Z' }
          },
          {
            id: 'summary_890_002',
            content: 'The feature has been postponed indefinitely.',
            agent: 'SAGE',
            loop_id: 'loop_890',
            metadata: { timestamp: '2025-04-22T14:50:00.000Z' }
          }
        ]);
      } catch (error) {
        console.error('Failed to load contradiction data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadMockData();
  }, []);
  
  // Handle resolving a contradiction
  const handleResolveContradiction = (resolvedContradiction) => {
    setContradictions(prev => 
      prev.map(c => 
        c.contradiction_id === resolvedContradiction.contradiction_id
          ? resolvedContradiction
          : c
      )
    );
  };
  
  // Handle triggering a reflection
  const handleTriggerReflection = (contradiction) => {
    // In a real implementation, this would trigger the reflection retraction panel
    console.log('Triggering reflection for contradiction:', contradiction);
    
    // Update contradiction status
    handleResolveContradiction({
      ...contradiction,
      resolution: 'flagged'
    });
  };
  
  // Handle rerouting a loop
  const handleRerouteLoop = (contradiction) => {
    // In a real implementation, this would trigger the replan process
    console.log('Rerouting loop for contradiction:', contradiction);
    
    // Trigger replan
    triggerReplan({
      revised_from_loop_id: contradiction.loop_id,
      agent: contradiction.agent,
      reason: 'contradiction',
      revised_reflection: `Resolving contradiction between: "${contradiction.belief_1}" and "${contradiction.belief_2}"`,
      project_id: 'contradiction_resolution',
    });
    
    // Update contradiction status
    handleResolveContradiction({
      ...contradiction,
      resolution: 'revised'
    });
  };
  
  // Handle refreshing contradictions
  const handleRefresh = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };
  
  return (
    <Box>
      <ContradictionDisplay
        contradictions={contradictions}
        onResolve={handleResolveContradiction}
        onTriggerReflection={handleTriggerReflection}
        onRerouteLoop={handleRerouteLoop}
        onRefresh={handleRefresh}
        isLoading={isLoading}
      />
    </Box>
  );
};

export default ContradictionIntegration;

/**
 * ContradictionBadge Component
 * 
 * Small badge component to show in LoopTraceViewer when a contradiction is detected.
 */
export const ContradictionBadge = ({ loopId, onClick }) => {
  const bgColor = useColorModeValue('red.100', 'red.900');
  const textColor = useColorModeValue('red.800', 'red.100');
  
  return (
    <Tooltip label="Contradiction detected in this loop">
      <Badge
        display="flex"
        alignItems="center"
        px={2}
        py={1}
        borderRadius="full"
        bg={bgColor}
        color={textColor}
        cursor="pointer"
        onClick={onClick}
      >
        <FiAlertTriangle style={{ marginRight: '4px' }} />
        Contradiction
      </Badge>
    </Tooltip>
  );
};

/**
 * ContradictionAlert Component
 * 
 * Alert component to show in AgentChatConsole when a contradiction is detected.
 */
export const ContradictionAlert = ({ contradiction, onResolve, onDismiss }) => {
  const bgColor = useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)');
  const borderColor = useColorModeValue('red.200', 'red.800');
  
  return (
    <Box
      p={3}
      mb={4}
      borderWidth="1px"
      borderRadius="md"
      borderColor={borderColor}
      bg={bgColor}
    >
      <Flex justify="space-between" align="center">
        <Flex align="center">
          <FiAlertTriangle color="red" style={{ marginRight: '8px' }} />
          <Text fontWeight="bold">Contradiction Detected</Text>
        </Flex>
        <IconButton
          icon={<FiAlertTriangle />}
          size="sm"
          variant="ghost"
          colorScheme="red"
          aria-label="Resolve contradiction"
          onClick={() => onResolve(contradiction)}
        />
      </Flex>
      <Text mt={2} fontSize="sm">
        This message contradicts a previous statement or belief.
      </Text>
      <Flex mt={3} justify="space-between">
        <Button size="xs" onClick={() => onResolve(contradiction)}>
          Resolve
        </Button>
        <Button size="xs" variant="ghost" onClick={onDismiss}>
          Dismiss
        </Button>
      </Flex>
    </Box>
  );
};

/**
 * useContradictionMonitor Hook
 * 
 * Custom hook for other components to use the contradiction detection system.
 */
export const useContradictionMonitor = (options = {}) => {
  const [contradictions, setContradictions] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(options.enabled !== false);
  
  // Use the contradiction detector
  const detector = useContradictionDetector({
    ...options,
    onContradictionDetected: (contradiction) => {
      setContradictions(prev => [...prev, contradiction]);
      if (options.onContradictionDetected) {
        options.onContradictionDetected(contradiction);
      }
    },
    enabled: isMonitoring,
  });
  
  // Check for contradictions in a specific item
  const checkItem = (item) => {
    return detector.processItem(item);
  };
  
  // Start monitoring
  const startMonitoring = () => {
    setIsMonitoring(true);
    detector.startDetection();
  };
  
  // Stop monitoring
  const stopMonitoring = () => {
    setIsMonitoring(false);
    detector.stopDetection();
  };
  
  return {
    contradictions,
    isMonitoring,
    checkItem,
    startMonitoring,
    stopMonitoring,
    clearContradictions: () => setContradictions([]),
  };
};
