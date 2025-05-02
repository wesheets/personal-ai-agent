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
  FaShieldAlt, 
  FaExclamationTriangle, 
  FaCheckCircle, 
  FaExclamationCircle,
  FaBalanceScale,
  FaLock,
  FaUserShield
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * TrustScoreDisplay Component
 * 
 * Displays trust scores and reliability metrics for the cognitive system.
 * Connected to /api/trust/scores endpoint for trust score data.
 */
const TrustScoreDisplay = ({ projectId = 'promethios-core' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  
  // Fetch trust score data from API
  const { 
    data: trustData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/trust/scores?projectId=${projectId}`, {}, {
    refreshInterval: 60000, // Refresh every minute
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'trust_score_manager',
      timestamp: new Date().toISOString(),
      overall_trust: 92,
      trust_trend: 'stable',
      categories: [
        { name: 'Belief Consistency', score: 95, previous_score: 94, status: 'healthy' },
        { name: 'Memory Integrity', score: 88, previous_score: 85, status: 'healthy' },
        { name: 'Reasoning Reliability', score: 94, previous_score: 94, status: 'healthy' },
        { name: 'Output Accuracy', score: 91, previous_score: 93, status: 'degraded' },
        { name: 'Safety Compliance', score: 97, previous_score: 97, status: 'healthy' }
      ],
      recent_events: [
        { 
          type: 'score_change', 
          category: 'Output Accuracy', 
          old_score: 93, 
          new_score: 91, 
          timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          reason: 'Minor factual inconsistencies detected in recent outputs'
        },
        { 
          type: 'audit_completed', 
          result: 'passed', 
          timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          details: 'Full system trust audit completed successfully'
        }
      ]
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'trust_score_manager',
      timestamp: data.timestamp || new Date().toISOString(),
      overall_trust: data.overall_trust || 0,
      trust_trend: data.trust_trend || 'stable',
      categories: Array.isArray(data.categories) ? data.categories : [],
      recent_events: Array.isArray(data.recent_events) ? data.recent_events : []
    })
  });
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Format time ago
  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = Math.abs(now - date);
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);
      
      if (diffDays > 0) return `${diffDays}d ago`;
      if (diffHours > 0) return `${diffHours}h ago`;
      return `${diffMins}m ago`;
    } catch (error) {
      return 'Unknown';
    }
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
  
  // Get trend icon and color
  const getTrendInfo = (trend) => {
    switch (trend) {
      case 'improving':
        return { icon: FaArrowUp, color: 'green' };
      case 'declining':
        return { icon: FaArrowDown, color: 'red' };
      case 'stable':
      default:
        return { icon: FaArrowRight, color: 'blue' };
    }
  };
  
  // Get trust score color
  const getTrustScoreColor = (score) => {
    if (score >= 90) return 'green';
    if (score >= 70) return 'yellow';
    if (score >= 50) return 'orange';
    return 'red';
  };
  
  // Get event icon
  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'score_change':
        return FaBalanceScale;
      case 'audit_completed':
        return FaCheckCircle;
      case 'security_alert':
        return FaExclamationTriangle;
      default:
        return FaInfoCircle;
    }
  };
  
  // Get event color
  const getEventColor = (event) => {
    if (event.type === 'score_change') {
      return event.new_score >= event.old_score ? 'green' : 'yellow';
    }
    if (event.type === 'audit_completed') {
      return event.result === 'passed' ? 'green' : 'red';
    }
    if (event.type === 'security_alert') {
      return 'red';
    }
    return 'blue';
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
        Trust Scores
      </Text>
      
      {loading && !trustData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !trustData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading trust scores: {error}</Text>
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {/* Overall Trust Score Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Flex justify="space-between" align="center" mb={4}>
              <HStack>
                <Icon as={FaShieldAlt} color="blue.500" boxSize={6} />
                <Text fontWeight="bold">Overall Trust Score</Text>
              </HStack>
              <Badge 
                colorScheme={getTrustScoreColor(trustData?.overall_trust || 0)}
                fontSize="lg"
                px={3}
                py={1}
                borderRadius="full"
              >
                {trustData?.overall_trust || 0}%
              </Badge>
            </Flex>
            
            <CircularProgress 
              value={trustData?.overall_trust || 0} 
              color={getTrustScoreColor(trustData?.overall_trust || 0)}
              size="120px"
              thickness="8px"
              mx="auto"
              mb={4}
            >
              <CircularProgressLabel fontSize="xl" fontWeight="bold">
                {trustData?.overall_trust || 0}%
              </CircularProgressLabel>
            </CircularProgress>
            
            <Flex justify="center" align="center">
              <Badge 
                colorScheme={getTrendInfo(trustData?.trust_trend).color}
                variant="subtle"
                px={2}
                py={1}
              >
                <HStack>
                  <Icon as={getTrendInfo(trustData?.trust_trend).icon} />
                  <Text>{trustData?.trust_trend || 'stable'}</Text>
                </HStack>
              </Badge>
            </Flex>
          </Box>
          
          {/* Trust Categories Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Text fontWeight="bold" mb={3}>Trust Categories</Text>
            <VStack spacing={3} align="stretch">
              {trustData?.categories?.map((category, index) => (
                <Box 
                  key={index} 
                  p={3} 
                  borderRadius="md" 
                  bg={useColorModeValue('white', 'gray.700')}
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <HStack>
                      <Icon 
                        as={category.status === 'healthy' ? FaCheckCircle : FaExclamationCircle} 
                        color={getStatusColor(category.status)} 
                      />
                      <Text fontWeight="medium">{category.name}</Text>
                    </HStack>
                    <Badge colorScheme={getTrustScoreColor(category.score)}>
                      {category.score}%
                    </Badge>
                  </Flex>
                  
                  <Progress 
                    value={category.score} 
                    colorScheme={getTrustScoreColor(category.score)}
                    size="sm"
                    borderRadius="full"
                    mt={1}
                  />
                  
                  <Flex justify="flex-end" mt={1}>
                    <Text fontSize="xs" color="gray.500">
                      {category.previous_score < category.score ? (
                        <Text as="span" color="green.500">
                          ↑ {category.score - category.previous_score}%
                        </Text>
                      ) : category.previous_score > category.score ? (
                        <Text as="span" color="red.500">
                          ↓ {category.previous_score - category.score}%
                        </Text>
                      ) : (
                        <Text as="span">
                          ↔ No change
                        </Text>
                      )}
                    </Text>
                  </Flex>
                </Box>
              ))}
            </VStack>
          </Box>
          
          {/* Recent Events Section */}
          {trustData?.recent_events?.length > 0 && (
            <Box 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Text fontWeight="bold" mb={3}>Recent Events</Text>
              <VStack spacing={2} align="stretch">
                {trustData.recent_events.map((event, index) => (
                  <Box 
                    key={index} 
                    p={3} 
                    borderRadius="md" 
                    bg={useColorModeValue('white', 'gray.700')}
                    borderLeftWidth="4px"
                    borderLeftColor={getEventColor(event)}
                  >
                    <Flex justify="space-between" align="center" mb={1}>
                      <HStack>
                        <Icon 
                          as={getEventIcon(event.type)} 
                          color={getEventColor(event)} 
                        />
                        <Text fontWeight="medium">
                          {event.type === 'score_change' 
                            ? `${event.category} Score Change` 
                            : event.type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </Text>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">
                        {formatTimeAgo(event.timestamp)}
                      </Text>
                    </Flex>
                    
                    {event.type === 'score_change' && (
                      <HStack spacing={2} mt={1}>
                        <Text fontSize="sm">{event.old_score}%</Text>
                        <Icon 
                          as={FaArrowRight} 
                          color={event.new_score >= event.old_score ? 'green.500' : 'red.500'} 
                        />
                        <Text 
                          fontSize="sm" 
                          fontWeight="bold"
                          color={event.new_score >= event.old_score ? 'green.500' : 'red.500'}
                        >
                          {event.new_score}%
                        </Text>
                      </HStack>
                    )}
                    
                    {event.reason && (
                      <Text fontSize="sm" mt={1}>
                        {event.reason}
                      </Text>
                    )}
                    
                    {event.details && (
                      <Text fontSize="sm" mt={1}>
                        {event.details}
                      </Text>
                    )}
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Last updated: {formatTimestamp(trustData?.timestamp || Date.now())}
      </Text>
    </Box>
  );
};

export default TrustScoreDisplay;
