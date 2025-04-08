
// src/components/AgentChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Box, Flex, Input, Text, VStack, IconButton, Tooltip,
  useColorMode, useColorModeValue, Button, Heading,
  Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton,
  DrawerHeader, DrawerBody
} from '@chakra-ui/react';
import { AttachmentIcon } from '@chakra-ui/icons';
import TerminalDrawer from './TerminalDrawer';
import { useAgentDebug } from '../hooks/useAgentDebug';
import AgentFileUpload from './AgentFileUpload';
import { createMemory } from '../api/memorySchema';
import { useMemoryStore } from '../hooks/useMemoryStore';
import MemoryFeed from './MemoryFeed';
import { useAgentTraining } from '../hooks/useAgentTraining';
import { injectContext } from '../hooks/useMemoryRecall';
import { callOpenAI } from '../api/callOpenAI';

const AgentChat = () => {
  const { colorMode } = useColorMode();
  const bg = useColorModeValue('gray.50', 'gray.900');
  const feedBg = useColorModeValue('gray.100', 'gray.800');
  const msgBg = useColorModeValue('white', 'gray.700');
  const halMsgBg = useColorModeValue('blue.50', 'blue.900');

  // Removed unused fileInputRef
  const feedRef = useRef(null);

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  // Removed streaming state as it's no longer needed with direct OpenAI calls
  const [showDebug, setShowDebug] = useState(false);
  const [showMemoryConfirm, setShowMemoryConfirm] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [loading, setLoading] = useState(false);

  const { payload, memory, logs, logPayload, logMemory } = useAgentDebug();
  const { addMemory, getAllMemories, memories } = useMemoryStore();
  const { isTraining, isTrained } = useAgentTraining();

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight);
  }, [messages]);

  useEffect(() => {
    if (showMemoryConfirm) {
      const timer = setTimeout(() => {
        setShowMemoryConfirm(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [showMemoryConfirm]);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);

    const newMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, newMessage]);
    setInput('');

    try {
      // Create context-enhanced prompt
      const contextPrompt = injectContext(input, memories);
      
      // Log the payload for debugging
      const taskPayload = {
        task_name: 'HAL',
        task_goal: contextPrompt
      };
      logPayload(taskPayload);
      
      // Call OpenAI to get natural language response
      const response = await callOpenAI(contextPrompt);
      
      // Add the response to messages
      setMessages(prev => [...prev, { role: 'hal', content: response }]);
      
      // Create and add memory entry
      const memoryEntry = createMemory({
        content: input,
        type: 'task',
        agent: 'HAL',
        tags: ['hal', 'task']
      });
      addMemory(memoryEntry);
      
      // Show memory confirmation and log the response
      setShowMemoryConfirm(true);
      logMemory(response);
    } catch (error) {
      console.error('Error processing request:', error);
      setMessages(prev => [...prev, { 
        role: 'hal', 
        content: "I'm sorry, I encountered an error processing your request. Please try again." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = (file) => {
    if (file) {
      console.log('File uploaded:', file.name);
      setMessages(prev => [...prev, {
        role: 'system',
        content: `File uploaded: ${file.name} (${Math.round(file.size / 1024)} KB)`
      }]);
      setShowFileUpload(false);
    }
  };

  return (
    <Box bg={bg} h="calc(100vh - 80px)" display="flex" flexDirection="column">
      {isTraining && (
        <Box bg="yellow.600" color="white" p={2} textAlign="center">
          🚧 Training HAL... Injecting Core Values
        </Box>
      )}
      {!isTraining && isTrained && messages.length === 0 && (
        <Box bg="green.600" color="white" p={2} textAlign="center">
          ✅ Training Complete — HAL is aligned
        </Box>
      )}

      <Flex justify="space-between" align="center" p={4} borderBottom="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <Heading size="lg">HAL Interface</Heading>
        <Button colorScheme="red" size="sm" onClick={() => {
          localStorage.removeItem('isAuthenticated');
          window.location.href = '/auth';
        }}>Logout</Button>
      </Flex>

      <Flex p={4} align="center" borderBottom="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <Text fontWeight="bold" mr={4}>HAL GPT-4 Interface</Text>
        <Tooltip label="Toggle Debug Drawer">
          <IconButton
            ml={4}
            icon={<Text>{"</>"}</Text>}
            onClick={() => setShowDebug(!showDebug)}
            aria-label="Toggle Debug"
            variant="outline"
          />
        </Tooltip>
      </Flex>

      <Box flex="1" overflow="hidden" display="flex" flexDirection="column" p={4} position="relative">
        <Box ref={feedRef} flex="1" overflowY="auto" bg={feedBg} borderRadius="md" p={4} mb={4} boxShadow="sm">
          {messages.map((msg, i) => (
            <Box key={i} bg={msg.role === 'hal' ? halMsgBg : msgBg} color={colorMode === 'light' ? 'gray.800' : 'white'} p={4} mb={3} borderRadius="lg" boxShadow="sm">
              <Text fontWeight="bold" mb={1}>{msg.role.toUpperCase()}:</Text>
              <Text>{msg.content}</Text>
            </Box>
          ))}
          {showMemoryConfirm && (
            <Text mt={2} color="green.400" fontSize="sm">💾 Memory Logged</Text>
          )}
        </Box>

        {showFileUpload && (
          <Box position="absolute" bottom="70px" left="0" right="0" px={4}>
            <AgentFileUpload onFileUpload={handleUpload} />
          </Box>
        )}

        <Flex position="sticky" bottom="0" bg={bg} pt={2}>
          <Input
            placeholder="Enter your task..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            mr={2}
            bg={colorMode === 'light' ? 'white' : 'gray.700'}
            border="1px"
            borderColor={colorMode === 'light' ? 'gray.300' : 'gray.600'}
          />
          <IconButton icon={<AttachmentIcon />} onClick={() => setShowFileUpload(!showFileUpload)} mr={2} aria-label="Attach file" />
          <Button onClick={handleSubmit} colorScheme="blue" disabled={loading || isTraining}>
            {loading ? 'Thinking...' : isTraining ? 'Training...' : 'Send'}
          </Button>
        </Flex>
      </Box>

      <Drawer isOpen={showDebug} placement="right" onClose={() => setShowDebug(false)} size="md">
        <DrawerOverlay />
        <DrawerContent bg="black" color="green.400">
          <DrawerCloseButton color="white" />
          <DrawerHeader borderBottomWidth="1px" borderColor="green.700">🧠 Agent Debug View</DrawerHeader>
          <DrawerBody>
            <VStack spacing={6} align="stretch">
              <Box>
                <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>🔁 Task Payload</Text>
                <Box whiteSpace="pre-wrap" fontSize="xs" overflowX="auto" bg="black" p={2} border="1px" borderColor="green.700" borderRadius="md">
                  {JSON.stringify(payload, null, 2) || '// No task submitted yet'}
                </Box>
              </Box>
              <Box>
                <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>🧠 Memory Accessed</Text>
                <Box whiteSpace="pre-wrap" fontSize="xs" overflowX="auto" bg="black" p={2} border="1px" borderColor="green.700" borderRadius="md">
                  {memory || '// No memory log yet'}
                </Box>
              </Box>
              <Box>
                <Text fontSize="sm" fontWeight="bold" borderBottom="1px" borderColor="green.700" mb={1}>🧪 Reasoning & Logs</Text>
                <Box whiteSpace="pre-wrap" fontSize="xs" overflowX="auto" bg="black" p={2} border="1px" borderColor="green.700" borderRadius="md">
                  {logs || '// Agent has not returned internal reasoning yet'}
                </Box>
              </Box>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      <Box p={4} borderTop="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <MemoryFeed memories={getAllMemories()} />
      </Box>
    </Box>
  );
};

export default AgentChat;
