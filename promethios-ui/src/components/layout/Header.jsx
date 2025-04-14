import React from 'react';
import { Box, Flex, Heading, Text, useColorModeValue, IconButton } from '@chakra-ui/react';
import { FiMenu } from 'react-icons/fi';
import { useLocation } from 'react-router-dom';

/**
 * Header component for the application
 * Displays page title and navigation controls
 */
const Header = ({ onSidebarToggle, children }) => {
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Determine page title based on current route
  const getPageTitle = () => {
    const path = location.pathname;
    
    if (path === '/dashboard') {
      return 'Dashboard';
    } else if (path.startsWith('/chat/')) {
      const agentId = path.split('/').pop();
      if (agentId === 'hal9000') {
        return 'Chat with HAL';
      } else if (agentId === 'ash-xenomorph') {
        return 'Chat with ASH';
      } else {
        return `Chat with Agent`;
      }
    } else if (path.startsWith('/agent/')) {
      return 'Agent Details';
    } else if (path === '/settings') {
      return 'Settings';
    }
    
    return 'Promethios UI v2';
  };
  
  return (
    <Box
      as="header"
      py={4}
      px={6}
      bg={bgColor}
      borderBottomWidth="1px"
      borderColor={borderColor}
      position="sticky"
      top="0"
      zIndex="sticky"
    >
      <Flex alignItems="center" justifyContent="space-between">
        <Flex alignItems="center">
          <IconButton
            display={{ base: 'flex', md: 'none' }}
            onClick={onSidebarToggle}
            variant="outline"
            aria-label="open menu"
            icon={<FiMenu />}
            mr={3}
          />
          
          <Heading as="h1" size="md">{getPageTitle()}</Heading>
        </Flex>
        
        <Flex alignItems="center">
          {children}
          <Text fontSize="sm" opacity="0.8" ml={4}>
            {new Date().toLocaleDateString()}
          </Text>
        </Flex>
      </Flex>
    </Box>
  );
};

export default Header;
