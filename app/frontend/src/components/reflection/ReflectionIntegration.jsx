import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Badge,
  Button,
  IconButton,
  HStack,
  VStack,
  useColorModeValue,
  Tooltip,
  Divider,
} from '@chakra-ui/react';
import { FiRefreshCw, FiAlertCircle, FiClock, FiThumbsUp } from 'react-icons/fi';
import UncertaintyBadge, { UncertaintyBadgeStack } from './UncertaintyBadge';
import { useRecursiveReflection } from '../../logic/RecursiveReflectionEngine';
import { useConfidenceThresholds } from '../../logic/ConfidenceThresholds';

/**
 * ReflectionIntegration Component
 * 
 * Integrates the recursive reflection system with existing components.
 * Provides hooks and UI components for other parts of the system to use.
 */
const ReflectionIntegration = () => {
  // Get recursive reflection and confidence thresholds
  const {
    isEnabled,
    processLoopState,
    getActiveReflection,
    getLoopReflectionHistory,
    enable,
    disable
  } = useRecursiveReflection({});
  
  const {
    thresholds,
    getThresholds,
    updateProjectThresholds
  } = useConfidenceThresholds({});
  
  return (
    <Box>
      <Heading size="md" mb={4}>Recursive Reflection System</Heading>
      <Text mb={4}>
        This system allows Promethios to recognize uncertainty and trigger additional
        reflection before proceeding with actions. It monitors confidence scores,
        trust metrics, contradictions, and other factors to determine when more
        reflection is needed.
      </Text>
      
      <VStack align="stretch" spacing={4}>
        <Box>
          <Heading size="sm" mb={2}>System Status</Heading>
          <HStack>
            <Badge colorScheme={isEnabled ? 'green' : 'red'}>
              {isEnabled ? 'Enabled' : 'Disabled'}
            </Badge>
            <Button
              size="sm"
              colorScheme={isEnabled ? 'red' : 'green'}
              onClick={isEnabled ? disable : enable}
            >
              {isEnabled ? 'Disable' : 'Enable'} Recursive Reflection
            </Button>
          </HStack>
        </Box>
        
        <Divider />
        
        <Box>
          <Heading size="sm" mb={2}>Example Uncertainty States</Heading>
          <VStack align="stretch" spacing={2}>
            <UncertaintyBadge
              isReflecting={true}
              reason="low_confidence"
              reflectionDepth={1}
              maxDepth={3}
              agent="SAGE"
              showDetails={true}
            />
            
            <UncertaintyBadge
              isReflecting={true}
              reason="trust_decay"
              reflectionDepth={2}
              maxDepth={3}
              agent="NOVA"
              showDetails={true}
            />
            
            <UncertaintyBadge
              isReflecting={false}
              reason="max_depth_reached"
              reflectionDepth={3}
              maxDepth={3}
              agent="CRITIC"
              confidence={0.85}
              timestamp={new Date().toISOString()}
              showDetails={true}
            />
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

/**
 * useReflectionMonitor Hook
 * 
 * Custom hook for components to monitor and react to reflection state.
 */
export const useReflectionMonitor = (loopId) => {
  const {
    processLoopState,
    getActiveReflection,
    getLoopReflectionHistory,
    completeReflection,
    cancelReflection
  } = useRecursiveReflection({});
  
  const [reflectionState, setReflectionState] = useState({
    isReflecting: false,
    activeReflection: null,
    reflectionHistory: [],
    reflectionDepth: 0
  });
  
  // Update reflection state
  useEffect(() => {
    if (!loopId) return;
    
    const updateReflectionState = () => {
      const activeReflection = getActiveReflection(loopId);
      const reflectionHistory = getLoopReflectionHistory(loopId);
      
      setReflectionState({
        isReflecting: !!activeReflection,
        activeReflection,
        reflectionHistory,
        reflectionDepth: reflectionHistory.length
      });
    };
    
    // Initial update
    updateReflectionState();
    
    // Set up interval for periodic updates
    const updateInterval = setInterval(updateReflectionState, 5000);
    
    return () => clearInterval(updateInterval);
  }, [loopId, getActiveReflection, getLoopReflectionHistory]);
  
  /**
   * Check if a loop needs reflection
   * 
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Processing result
   */
  const checkReflectionNeeded = (loopState) => {
    return processLoopState(loopId, {
      ...loopState,
      reflection_depth: reflectionState.reflectionDepth
    });
  };
  
  /**
   * Complete the current reflection
   * 
   * @param {Object} result - Reflection result
   * @returns {Object} Updated reflection
   */
  const finishReflection = (result) => {
    if (!reflectionState.isReflecting) return null;
    return completeReflection(loopId, result);
  };
  
  /**
   * Cancel the current reflection
   * 
   * @param {string} reason - Reason for cancellation
   * @returns {Object} Updated reflection
   */
  const abortReflection = (reason = 'manual_cancellation') => {
    if (!reflectionState.isReflecting) return null;
    return cancelReflection(loopId, reason);
  };
  
  return {
    ...reflectionState,
    checkReflectionNeeded,
    finishReflection,
    abortReflection
  };
};

/**
 * ReflectionBadge Component
 * 
 * Simple badge component for showing reflection status in other components.
 */
export const ReflectionBadge = ({ loopId, size = 'md' }) => {
  const {
    isReflecting,
    activeReflection,
    reflectionHistory,
    reflectionDepth
  } = useReflectionMonitor(loopId);
  
  if (!isReflecting && reflectionHistory.length === 0) {
    return null;
  }
  
  if (size === 'sm') {
    return (
      <Badge colorScheme="purple" variant="subtle">
        <Flex align="center">
          <FiRefreshCw />
          <Text ml={1}>Depth: {reflectionDepth}</Text>
        </Flex>
      </Badge>
    );
  }
  
  return (
    <UncertaintyBadgeStack
      reflections={reflectionHistory}
      isActive={isReflecting}
      maxDepth={3}
    />
  );
};

/**
 * LoopPlannerIntegration Component
 * 
 * Integration with LoopPlanner.js to wait for recursive reflection result if trigger is active.
 */
export const LoopPlannerIntegration = ({ loopId, loopState, onProceed, onWait }) => {
  const {
    isReflecting,
    activeReflection,
    checkReflectionNeeded
  } = useReflectionMonitor(loopId);
  
  // Check if reflection is needed when loop state changes
  useEffect(() => {
    if (!loopId || !loopState) return;
    
    // Skip if already reflecting
    if (isReflecting) {
      if (onWait) onWait(activeReflection);
      return;
    }
    
    // Check if reflection is needed
    const result = checkReflectionNeeded(loopState);
    
    if (result.action === 'reflect') {
      if (onWait) onWait(result.reflection);
    } else if (result.action === 'proceed') {
      if (onProceed) onProceed();
    }
  }, [loopId, loopState, isReflecting, activeReflection, checkReflectionNeeded, onProceed, onWait]);
  
  return null; // This is a logic-only component
};

/**
 * AgentChatIntegration Component
 * 
 * Integration with AgentChatConsole to show when Promethios chooses to delay itself.
 */
export const AgentChatIntegration = ({ loopId, messageId }) => {
  const {
    isReflecting,
    activeReflection,
    reflectionHistory
  } = useReflectionMonitor(loopId);
  
  if (!isReflecting && reflectionHistory.length === 0) {
    return null;
  }
  
  return (
    <Box mb={3}>
      <UncertaintyBadge
        isReflecting={isReflecting}
        reason={activeReflection ? activeReflection.triggered_by : 'reflecting'}
        reflectionDepth={reflectionHistory.length + (isReflecting ? 1 : 0)}
        maxDepth={3}
        agent={activeReflection ? activeReflection.agent : 'SAGE'}
        showDetails={true}
      />
      
      {isReflecting && (
        <Text fontSize="sm" fontStyle="italic" color="gray.500">
          Promethios is reflecting on this response before proceeding...
        </Text>
      )}
    </Box>
  );
};

/**
 * BeliefChangeIntegration Component
 * 
 * Integration with BeliefChangeLog to mark reflection-induced belief updates.
 */
export const BeliefChangeIntegration = ({ beliefChange }) => {
  // Check if belief change was triggered by reflection
  const isReflectionInduced = beliefChange && 
    beliefChange.source && 
    beliefChange.source.includes('reflection');
  
  if (!isReflectionInduced) {
    return null;
  }
  
  return (
    <Badge colorScheme="purple" ml={2}>
      <Flex align="center">
        <FiRefreshCw />
        <Text ml={1}>Reflection-induced</Text>
      </Flex>
    </Badge>
  );
};

/**
 * TrustTimelineIntegration Component
 * 
 * Integration with TrustHistoryTimeline to annotate when trust breach caused self-reflection.
 */
export const TrustTimelineIntegration = ({ trustEvent }) => {
  // Check if trust event triggered a reflection
  const triggeredReflection = trustEvent && 
    trustEvent.effects && 
    trustEvent.effects.includes('triggered_reflection');
  
  if (!triggeredReflection) {
    return null;
  }
  
  return (
    <Badge colorScheme="purple" ml={2}>
      <Flex align="center">
        <FiRefreshCw />
        <Text ml={1}>Triggered reflection</Text>
      </Flex>
    </Badge>
  );
};

export default ReflectionIntegration;
