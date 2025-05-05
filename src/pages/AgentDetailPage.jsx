import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  Spinner,
  useColorModeValue,
  Heading,
  Avatar,
  HStack,
  Icon,
  Divider
} from '@chakra-ui/react';
import { FiMessageCircle, FiCpu } from 'react-icons/fi';
import { useParams } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import { useAuth } from '../context/AuthContext';

const AgentDetailPage = () => {
  const { agentId } = useParams();
  const { isAuthenticated } = useAuth();
  const [agent, setAgent] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const mutedColor = useColorModeValue('gray.500', 'gray.500');
  
  // Generate avatar background color based on name
  const getAvatarBg = (name) => {
    if (!name) return 'blue.500';
    const colors = ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'cyan', 'purple', 'pink'];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return `${colors[hash % colors.length]}.500`;
  };
  
  // Fetch agent details from API
  useEffect(() => {
    const fetchAgentDetails = async () => {
      if (!isAuthenticated || !agentId) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch agent from API
        const response = await fetch(`/api/agents/${agentId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch agent details');
        }
        
        const data = await response.json();
        setAgent(data.agent);
      } catch (err) {
        console.error('Error fetching agent details:', err);
        setError('Failed to load agent details');
        
        // Fallback to default agent data based on ID
        if (agentId === 'hal9000') {
          setAgent({
            id: 'hal9000',
            name: 'HAL',
            avatar: '',
            description: 'General purpose assistant for everyday tasks and questions.',
            isSystem: true,
            status: 'idle',
            lastActive: '2 hours ago',
            capabilities: [
              'Answer general knowledge questions',
              'Assist with task planning',
              'Provide recommendations',
              'Search the web for information',
              'Summarize content'
            ]
          });
        } else if (agentId === 'ash-xenomorph') {
          setAgent({
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Advanced security handler for sensitive operations and security monitoring.',
            isSystem: true,
            status: 'active',
            lastActive: '5 minutes ago',
            capabilities: [
              'Monitor system security',
              'Detect anomalies',
              'Manage access control',
              'Perform security audits',
              'Handle sensitive operations'
            ]
          });
        } else {
          setAgent({
            id: agentId,
            name: 'Unknown Agent',
            avatar: '',
            description: 'Agent details could not be loaded.',
            isSystem: false,
            status: 'error',
            lastActive: 'Unknown',
            capabilities: []
          });
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAgentDetails();
  }, [isAuthenticated, agentId]);
  
  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="100%" py={10}>
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }
  
  if (error && !agent) {
    return (
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
    );
  }
  
  return (
    <Box>
      <PageHeader
        title={agent?.name || 'Agent Details'}
        subtitle={agent?.isSystem ? 'System Agent' : 'Custom Agent'}
        icon={FiCpu}
        status={{ 
          type: agent?.status === 'active' ? 'success' : 
                agent?.status === 'busy' ? 'warning' : 
                agent?.status === 'error' ? 'error' : 'info',
          text: agent?.status === 'active' ? 'Active' : 
                agent?.status === 'busy' ? 'Busy' : 
                agent?.status === 'error' ? 'Error' : 'Idle'
        }}
      />
      
      <VStack spacing={6} align="stretch">
        {/* Agent Profile */}
        <Box 
          p={6} 
          bg={bgColor} 
          borderRadius="lg" 
          boxShadow="sm" 
          borderWidth="1px" 
          borderColor={borderColor}
        >
          <Flex direction={{ base: 'column', md: 'row' }} align={{ base: 'center', md: 'flex-start' }}>
            <Avatar 
              size="xl" 
              name={agent?.name} 
              src={agent?.avatar} 
              bg={getAvatarBg(agent?.name)}
              mr={{ base: 0, md: 6 }}
              mb={{ base: 4, md: 0 }}
            />
            
            <Box flex="1">
              <Heading as="h2" size="lg" mb={2}>
                {agent?.name}
              </Heading>
              
              <Text color={mutedColor} mb={4}>
                Last active: {agent?.lastActive || 'Unknown'}
              </Text>
              
              <Text fontSize="md" mb={4}>
                {agent?.description}
              </Text>
              
              <HStack spacing={4}>
                <Flex
                  as="button"
                  align="center"
                  bg="blue.500"
                  color="white"
                  px={4}
                  py={2}
                  borderRadius="md"
                  _hover={{ bg: 'blue.600' }}
                >
                  <Icon as={FiMessageCircle} mr={2} />
                  <Text>Start Chat</Text>
                </Flex>
              </HStack>
            </Box>
          </Flex>
        </Box>
        
        {/* Agent Capabilities */}
        {agent?.capabilities && agent.capabilities.length > 0 && (
          <Box 
            p={6} 
            bg={bgColor} 
            borderRadius="lg" 
            boxShadow="sm" 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Heading as="h3" size="md" mb={4}>
              Capabilities
            </Heading>
            
            <Divider mb={4} />
            
            <VStack spacing={2} align="stretch">
              {agent.capabilities.map((capability, index) => (
                <HStack key={index} spacing={3} p={2}>
                  <Box 
                    w={2} 
                    h={2} 
                    borderRadius="full" 
                    bg="blue.500" 
                  />
                  <Text>{capability}</Text>
                </HStack>
              ))}
            </VStack>
          </Box>
        )}
        
        {/* Agent History - Placeholder for future implementation */}
        <Box 
          p={6} 
          bg={bgColor} 
          borderRadius="lg" 
          boxShadow="sm" 
          borderWidth="1px" 
          borderColor={borderColor}
        >
          <Heading as="h3" size="md" mb={4}>
            Recent Interactions
          </Heading>
          
          <Divider mb={4} />
          
          <Text color={mutedColor} textAlign="center" py={4}>
            No recent interactions with this agent
          </Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default AgentDetailPage;
