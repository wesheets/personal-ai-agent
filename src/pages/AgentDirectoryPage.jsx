import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  Spinner,
  useColorModeValue,
  Heading,
  SimpleGrid,
  Button,
  Icon,
  Input,
  InputGroup,
  InputLeftElement
} from '@chakra-ui/react';
import { FiSearch, FiPlus, FiUsers } from 'react-icons/fi';
import AgentCard from '../components/layout/AgentCard';
import { useAuth } from '../context/AuthContext';

const AgentListPage = () => {
  const { isAuthenticated } = useAuth();
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const mutedColor = useColorModeValue('gray.500', 'gray.500');
  
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
            description: 'General purpose assistant for everyday tasks and questions.',
            isSystem: true,
            status: 'idle',
            lastActive: '2 hours ago'
          });
        }
        
        if (!hasASH) {
          data.agents.push({
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Advanced security handler for sensitive operations and security monitoring.',
            isSystem: true,
            status: 'active',
            lastActive: '5 minutes ago'
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
            description: 'General purpose assistant for everyday tasks and questions.',
            isSystem: true,
            status: 'idle',
            lastActive: '2 hours ago'
          },
          {
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Advanced security handler for sensitive operations and security monitoring.',
            isSystem: true,
            status: 'active',
            lastActive: '5 minutes ago'
          },
          {
            id: 'research-agent',
            name: 'Research Agent',
            avatar: '',
            description: 'Specialized in research tasks, data analysis, and information gathering.',
            isSystem: false,
            status: 'idle',
            lastActive: 'Yesterday'
          },
          {
            id: 'code-assistant',
            name: 'Code Assistant',
            avatar: '',
            description: 'Helps with programming tasks, code reviews, and technical documentation.',
            status: 'busy',
            isSystem: false,
            lastActive: '3 days ago'
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
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Separate system and user agents
  const systemAgents = filteredAgents.filter(agent => agent.isSystem);
  const userAgents = filteredAgents.filter(agent => !agent.isSystem);
  
  return (
    <Box>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Box>
          <Heading as="h1" size="xl">
            Agent Directory
          </Heading>
          <Text color={mutedColor} mt={1}>
            Access and manage your AI agents
          </Text>
        </Box>
        
        <Button leftIcon={<FiPlus />} colorScheme="blue">
          Create New Agent
        </Button>
      </Flex>
      
      <Box 
        p={4} 
        bg={bgColor} 
        borderRadius="lg" 
        boxShadow="sm" 
        borderWidth="1px" 
        borderColor={borderColor}
        mb={6}
      >
        <InputGroup>
          <InputLeftElement pointerEvents="none">
            <Icon as={FiSearch} color={mutedColor} />
          </InputLeftElement>
          <Input
            placeholder="Search agents by name or description"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </InputGroup>
      </Box>
      
      {isLoading ? (
        <Flex justify="center" py={10}>
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : error ? (
        <Box 
          p={6} 
          bg={bgColor} 
          borderRadius="lg" 
          boxShadow="sm" 
          borderWidth="1px" 
          borderColor="red.300"
          textAlign="center"
        >
          <Text color="red.500">{error}</Text>
        </Box>
      ) : (
        <VStack spacing={8} align="stretch">
          {/* System Agents Section */}
          <Box>
            <Flex alignItems="center" mb={4}>
              <Icon as={FiUsers} mr={2} color="purple.500" />
              <Heading as="h2" size="md">
                System Agents
              </Heading>
            </Flex>
            
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              {systemAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  name={agent.name}
                  description={agent.description}
                  avatar={agent.avatar}
                  status={agent.status}
                  isSystem={agent.isSystem}
                  lastActive={agent.lastActive}
                  onClick={() => window.location.href = `/agent/${agent.id}`}
                />
              ))}
            </SimpleGrid>
          </Box>
          
          {/* User Agents Section */}
          {userAgents.length > 0 && (
            <Box>
              <Flex alignItems="center" mb={4}>
                <Icon as={FiUsers} mr={2} color="blue.500" />
                <Heading as="h2" size="md">
                  Your Custom Agents
                </Heading>
              </Flex>
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {userAgents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    name={agent.name}
                    description={agent.description}
                    avatar={agent.avatar}
                    status={agent.status}
                    isSystem={agent.isSystem}
                    lastActive={agent.lastActive}
                    onClick={() => window.location.href = `/agent/${agent.id}`}
                  />
                ))}
              </SimpleGrid>
            </Box>
          )}
          
          {filteredAgents.length === 0 && (
            <Box 
              p={6} 
              bg={bgColor} 
              borderRadius="lg" 
              boxShadow="sm" 
              borderWidth="1px" 
              borderColor={borderColor}
              textAlign="center"
            >
              <Text color={mutedColor}>No agents found matching your search criteria</Text>
            </Box>
          )}
        </VStack>
      )}
    </Box>
  );
};

export default AgentListPage;
