import { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Divider,
  useColorModeValue,
  Avatar,
  IconButton,
  Select,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { ArrowUpIcon } from '@chakra-ui/icons';

// Mock API functions for testing
const mockSendAgentRequest = async (agentType: string) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  return {
    output: `This is a simulated response from the ${agentType} agent. In the actual implementation, this would come from the backend API.`,
    metadata: {
      processingTime: '1.2s',
      tokens: 150
    }
  };
};

// Message type definition
interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  metadata?: Record<string, any>;
}

const AgentChat: React.FC<{
  agentType: string;
  agentTitle: string;
  agentDescription: string;
}> = ({ agentType, agentTitle, agentDescription }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [availableModels] = useState<string[]>(['gpt-4', 'claude-3', 'mistral']);
  
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    
    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Send request to the agent API (mock for now)
      const response = await mockSendAgentRequest(agentType);
      
      // Create agent message from response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.output,
        sender: 'agent',
        timestamp: new Date(),
        metadata: {
          model: selectedModel,
          agentType,
          // Spread response metadata without overwriting model
          processingTime: response.metadata.processingTime,
          tokens: response.metadata.tokens
        }
      };
      
      // Add agent message to chat
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message to agent:', error);
      toast({
        title: 'Error',
        description: 'Failed to get response from agent. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'agent',
        timestamp: new Date(),
        metadata: {
          isError: true
        }
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <Heading as="h1" size="xl" mb={2}>
        {agentTitle}
      </Heading>
      <Text fontSize="md" color="gray.600" _dark={{ color: 'gray.400' }} mb={6}>
        {agentDescription}
      </Text>
      
      <Flex mb={4}>
        <Select 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          maxW="200px"
          mr={2}
        >
          {availableModels.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </Select>
      </Flex>
      
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        bg={bgColor}
        borderColor={borderColor}
        height="600px"
        display="flex"
        flexDirection="column"
      >
        <Box
          p={4}
          overflowY="auto"
          flex="1"
        >
          {messages.length === 0 ? (
            <Flex 
              height="100%" 
              alignItems="center" 
              justifyContent="center" 
              flexDirection="column"
              color="gray.500"
              textAlign="center"
              p={8}
            >
              <Text fontSize="lg" fontWeight="medium" mb={2}>
                No messages yet
              </Text>
              <Text>
                Start a conversation with the {agentTitle} by typing a message below.
              </Text>
            </Flex>
          ) : (
            <VStack spacing={4} align="stretch">
              {messages.map((message) => (
                <Box
                  key={message.id}
                  alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                  maxW="80%"
                  p={4}
                  borderRadius="lg"
                  bg={message.sender === 'user' ? 'brand.500' : 'gray.100'}
                  color={message.sender === 'user' ? 'white' : 'gray.800'}
                  _dark={{
                    bg: message.sender === 'user' ? 'brand.600' : 'gray.700',
                    color: message.sender === 'user' ? 'white' : 'gray.100'
                  }}
                >
                  <HStack spacing={3} mb={1}>
                    {message.sender === 'agent' && (
                      <Avatar size="xs" name={agentTitle} bg="brand.500" />
                    )}
                    <Text fontWeight="bold">
                      {message.sender === 'user' ? 'You' : agentTitle}
                    </Text>
                  </HStack>
                  <Text whiteSpace="pre-wrap">{message.content}</Text>
                  <Text fontSize="xs" textAlign="right" mt={1} opacity={0.8}>
                    {message.timestamp.toLocaleTimeString()}
                  </Text>
                </Box>
              ))}
              {isLoading && (
                <Box alignSelf="flex-start" p={4}>
                  <Spinner size="sm" color="brand.500" />
                </Box>
              )}
            </VStack>
          )}
        </Box>
        
        <Divider />
        
        <Box p={4}>
          <HStack>
            <Input
              placeholder={`Ask the ${agentTitle} something...`}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
            />
            <IconButton
              colorScheme="brand"
              aria-label="Send message"
              icon={<ArrowUpIcon />}
              onClick={handleSendMessage}
              isLoading={isLoading}
            />
          </HStack>
        </Box>
      </Box>
    </Box>
  );
};

export default AgentChat;
