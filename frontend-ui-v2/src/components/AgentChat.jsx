import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  Flex,
  Input,
  Text,
  VStack,
  HStack,
  Textarea,
  IconButton,
  useDisclosure,
  useColorModeValue,
  Divider,
  Badge,
  useToast
} from '@chakra-ui/react';
import { AttachmentIcon, CodeIcon } from '@chakra-ui/icons';
import TerminalDrawer from './TerminalDrawer';
import { useAgentDebug } from '../hooks/useAgentDebug';
import ApiService from '../api/ApiService';

const AgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState('');
  const [fileUpload, setFileUpload] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const toast = useToast();
  
  // Debug drawer state
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { payload, memory, logs, logPayload, logMemory, logThoughts, resetDebug } = useAgentDebug();

  // Define color mode values outside of render conditions
  const userBgColor = useColorModeValue('blue.500', 'blue.600');
  const assistantBgColor = useColorModeValue('gray.200', 'gray.700');
  const systemBgColor = useColorModeValue('green.500', 'green.600');
  const errorBgColor = useColorModeValue('red.500', 'red.600');
  const textColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.900');
  const chatBgColor = useColorModeValue('gray.50', 'gray.800');

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamedResponse]);

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFileUpload(file);
      toast({
        title: 'File selected',
        description: `${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Handle file drop
  const handleFileDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      setFileUpload(file);
      toast({
        title: 'File dropped',
        description: `${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Handle paste (for images)
  const handlePaste = (event) => {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    
    for (const item of items) {
      if (item.kind === 'file') {
        const file = item.getAsFile();
        setFileUpload(file);
        toast({
          title: 'Image pasted',
          description: `${file.name || 'Pasted image'} (${(file.size / 1024).toFixed(2)} KB)`,
          status: 'info',
          duration: 3000,
          isClosable: true,
        });
        break;
      }
    }
  };

  // Handle message submission
  const handleSubmit = async () => {
    if (!input.trim() && !fileUpload) return;
    
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      file: fileUpload ? {
        name: fileUpload.name,
        size: fileUpload.size,
        type: fileUpload.type
      } : null
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamedResponse('');
    
    // Reset debug info for new conversation
    resetDebug();
    
    try {
      // Log the payload for debugging
      logPayload({
        message: input,
        file: fileUpload ? {
          name: fileUpload.name,
          size: fileUpload.size,
          type: fileUpload.type
        } : null
      });
      
      // Upload file if present
      let fileUrl = null;
      if (fileUpload) {
        try {
          const uploadResult = await ApiService.uploadFile(fileUpload);
          fileUrl = uploadResult?.url || null;
          logMemory(`File uploaded: ${fileUpload.name} (${fileUrl})`);
        } catch (error) {
          console.error('File upload error:', error);
          toast({
            title: 'File upload failed',
            description: error.message || 'Could not upload file',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        }
      }
      
      // Stream the response
      await ApiService.delegateTaskStreaming(
        'hal9000',
        'chat',
        input,
        (data) => {
          // Handle streaming progress
          if (data.content) {
            setStreamedResponse(prev => prev + data.content);
            
            // Log agent thoughts if available
            if (data.thoughts) {
              logThoughts(data.thoughts);
            }
          }
        },
        (data) => {
          // Handle completion
          setIsLoading(false);
          
          // Add agent response to chat
          setMessages(prev => [
            ...prev, 
            { 
              role: 'assistant', 
              content: data.content || streamedResponse,
              memoryLogged: true
            }
          ]);
          
          // Clear streamed response
          setStreamedResponse('');
          
          // Add memory logged message
          setTimeout(() => {
            setMessages(prev => [
              ...prev,
              {
                role: 'system',
                content: '💾 Memory Logged',
                isMemoryLog: true
              }
            ]);
            
            // Log memory access
            logMemory('Chat history saved to memory');
          }, 500);
        },
        (error) => {
          // Handle error
          setIsLoading(false);
          console.error('Streaming error:', error);
          
          setMessages(prev => [
            ...prev,
            {
              role: 'system',
              content: `Error: ${error.message || 'Something went wrong'}`,
              isError: true
            }
          ]);
        }
      );
    } catch (error) {
      console.error('Chat error:', error);
      setIsLoading(false);
      
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: `Error: ${error.message || 'Something went wrong'}`,
          isError: true
        }
      ]);
    }
    
    // Clear file upload
    setFileUpload(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle key press (Enter to submit)
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box 
      h="100vh" 
      display="flex" 
      flexDirection="column"
      onDrop={handleFileDrop}
      onDragOver={(e) => e.preventDefault()}
      onPaste={handlePaste}
    >
      {/* Chat messages area */}
      <Box 
        flex="1" 
        p={4} 
        overflowY="auto" 
        bg={chatBgColor}
      >
        <VStack spacing={4} align="stretch">
          {messages.map((msg, index) => (
            <Flex 
              key={index} 
              justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
            >
              <Box 
                maxW="70%" 
                p={3} 
                borderRadius="lg" 
                bg={
                  msg.role === 'user' 
                    ? userBgColor 
                    : msg.role === 'assistant' 
                      ? assistantBgColor 
                      : msg.isError 
                        ? errorBgColor 
                        : systemBgColor
                }
                color={msg.role === 'assistant' ? textColor : 'white'}
                boxShadow="md"
              >
                {msg.role === 'user' && msg.file && (
                  <HStack mb={2}>
                    <AttachmentIcon />
                    <Text fontSize="sm" fontStyle="italic">
                      {msg.file.name} ({(msg.file.size / 1024).toFixed(2)} KB)
                    </Text>
                  </HStack>
                )}
                
                <Text whiteSpace="pre-wrap">{msg.content}</Text>
                
                {msg.memoryLogged && (
                  <Badge colorScheme="green" mt={2} size="sm">
                    Memory Indexed
                  </Badge>
                )}
              </Box>
            </Flex>
          ))}
          
          {/* Streaming response */}
          {streamedResponse && (
            <Flex justify="flex-start">
              <Box 
                maxW="70%" 
                p={3} 
                borderRadius="lg" 
                bg={assistantBgColor}
                color={textColor}
                boxShadow="md"
              >
                <Text whiteSpace="pre-wrap">{streamedResponse}</Text>
              </Box>
            </Flex>
          )}
          
          {/* Loading indicator */}
          {isLoading && !streamedResponse && (
            <Flex justify="flex-start">
              <Box 
                maxW="70%" 
                p={3} 
                borderRadius="lg" 
                bg={assistantBgColor}
                color={textColor}
                boxShadow="md"
              >
                <Text>Thinking...</Text>
              </Box>
            </Flex>
          )}
          
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      
      {/* Input area */}
      <Box 
        p={4} 
        borderTop="1px" 
        borderColor={borderColor}
        bg={bgColor}
      >
        <HStack spacing={2} align="flex-end">
          {/* Debug drawer toggle */}
          <IconButton
            icon={<CodeIcon />}
            aria-label="Toggle debug drawer"
            onClick={isOpen ? onClose : onOpen}
            colorScheme={isOpen ? 'blue' : 'gray'}
            size="md"
          />
          
          {/* File upload button */}
          <IconButton
            icon={<AttachmentIcon />}
            aria-label="Upload file"
            onClick={() => fileInputRef.current?.click()}
            colorScheme={fileUpload ? 'green' : 'gray'}
            size="md"
          />
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
          
          {/* Text input */}
          <Textarea
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            resize="none"
            rows={1}
            minH="40px"
            maxH="200px"
            flex="1"
          />
          
          {/* Send button */}
          <Button
            colorScheme="blue"
            onClick={handleSubmit}
            isLoading={isLoading}
            loadingText="Sending"
          >
            Send
          </Button>
        </HStack>
        
        {/* File upload preview */}
        {fileUpload && (
          <HStack mt={2} p={2} borderRadius="md" bg="gray.100" color="gray.800">
            <AttachmentIcon />
            <Text fontSize="sm">
              {fileUpload.name} ({(fileUpload.size / 1024).toFixed(2)} KB)
            </Text>
            <Button
              size="xs"
              colorScheme="red"
              variant="ghost"
              onClick={() => {
                setFileUpload(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}
            >
              Remove
            </Button>
          </HStack>
        )}
      </Box>
      
      {/* Debug drawer */}
      <TerminalDrawer
        open={isOpen}
        onClose={onClose}
        payload={payload}
        memory={memory}
        logs={logs}
      />
    </Box>
  );
};

export default AgentChat;
