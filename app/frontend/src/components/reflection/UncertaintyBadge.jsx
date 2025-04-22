import React, { useState, useEffect } from 'react';
import {
  Badge,
  Box,
  Flex,
  Text,
  Tooltip,
  Spinner,
  HStack,
  VStack,
  useColorModeValue,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverBody,
  PopoverArrow,
  PopoverCloseButton,
} from '@chakra-ui/react';
import { FiAlertCircle, FiClock, FiRefreshCw, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';

/**
 * UncertaintyBadge Component
 * 
 * Shows when a loop is paused for reflection, displaying status messages like:
 * - "Confidence too low — reflecting again"
 * - "Trust threshold breached — waiting for resolution"
 * 
 * Renders above loop card or in LoopTraceViewer
 */
const UncertaintyBadge = ({
  isReflecting = false,
  reason = '',
  reflectionDepth = 0,
  maxDepth = 3,
  agent = 'SAGE',
  confidence = null,
  timestamp = null,
  size = 'md',
  showDetails = true,
  onComplete = null,
}) => {
  // Color mode values
  const bgColor = useColorModeValue('red.50', 'red.900');
  const borderColor = useColorModeValue('red.200', 'red.700');
  const textColor = useColorModeValue('red.800', 'red.100');
  const spinnerColor = useColorModeValue('red.500', 'red.300');
  
  // State for animation
  const [isAnimating, setIsAnimating] = useState(false);
  
  // Start animation when reflection starts
  useEffect(() => {
    if (isReflecting) {
      setIsAnimating(true);
    } else {
      setIsAnimating(false);
    }
  }, [isReflecting]);
  
  // Get status message based on reason
  const getStatusMessage = () => {
    switch (reason) {
      case 'low_confidence':
        return 'Confidence too low — reflecting again';
      case 'trust_decay':
        return 'Trust threshold breached — waiting for resolution';
      case 'unresolved_contradiction':
        return 'Contradiction detected — resolving conflict';
      case 'high_drift':
        return 'Drift detected — recalibrating beliefs';
      case 'no_manual_override':
        return 'Awaiting operator confirmation';
      case 'max_depth_reached':
        return 'Maximum reflection depth reached';
      default:
        return 'Reflecting on current state';
    }
  };
  
  // Get icon based on reason
  const getIcon = () => {
    switch (reason) {
      case 'low_confidence':
        return <FiThumbsDown />;
      case 'trust_decay':
        return <FiAlertCircle />;
      case 'unresolved_contradiction':
        return <FiRefreshCw />;
      case 'high_drift':
        return <FiClock />;
      case 'no_manual_override':
        return <FiThumbsUp />;
      case 'max_depth_reached':
        return <FiAlertCircle />;
      default:
        return <FiRefreshCw />;
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  // If not reflecting and no details needed, return null
  if (!isReflecting && !showDetails) {
    return null;
  }
  
  // Compact badge for small size
  if (size === 'sm' && !showDetails) {
    return (
      <Tooltip label={getStatusMessage()}>
        <Badge colorScheme="red" variant="subtle">
          <Flex align="center">
            {isReflecting && <Spinner size="xs" mr={1} />}
            {getIcon()}
            <Text ml={1}>Reflecting</Text>
          </Flex>
        </Badge>
      </Tooltip>
    );
  }
  
  // Full badge with popover for details
  return (
    <Popover trigger="hover" placement="top">
      <PopoverTrigger>
        <Box
          p={2}
          borderRadius="md"
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
          mb={2}
          cursor="pointer"
        >
          <Flex align="center">
            {isReflecting && (
              <Spinner
                size="sm"
                color={spinnerColor}
                mr={2}
                speed="0.8s"
              />
            )}
            {getIcon()}
            <Text ml={2} color={textColor} fontWeight="medium">
              {getStatusMessage()}
            </Text>
            {reflectionDepth > 0 && (
              <Badge ml={2} colorScheme="purple">
                Depth: {reflectionDepth}/{maxDepth}
              </Badge>
            )}
          </Flex>
        </Box>
      </PopoverTrigger>
      
      {showDetails && (
        <PopoverContent>
          <PopoverArrow />
          <PopoverCloseButton />
          <PopoverHeader>Reflection Details</PopoverHeader>
          <PopoverBody>
            <VStack align="start" spacing={2}>
              <HStack>
                <Text fontWeight="bold">Agent:</Text>
                <Text>{agent}</Text>
              </HStack>
              
              <HStack>
                <Text fontWeight="bold">Status:</Text>
                <Text>{isReflecting ? 'Active' : 'Completed'}</Text>
              </HStack>
              
              <HStack>
                <Text fontWeight="bold">Reason:</Text>
                <Text>{reason}</Text>
              </HStack>
              
              <HStack>
                <Text fontWeight="bold">Depth:</Text>
                <Text>{reflectionDepth}/{maxDepth}</Text>
              </HStack>
              
              {confidence !== null && (
                <HStack>
                  <Text fontWeight="bold">Confidence:</Text>
                  <Text>{(confidence * 100).toFixed(0)}%</Text>
                </HStack>
              )}
              
              {timestamp && (
                <HStack>
                  <Text fontWeight="bold">Time:</Text>
                  <Text>{formatTimestamp(timestamp)}</Text>
                </HStack>
              )}
            </VStack>
          </PopoverBody>
        </PopoverContent>
      )}
    </Popover>
  );
};

/**
 * UncertaintyBadgeStack Component
 * 
 * Displays a stack of uncertainty badges for a loop with multiple reflections
 */
export const UncertaintyBadgeStack = ({
  reflections = [],
  isActive = false,
  maxDepth = 3,
}) => {
  if (reflections.length === 0 && !isActive) {
    return null;
  }
  
  return (
    <VStack align="stretch" spacing={1} mb={3}>
      {reflections.map((reflection, index) => (
        <UncertaintyBadge
          key={index}
          isReflecting={false}
          reason={reflection.reason}
          reflectionDepth={reflection.depth}
          maxDepth={maxDepth}
          agent={reflection.agent}
          confidence={reflection.confidence}
          timestamp={reflection.timestamp}
          showDetails={true}
        />
      ))}
      
      {isActive && (
        <UncertaintyBadge
          isReflecting={true}
          reason="reflecting"
          reflectionDepth={reflections.length + 1}
          maxDepth={maxDepth}
          showDetails={true}
        />
      )}
    </VStack>
  );
};

export default UncertaintyBadge;
