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
  Spinner
} from '@chakra-ui/react';
import { FiMessageCircle, FiCpu } from 'react-icons/fi';
import { useParams } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import AgentChatPanel from '../components/AgentChatPanel';
import { useAuth } from '../context/AuthContext';

const ChatPage = () => {
  const { agentId } = useParams();
  const { isAuthenticated } = useAuth();
  const [agent, setAgent] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
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
            lastActive: '2 hours ago'
          });
        } else if (agentId === 'ash-xenomorph') {
          setAgent({
            id: 'ash-xenomorph',
            name: 'ASH',
            avatar: '',
            description: 'Advanced security handler for sensitive operations and security monitoring.',
            isSystem: true,
            status: 'active',
            lastActive: '5 minutes ago'
          });
        } else {
          setAgent({
            id: agentId,
            name: 'Unknown Agent',
            avatar: '',
            description: 'Agent details could not be loaded.',
            isSystem: false,
            status: 'error',
            lastActive: 'Unknown'
          });
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAgentDetails();
  }, [isAuthenticated, agentId]);
  
  // Mock function for sending messages
  const handleSendMessage = async ({ conversationId, message, attachments }) => {
    console.log('Sending message:', { conversationId, message, attachments });
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return mock response
    return {
      conversationId: conversationId || `conv-${Date.now()}`,
      message: `This is a mock response to: "${message}"`
    };
  };
  
  // Mock function for streaming messages
  const handleStreamMessage = async ({ conversationId, message, attachments, signal }) => {
    console.log('Streaming message:', { conversationId, message, attachments });
    
    // Create a ReadableStream that emits chunks of text
    const stream = new ReadableStream({
      start(controller) {
        const responses = [
          "I'm processing your request",
          "...\n\n",
          "Based on your message, ",
          "I can provide the following information:\n\n",
          "1. The implementation of streaming responses is working correctly\n",
          "2. This demonstrates how text can be streamed word by word\n",
          "3. The UI updates in real-time as new content arrives\n\n",
          "Is there anything specific you'd like to know about this feature?"
        ];
        
        let index = 0;
        
        const interval = setInterval(() => {
          if (index < responses.length) {
            const chunk = responses[index];
            const encoder = new TextEncoder();
            controller.enqueue(encoder.encode(chunk));
            index++;
          } else {
            clearInterval(interval);
            controller.close();
          }
        }, 300);
        
        // Handle abort signal
        if (signal) {
          signal.addEventListener('abort', () => {
            clearInterval(interval);
            controller.close();
          });
        }
      }
    });
    
    // Return mock streaming response
    return {
      conversationId: conversationId || `conv-${Date.now()}`,
      stream
    };
  };
  
  // Handle starting a new conversation
  const handleNewConversation = () => {
    console.log('Starting new conversation with agent:', agentId);
  };
  
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
    <Box h="calc(100vh - 16rem)">
      <PageHeader
        title={`Chat with ${agent?.name || 'Agent'}`}
        subtitle={agent?.description || 'Start a conversation with this agent'}
        icon={FiMessageCircle}
        status={{ 
          type: agent?.status === 'active' ? 'success' : 
                agent?.status === 'busy' ? 'warning' : 
                agent?.status === 'error' ? 'error' : 'info',
          text: agent?.status === 'active' ? 'Active' : 
                agent?.status === 'busy' ? 'Busy' : 
                agent?.status === 'error' ? 'Error' : 'Idle'
        }}
      />
      
      <Box h="calc(100% - 6rem)" mt={6}>
        <AgentChatPanel
          agentId={agent?.id}
          agentName={agent?.name}
          agentAvatar={agent?.avatar}
          isSystemAgent={agent?.isSystem}
          onNewConversation={handleNewConversation}
          onSendMessage={handleSendMessage}
          onStreamMessage={handleStreamMessage}
        />
      </Box>
    </Box>
  );
};

export default ChatPage;
