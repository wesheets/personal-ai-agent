import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Icon,
  Flex,
  Divider,
  useColorModeValue,
  Link
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';

// Import icons (using box icons as placeholders - in a real implementation, you'd use a proper icon library)
const DashboardIcon = () => (
  <Box as="span" fontSize="1.2em">
    📊
  </Box>
);
const AgentsIcon = () => (
  <Box as="span" fontSize="1.2em">
    🤖
  </Box>
);
const MemoryIcon = () => (
  <Box as="span" fontSize="1.2em">
    🧠
  </Box>
);
const SettingsIcon = () => (
  <Box as="span" fontSize="1.2em">
    ⚙️
  </Box>
);

const Sidebar = () => {
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.200');

  const navItems = [
    { name: 'Dashboard', icon: DashboardIcon, path: '/' },
    { name: 'Agents', icon: AgentsIcon, path: '/agents' },
    { name: 'Memory', icon: MemoryIcon, path: '/memory' },
    { name: 'Settings', icon: SettingsIcon, path: '/settings' }
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <Box
      as="nav"
      pos="fixed"
      top="0"
      left="0"
      h="100vh"
      w="64"
      bg={bgColor}
      borderRight="1px"
      borderColor={borderColor}
      py={5}
    >
      <VStack spacing={6} align="stretch">
        <Box px={5}>
          <Text fontSize="xl" fontWeight="bold">
            Personal AI
          </Text>
          <Text fontSize="sm" color="gray.500">
            Agent System
          </Text>
        </Box>

        <Divider />

        <VStack spacing={1} align="stretch">
          {navItems.map((item) => (
            <Link
              key={item.name}
              as={RouterLink}
              to={item.path}
              textDecoration="none"
              _hover={{ textDecoration: 'none' }}
            >
              <HStack
                px={5}
                py={3}
                spacing={3}
                bg={isActive(item.path) ? activeBg : 'transparent'}
                color={isActive(item.path) ? activeColor : 'inherit'}
                _hover={{ bg: isActive(item.path) ? activeBg : hoverBg }}
                borderRadius="md"
                mx={2}
              >
                <item.icon />
                <Text fontWeight={isActive(item.path) ? 'bold' : 'normal'}>{item.name}</Text>
              </HStack>
            </Link>
          ))}
        </VStack>

        <Divider mt="auto" />

        <Box px={5} py={3}>
          <Text fontSize="xs" color="gray.500">
            Version 1.0.0
          </Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar;
