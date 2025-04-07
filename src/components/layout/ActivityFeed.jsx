import React from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  HStack, 
  Text, 
  Icon, 
  Avatar, 
  useColorModeValue,
  Divider,
  Badge,
  IconButton
} from '@chakra-ui/react';
import { FiMessageCircle, FiClock, FiInfo, FiAlertCircle, FiCheckCircle, FiX } from 'react-icons/fi';

const ActivityCard = ({ 
  title, 
  timestamp, 
  agent = null, 
  type = 'info', 
  message, 
  onDismiss,
  onClick
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  
  // Type configuration
  const typeConfig = {
    info: { color: 'blue', icon: FiInfo },
    success: { color: 'green', icon: FiCheckCircle },
    warning: { color: 'orange', icon: FiAlertCircle },
    error: { color: 'red', icon: FiAlertCircle },
    message: { color: 'purple', icon: FiMessageCircle }
  };
  
  const typeInfo = typeConfig[type] || typeConfig.info;
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return 'Unknown time';
    
    // If timestamp is a string, convert to Date
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    
    // Check if it's today
    const today = new Date();
    const isToday = date.getDate() === today.getDate() && 
                    date.getMonth() === today.getMonth() && 
                    date.getFullYear() === today.getFullYear();
    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' }) + 
             ' at ' + 
             date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  };
  
  return (
    <Box
      p={4}
      bg={bgColor}
      borderRadius="lg"
      boxShadow="sm"
      borderWidth="1px"
      borderColor={borderColor}
      _hover={{ 
        boxShadow: 'md', 
        bg: hoverBg,
        transition: 'all 0.2s ease-in-out'
      }}
      transition="all 0.2s ease-in-out"
      cursor={onClick ? "pointer" : "default"}
      onClick={onClick}
      position="relative"
    >
      {/* Dismiss button */}
      {onDismiss && (
        <IconButton
          icon={<FiX />}
          size="xs"
          aria-label="Dismiss"
          position="absolute"
          top={2}
          right={2}
          variant="ghost"
          onClick={(e) => {
            e.stopPropagation();
            onDismiss();
          }}
        />
      )}
      
      <HStack spacing={4} align="flex-start" mb={3}>
        {/* Icon */}
        <Flex
          w={10}
          h={10}
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
          bg={`${typeInfo.color}.100`}
          color={`${typeInfo.color}.700`}
        >
          <Icon as={typeInfo.icon} boxSize={5} />
        </Flex>
        
        <VStack spacing={0} align="flex-start" flex={1}>
          <Text fontWeight="bold">{title}</Text>
          
          <HStack spacing={2}>
            {agent && (
              <HStack spacing={1}>
                <Avatar size="xs" name={agent.name} src={agent.avatar} />
                <Text fontSize="xs" color="gray.500">{agent.name}</Text>
              </HStack>
            )}
            
            <HStack spacing={1}>
              <Icon as={FiClock} boxSize={3} color="gray.500" />
              <Text fontSize="xs" color="gray.500">
                {formatTime(timestamp)}
              </Text>
            </HStack>
            
            <Badge colorScheme={typeInfo.color} size="sm">
              {type}
            </Badge>
          </HStack>
        </VStack>
      </HStack>
      
      <Text 
        fontSize="sm" 
        color={useColorModeValue('gray.600', 'gray.400')}
        ml={14}
      >
        {message}
      </Text>
    </Box>
  );
};

const ActivityFeed = ({ activities = [] }) => {
  return (
    <VStack spacing={4} align="stretch">
      {activities.map((activity, index) => (
        <ActivityCard key={index} {...activity} />
      ))}
      
      {activities.length === 0 && (
        <Box 
          p={6} 
          textAlign="center" 
          bg={useColorModeValue('white', 'gray.800')}
          borderRadius="lg"
          boxShadow="sm"
          borderWidth="1px"
          borderColor={useColorModeValue('gray.200', 'gray.700')}
        >
          <Text color="gray.500">No activity to display</Text>
        </Box>
      )}
    </VStack>
  );
};

export default ActivityFeed;
