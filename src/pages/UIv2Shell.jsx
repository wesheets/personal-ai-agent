import React, { useState, useEffect } from 'react';
import { Box, Flex, Container, VStack, HStack, Button, useColorModeValue, Heading, Text, Grid, GridItem, Input, IconButton } from '@chakra-ui/react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { FiSend, FiPaperclip } from 'react-icons/fi';
import AppLayout from '../components/layout/AppLayout';

/**
 * UIv2Shell - The main shell component for the Promethios UI v2
 * This component serves as the container for all authenticated pages
 */
const UIv2Shell = ({ activePage }) => {
  const params = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Determine which content to show based on the active page
  const renderContent = () => {
    // Extract agent ID from URL if present
    const agentId = params.agentId;
    
    switch (activePage) {
      case 'dashboard':
        return <DashboardContent />;
      case 'chat':
        return <ChatContent agentId={agentId} />;
      case 'agent':
        return <AgentDetailContent agentId={agentId} />;
      default:
        return <DashboardContent />;
    }
  };

  return (
    <AppLayout activePage={activePage}>
      {renderContent()}
    </AppLayout>
  );
};

// Dashboard content component
const DashboardContent = () => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const navigate = useNavigate();
  
  const handleAgentChat = (agentId) => {
    navigate(`/chat/${agentId}`);
  };
  
  return (
    <VStack spacing={6} align="stretch">
      <Heading as="h1" size="lg" mb={4}>Dashboard</Heading>
      
      <Grid templateColumns={{ base: "repeat(1, 1fr)", md: "repeat(2, 1fr)" }} gap={6}>
        {/* System Agents Section */}
        <GridItem 
          p={6} 
          borderWidth="1px" 
          borderRadius="lg" 
          borderColor={borderColor}
          bg={useColorModeValue('white', 'gray.800')}
          shadow="md"
        >
          <Heading as="h2" size="md" mb={4}>System Agents</Heading>
          <VStack align="stretch" spacing={4}>
            <HStack p={3} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
              <Box fontWeight="bold" flex="1">HAL</Box>
              <Button size="sm" colorScheme="blue" onClick={() => handleAgentChat('hal9000')}>Chat</Button>
            </HStack>
            <HStack p={3} bg={useColorModeValue('purple.50', 'purple.900')} borderRadius="md">
              <Box fontWeight="bold" flex="1">ASH</Box>
              <Button size="sm" colorScheme="purple" onClick={() => handleAgentChat('ash-xenomorph')}>Chat</Button>
            </HStack>
          </VStack>
        </GridItem>
        
        {/* Activity Summary */}
        <GridItem 
          p={6} 
          borderWidth="1px" 
          borderRadius="lg" 
          borderColor={borderColor}
          bg={useColorModeValue('white', 'gray.800')}
          shadow="md"
        >
          <Heading as="h2" size="md" mb={4}>Recent Activity</Heading>
          <VStack align="stretch" spacing={3}>
            <Box p={3} borderRadius="md" bg={useColorModeValue('gray.50', 'gray.700')}>
              <Text fontWeight="bold">HAL completed a task</Text>
              <Text fontSize="sm" color="gray.500">Today at 10:30 AM</Text>
            </Box>
            <Box p={3} borderRadius="md" bg={useColorModeValue('gray.50', 'gray.700')}>
              <Text fontWeight="bold">ASH analyzed a document</Text>
              <Text fontSize="sm" color="gray.500">Yesterday at 3:45 PM</Text>
            </Box>
          </VStack>
        </GridItem>
      </Grid>
      
      {/* Features Section */}
      <Box 
        p={6} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={useColorModeValue('white', 'gray.800')}
        shadow="md"
      >
        <Heading as="h2" size="md" mb={4}>Key Features</Heading>
        <Grid templateColumns={{ base: "repeat(1, 1fr)", md: "repeat(3, 1fr)" }} gap={4}>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ JWT-based authentication</Text>
          </Box>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ Multi-agent support</Text>
          </Box>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ User-scoped memory</Text>
          </Box>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ File attachments</Text>
          </Box>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ Activity logging</Text>
          </Box>
          <Box p={3} borderRadius="md" bg={useColorModeValue('green.50', 'green.900')}>
            <Text>✅ Responsive design</Text>
          </Box>
        </Grid>
      </Box>
    </VStack>
  );
};

// Chat content component
const ChatContent = ({ agentId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Determine agent details based on agentId
  const getAgentDetails = (id) => {
    switch(id) {
      case 'hal9000':
        return { name: 'HAL', color: 'blue', systemMessage: true };
      case 'ash-xenomorph':
        return { name: 'ASH', color: 'purple', systemMessage: true };
      default:
        return { name: 'Agent', color: 'gray', systemMessage: false };
    }
  };
  
  const agentDetails = getAgentDetails(agentId);
  
  // Initialize chat with welcome message
  useEffect(() => {
    if (agentDetails.systemMessage) {
      setMessages([
        {
          sender: 'agent',
          text: `Hello! I'm ${agentDetails.name}. How can I assist you today?`,
          timestamp: new Date()
        }
      ]);
    } else {
      setMessages([]);
    }
  }, [agentId]);
  
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    
    // Add user message
    const userMessage = {
      sender: 'user',
      text: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    // Simulate agent response after delay
    setTimeout(() => {
      const agentResponse = {
        sender: 'agent',
        text: `I'm ${agentDetails.name}, responding to your message: "${inputMessage}"`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, agentResponse]);
      setIsLoading(false);
    }, 1500);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };
  
  return (
    <VStack spacing={4} align="stretch" h="calc(100vh - 140px)">
      <Flex 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={useColorModeValue('white', 'gray.800')}
        align="center"
      >
        <Box
          bg={`${agentDetails.color}.500`}
          color="white"
          borderRadius="full"
          boxSize="40px"
          fontSize="md"
          fontWeight="bold"
          display="flex"
          alignItems="center"
          justifyContent="center"
          mr={3}
        >
          {agentDetails.name.charAt(0)}
        </Box>
        <Box>
          <Heading as="h2" size="md">Chat with {agentDetails.name}</Heading>
          <Text fontSize="sm" opacity="0.8">System Agent</Text>
        </Box>
      </Flex>
      
      <Box 
        flex="1" 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={useColorModeValue('white', 'gray.800')}
        overflowY="auto"
      >
        <VStack spacing={4} align="stretch">
          {messages.map((message, index) => (
            <Box 
              key={index}
              alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
              maxW="80%" 
              p={3} 
              borderRadius="lg" 
              bg={message.sender === 'user' 
                ? useColorModeValue('blue.100', 'blue.700') 
                : useColorModeValue(`${agentDetails.color}.50`, `${agentDetails.color}.900`)}
            >
              <Text>{message.text}</Text>
              <Text fontSize="xs" opacity="0.7" textAlign="right" mt={1}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            </Box>
          ))}
          
          {isLoading && (
            <Box alignSelf="flex-start" maxW="80%" p={3} borderRadius="lg" bg={useColorModeValue(`${agentDetails.color}.50`, `${agentDetails.color}.900`)}>
              <Text>Thinking...</Text>
            </Box>
          )}
        </VStack>
      </Box>
      
      <Flex 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={useColorModeValue('white', 'gray.800')}
      >
        <IconButton
          icon={<FiPaperclip />}
          aria-label="Attach file"
          variant="ghost"
          mr={2}
        />
        <Input
          flex="1"
          mr={2}
          placeholder="Type your message here..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <Button 
          colorScheme={agentDetails.color}
          onClick={handleSendMessage}
          isDisabled={!inputMessage.trim()}
          leftIcon={<FiSend />}
        >
          Send
        </Button>
      </Flex>
    </VStack>
  );
};

// Agent detail content component
const AgentDetailContent = ({ agentId }) => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const navigate = useNavigate();
  
  // Determine agent details based on agentId
  const getAgentDetails = (id) => {
    switch(id) {
      case 'hal9000':
        return { 
          name: 'HAL', 
          color: 'blue',
          description: 'HAL is an advanced AI system designed to assist with a wide range of tasks and provide information on various topics.',
          capabilities: ['Information retrieval', 'Task automation', 'Problem solving', 'Data analysis']
        };
      case 'ash-xenomorph':
        return { 
          name: 'ASH', 
          color: 'purple',
          description: 'ASH is a specialized AI focused on scientific analysis and research assistance.',
          capabilities: ['Scientific research', 'Data visualization', 'Pattern recognition', 'Technical documentation']
        };
      default:
        return { 
          name: 'Agent', 
          color: 'gray',
          description: 'A general-purpose AI assistant.',
          capabilities: ['Information retrieval', 'Task automation']
        };
    }
  };
  
  const agentDetails = getAgentDetails(agentId);
  
  const handleChatWithAgent = () => {
    navigate(`/chat/${agentId}`);
  };
  
  return (
    <VStack spacing={6} align="stretch">
      <Heading as="h1" size="lg" mb={4}>{agentDetails.name} Details</Heading>
      
      <Box 
        p={6} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={useColorModeValue('white', 'gray.800')}
        shadow="md"
      >
        <Flex align="center" mb={6}>
          <Box
            bg={`${agentDetails.color}.500`}
            color="white"
            borderRadius="full"
            boxSize="60px"
            fontSize="xl"
            fontWeight="bold"
            display="flex"
            alignItems="center"
            justifyContent="center"
            mr={4}
          >
            {agentDetails.name.charAt(0)}
          </Box>
          <Box>
            <Heading as="h2" size="lg">{agentDetails.name}</Heading>
            <Text>System Agent</Text>
          </Box>
        </Flex>
        
        <VStack align="stretch" spacing={4}>
          <Box>
            <Text fontWeight="bold" mb={1}>Description</Text>
            <Text>{agentDetails.description}</Text>
          </Box>
          
          <Box>
            <Text fontWeight="bold" mb={1}>Capabilities</Text>
            <Grid templateColumns={{ base: "repeat(1, 1fr)", md: "repeat(2, 1fr)" }} gap={3}>
              {agentDetails.capabilities.map((capability, index) => (
                <Box key={index} p={2} borderRadius="md" bg={useColorModeValue(`${agentDetails.color}.50`, `${agentDetails.color}.900`)}>
                  <Text>{capability}</Text>
                </Box>
              ))}
            </Grid>
          </Box>
        </VStack>
        
        <Button colorScheme={agentDetails.color} mt={6} onClick={handleChatWithAgent}>
          Chat with {agentDetails.name}
        </Button>
      </Box>
    </VStack>
  );
};

export default UIv2Shell;
