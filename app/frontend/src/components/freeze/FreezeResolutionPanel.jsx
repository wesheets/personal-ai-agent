import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Badge,
  Button,
  ButtonGroup,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  VStack,
  HStack,
  Tooltip,
  useColorModeValue,
  Collapse,
  Icon,
  Spinner,
} from '@chakra-ui/react';
import { FiAlertTriangle, FiLock, FiUnlock, FiRefreshCw, FiThumbsUp, FiInfo } from 'react-icons/fi';
import { useLoopFreezeController } from '../../logic/LoopFreezeController';

/**
 * FreezeResolutionPanel Component
 * 
 * UI component that displays:
 * - Why the loop is frozen
 * - Suggested resolution (e.g. re-run reflection, escalate to SAGE, or override)
 * - Button to Override Freeze (manual unlock)
 */
const FreezeResolutionPanel = ({
  loopId,
  loopState = {},
  onReReflect = () => {},
  onOverride = () => {},
  onEscalate = () => {},
  showWhenUnfrozen = false,
  size = 'md',
}) => {
  // Color mode values
  const bgColor = useColorModeValue('red.50', 'red.900');
  const borderColor = useColorModeValue('red.200', 'red.700');
  const textColor = useColorModeValue('red.800', 'red.100');
  const buttonColorScheme = useColorModeValue('red', 'red');
  
  // Get freeze controller
  const {
    isLoopFrozen,
    getLoopFreezeEvent,
    overrideFreeze,
    canLoopExecute,
    processLoopState,
  } = useLoopFreezeController({});
  
  // State
  const [freezeStatus, setFreezeStatus] = useState({
    isFrozen: false,
    event: null,
    executionStatus: null,
  });
  const [isExpanded, setIsExpanded] = useState(true);
  
  // Update freeze status when loopId or loopState changes
  useEffect(() => {
    if (!loopId) return;
    
    // Check if loop is frozen
    const isFrozen = isLoopFrozen(loopId);
    const freezeEvent = getLoopFreezeEvent(loopId);
    
    // Check if loop can execute
    const executionStatus = canLoopExecute(loopId, loopState);
    
    // Update state
    setFreezeStatus({
      isFrozen,
      event: freezeEvent,
      executionStatus,
    });
    
    // Auto-expand when frozen
    if (isFrozen || !executionStatus.can_execute) {
      setIsExpanded(true);
    }
  }, [loopId, loopState, isLoopFrozen, getLoopFreezeEvent, canLoopExecute]);
  
  // Handle re-reflection
  const handleReReflect = () => {
    onReReflect(freezeStatus.event);
  };
  
  // Handle override
  const handleOverride = () => {
    const updatedEvent = overrideFreeze(loopId, 'manual_operator_override');
    onOverride(updatedEvent);
  };
  
  // Handle escalation
  const handleEscalate = () => {
    onEscalate(freezeStatus.event);
  };
  
  // Get action button based on required action
  const getActionButton = () => {
    const event = freezeStatus.event || freezeStatus.executionStatus?.freeze_event;
    if (!event) return null;
    
    switch (event.required_action) {
      case 're-reflect':
        return (
          <Button
            leftIcon={<FiRefreshCw />}
            colorScheme="blue"
            onClick={handleReReflect}
          >
            Re-run Reflection
          </Button>
        );
      case 'operator_override':
        return (
          <Button
            leftIcon={<FiThumbsUp />}
            colorScheme="green"
            onClick={handleOverride}
          >
            Approve & Override
          </Button>
        );
      default:
        return (
          <Button
            leftIcon={<FiInfo />}
            colorScheme="gray"
            onClick={handleEscalate}
          >
            Escalate to SAGE
          </Button>
        );
    }
  };
  
  // If not frozen and not showing when unfrozen, return null
  if (!freezeStatus.isFrozen && !freezeStatus.executionStatus?.freeze_event && !showWhenUnfrozen) {
    return null;
  }
  
  // If not frozen but showing when unfrozen, show minimal panel
  if (!freezeStatus.isFrozen && !freezeStatus.executionStatus?.freeze_event && showWhenUnfrozen) {
    return (
      <Box
        p={2}
        borderRadius="md"
        bg="green.50"
        borderWidth="1px"
        borderColor="green.200"
        mb={2}
      >
        <Flex align="center" justify="space-between">
          <HStack>
            <Icon as={FiUnlock} color="green.500" />
            <Text color="green.800" fontWeight="medium">
              Loop is clear to execute
            </Text>
          </HStack>
          <Badge colorScheme="green">Execution Approved</Badge>
        </Flex>
      </Box>
    );
  }
  
  // Get event data
  const event = freezeStatus.event || freezeStatus.executionStatus?.freeze_event;
  
  // Compact panel for small size
  if (size === 'sm') {
    return (
      <Alert status="error" variant="left-accent" mb={2}>
        <AlertIcon />
        <Flex justify="space-between" width="100%" align="center">
          <AlertTitle>Loop Frozen: {event.reason}</AlertTitle>
          <ButtonGroup size="sm">
            {getActionButton()}
            <Button
              leftIcon={<FiUnlock />}
              colorScheme={buttonColorScheme}
              variant="outline"
              onClick={handleOverride}
            >
              Override
            </Button>
          </ButtonGroup>
        </Flex>
      </Alert>
    );
  }
  
  // Full panel
  return (
    <Box
      p={4}
      borderRadius="md"
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
      mb={4}
    >
      <Flex direction="column">
        <Flex justify="space-between" align="center" mb={2}>
          <HStack>
            <Icon as={FiLock} boxSize={5} color={textColor} />
            <Heading size="md" color={textColor}>
              Loop Execution Frozen
            </Heading>
          </HStack>
          <Badge colorScheme="red" fontSize="md" px={2} py={1}>
            {event.status.toUpperCase()}
          </Badge>
        </Flex>
        
        <Divider mb={3} />
        
        <Collapse in={isExpanded} animateOpacity>
          <VStack align="stretch" spacing={3}>
            <Box>
              <Text fontWeight="bold" mb={1}>Reason:</Text>
              <Alert status="error" variant="left-accent">
                <AlertIcon />
                <AlertDescription>{event.reason}</AlertDescription>
              </Alert>
            </Box>
            
            <Box>
              <Text fontWeight="bold" mb={1}>Required Action:</Text>
              <Alert status="info" variant="left-accent">
                <AlertIcon />
                <AlertDescription>
                  {event.required_action === 're-reflect' && 'Additional reflection needed before proceeding'}
                  {event.required_action === 'operator_override' && 'Operator approval required to proceed'}
                  {event.required_action === 'none' && 'No specific action required'}
                </AlertDescription>
              </Alert>
            </Box>
            
            <Box>
              <Text fontWeight="bold" mb={1}>Loop State:</Text>
              <VStack align="stretch" spacing={1}>
                {event.original_state?.confidence_score !== undefined && (
                  <HStack justify="space-between">
                    <Text>Confidence Score:</Text>
                    <Badge colorScheme={event.original_state.confidence_score < 0.6 ? "red" : "green"}>
                      {(event.original_state.confidence_score * 100).toFixed(0)}%
                    </Badge>
                  </HStack>
                )}
                {event.original_state?.trust_score !== undefined && (
                  <HStack justify="space-between">
                    <Text>Trust Score:</Text>
                    <Badge colorScheme={event.original_state.trust_score < 0.5 ? "red" : "green"}>
                      {(event.original_state.trust_score * 100).toFixed(0)}%
                    </Badge>
                  </HStack>
                )}
                {event.original_state?.reflection_depth !== undefined && (
                  <HStack justify="space-between">
                    <Text>Reflection Depth:</Text>
                    <Badge colorScheme="purple">{event.original_state.reflection_depth}</Badge>
                  </HStack>
                )}
                {event.original_state?.contradictions_unresolved !== undefined && (
                  <HStack justify="space-between">
                    <Text>Unresolved Contradictions:</Text>
                    <Badge colorScheme={event.original_state.contradictions_unresolved > 0 ? "red" : "green"}>
                      {event.original_state.contradictions_unresolved}
                    </Badge>
                  </HStack>
                )}
                {event.original_state?.manual_override !== undefined && (
                  <HStack justify="space-between">
                    <Text>Manual Override:</Text>
                    <Badge colorScheme={event.original_state.manual_override ? "green" : "gray"}>
                      {event.original_state.manual_override ? "Yes" : "No"}
                    </Badge>
                  </HStack>
                )}
              </VStack>
            </Box>
            
            <Divider />
            
            <Box>
              <Text fontWeight="bold" mb={2}>Resolution Options:</Text>
              <ButtonGroup spacing={3}>
                {getActionButton()}
                <Tooltip label="Manually override freeze and allow execution">
                  <Button
                    leftIcon={<FiUnlock />}
                    colorScheme={buttonColorScheme}
                    variant="outline"
                    onClick={handleOverride}
                  >
                    Manual Override
                  </Button>
                </Tooltip>
                <Tooltip label="Escalate to SAGE for resolution">
                  <Button
                    leftIcon={<FiAlertTriangle />}
                    colorScheme="gray"
                    variant="outline"
                    onClick={handleEscalate}
                  >
                    Escalate
                  </Button>
                </Tooltip>
              </ButtonGroup>
            </Box>
          </VStack>
        </Collapse>
        
        {!isExpanded && (
          <Button
            variant="link"
            onClick={() => setIsExpanded(true)}
            mt={2}
          >
            Show Details
          </Button>
        )}
        
        {isExpanded && (
          <Button
            variant="link"
            onClick={() => setIsExpanded(false)}
            mt={2}
          >
            Hide Details
          </Button>
        )}
      </Flex>
    </Box>
  );
};

/**
 * FreezeBadge Component
 * 
 * Simple badge component for showing freeze status in other components.
 */
export const FreezeBadge = ({ loopId, size = 'md' }) => {
  // Get freeze controller
  const { isLoopFrozen, getLoopFreezeEvent } = useLoopFreezeController({});
  
  // State
  const [isFrozen, setIsFrozen] = useState(false);
  const [freezeEvent, setFreezeEvent] = useState(null);
  
  // Update state when loopId changes
  useEffect(() => {
    if (!loopId) return;
    
    // Check if loop is frozen
    const frozen = isLoopFrozen(loopId);
    const event = getLoopFreezeEvent(loopId);
    
    setIsFrozen(frozen);
    setFreezeEvent(event);
  }, [loopId, isLoopFrozen, getLoopFreezeEvent]);
  
  if (!isFrozen) {
    return null;
  }
  
  if (size === 'sm') {
    return (
      <Badge colorScheme="red" variant="subtle">
        <Flex align="center">
          <Icon as={FiLock} mr={1} />
          <Text>Frozen</Text>
        </Flex>
      </Badge>
    );
  }
  
  return (
    <Badge colorScheme="red" px={2} py={1} borderRadius="md">
      <Flex align="center">
        <Icon as={FiLock} mr={1} />
        <Text>Execution Frozen: {freezeEvent?.reason}</Text>
      </Flex>
    </Badge>
  );
};

/**
 * FreezeStatusIndicator Component
 * 
 * Minimal indicator for showing freeze status.
 */
export const FreezeStatusIndicator = ({ loopId, showUnfrozen = false }) => {
  // Get freeze controller
  const { isLoopFrozen, getLoopFreezeEvent } = useLoopFreezeController({});
  
  // State
  const [isFrozen, setIsFrozen] = useState(false);
  const [freezeEvent, setFreezeEvent] = useState(null);
  
  // Update state when loopId changes
  useEffect(() => {
    if (!loopId) return;
    
    // Check if loop is frozen
    const frozen = isLoopFrozen(loopId);
    const event = getLoopFreezeEvent(loopId);
    
    setIsFrozen(frozen);
    setFreezeEvent(event);
  }, [loopId, isLoopFrozen, getLoopFreezeEvent]);
  
  if (!isFrozen && !showUnfrozen) {
    return null;
  }
  
  if (!isFrozen && showUnfrozen) {
    return (
      <Flex align="center">
        <Icon as={FiUnlock} color="green.500" mr={1} />
        <Text color="green.500" fontWeight="medium">Clear</Text>
      </Flex>
    );
  }
  
  return (
    <Flex align="center">
      <Icon as={FiLock} color="red.500" mr={1} />
      <Text color="red.500" fontWeight="medium">Frozen</Text>
    </Flex>
  );
};

export default FreezeResolutionPanel;
