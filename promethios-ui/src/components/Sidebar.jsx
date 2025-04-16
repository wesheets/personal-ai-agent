import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  Icon,
  VStack,
  HStack,
  useColorMode,
  Divider,
  Spinner,
  Badge
} from '@chakra-ui/react';
import {
  FiMenu,
  FiHome,
  FiSettings,
  FiActivity,
  FiDatabase,
  FiList,
  FiCode,
  FiServer,
  FiSearch,
  FiMessageCircle
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';
import { getVisibleAgents } from '../utils/agentUtils';

const Sidebar = () => {
  const { colorMode } = useColorMode();
  const location = useLocation();
  const [systemAgents, setSystemAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch system agents
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const agents = await getVisibleAgents();
        setSystemAgents(agents);
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgents();
  }, []);

  // Navigation items
  const navItems = [
    { name: 'Dashboard', icon: FiHome, path: '/' },
    { name: 'Builder Agent', icon: FiCode, path: '/agent/builder' },
    { name: 'Ops Agent', icon: FiServer, path: '/agent/ops-agent' },
    { name: 'Research Agent', icon: FiSearch, path: '/agent/research' },
    { name: 'Memory Agent', icon: FiDatabase, path: '/agent/memory-agent' },
    { name: 'Memory Browser', icon: FiList, path: '/memory-browser' },
    { name: 'Activity Feed', icon: FiActivity, path: '/activity' },
    { name: 'Agent Activity', icon: FiActivity, path: '/agent-activity' },
    { name: 'Settings', icon: FiSettings, path: '/settings' }
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
        <Text
          fontSize="2xl"
          fontWeight="bold"
          color={colorMode === 'light' ? 'brand.500' : 'brand.300'}
        >
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
              bg={
                location.pathname === item.path
                  ? colorMode === 'light'
                    ? 'gray.100'
                    : 'gray.700'
                  : 'transparent'
              }
              color={
                location.pathname === item.path
                  ? colorMode === 'light'
                    ? 'brand.600'
                    : 'brand.300'
                  : colorMode === 'light'
                    ? 'gray.600'
                    : 'gray.300'
              }
              _hover={{
                bg: colorMode === 'light' ? 'gray.100' : 'gray.700',
                color: colorMode === 'light' ? 'brand.600' : 'brand.300'
              }}
              transition="all 0.2s"
              borderLeftWidth={location.pathname === item.path ? '4px' : '0px'}
              borderColor={
                location.pathname === item.path
                  ? colorMode === 'light'
                    ? 'brand.500'
                    : 'brand.300'
                  : 'transparent'
              }
            >
              <Icon as={item.icon} />
              <Text fontWeight={location.pathname === item.path ? 'medium' : 'normal'}>
                {item.name}
              </Text>
            </HStack>
          </Link>
        ))}

        {/* System Agents Section */}
        <Box px={8} py={3} mt={2}>
          <Flex align="center" mb={2}>
            <Text
              fontSize="sm"
              fontWeight="medium"
              color={colorMode === 'light' ? 'gray.500' : 'gray.400'}
            >
              SYSTEM AGENTS
            </Text>
            {isLoading && <Spinner size="xs" ml={2} color="blue.500" />}
          </Flex>

          {systemAgents.map((agent) => (
            <Link to={`/agent/${agent.id.toLowerCase()}`} key={agent.id}>
              <HStack
                py={2}
                spacing={3}
                bg={
                  location.pathname === `/agent/${agent.id.toLowerCase()}`
                    ? colorMode === 'light'
                      ? 'gray.100'
                      : 'gray.700'
                    : 'transparent'
                }
                color={
                  location.pathname === `/agent/${agent.id.toLowerCase()}`
                    ? colorMode === 'light'
                      ? 'brand.600'
                      : 'brand.300'
                    : colorMode === 'light'
                      ? 'gray.600'
                      : 'gray.300'
                }
                _hover={{
                  bg: colorMode === 'light' ? 'gray.100' : 'gray.700',
                  color: colorMode === 'light' ? 'brand.600' : 'brand.300'
                }}
                transition="all 0.2s"
                borderLeftWidth={
                  location.pathname === `/agent/${agent.id.toLowerCase()}` ? '4px' : '0px'
                }
                borderColor={
                  location.pathname === `/agent/${agent.id.toLowerCase()}`
                    ? colorMode === 'light'
                      ? 'brand.500'
                      : 'brand.300'
                    : 'transparent'
                }
                pl={location.pathname === `/agent/${agent.id.toLowerCase()}` ? 3 : 4}
              >
                <Text fontSize="lg">{agent.icon || '🤖'}</Text>
                <Text
                  fontWeight={
                    location.pathname === `/agent/${agent.id.toLowerCase()}` ? 'medium' : 'normal'
                  }
                  fontSize="sm"
                >
                  {agent.name}
                </Text>
                <Badge
                  size="sm"
                  colorScheme={
                    agent.status === 'ready' ? 'green' : agent.status === 'idle' ? 'yellow' : 'gray'
                  }
                  ml="auto"
                >
                  {agent.status}
                </Badge>
              </HStack>
            </Link>
          ))}

          {!isLoading && systemAgents.length === 0 && (
            <Text fontSize="sm" color="gray.500" py={2}>
              No agents available
            </Text>
          )}
        </Box>
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
