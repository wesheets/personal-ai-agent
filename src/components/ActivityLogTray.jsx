import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  HStack,
  useColorModeValue,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Badge,
  Avatar,
  Divider,
  Button,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  Icon
} from '@chakra-ui/react';
import { 
  FiActivity, 
  FiClock, 
  FiFilter, 
  FiTrash2, 
  FiMoreVertical,
  FiCheck,
  FiX,
  FiAlertCircle,
  FiInfo,
  FiMessageCircle,
  FiFile,
  FiRefreshCw
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

// Activity log types
const ActivityType = {
  CHAT: 'chat',
  FILE: 'file',
  SYSTEM: 'system',
  ERROR: 'error',
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning'
};

const ActivityLogTray = ({ 
  isOpen, 
  onClose,
  placement = 'right',
  size = 'md'
}) => {
  const { user } = useAuth();
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Fetch activities from API
  useEffect(() => {
    const fetchActivities = async () => {
      setIsLoading(true);
      
      try {
        const response = await fetch('/api/logs/latest', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch activity logs');
        }
        
        const data = await response.json();
        setActivities(data.logs || []);
      } catch (err) {
        console.error('Error fetching activity logs:', err);
        // Set some mock data for demonstration
        setActivities([
          {
            id: 'log-1',
            type: ActivityType.CHAT,
            agent: {
              id: 'hal9000',
              name: 'HAL',
              avatar: ''
            },
            message: 'Conversation started with HAL',
            timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
            metadata: {
              conversationId: 'conv-123'
            }
          },
          {
            id: 'log-2',
            type: ActivityType.FILE,
            agent: {
              id: 'hal9000',
              name: 'HAL',
              avatar: ''
            },
            message: 'File uploaded: report.pdf',
            timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
            metadata: {
              fileId: 'file-123',
              fileName: 'report.pdf',
              fileSize: 1024 * 1024 * 2.5, // 2.5MB
              fileType: 'application/pdf'
            }
          },
          {
            id: 'log-3',
            type: ActivityType.SYSTEM,
            message: 'System maintenance scheduled for tomorrow',
            timestamp: new Date(Date.now() - 60 * 60000).toISOString()
          },
          {
            id: 'log-4',
            type: ActivityType.ERROR,
            message: 'Failed to process request due to server error',
            timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString()
          },
          {
            id: 'log-5',
            type: ActivityType.SUCCESS,
            message: 'Successfully updated user profile',
            timestamp: new Date(Date.now() - 3 * 60 * 60000).toISOString()
          },
          {
            id: 'log-6',
            type: ActivityType.WARNING,
            message: 'Your session will expire in 5 minutes',
            timestamp: new Date(Date.now() - 4 * 60 * 60000).toISOString()
          },
          {
            id: 'log-7',
            type: ActivityType.INFO,
            message: 'New feature available: File sharing',
            timestamp: new Date(Date.now() - 5 * 60 * 60000).toISOString()
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    if (isOpen) {
      fetchActivities();
    }
  }, [isOpen]);
  
  // Filter activities
  const filteredActivities = filter === 'all' 
    ? activities 
    : activities.filter(activity => activity.type === filter);
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins} min${diffMins === 1 ? '' : 's'} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
    } else {
      return date.toLocaleDateString();
    }
  };
  
  // Get activity icon based on type
  const getActivityIcon = (type) => {
    switch (type) {
      case ActivityType.CHAT:
        return FiMessageCircle;
      case ActivityType.FILE:
        return FiFile;
      case ActivityType.SYSTEM:
        return FiInfo;
      case ActivityType.ERROR:
        return FiX;
      case ActivityType.INFO:
        return FiInfo;
      case ActivityType.SUCCESS:
        return FiCheck;
      case ActivityType.WARNING:
        return FiAlertCircle;
      default:
        return FiActivity;
    }
  };
  
  // Get activity color based on type
  const getActivityColor = (type) => {
    switch (type) {
      case ActivityType.CHAT:
        return 'blue';
      case ActivityType.FILE:
        return 'purple';
      case ActivityType.SYSTEM:
        return 'gray';
      case ActivityType.ERROR:
        return 'red';
      case ActivityType.INFO:
        return 'blue';
      case ActivityType.SUCCESS:
        return 'green';
      case ActivityType.WARNING:
        return 'orange';
      default:
        return 'gray';
    }
  };
  
  // Clear all activities
  const handleClearAll = () => {
    setActivities([]);
  };
  
  // Refresh activities
  const handleRefresh = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };
  
  return (
    <Drawer
      isOpen={isOpen}
      placement={placement}
      onClose={onClose}
      size={size}
    >
      <DrawerOverlay />
      <DrawerContent>
        <DrawerHeader borderBottomWidth="1px">
          <Flex justify="space-between" align="center">
            <HStack>
              <Icon as={FiActivity} />
              <Text>Activity Log</Text>
            </HStack>
            
            <HStack>
              <Menu>
                <MenuButton
                  as={IconButton}
                  icon={<FiFilter />}
                  variant="ghost"
                  size="sm"
                  aria-label="Filter activities"
                />
                <MenuList>
                  <MenuItem onClick={() => setFilter('all')} fontWeight={filter === 'all' ? 'bold' : 'normal'}>
                    All Activities
                  </MenuItem>
                  <MenuItem onClick={() => setFilter(ActivityType.CHAT)} fontWeight={filter === ActivityType.CHAT ? 'bold' : 'normal'}>
                    Chat Activities
                  </MenuItem>
                  <MenuItem onClick={() => setFilter(ActivityType.FILE)} fontWeight={filter === ActivityType.FILE ? 'bold' : 'normal'}>
                    File Activities
                  </MenuItem>
                  <MenuItem onClick={() => setFilter(ActivityType.SYSTEM)} fontWeight={filter === ActivityType.SYSTEM ? 'bold' : 'normal'}>
                    System Activities
                  </MenuItem>
                  <MenuItem onClick={() => setFilter(ActivityType.ERROR)} fontWeight={filter === ActivityType.ERROR ? 'bold' : 'normal'}>
                    Errors
                  </MenuItem>
                </MenuList>
              </Menu>
              
              <Tooltip label="Refresh">
                <IconButton
                  icon={<FiRefreshCw />}
                  variant="ghost"
                  size="sm"
                  aria-label="Refresh activities"
                  onClick={handleRefresh}
                  isLoading={isLoading}
                />
              </Tooltip>
              
              <Tooltip label="Clear all">
                <IconButton
                  icon={<FiTrash2 />}
                  variant="ghost"
                  size="sm"
                  aria-label="Clear all activities"
                  onClick={handleClearAll}
                />
              </Tooltip>
              
              <DrawerCloseButton position="relative" right={0} top={0} />
            </HStack>
          </Flex>
        </DrawerHeader>
        
        <DrawerBody p={0}>
          {isLoading ? (
            <Flex justify="center" align="center" h="100%" py={10}>
              <Text>Loading activities...</Text>
            </Flex>
          ) : filteredActivities.length === 0 ? (
            <Flex justify="center" align="center" h="100%" py={10} direction="column">
              <Icon as={FiClock} boxSize={10} color="gray.400" mb={4} />
              <Text color="gray.500">No activities to display</Text>
              {filter !== 'all' && (
                <Button variant="link" colorScheme="blue" mt={2} onClick={() => setFilter('all')}>
                  Show all activities
                </Button>
              )}
            </Flex>
          ) : (
            <VStack spacing={0} align="stretch" divider={<Divider />}>
              {filteredActivities.map((activity) => (
                <Box key={activity.id} p={4} _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}>
                  <HStack spacing={3} align="flex-start">
                    <Flex
                      w={10}
                      h={10}
                      borderRadius="full"
                      bg={`${getActivityColor(activity.type)}.100`}
                      color={`${getActivityColor(activity.type)}.500`}
                      justify="center"
                      align="center"
                    >
                      <Icon as={getActivityIcon(activity.type)} boxSize={5} />
                    </Flex>
                    
                    <VStack spacing={1} align="stretch" flex={1}>
                      <HStack justify="space-between">
                        <HStack>
                          <Text fontWeight="medium">
                            {activity.agent?.name || 'System'}
                          </Text>
                          
                          <Badge colorScheme={getActivityColor(activity.type)} variant="subtle">
                            {activity.type}
                          </Badge>
                        </HStack>
                        
                        <Text fontSize="xs" color="gray.500">
                          {formatTimestamp(activity.timestamp)}
                        </Text>
                      </HStack>
                      
                      <Text>{activity.message}</Text>
                      
                      {activity.type === ActivityType.FILE && activity.metadata && (
                        <HStack 
                          mt={1} 
                          p={2} 
                          bg={useColorModeValue('gray.50', 'gray.700')} 
                          borderRadius="md"
                          fontSize="sm"
                        >
                          <Icon as={FiFile} />
                          <Text>{activity.metadata.fileName}</Text>
                          <Text color="gray.500">
                            ({Math.round(activity.metadata.fileSize / 1024)} KB)
                          </Text>
                        </HStack>
                      )}
                    </VStack>
                    
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                        aria-label="More options"
                      />
                      <MenuList>
                        {activity.type === ActivityType.CHAT && (
                          <MenuItem>View Conversation</MenuItem>
                        )}
                        {activity.type === ActivityType.FILE && (
                          <MenuItem>Download File</MenuItem>
                        )}
                        <MenuItem color="red.500">Remove from Log</MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </Box>
              ))}
            </VStack>
          )}
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
};

export default ActivityLogTray;
