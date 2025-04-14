import React, { useState, useEffect, useRef } from 'react';
import { Box, Flex, VStack, Text, Input, Button, IconButton, useColorModeValue, Spinner, Center } from '@chakra-ui/react';
import { FiSend, FiPaperclip } from 'react-icons/fi';
import { useParams } from 'react-router-dom';
import FileAttachmentHandler from './FileAttachmentHandler';
import ActivityLogTray from './ActivityLogTray';
import MemoryUserScoping from './MemoryUserScoping';
import { controlService } from '../api/ApiService';

/**
 * AgentChatPanel component
 * Handles chat interactions with streaming support
 */
const AgentChatPanel = () => {
  // Get agentId from URL params
  const { agentId } = useParams();
  const [agentData, setAgentData] = useState(null);
  const [isAgentLoading, setIsAgentLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showMemory, setShowMemory] = useState(false);
  const messagesEndRef = useRef(null);
  
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // Fetch agent data from API
  useEffect(() => {
    const fetchAgentData = async () => {
      setIsAgentLoading(true);
      try {
        const response = await controlService.getAgentStatus();
        if (response && response.agents) {
          const agent = response.agents.find(a => a.id === agentId);
          if (agent) {
            setAgentData(agent);
          } else {
            console.warn(`Agent with ID ${agentId} not found in API response`);
            // Use fallback data if agent not found
            setAgentData({
              id: agentId,
              name: getAgentNameFromId(agentId),
              status: 'unknown',
              type: 'system'
            });
          }
        }
      } catch (error) {
        console.error('Error fetching agent data:', error);
      } finally {
        setIsAgentLoading(false);
      }
    };
    
    if (agentId) {
      fetchAgentData();
    }
  }, [agentId]);
  
  // Helper function to get agent name from ID
  const getAgentNameFromId = (id) => {
    switch(id) {
      case 'hal9000':
        return 'HAL 9000';
      case 'ash-xenomorph':
        return 'ASH';
      default:
        return 'Unknown Agent';
    }
  };
  
  // Determine agent details based on agentId or agentData
  const getAgentDetails = (id) => {
    // If we have agent data from API, use that
    if (agentData) {
      const color = id === 'hal9000' ? 'blue' : id === 'ash-xenomorph' ? 'purple' : 'gray';
      return { 
        name: agentData.name?.split(' ')[0] || 'Agent', 
        color: color, 
        systemMessage: true 
      };
    }
    
    // Fallback to hardcoded values
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
  }, [agentId, agentDetails.systemMessage, agentDetails.name]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamedText]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
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
    
    // Simulate streaming response
    simulateStreamingResponse(inputMessage);
  };
  
  const simulateStreamingResponse = (userInput) => {
    // Start streaming
    setIsStreaming(true);
    setStreamedText('');
    
    // Generate response based on user input
    let response = '';
    if (userInput.toLowerCase().includes('help')) {
      response = `I'd be happy to help you with that. As ${agentDetails.name}, I can assist with various tasks including information retrieval, data analysis, and problem-solving.`;
    } else if (userInput.toLowerCase().includes('file') || userInput.toLowerCase().includes('upload')) {
      response = `You can upload files using the attachment button in the chat interface. I can process various file types including documents, images, and data files.`;
    } else if (userInput.toLowerCase().includes('memory')) {
      response = `I maintain a memory of our conversations and any files you've shared with me. This helps me provide more contextual and relevant responses over time.`;
    } else {
      response = `Thank you for your message. I'm ${agentDetails.name}, and I'm processing your request: "${userInput}". Is there anything specific you'd like to know more about?`;
    }
    
    // Simulate streaming by adding one character at a time
    let index = 0;
    const streamInterval = setInterval(() => {
      if (index < response.length) {
        setStreamedText(prev => prev + response.charAt(index));
        index++;
      } else {
        // Streaming complete
        clearInterval(streamInterval);
        setIsStreaming(false);
        setIsLoading(false);
        
        // Add completed response to messages
        const agentResponse = {
          sender: 'agent',
          text: response,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, agentResponse]);
        setStreamedText('');
      }
    }, 30); // Adjust speed as needed
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload);
    setShowMemory(false);
  };
  
  const toggleMemory = () => {
    setShowMemory(!showMemory);
    setShowFileUpload(false);
  };
  
  const handleFileUpload = (files) => {
    // Add message about file upload
    const fileMessage = {
      sender: 'user',
      text: `Uploaded ${files.length} file${files.length !== 1 ? 's' : ''}: ${files.map(f => f.name).join(', ')}`,
      timestamp: new Date(),
      isFileUpload: true
    };
    
    setMessages(prev => [...prev, fileMessage]);
    setShowFileUpload(false);
    
    // Simulate agent response to file upload
    setIsLoading(true);
    
    setTimeout(() => {
      const agentResponse = {
        sender: 'agent',
        text: `I've received your file${files.length !== 1 ? 's' : ''} and added ${files.length !== 1 ? 'them' : 'it'} to our conversation memory. Is there anything specific you'd like me to do with ${files.length !== 1 ? 'these files' : 'this file'}?`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, agentResponse]);
      setIsLoading(false);
    }, 1500);
  };
  
  // Render loading state
  if (isAgentLoading) {
    return (
      <Center h="calc(100vh - 140px)">
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" thickness="4px" />
          <Text>Loading agent interface...</Text>
        </VStack>
      </Center>
    );
  }

  // Render error state if no agent data and not loading
  if (!agentId) {
    return (
      <Center h="calc(100vh - 140px)">
        <VStack spacing={4} maxW="md" textAlign="center" p={8} borderWidth="1px" borderRadius="lg" borderColor={borderColor} bg={bgColor}>
          <Box
            bg="red.500"
            color="white"
            borderRadius="full"
            boxSize="60px"
            fontSize="xl"
            fontWeight="bold"
            display="flex"
            alignItems="center"
            justifyContent="center"
            mb={2}
          >
            !
          </Box>
          <Text fontWeight="bold" fontSize="xl">Agent Not Found</Text>
          <Text>The requested agent could not be loaded. Please select a valid agent from the dashboard.</Text>
          <Button colorScheme="blue" onClick={() => window.location.href = '/dashboard'}>
            Return to Dashboard
          </Button>
        </VStack>
      </Center>
    );
  }

  return (
    <VStack spacing={4} align="stretch" h="calc(100vh - 140px)">
      <Flex 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={bgColor}
        align="center"
        justify="space-between"
      >
        <Flex align="center">
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
            <Text fontWeight="bold">Chat with {agentDetails.name}</Text>
            <Text fontSize="sm" opacity="0.8">{agentData?.type || 'System'} Agent</Text>
          </Box>
        </Flex>
        
        <Flex>
          <Button 
            size="sm" 
            variant="ghost" 
            colorScheme={agentDetails.color} 
            mr={2}
            onClick={toggleMemory}
          >
            Memory
          </Button>
          <ActivityLogTray agentId={agentId} />
        </Flex>
      </Flex>
      
      {showMemory && (
        <Box 
          p={4} 
          borderWidth="1px" 
          borderRadius="lg" 
          borderColor={borderColor}
          bg={bgColor}
        >
          <MemoryUserScoping agentId={agentId} userId="current-user" />
        </Box>
      )}
      
      <Box 
        flex="1" 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={bgColor}
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
          
          {isStreaming && (
            <Box 
              alignSelf="flex-start"
              maxW="80%" 
              p={3} 
              borderRadius="lg" 
              bg={useColorModeValue(`${agentDetails.color}.50`, `${agentDetails.color}.900`)}
            >
              <Text>{streamedText}<span className="cursor">|</span></Text>
            </Box>
          )}
          
          {isLoading && !isStreaming && (
            <Box 
              alignSelf="flex-start"
              maxW="80%" 
              p={3} 
              borderRadius="lg" 
              bg={useColorModeValue(`${agentDetails.color}.50`, `${agentDetails.color}.900`)}
            >
              <Text>Thinking...</Text>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      
      {showFileUpload && (
        <Box 
          p={4} 
          borderWidth="1px" 
          borderRadius="lg" 
          borderColor={borderColor}
          bg={bgColor}
        >
          <FileAttachmentHandler onFileUpload={handleFileUpload} />
        </Box>
      )}
      
      <Flex 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        borderColor={borderColor}
        bg={bgColor}
      >
        <IconButton
          icon={<FiPaperclip />}
          aria-label="Attach file"
          variant="ghost"
          mr={2}
          onClick={toggleFileUpload}
          colorScheme={showFileUpload ? agentDetails.color : 'gray'}
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
          isDisabled={!inputMessage.trim() || isLoading}
          leftIcon={<FiSend />}
        >
          Send
        </Button>
      </Flex>
    </VStack>
  );
};

export default AgentChatPanel;
