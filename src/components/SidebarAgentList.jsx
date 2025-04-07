import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  Icon,
  VStack,
  HStack,
  useColorModeValue,
  Divider,
  Avatar,
  Spinner,
  Badge,
  Input,
  InputGroup,
  InputLeftElement,
  Collapse,
  Button,
  Tooltip
} from '@chakra-ui/react';
import { 
  FiHome, 
  FiSettings, 
  FiActivity, 
  FiSearch, 
  FiUsers, 
  FiMessageSquare,
  FiPlus,
  FiChevronDown,
  FiChevronRight
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Agent type with required properties
const AgentType = {
  id: '',
  name: '',
  avatar: '',
  description: '',
  isSystem: false,
  status: 'idle'
};

const SidebarAgentList = () => {
  const { colorMode } = useColorModeValue('light', 'dark');
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  
  // States
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAgentsExpanded, setIsAgentsExpanded] = useState(true);
  const [error, setError] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.200');
  const textColor = useColorModeValue('gray.700', 'gray.200');
  const mutedColor = useColorModeValue('gray.500', 'gray.500');
  
  // Navigation items
  const navItems = [
    { name: 'Dashboard', icon: FiHome, path: '/' },
    { name: 'Agents', icon: FiUsers, path: '/agents' },
    { name: 'Chat', icon: FiMessageSquare, path: '/chat' },
    { name: 'Activity', icon: FiActivity, path: '/activity' },
    { name: 'Settings', icon: FiSettings, path: '/settings' },
  ];
  
  // Fetch agents from API
  useEffect(() => {
    const fetchAgents = async () => {
      if (!isAuthenticated) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch agents from API
        const response = await fetch('/api/agents', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch agents');
        }
        
        const data = await response.json();
        
        // Ensure HAL and ASH are always visible as system agents
        const systemAgents = data.agents.filter(agent => agent.isSystem);
        const hasHAL = systemAgents.some(agent => agent.name === 'HAL');
        const hasASH = systemAgents.some(agent => agent.name === 'ASH');
        
        // Add HAL and ASH if they don't exist
        if (!hasHAL) {
          data.agents.push({
            id: 'hal9000',
            name: 'HAL',
            avatar: '',
            description: 'General purpose assistant',
            isSystem: true,
            status: 'idle'
          });
        }
        
        if (!hasASH) {
          data.agents.push({
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Security and monitoring assistant',
            isSystem: true,
            status: 'idle'
          });
        }
        
        setAgents(data.agents);
      } catch (err) {
        console.error('Error fetching agents:', err);
        setError('Failed to load agents');
        
        // Fallback to default system agents
        setAgents([
          {
            id: 'hal9000',
            name: 'HAL',
            avatar: '',
            description: 'General purpose assistant',
            isSystem: true,
            status: 'idle'
          },
          {
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Security and monitoring assistant',
            isSystem: true,
            status: 'idle'
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAgents();
  }, [isAuthenticated]);
  
  // Filter agents based on search query
  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Separate system and user agents
  const systemAgents = filteredAgents.filter(agent => agent.isSystem);
  const userAgents = filteredAgents.filter(agent => !agent.isSystem);
  
  // Generate avatar background color based on name
  const getAvatarBg = (name) => {
    const colors = ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'cyan', 'purple', 'pink'];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return `${colors[hash % colors.length]}.500`;
  };
  
  // Status indicator color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'green.500';
      case 'busy': return 'orange.500';
      case 'error': return 'red.500';
      default: return 'gray.400';
    }
  };
  
  if (!isAuthenticated) {
    return null;
  }
  
  return (
    <Box
      as="nav"
      position="fixed"
      left="0"
      w="64"
      h="calc(100vh - 4rem)"
      top="16"
      bg={bgColor}
      borderRightWidth="1px"
      borderColor={borderColor}
      display={{ base: 'none', md: 'block' }}
      zIndex="900"
      overflowY="auto"
      css={{
        '&::-webkit-scrollbar': {
          width: '4px',
        },
        '&::-webkit-scrollbar-track': {
          width: '6px',
        },
        '&::-webkit-scrollbar-thumb': {
          background: borderColor,
          borderRadius: '24px',
        },
      }}
    >
      {/* Main Navigation */}
      <VStack spacing={1} align="stretch" p={4}>
        {navItems.map((item) => (
          <Link to={item.path} key={item.name}>
            <HStack
              px={3}
              py={2}
              spacing={3}
              borderRadius="md"
              bg={location.pathname === item.path ? activeBg : 'transparent'}
              color={location.pathname === item.path ? activeColor : textColor}
              _hover={{
                bg: hoverBg,
                color: activeColor,
              }}
              transition="all 0.2s"
            >
              <Icon as={item.icon} boxSize={5} />
              <Text fontWeight={location.pathname === item.path ? 'medium' : 'normal'}>
                {item.name}
              </Text>
            </HStack>
          </Link>
        ))}
      </VStack>
      
      <Divider my={2} />
      
      {/* Agent Search */}
      <Box px={4} mb={2}>
        <InputGroup size="sm">
          <InputLeftElement pointerEvents="none">
            <Icon as={FiSearch} color={mutedColor} />
          </InputLeftElement>
          <Input
            placeholder="Search agents"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            borderRadius="md"
          />
        </InputGroup>
      </Box>
      
      {/* System Agents Section */}
      <Box px={4} mb={2}>
        <HStack 
          justifyContent="space-between" 
          mb={2}
          cursor="pointer"
          onClick={() => setIsAgentsExpanded(!isAgentsExpanded)}
        >
          <Text fontSize="xs" fontWeight="bold" color={mutedColor}>
            SYSTEM AGENTS
          </Text>
          <Icon 
            as={isAgentsExpanded ? FiChevronDown : FiChevronRight} 
            color={mutedColor}
            boxSize={4}
          />
        </HStack>
        
        <Collapse in={isAgentsExpanded} animateOpacity>
          {isLoading ? (
            <Flex justify="center" py={4}>
              <Spinner size="sm" color={activeColor} />
            </Flex>
          ) : error ? (
            <Text fontSize="sm" color="red.500" textAlign="center" py={2}>
              {error}
            </Text>
          ) : (
            <VStack spacing={1} align="stretch">
              {systemAgents.map((agent) => (
                <Link to={`/agent/${agent.id}`} key={agent.id}>
                  <HStack
                    px={2}
                    py={2}
                    spacing={3}
                    borderRadius="md"
                    bg={location.pathname === `/agent/${agent.id}` ? activeBg : 'transparent'}
                    color={location.pathname === `/agent/${agent.id}` ? activeColor : textColor}
                    _hover={{
                      bg: hoverBg,
                    }}
                    transition="all 0.2s"
                  >
                    <Box position="relative">
                      <Avatar 
                        size="xs" 
                        name={agent.name} 
                        src={agent.avatar} 
                        bg={getAvatarBg(agent.name)}
                      />
                      <Box
                        position="absolute"
                        bottom="0"
                        right="0"
                        width="8px"
                        height="8px"
                        borderRadius="full"
                        bg={getStatusColor(agent.status)}
                        border="1px solid"
                        borderColor={bgColor}
                      />
                    </Box>
                    <Text fontSize="sm">
                      {agent.name}
                    </Text>
                  </HStack>
                </Link>
              ))}
            </VStack>
          )}
        </Collapse>
      </Box>
      
      {/* User Agents Section */}
      <Box px={4} mb={2}>
        <HStack justifyContent="space-between" mb={2}>
          <Text fontSize="xs" fontWeight="bold" color={mutedColor}>
            YOUR AGENTS
          </Text>
          <Tooltip label="Create new agent">
            <Button
              size="xs"
              variant="ghost"
              p={1}
              minW="auto"
              h="auto"
              borderRadius="full"
            >
              <Icon as={FiPlus} boxSize={4} color={mutedColor} />
            </Button>
          </Tooltip>
        </HStack>
        
        <VStack spacing={1} align="stretch">
          {userAgents.length > 0 ? (
            userAgents.map((agent) => (
              <Link to={`/agent/${agent.id}`} key={agent.id}>
                <HStack
                  px={2}
                  py={2}
                  spacing={3}
                  borderRadius="md"
                  bg={location.pathname === `/agent/${agent.id}` ? activeBg : 'transparent'}
                  color={location.pathname === `/agent/${agent.id}` ? activeColor : textColor}
                  _hover={{
                    bg: hoverBg,
                  }}
                  transition="all 0.2s"
                >
                  <Box position="relative">
                    <Avatar 
                      size="xs" 
                      name={agent.name} 
                      src={agent.avatar} 
                      bg={getAvatarBg(agent.name)}
                    />
                    <Box
                      position="absolute"
                      bottom="0"
                      right="0"
                      width="8px"
                      height="8px"
                      borderRadius="full"
                      bg={getStatusColor(agent.status)}
                      border="1px solid"
                      borderColor={bgColor}
                    />
                  </Box>
                  <Text fontSize="sm">
                    {agent.name}
                  </Text>
                </HStack>
              </Link>
            ))
          ) : (
            <Text fontSize="sm" color={mutedColor} py={2} textAlign="center">
              No custom agents yet
            </Text>
          )}
        </VStack>
      </Box>
      
      <Divider my={2} />
      
      {/* Version Info */}
      <Box px={4} py={2}>
        <Text fontSize="xs" color={mutedColor}>
          Promethios OS v2.0.0
        </Text>
      </Box>
    </Box>
  );
};

export default SidebarAgentList;
