import React, { useState, useEffect } from 'react';
import { Box, Flex, VStack, Text, useColorModeValue, IconButton, Drawer, DrawerBody, DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton, Heading } from '@chakra-ui/react';
import { FiBell } from 'react-icons/fi';

/**
 * ActivityLogTray component
 * Displays activity history for agents in a slide-out drawer
 */
const ActivityLogTray = ({ agentId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // Determine agent details based on agentId
  const getAgentDetails = (id) => {
    switch(id) {
      case 'hal9000':
        return { name: 'HAL', color: 'blue' };
      case 'ash-xenomorph':
        return { name: 'ASH', color: 'purple' };
      default:
        return { name: 'All Agents', color: 'gray' };
    }
  };
  
  const agentDetails = getAgentDetails(agentId);
  
  // Load activities when drawer opens or agent changes
  useEffect(() => {
    if (isOpen) {
      loadActivities();
    }
  }, [isOpen, agentId]);
  
  const loadActivities = () => {
    setLoading(true);
    
    // Simulate API call to fetch activities
    setTimeout(() => {
      const mockActivities = [
        {
          id: 1,
          agentId: 'hal9000',
          agentName: 'HAL',
          action: 'Completed task',
          details: 'Analyzed market data and generated report',
          timestamp: new Date(Date.now() - 30 * 60000) // 30 minutes ago
        },
        {
          id: 2,
          agentId: 'ash-xenomorph',
          agentName: 'ASH',
          action: 'Processed file',
          details: 'Analyzed research paper and extracted key findings',
          timestamp: new Date(Date.now() - 2 * 60 * 60000) // 2 hours ago
        },
        {
          id: 3,
          agentId: 'hal9000',
          agentName: 'HAL',
          action: 'Answered question',
          details: 'Provided information about quantum computing',
          timestamp: new Date(Date.now() - 5 * 60 * 60000) // 5 hours ago
        },
        {
          id: 4,
          agentId: 'ash-xenomorph',
          agentName: 'ASH',
          action: 'Generated visualization',
          details: 'Created data visualization from uploaded dataset',
          timestamp: new Date(Date.now() - 1 * 24 * 60 * 60000) // 1 day ago
        }
      ];
      
      // Filter activities by agent if specific agent is selected
      const filteredActivities = agentId && agentId !== 'all' 
        ? mockActivities.filter(activity => activity.agentId === agentId)
        : mockActivities;
      
      setActivities(filteredActivities);
      setLoading(false);
    }, 1000);
  };
  
  const onOpen = () => setIsOpen(true);
  const onClose = () => setIsOpen(false);
  
  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diffMs = now - timestamp;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
  };
  
  return (
    <>
      <IconButton
        icon={<FiBell />}
        aria-label="Activity Log"
        variant="ghost"
        onClick={onOpen}
      />
      
      <Drawer
        isOpen={isOpen}
        placement="right"
        onClose={onClose}
        size="md"
      >
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            {agentId && agentId !== 'all' ? `${agentDetails.name} Activity Log` : 'Activity Log'}
          </DrawerHeader>
          
          <DrawerBody p={4}>
            {loading ? (
              <Flex justify="center" align="center" h="100%">
                <Text>Loading activities...</Text>
              </Flex>
            ) : activities.length === 0 ? (
              <Flex justify="center" align="center" h="100%">
                <Text>No activities found</Text>
              </Flex>
            ) : (
              <VStack spacing={4} align="stretch">
                {activities.map((activity) => (
                  <Box
                    key={activity.id}
                    p={4}
                    borderWidth="1px"
                    borderRadius="md"
                    borderColor={borderColor}
                    bg={bgColor}
                  >
                    <Flex justify="space-between" align="center" mb={2}>
                      <Box
                        bg={getAgentDetails(activity.agentId).color + '.500'}
                        color="white"
                        borderRadius="full"
                        px={2}
                        py={1}
                        fontSize="xs"
                      >
                        {activity.agentName}
                      </Box>
                      <Text fontSize="sm" color="gray.500">
                        {formatTimestamp(activity.timestamp)}
                      </Text>
                    </Flex>
                    <Heading as="h4" size="sm" mb={1}>
                      {activity.action}
                    </Heading>
                    <Text fontSize="sm">{activity.details}</Text>
                  </Box>
                ))}
              </VStack>
            )}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};

export default ActivityLogTray;
