import React, { useState, useEffect } from 'react';
import { Box, Flex, Text, Button, Icon, useColorModeValue, Badge, Tooltip, Spinner } from '@chakra-ui/react';
import { FaUser, FaBell, FaCog, FaSignOutAlt, FaExclamationTriangle } from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * OperatorHUDBar Component
 * 
 * Displays operator information and system-wide controls in the left panel.
 * Connected to /api/operator/status endpoint for real-time operator data.
 */
const OperatorHUDBar = () => {
  const bgColor = useColorModeValue('blue.500', 'blue.700');
  const textColor = useColorModeValue('white', 'gray.100');
  const iconColor = useColorModeValue('white', 'gray.200');
  const [alertCount, setAlertCount] = useState(0);
  
  // Fetch operator data from API
  const { data: operatorData, error, loading } = useFetch('/api/operator/status', {}, {
    refreshInterval: 30000, // Refresh every 30 seconds
    initialData: {
      name: 'Operator',
      role: 'Admin',
      status: 'active',
      alerts: 0
    },
    transformResponse: (data) => ({
      name: data.name || 'Operator',
      role: data.role || 'Admin',
      status: data.status || 'active',
      alerts: data.alerts || 0
    })
  });
  
  // Update alert count when operator data changes
  useEffect(() => {
    if (operatorData && typeof operatorData.alerts === 'number') {
      setAlertCount(operatorData.alerts);
    }
  }, [operatorData]);
  
  // Handle logout
  const handleLogout = () => {
    console.log('Logout clicked');
    // In a real implementation, this would call an API to log out the operator
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'busy':
        return 'orange';
      case 'away':
        return 'yellow';
      case 'offline':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  return (
    <Flex
      width="100%"
      bg={bgColor}
      color={textColor}
      p={2}
      borderRadius="md"
      alignItems="center"
      justifyContent="space-between"
      position="relative"
      overflow="hidden"
    >
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="2px" right="2px">
          <Spinner size="xs" color="white" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="2px" right="2px">
            <Icon as={FaExclamationTriangle} color="red.300" />
          </Box>
        </Tooltip>
      )}
      
      <Flex alignItems="center">
        <Icon as={FaUser} mr={2} color={iconColor} />
        <Box>
          <Text fontWeight="bold">{operatorData?.name || 'Operator'}</Text>
          <Flex alignItems="center">
            <Text fontSize="xs">{operatorData?.role || 'Admin'}</Text>
            <Badge 
              ml={2} 
              size="sm" 
              colorScheme={getStatusColor(operatorData?.status)} 
              variant="solid"
              fontSize="2xs"
            >
              {operatorData?.status || 'active'}
            </Badge>
          </Flex>
        </Box>
      </Flex>
      
      <Flex>
        <Tooltip label={`${alertCount} alerts`}>
          <Button 
            variant="ghost" 
            size="sm" 
            mr={2} 
            leftIcon={<FaBell />} 
            color={textColor}
            position="relative"
          >
            <Text display={{ base: 'none', md: 'block' }}>Alerts</Text>
            {alertCount > 0 && (
              <Badge 
                position="absolute" 
                top="-5px" 
                right="-5px" 
                colorScheme="red" 
                borderRadius="full"
                fontSize="xs"
              >
                {alertCount}
              </Badge>
            )}
          </Button>
        </Tooltip>
        <Button variant="ghost" size="sm" mr={2} leftIcon={<FaCog />} color={textColor}>
          <Text display={{ base: 'none', md: 'block' }}>Settings</Text>
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          leftIcon={<FaSignOutAlt />} 
          color={textColor}
          onClick={handleLogout}
        >
          <Text display={{ base: 'none', md: 'block' }}>Logout</Text>
        </Button>
      </Flex>
    </Flex>
  );
};

export default OperatorHUDBar;
