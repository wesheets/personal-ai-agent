import React from 'react';
import {
  Box,
  Flex,
  Text,
  Icon,
  VStack,
  HStack,
  useColorMode,
  Divider,
} from '@chakra-ui/react';
import { FiMenu, FiHome, FiSettings, FiActivity, FiDatabase, FiList, FiCode, FiServer, FiSearch } from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const { colorMode } = useColorMode();
  const location = useLocation();
  
  // Navigation items with corrected paths to match App.jsx routes
  const navItems = [
    { name: 'Dashboard', icon: FiHome, path: '/dashboard' },
    { name: 'Builder Agent', icon: FiCode, path: '/builder' },
    { name: 'Ops Agent', icon: FiServer, path: '/ops' },
    { name: 'Research Agent', icon: FiSearch, path: '/research' },
    { name: 'Memory Agent', icon: FiDatabase, path: '/memory' },
    { name: 'Memory Browser', icon: FiList, path: '/memory-browser' },
    { name: 'Activity Feed', icon: FiActivity, path: '/activity' },
    { name: 'Agent Activity', icon: FiActivity, path: '/agent-activity' },
    { name: 'Settings', icon: FiSettings, path: '/settings' },
    { name: 'HAL Interface', icon: FiCode, path: '/hal' },
  ];
  
  return (
    <Box
      as="nav"
      position="fixed"
      left="0"
      w={{ base: 'full', md: '60' }}
      h="full"
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
      borderRightWidth="1px"
      borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
      display={{ base: 'none', md: 'block' }}
      zIndex="900"
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold" color={colorMode === 'light' ? 'brand.500' : 'brand.300'}>
          Promethios
        </Text>
        <Icon as={FiMenu} display={{ base: 'flex', md: 'none' }} />
      </Flex>
      
      <VStack spacing={0} align="stretch" mt={4}>
        {navItems.map((item) => (
          <Link to={item.path} key={item.name}>
            <HStack
              px={8}
              py={3}
              spacing={4}
              bg={location.pathname === item.path ? (colorMode === 'light' ? 'gray.100' : 'gray.700') : 'transparent'}
              color={location.pathname === item.path ? (colorMode === 'light' ? 'brand.600' : 'brand.300') : (colorMode === 'light' ? 'gray.600' : 'gray.300')}
              _hover={{
                bg: colorMode === 'light' ? 'gray.100' : 'gray.700',
                color: colorMode === 'light' ? 'brand.600' : 'brand.300',
              }}
              transition="all 0.2s"
              borderLeftWidth={location.pathname === item.path ? '4px' : '0px'}
              borderColor={location.pathname === item.path ? (colorMode === 'light' ? 'brand.500' : 'brand.300') : 'transparent'}
            >
              <Icon as={item.icon} />
              <Text fontWeight={location.pathname === item.path ? 'medium' : 'normal'}>
                {item.name}
              </Text>
            </HStack>
          </Link>
        ))}
      </VStack>
      
      <Divider my={4} />
      
      <Box px={8} py={4}>
        <Text fontSize="xs" color="gray.500">
          Promethios OS v1.0.0
        </Text>
      </Box>
    </Box>
  );
};

export default Sidebar;
