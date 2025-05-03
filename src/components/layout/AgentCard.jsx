import React from 'react';
import { 
  Box, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  VStack, 
  HStack, 
  Icon, 
  useColorModeValue,
  Divider,
  Avatar,
  Badge
} from '@chakra-ui/react';
import { FiMessageCircle, FiCpu, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';

const AgentCard = ({ 
  name, 
  description, 
  avatar, 
  status = 'idle', 
  isSystem = false,
  lastActive,
  onClick
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  
  // Status configuration
  const statusConfig = {
    idle: { color: 'gray', icon: FiCpu, text: 'Idle' },
    active: { color: 'green', icon: FiCheckCircle, text: 'Active' },
    busy: { color: 'orange', icon: FiAlertCircle, text: 'Busy' },
    error: { color: 'red', icon: FiAlertCircle, text: 'Error' }
  };
  
  const statusInfo = statusConfig[status] || statusConfig.idle;
  
  // Generate avatar background color based on name
  const getAvatarBg = (name) => {
    const colors = ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'cyan', 'purple', 'pink'];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return `${colors[hash % colors.length]}.500`;
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
        transform: 'translateY(-2px)',
        transition: 'all 0.2s ease-in-out'
      }}
      transition="all 0.2s ease-in-out"
      cursor="pointer"
      onClick={onClick}
    >
      <Flex justifyContent="space-between" alignItems="center" mb={3}>
        <HStack spacing={3}>
          <Avatar 
            size="md" 
            name={name} 
            src={avatar} 
            bg={getAvatarBg(name)}
          />
          <VStack spacing={0} align="flex-start">
            <Heading as="h3" size="md">
              {name}
            </Heading>
            {isSystem && (
              <Badge colorScheme="purple" fontSize="xs">
                System Agent
              </Badge>
            )}
          </VStack>
        </HStack>
        
        <Badge 
          colorScheme={statusInfo.color} 
          variant="subtle"
          display="flex"
          alignItems="center"
          px={2}
          py={1}
          borderRadius="full"
        >
          <Icon as={statusInfo.icon} mr={1} boxSize={3} />
          {statusInfo.text}
        </Badge>
      </Flex>
      
      <Text 
        fontSize="sm" 
        color={useColorModeValue('gray.600', 'gray.400')}
        noOfLines={2}
        mb={4}
      >
        {description}
      </Text>
      
      <Divider mb={3} />
      
      <Flex justifyContent="space-between" alignItems="center">
        <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.500')}>
          {lastActive ? `Last active: ${lastActive}` : 'Never used'}
        </Text>
        
        <Button 
          size="sm" 
          colorScheme="blue" 
          leftIcon={<FiMessageCircle />}
          variant="ghost"
        >
          Chat
        </Button>
      </Flex>
    </Box>
  );
};

export default AgentCard;
