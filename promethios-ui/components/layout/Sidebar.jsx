import React from 'react';
import {
  Box,
  Flex,
  VStack,
  Heading,
  Text,
  Icon,
  Button,
  useColorModeValue
} from '@chakra-ui/react';
import { FiHome, FiMessageSquare, FiUsers, FiSettings, FiLogOut } from 'react-icons/fi';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LogoutButton from '../auth/LogoutButton';

/**
 * Sidebar component for navigation
 * Displays user info, navigation links, and system agents
 */
const Sidebar = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.200');

  // Navigation items
  const navItems = [
    { name: 'Dashboard', icon: FiHome, path: '/dashboard' },
    { name: 'Agents', icon: FiUsers, path: '/agents' },
    { name: 'Settings', icon: FiSettings, path: '/settings' }
  ];

  // System agents
  const systemAgents = [
    { id: 'hal9000', name: 'HAL', color: 'blue' },
    { id: 'ash-xenomorph', name: 'ASH', color: 'purple' }
  ];

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleAgentChat = (agentId) => {
    navigate(`/agent/${agentId}`);
  };

  return (
    <Box
      as="aside"
      w={{ base: 'full', md: '250px' }}
      h="100vh"
      bg={bgColor}
      borderRight="1px"
      borderColor={borderColor}
      position="fixed"
      overflowY="auto"
    >
      <VStack spacing={6} align="stretch" p={4}>
        {/* User Profile Section */}
        <Box pt={2} pb={4}>
          <Flex align="center" mb={4}>
            <Box
              bg="blue.500"
              color="white"
              borderRadius="md"
              boxSize="40px"
              fontSize="xl"
              fontWeight="bold"
              display="flex"
              alignItems="center"
              justifyContent="center"
              mr={3}
            >
              P
            </Box>
            <Box>
              <Heading as="h1" size="sm">
                Promethios UI v2
              </Heading>
              <Text fontSize="xs" opacity="0.8">
                Agent OS Shell
              </Text>
            </Box>
          </Flex>

          {currentUser && (
            <Box p={3} borderRadius="md" bg={useColorModeValue('gray.50', 'gray.700')}>
              <Text fontWeight="bold">{currentUser?.name || 'User'}</Text>
              <Text fontSize="sm" opacity="0.8">
                {currentUser?.email || 'user@example.com'}
              </Text>
            </Box>
          )}
        </Box>

        {/* Navigation Links */}
        <VStack spacing={1} align="stretch">
          <Text fontSize="xs" fontWeight="bold" color="gray.500" px={3} mb={1}>
            NAVIGATION
          </Text>

          {navItems.map((item) => (
            <Button
              key={item.name}
              variant="ghost"
              justifyContent="flex-start"
              py={3}
              px={3}
              borderRadius="md"
              bg={location.pathname === item.path ? activeBg : 'transparent'}
              color={location.pathname === item.path ? activeColor : 'inherit'}
              _hover={{ bg: hoverBg }}
              leftIcon={<Icon as={item.icon} boxSize={5} />}
              onClick={() => handleNavigation(item.path)}
            >
              {item.name}
            </Button>
          ))}
        </VStack>

        {/* System Agents */}
        <VStack spacing={1} align="stretch">
          <Text fontSize="xs" fontWeight="bold" color="gray.500" px={3} mb={1}>
            SYSTEM AGENTS
          </Text>

          {systemAgents.map((agent) => (
            <Button
              key={agent.id}
              variant="ghost"
              justifyContent="flex-start"
              py={3}
              px={3}
              borderRadius="md"
              bg={location.pathname === `/agent/${agent.id}` ? activeBg : 'transparent'}
              color={location.pathname === `/agent/${agent.id}` ? activeColor : 'inherit'}
              _hover={{ bg: hoverBg }}
              leftIcon={
                <Box
                  bg={`${agent.color}.500`}
                  color="white"
                  borderRadius="full"
                  boxSize="24px"
                  fontSize="xs"
                  fontWeight="bold"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  {agent.name.charAt(0)}
                </Box>
              }
              onClick={() => handleAgentChat(agent.id)}
            >
              {agent.name}
            </Button>
          ))}
        </VStack>

        {/* Logout Button */}
        <Box mt="auto" pt={6}>
          <LogoutButton>
            <Button
              variant="ghost"
              justifyContent="flex-start"
              width="full"
              py={3}
              px={3}
              borderRadius="md"
              _hover={{ bg: hoverBg }}
              leftIcon={<Icon as={FiLogOut} boxSize={5} />}
            >
              Logout
            </Button>
          </LogoutButton>
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar;
