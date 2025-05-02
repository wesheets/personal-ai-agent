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
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverBody,
  PopoverArrow,
  PopoverCloseButton,
} from '@chakra-ui/react';
import { FiAlertTriangle, FiInfo, FiShield, FiTrendingDown, FiTrendingUp } from 'react-icons/fi';
import { useTrustScoreEvaluator } from '../../logic/TrustScoreEvaluator';
import { useAutoDemoteAgent } from '../../logic/AutoDemoteAgent';

/**
 * TrustBadge Component
 * 
 * Displays a badge with the current trust score for an agent.
 */
export const TrustBadge = ({ agent, size = 'md' }) => {
  const { getTrustScore, getTrustStatus } = useTrustScoreEvaluator({});
  const [score, setScore] = useState(0.7);
  const [status, setStatus] = useState('active');
  
  // Update score and status
  useEffect(() => {
    setScore(getTrustScore(agent));
    setStatus(getTrustStatus(agent));
  }, [agent, getTrustScore, getTrustStatus]);
  
  // Get badge color based on trust status
  const getBadgeProps = () => {
    switch (status) {
      case 'active':
        return { colorScheme: 'green', variant: 'subtle' };
      case 'warning':
        return { colorScheme: 'yellow', variant: 'subtle' };
      case 'demoted':
        return { colorScheme: 'red', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  return (
    <Popover trigger="hover" placement="top">
      <PopoverTrigger>
        <Badge {...getBadgeProps()} fontSize={size}>
          Trust: {(score * 100).toFixed(0)}%
        </Badge>
      </PopoverTrigger>
      <PopoverContent>
        <PopoverArrow />
        <PopoverCloseButton />
        <PopoverHeader>Agent Trust Score</PopoverHeader>
        <PopoverBody>
          <VStack align="start" spacing={2}>
            <Text fontSize="sm">
              Agent: <strong>{agent}</strong>
            </Text>
            <Text fontSize="sm">
              Trust Score: <strong>{(score * 100).toFixed(1)}%</strong>
            </Text>
            <Text fontSize="sm">
              Status: <strong>{status}</strong>
            </Text>
            <Text fontSize="xs" color="gray.500">
              Trust scores evaluate agent performance based on multiple factors.
            </Text>
          </VStack>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

/**
 * TrustAlert Component
 * 
 * Displays an alert when an agent's trust score drops below a threshold.
 */
export const TrustAlert = ({ agent, threshold = 0.6 }) => {
  const { getTrustScore, getTrustStatus } = useTrustScoreEvaluator({});
  const { isAgentDemoted, getEffectiveAgent } = useAutoDemoteAgent({});
  const [score, setScore] = useState(0.7);
  const [status, setStatus] = useState('active');
  const [isDemoted, setIsDemoted] = useState(false);
  const [effectiveAgent, setEffectiveAgent] = useState(agent);
  
  // Update state
  useEffect(() => {
    setScore(getTrustScore(agent));
    setStatus(getTrustStatus(agent));
    setIsDemoted(isAgentDemoted(agent));
    setEffectiveAgent(getEffectiveAgent(agent));
  }, [agent, getTrustScore, getTrustStatus, isAgentDemoted, getEffectiveAgent]);
  
  // Don't show alert if trust is above threshold
  if (score >= threshold && !isDemoted) {
    return null;
  }
  
  return (
    <Box
      p={2}
      borderRadius="md"
      bg={useColorModeValue('red.50', 'red.900')}
      borderWidth="1px"
      borderColor={useColorModeValue('red.200', 'red.700')}
      mb={4}
    >
      <Flex align="center">
        <FiAlertTriangle color="red" />
        <Text ml={2} fontSize="sm" fontWeight="medium">
          {isDemoted ? (
            <>
              Agent <strong>{agent}</strong> has been demoted due to low trust. 
              Using <strong>{effectiveAgent}</strong> instead.
            </>
          ) : (
            <>
              Agent <strong>{agent}</strong> has low trust ({(score * 100).toFixed(0)}%).
              Consider reviewing recent outputs.
            </>
          )}
        </Text>
      </Flex>
    </Box>
  );
};

/**
 * TrustMeter Component
 * 
 * Displays a visual meter of an agent's trust score.
 */
export const TrustMeter = ({ agent, showLabel = true, size = 'md' }) => {
  const { getTrustScore, getTrustStatus } = useTrustScoreEvaluator({});
  const [score, setScore] = useState(0.7);
  const [status, setStatus] = useState('active');
  
  // Update score and status
  useEffect(() => {
    setScore(getTrustScore(agent));
    setStatus(getTrustStatus(agent));
  }, [agent, getTrustScore, getTrustStatus]);
  
  // Get color based on trust score
  const getColor = () => {
    if (score >= 0.8) return 'green.500';
    if (score >= 0.6) return 'blue.500';
    if (score >= 0.4) return 'yellow.500';
    return 'red.500';
  };
  
  // Get icon based on trust status
  const getIcon = () => {
    switch (status) {
      case 'active':
        return <FiShield color="green" />;
      case 'warning':
        return <FiInfo color="orange" />;
      case 'demoted':
        return <FiAlertTriangle color="red" />;
      default:
        return <FiInfo color="gray" />;
    }
  };
  
  return (
    <Tooltip label={`Trust Score: ${(score * 100).toFixed(1)}%`}>
      <Flex align="center">
        {getIcon()}
        <Box
          ml={2}
          mr={2}
          height={size === 'sm' ? '8px' : size === 'md' ? '12px' : '16px'}
          width={size === 'sm' ? '60px' : size === 'md' ? '80px' : '100px'}
          bg={useColorModeValue('gray.200', 'gray.700')}
          borderRadius="full"
        >
          <Box
            height="100%"
            width={`${score * 100}%`}
            bg={getColor()}
            borderRadius="full"
            transition="width 0.3s ease-in-out"
          />
        </Box>
        {showLabel && (
          <Text fontSize={size === 'sm' ? 'xs' : size === 'md' ? 'sm' : 'md'}>
            {(score * 100).toFixed(0)}%
          </Text>
        )}
      </Flex>
    </Tooltip>
  );
};

/**
 * TrustDeltaIndicator Component
 * 
 * Displays an indicator for trust score changes.
 */
export const TrustDeltaIndicator = ({ delta }) => {
  if (Math.abs(delta) < 0.01) {
    return null;
  }
  
  const isPositive = delta > 0;
  const color = isPositive ? 'green.500' : 'red.500';
  const Icon = isPositive ? FiTrendingUp : FiTrendingDown;
  
  return (
    <Flex align="center" color={color}>
      <Icon />
      <Text ml={1} fontSize="sm" fontWeight="medium">
        {isPositive ? '+' : ''}{(delta * 100).toFixed(1)}%
      </Text>
    </Flex>
  );
};

/**
 * useTrustMonitor Hook
 * 
 * Custom hook for components to monitor and react to trust changes.
 */
export const useTrustMonitor = (agent) => {
  const { 
    getTrustScore, 
    getTrustStatus,
    getTrustHistory
  } = useTrustScoreEvaluator({});
  
  const {
    isAgentDemoted,
    getEffectiveAgent
  } = useAutoDemoteAgent({});
  
  const [trustData, setTrustData] = useState({
    score: 0.7,
    status: 'active',
    isDemoted: false,
    effectiveAgent: agent,
    history: []
  });
  
  // Update trust data
  useEffect(() => {
    const updateTrustData = () => {
      setTrustData({
        score: getTrustScore(agent),
        status: getTrustStatus(agent),
        isDemoted: isAgentDemoted(agent),
        effectiveAgent: getEffectiveAgent(agent),
        history: getTrustHistory(agent)
      });
    };
    
    // Initial update
    updateTrustData();
    
    // Set up interval for periodic updates
    const updateInterval = setInterval(updateTrustData, 10000);
    
    return () => clearInterval(updateInterval);
  }, [agent, getTrustScore, getTrustStatus, isAgentDemoted, getEffectiveAgent, getTrustHistory]);
  
  return trustData;
};

/**
 * TrustIntegration Component
 * 
 * Main component that provides trust monitoring functionality.
 */
const TrustIntegration = () => {
  return (
    <Box>
      <Heading size="md" mb={4}>Trust Monitoring</Heading>
      <Text mb={4}>
        This component provides trust monitoring for all agents in the system.
        It evaluates agent performance based on multiple factors and adjusts their
        influence in future loops accordingly.
      </Text>
      
      <VStack align="stretch" spacing={4}>
        <Box>
          <Heading size="sm" mb={2}>Agent Trust Scores</Heading>
          <HStack spacing={4}>
            <VStack align="start">
              <Text fontSize="sm">SAGE:</Text>
              <TrustMeter agent="SAGE" />
            </VStack>
            <VStack align="start">
              <Text fontSize="sm">NOVA:</Text>
              <TrustMeter agent="NOVA" />
            </VStack>
            <VStack align="start">
              <Text fontSize="sm">HAL:</Text>
              <TrustMeter agent="HAL" />
            </VStack>
            <VStack align="start">
              <Text fontSize="sm">CRITIC:</Text>
              <TrustMeter agent="CRITIC" />
            </VStack>
          </HStack>
        </Box>
        
        <Box>
          <Heading size="sm" mb={2}>Trust Alerts</Heading>
          <TrustAlert agent="HAL" />
          <Text fontSize="sm">
            Alerts appear when an agent's trust score drops below a threshold.
            Agents may be automatically demoted if their trust score is too low.
          </Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default TrustIntegration;
