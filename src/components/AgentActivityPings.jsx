import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Badge,
  HStack,
  VStack,
  Circle,
  useColorMode,
  Divider,
  Tooltip,
  Icon,
  Grid,
  GridItem,
  Card,
  CardBody,
  Spinner,
  Button
} from '@chakra-ui/react';
import { FiActivity, FiRefreshCw, FiClock, FiInfo } from 'react-icons/fi';
import { useStatus } from '../context/StatusContext';
import { useSettings } from '../context/SettingsContext';
import { getVisibleAgents } from '../utils/agentUtils';
import { getAgentActivity } from '../api/AgentActivityService';

/**
 * AgentActivityPings Component
 * 
 * Visualizes real-time agent activity with pings and status indicators
 */
const AgentActivityPings = () => {
  const { colorMode } = useColorMode();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [agentActivities, setAgentActivities] = useState({});
  
  // Get status from context
  const { agentHealthPings } = useStatus();
  
  // Get settings from context
  const { settings } = useSettings();
  
  // Fetch agents
  useEffect(() => {
    let isMounted = true;
    
    const fetchAgents = async () => {
      try {
        setLoading(true);
        
        // Use the centralized getVisibleAgents utility
        const visibleAgents = await getVisibleAgents({ includeInactive: true });
        
        if (isMounted) {
          // Merge with health pings data
          const mergedAgents = visibleAgents.map(agent => {
            const healthPing = agentHealthPings.find(ping => ping.id === agent.id);
            return {
              ...agent,
              lastPing: healthPing?.lastPing || null,
              status: healthPing?.status || agent.status || 'unknown'
            };
          });
          
          setAgents(mergedAgents);
          setLastUpdated(new Date());
          
          // Fetch activity data for each agent
          const activityPromises = mergedAgents.map(agent => 
            getAgentActivity(agent.id)
              .then(data => ({ agentId: agent.id, data }))
              .catch(() => ({ agentId: agent.id, data: null }))
          );
          
          const activitiesResults = await Promise.all(activityPromises);
          const activitiesMap = {};
          
          activitiesResults.forEach(result => {
            if (result.data) {
              activitiesMap[result.agentId] = result.data;
            }
          });
          
          if (isMounted) {
            setAgentActivities(activitiesMap);
          }
        }
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    fetchAgents();
    
    // Set up auto-refresh if enabled
    let intervalId;
    if (settings.autoRefreshPanels) {
      intervalId = setInterval(fetchAgents, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [agentHealthPings, settings.autoRefreshPanels]);
  
  // Manual refresh
  const handleRefresh = async () => {
    setLoading(true);
    
    try {
      // Use the centralized getVisibleAgents utility
      const visibleAgents = await getVisibleAgents({ includeInactive: true });
      
      // Merge with health pings data
      const mergedAgents = visibleAgents.map(agent => {
        const healthPing = agentHealthPings.find(ping => ping.id === agent.id);
        return {
          ...agent,
          lastPing: healthPing?.lastPing || null,
          status: healthPing?.status || agent.status || 'unknown'
        };
      });
      
      setAgents(mergedAgents);
      setLastUpdated(new Date());
      
      // Fetch activity data for each agent
      const activityPromises = mergedAgents.map(agent => 
        getAgentActivity(agent.id)
          .then(data => ({ agentId: agent.id, data }))
          .catch(() => ({ agentId: agent.id, data: null }))
      );
      
      const activitiesResults = await Promise.all(activityPromises);
      const activitiesMap = {};
      
      activitiesResults.forEach(result => {
        if (result.data) {
          activitiesMap[result.agentId] = result.data;
        }
      });
      
      setAgentActivities(activitiesMap);
    } catch (error) {
      console.error('Error refreshing agents:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Format time difference
  const formatTimeDiff = (timestamp) => {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const pingTime = new Date(timestamp);
    const diffMs = now - pingTime;
    
    // Convert to seconds
    const diffSec = Math.floor(diffMs / 1000);
    
    if (diffSec < 60) {
      return `${diffSec}s ago`;
    } else if (diffSec < 3600) {
      return `${Math.floor(diffSec / 60)}m ago`;
    } else if (diffSec < 86400) {
      return `${Math.floor(diffSec / 3600)}h ago`;
    } else {
      return `${Math.floor(diffSec / 86400)}d ago`;
    }
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'degraded':
        return 'yellow';
      case 'unavailable':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Get ping animation based on status
  const getPingAnimation = (status) => {
    switch (status) {
      case 'active':
        return 'ping-animation-fast';
      case 'degraded':
        return 'ping-animation-medium';
      case 'unavailable':
        return 'ping-animation-slow';
      default:
        return '';
    }
  };
  
  // Get latest activity for an agent
  const getLatestActivity = (agentId) => {
    const activities = agentActivities[agentId]?.activities || [];
    if (activities.length === 0) return null;
    
    // Sort by timestamp (newest first) and return the first one
    return activities.sort((a, b) => 
      new Date(b.timestamp) - new Date(a.timestamp)
    )[0];
  };
  
  return (
    <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} boxShadow="md" borderRadius="lg">
      <CardBody>
        <Flex justify="space-between" align="center" mb={4}>
          <HStack>
            <Icon as={FiActivity} color={colorMode === 'light' ? 'blue.500' : 'blue.300'} />
            <Heading size="md">Agent Activity Map</Heading>
          </HStack>
          
          <HStack>
            {lastUpdated && (
              <Text fontSize="xs" color="gray.500">
                <Icon as={FiClock} mr={1} />
                Updated: {lastUpdated.toLocaleTimeString()}
              </Text>
            )}
            <Button
              size="xs"
              leftIcon={<FiRefreshCw />}
              onClick={handleRefresh}
              isLoading={loading}
            >
              Refresh
            </Button>
          </HStack>
        </Flex>
        
        <Divider mb={4} />
        
        {loading && agents.length === 0 ? (
          <Flex justify="center" align="center" h="200px">
            <Spinner size="xl" />
          </Flex>
        ) : agents.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text color="gray.500">No agents available</Text>
          </Box>
        ) : (
          <Grid templateColumns={{ base: "repeat(1, 1fr)", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={4}>
            {agents.map(agent => {
              const latestActivity = getLatestActivity(agent.id);
              
              return (
                <GridItem key={agent.id}>
                  <Box
                    p={4}
                    borderWidth="1px"
                    borderRadius="md"
                    borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                    position="relative"
                    overflow="hidden"
                  >
                    {/* Ping animation */}
                    <Box
                      position="absolute"
                      top={0}
                      right={0}
                      width="100%"
                      height="100%"
                      pointerEvents="none"
                      opacity={0.1}
                      className={getPingAnimation(agent.status)}
                    >
                      <Circle
                        size="300px"
                        position="absolute"
                        top="-150px"
                        right="-150px"
                        bg={`${getStatusColor(agent.status)}.500`}
                      />
                    </Box>
                    
                    <VStack align="stretch" spacing={2}>
                      <HStack justify="space-between">
                        <HStack>
                          <Circle size="10px" bg={`${getStatusColor(agent.status)}.500`} />
                          <Text fontWeight="bold">{agent.name || agent.id}</Text>
                        </HStack>
                        <Badge colorScheme={getStatusColor(agent.status)}>
                          {agent.status || 'unknown'}
                        </Badge>
                      </HStack>
                      
                      <Text fontSize="sm" color="gray.500" noOfLines={2}>
                        {agent.description || 'No description available'}
                      </Text>
                      
                      {latestActivity && (
                        <Box 
                          mt={1} 
                          p={2} 
                          bg={colorMode === 'light' ? 'gray.50' : 'gray.600'} 
                          borderRadius="md"
                          fontSize="xs"
                        >
                          <Text fontWeight="medium">Latest Activity:</Text>
                          <Text noOfLines={2}>{latestActivity.content}</Text>
                          <Text color="gray.500" mt={1}>
                            {formatTimeDiff(latestActivity.timestamp)}
                          </Text>
                        </Box>
                      )}
                      
                      <HStack justify="space-between" mt={2}>
                        <Badge variant="outline" colorScheme={agent.type === 'system' ? 'blue' : 'purple'}>
                          {agent.type || 'unknown'}
                        </Badge>
                        
                        <Tooltip label={agent.lastPing ? new Date(agent.lastPing).toLocaleString() : 'No ping data'}>
                          <Text fontSize="xs" color="gray.500">
                            <Icon as={FiClock} mr={1} />
                            {formatTimeDiff(agent.lastPing)}
                          </Text>
                        </Tooltip>
                      </HStack>
                    </VStack>
                  </Box>
                </GridItem>
              );
            })}
          </Grid>
        )}
        
        <Box mt={4}>
          <Text fontSize="xs" color="gray.500">
            <Icon as={FiInfo} mr={1} />
            Agent status is updated every 30 seconds when auto-refresh is enabled
          </Text>
        </Box>
      </CardBody>
    </Card>
  );
};

export default AgentActivityPings;
