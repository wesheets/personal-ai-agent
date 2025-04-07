import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  HStack,
  useColorModeValue,
  Heading,
  Divider,
  Button,
  Icon,
  Badge,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { FiDatabase, FiUser, FiUsers, FiLock, FiUnlock } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const MemoryUserScoping = ({ agentId }) => {
  const { user } = useAuth();
  const toast = useToast();
  const [memories, setMemories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const publicBadgeBg = useColorModeValue('green.100', 'green.800');
  const privateBadgeBg = useColorModeValue('blue.100', 'blue.800');
  const systemBadgeBg = useColorModeValue('purple.100', 'purple.800');
  
  // Fetch memories from API
  useEffect(() => {
    const fetchMemories = async () => {
      if (!agentId) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`/api/memory/agent-${agentId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch memories');
        }
        
        const data = await response.json();
        setMemories(data.memories || []);
      } catch (err) {
        console.error('Error fetching memories:', err);
        setError('Failed to load memories');
        setMemories([]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchMemories();
  }, [agentId]);
  
  // Group memories by type
  const userMemories = memories.filter(memory => memory.user_id === user?.id);
  const publicMemories = memories.filter(memory => memory.user_id !== user?.id);
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Get badge for memory type
  const getMemoryBadge = (memory) => {
    if (memory.user_id === 'system') {
      return (
        <Badge bg={systemBadgeBg} px={2} py={1} borderRadius="full">
          <HStack spacing={1}>
            <Icon as={FiUsers} />
            <Text>System</Text>
          </HStack>
        </Badge>
      );
    } else if (memory.user_id === user?.id) {
      return (
        <Badge bg={privateBadgeBg} px={2} py={1} borderRadius="full">
          <HStack spacing={1}>
            <Icon as={FiLock} />
            <Text>Private</Text>
          </HStack>
        </Badge>
      );
    } else {
      return (
        <Badge bg={publicBadgeBg} px={2} py={1} borderRadius="full">
          <HStack spacing={1}>
            <Icon as={FiUnlock} />
            <Text>Public</Text>
          </HStack>
        </Badge>
      );
    }
  };
  
  return (
    <Box>
      <Heading size="md" mb={4}>
        <HStack>
          <Icon as={FiDatabase} />
          <Text>Agent Memory</Text>
        </HStack>
      </Heading>
      
      {isLoading ? (
        <Flex justify="center" align="center" py={10}>
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : error ? (
        <Box 
          p={4} 
          bg="red.50" 
          color="red.500" 
          borderRadius="md" 
          borderWidth="1px" 
          borderColor="red.200"
        >
          {error}
        </Box>
      ) : memories.length === 0 ? (
        <Box 
          p={4} 
          bg="gray.50" 
          borderRadius="md" 
          borderWidth="1px" 
          borderColor="gray.200"
          textAlign="center"
        >
          No memories found for this agent.
        </Box>
      ) : (
        <VStack spacing={4} align="stretch">
          {userMemories.length > 0 && (
            <Box>
              <HStack mb={2}>
                <Icon as={FiUser} />
                <Text fontWeight="bold">Your Memories</Text>
              </HStack>
              
              <VStack 
                spacing={2} 
                align="stretch" 
                p={4} 
                bg={bgColor} 
                borderRadius="md" 
                borderWidth="1px" 
                borderColor={borderColor}
              >
                {userMemories.map((memory) => (
                  <Box 
                    key={memory.id} 
                    p={3} 
                    borderRadius="md" 
                    borderWidth="1px" 
                    borderColor={borderColor}
                  >
                    <HStack justify="space-between" mb={2}>
                      {getMemoryBadge(memory)}
                      <Text fontSize="sm" color="gray.500">
                        {formatTimestamp(memory.timestamp)}
                      </Text>
                    </HStack>
                    
                    <Text>{memory.content}</Text>
                    
                    {memory.metadata && memory.metadata.tags && (
                      <HStack mt={2} spacing={1}>
                        {memory.metadata.tags.map((tag) => (
                          <Badge key={tag} colorScheme="blue" variant="subtle">
                            {tag}
                          </Badge>
                        ))}
                      </HStack>
                    )}
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
          
          {publicMemories.length > 0 && (
            <Box>
              <HStack mb={2}>
                <Icon as={FiUsers} />
                <Text fontWeight="bold">Public Memories</Text>
              </HStack>
              
              <VStack 
                spacing={2} 
                align="stretch" 
                p={4} 
                bg={bgColor} 
                borderRadius="md" 
                borderWidth="1px" 
                borderColor={borderColor}
              >
                {publicMemories.map((memory) => (
                  <Box 
                    key={memory.id} 
                    p={3} 
                    borderRadius="md" 
                    borderWidth="1px" 
                    borderColor={borderColor}
                  >
                    <HStack justify="space-between" mb={2}>
                      {getMemoryBadge(memory)}
                      <Text fontSize="sm" color="gray.500">
                        {formatTimestamp(memory.timestamp)}
                      </Text>
                    </HStack>
                    
                    <Text>{memory.content}</Text>
                    
                    {memory.metadata && memory.metadata.tags && (
                      <HStack mt={2} spacing={1}>
                        {memory.metadata.tags.map((tag) => (
                          <Badge key={tag} colorScheme="purple" variant="subtle">
                            {tag}
                          </Badge>
                        ))}
                      </HStack>
                    )}
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
        </VStack>
      )}
    </Box>
  );
};

export default MemoryUserScoping;
