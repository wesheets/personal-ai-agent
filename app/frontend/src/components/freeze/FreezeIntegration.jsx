import React from 'react';
import { Box, Flex, Heading, Text, Divider, useColorModeValue } from '@chakra-ui/react';
import FreezeResolutionPanel, { FreezeBadge, FreezeStatusIndicator } from './freeze/FreezeResolutionPanel';
import { useLoopFreezeController } from '../logic/LoopFreezeController';

/**
 * FreezeIntegration Component
 * 
 * Provides integration points for the freeze lock system with existing components.
 * This component serves as a central hub for integrating freeze functionality.
 */
const FreezeIntegration = () => {
  return (
    <Box>
      <Heading size="md" mb={4}>Freeze Integration</Heading>
      <Text mb={4}>
        This component provides integration points for the freeze lock system with existing components.
      </Text>
    </Box>
  );
};

/**
 * LoopPlannerIntegration Component
 * 
 * Integrates with LoopPlanner.js to halt final plan unless freeze is cleared.
 */
export const LoopPlannerIntegration = ({ loopId, loopState, onReReflect }) => {
  const { canLoopExecute } = useLoopFreezeController({});
  
  // Check if loop can execute
  const executionStatus = canLoopExecute(loopId, loopState);
  
  if (!executionStatus.can_execute) {
    return (
      <Box mb={4}>
        <FreezeResolutionPanel
          loopId={loopId}
          loopState={loopState}
          onReReflect={onReReflect}
        />
      </Box>
    );
  }
  
  return null;
};

/**
 * RecursiveReflectionIntegration Component
 * 
 * Integrates with RecursiveReflectionEngine.js to update loop status on recursive fail.
 */
export const RecursiveReflectionIntegration = ({ loopId, reflectionState, onStatusChange }) => {
  const { processLoopState } = useLoopFreezeController({});
  
  // Process reflection state to update freeze status
  const handleProcessState = () => {
    const result = processLoopState(loopId, {
      ...reflectionState,
      confidence_score: reflectionState.confidence || 0,
      contradictions_unresolved: reflectionState.contradictions || 0
    });
    
    if (result.action !== 'proceed') {
      onStatusChange(result);
    }
  };
  
  return null; // This is a functional component, not a visual one
};

/**
 * AgentChatIntegration Component
 * 
 * Integrates with AgentChatConsole to show freeze status near loop summaries.
 */
export const AgentChatIntegration = ({ loopId, size = 'sm' }) => {
  const { isLoopFrozen } = useLoopFreezeController({});
  
  if (!isLoopFrozen(loopId)) {
    return null;
  }
  
  return <FreezeBadge loopId={loopId} size={size} />;
};

/**
 * OperatorHUDIntegration Component
 * 
 * Integrates with OperatorHUDBar to show system frozen alert badge.
 */
export const OperatorHUDIntegration = ({ loopIds = [] }) => {
  const { isLoopFrozen } = useLoopFreezeController({});
  const bgColor = useColorModeValue('red.50', 'red.900');
  const borderColor = useColorModeValue('red.200', 'red.700');
  
  // Check if any loops are frozen
  const frozenLoops = loopIds.filter(id => isLoopFrozen(id));
  
  if (frozenLoops.length === 0) {
    return null;
  }
  
  return (
    <Box
      p={2}
      borderRadius="md"
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
    >
      <Flex align="center" justify="space-between">
        <Text fontWeight="bold">System Alert: {frozenLoops.length} Loop{frozenLoops.length > 1 ? 's' : ''} Frozen</Text>
        <FreezeBadge loopId={frozenLoops[0]} size="sm" />
      </Flex>
    </Box>
  );
};

export default FreezeIntegration;
