import React, { useState, useEffect, useRef } from 'react';
import { Box, VStack, Text, Flex, Spinner, Badge, Divider, useColorModeValue } from '@chakra-ui/react';
import { logsService } from '../services/api';

const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const feedEndRef = useRef(null);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const userBgColor = useColorModeValue('blue.50', 'blue.900');
  const agentBgColor = useColorModeValue('gray.50', 'gray.800');

  useEffect(() => {
    // Function to fetch latest logs
    const fetchLogs = async () => {
      try {
        const data = await logsService.getLatestLogs();
        setActivities(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch activity logs');
        setLoading(false);
        console.error('Error fetching logs:', err);
      }
    };

    // Initial fetch
    fetchLogs();

    // Set up polling for real-time updates (every 5 seconds)
    const intervalId = setInterval(fetchLogs, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Scroll to bottom when new activities arrive
  useEffect(() => {
    if (feedEndRef.current) {
      feedEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activities]);

  // Function to determine badge color based on agent type
  const getAgentColor = (agentType) => {
    switch (agentType?.toLowerCase()) {
      case 'builder':
        return 'blue';
      case 'research':
        return 'green';
      case 'memory':
        return 'purple';
      case 'ops':
        return 'orange';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading activity feed...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
        <Text fontSize="lg">{error}</Text>
        <Text mt={2}>Please try refreshing the page.</Text>
      </Box>
    );
  }

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      p={4} 
      shadow="md" 
      bg={bgColor} 
      borderColor={borderColor}
      height="100%"
      overflowY="auto"
    >
      <VStack spacing={4} align="stretch">
        <Text fontWeight="bold" fontSize="lg">Activity Feed</Text>
        
        {activities.length === 0 ? (
          <Text textAlign="center" py={10} color="gray.500">
            No activities to display
          </Text>
        ) : (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {activities.map((activity, index) => (
              <Box 
                key={index} 
                p={3} 
                borderRadius="md" 
                bg={activity.source === 'user' ? userBgColor : agentBgColor}
                borderWidth="1px"
                borderColor={borderColor}
              >
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Badge colorScheme={activity.source === 'user' ? 'blue' : getAgentColor(activity.agent_type)}>
                    {activity.source === 'user' ? 'User' : activity.agent_type || 'System'}
                  </Badge>
                  <Text fontSize="xs" color="gray.500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </Text>
                </Flex>
                
                <Text whiteSpace="pre-wrap">{activity.content}</Text>
                
                {activity.metadata && (
                  <Box mt={2} fontSize="sm" color="gray.500">
                    {Object.entries(activity.metadata).map(([key, value]) => (
                      <Text key={key}>
                        <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
                      </Text>
                    ))}
                  </Box>
                )}
              </Box>
            ))}
          </VStack>
        )}
        
        {/* Invisible element to scroll to */}
        <div ref={feedEndRef} />
      </VStack>
    </Box>
  );
};

export default ActivityFeed;
