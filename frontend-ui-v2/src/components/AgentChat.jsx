// src/components/AgentChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  Input,
  Text,
  VStack,
  IconButton,
  Tooltip,
  useColorMode,
  useColorModeValue,
  Button,
  Heading,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody
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

const AgentChat = ({ agentId = 'core-forge' }) => {
  const { colorMode } = useColorMode();
  const bg = useColorModeValue('gray.50', 'gray.900');
  const feedBg = useColorModeValue('gray.100', 'gray.800');
  const msgBg = useColorModeValue('white', 'gray.700');
  const agentMsgBg = useColorModeValue('blue.50', 'blue.900');
  
  // Get agent display name
  const getAgentDisplayName = () => {
    if (agentId === 'core-forge') return 'Core.Forge';
    if (agentId === 'hal') return 'HAL';
    return agentId.charAt(0).toUpperCase() + agentId.slice(1);
  };
  
  const agentName = getAgentDisplayName();
  const feedRef = useRef(null);
  const [input, setInput] = useState('');
  
  // Load & store conversationHistory from localStorage
  const [messages, setMessages] = useState(() => {
    const stored = localStorage.getItem(`chat_history_${agentId}`);
    return stored ? JSON.parse(stored) : [];
  });
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(`chat_history_${agentId}`, JSON.stringify(messages));
  }, [messages, agentId]);
  
  // Create a unique threadId for this conversation
  const threadId = useRef(Date.now().toString());
  
  const [showDebug, setShowDebug] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showMemoryConfirm, setShowMemoryConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const { logPayload, logs, memory, payload } = useAgentDebug();
  const { addMemory, getAllMemories, memories } = useMemoryStore();
  const { isTraining } = useAgentTraining();
  
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleUpload = (file) => {
    console.log('File uploaded:', file);
    setShowFileUpload(false);
    // Here you would typically process the file
  };
  
  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const newMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput('');
    try {
      // Create context-enhanced prompt
      const contextPrompt = injectContext(input, memories);
      // Log the payload for debugging
      const taskPayload = {
        task_name: agentName,
        task_goal: contextPrompt,
        agent_id: agentId
      };
      logPayload(taskPayload);
      
      // Call OpenAI to get natural language response with history and threadId
      const response = await callOpenAI(
        contextPrompt, 
        agentId, 
        messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        threadId.current
      );
      
      // Add the response to messages
      setMessages(prev => [...prev, { role: agentId, content: response }]);
      
      // Create and add memory entry
      const memoryEntry = createMemory({
        content: input,
        type: 'task',
        agent: agentName,
        tags: [agentId, 'task']
      });
      
      addMemory(memoryEntry);
      setShowMemoryConfirm(true);
      setTimeout(() => setShowMemoryConfirm(false), 2000);
    } catch (error) {
      console.error('Error in chat submission:', error);
      setMessages(prev => [...prev, { role: agentId, content: "I'm sorry, I encountered an error processing your request." }]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box h="100%" display="flex" flexDirection="column">
      <Flex
        p={4}
        bg={bg}
        borderBottom="1px"
        borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
        justify="space-between"
        align="center"
      >
        <Heading size="md">{agentName}</Heading>
        <Tooltip label="Debug View">
          <IconButton
            icon={<span>🛠️</span>}
            onClick={() => setShowDebug(!showDebug)}
            aria-label="Toggle Debug"
            variant="outline"
          />
        </Tooltip>
      </Flex>
      <Box
        flex="1"
        overflow="hidden"
        display="flex"
        flexDirection="column"
        p={4}
        position="relative"
      >
        <Box
          ref={feedRef}
          flex="1"
          overflowY="auto"
          bg={feedBg}
          borderRadius="md"
          p={4}
          mb={4}
          boxShadow="sm"
        >
          {messages.map((msg, i) => (
            <Box key={i} bg={msg.role === agentId ? agentMsgBg : msgBg} color={colorMode === 'light' ? 'gray.800' : 'white'} p={4} mb={3} borderRadius="lg" boxShadow="sm">
              <Text fontWeight="bold" mb={1}>{msg.role === agentId ? agentName : msg.role.toUpperCase()}:</Text>
              <Text>{msg.content}</Text>
            </Box>
          ))}
          {showMemoryConfirm && (
            <Text mt={2} color="green.400" fontSize="sm">
              💾 Memory Logged
            </Text>
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
          <IconButton
            icon={<AttachmentIcon />}
            onClick={() => setShowFileUpload(!showFileUpload)}
            mr={2}
            aria-label="Attach file"
          />
          <Button onClick={handleSubmit} colorScheme="blue" disabled={loading || isTraining}>
            {loading ? 'Thinking...' : isTraining ? 'Training...' : 'Send'}
          </Button>
        </Flex>
      </Box>
      <Drawer isOpen={showDebug} placement="right" onClose={() => setShowDebug(false)} size="md">
        <DrawerOverlay />
        <DrawerContent bg="black" color="green.400">
          <DrawerCloseButton color="white" />
          <DrawerHeader borderBottomWidth="1px" borderColor="green.700">
            🧠 Agent Debug View
          </DrawerHeader>
          <DrawerBody>
            <VStack spacing={6} align="stretch">
              <Box>
                <Text
                  fontSize="sm"
                  fontWeight="bold"
                  borderBottom="1px"
                  borderColor="green.700"
                  mb={1}
                >
                  🔁 Task Payload
                </Text>
                <Box
                  whiteSpace="pre-wrap"
                  fontSize="xs"
                  overflowX="auto"
                  bg="black"
                  p={2}
                  border="1px"
                  borderColor="green.700"
                  borderRadius="md"
                >
                  {JSON.stringify(payload, null, 2) || '// No task submitted yet'}
                </Box>
              </Box>
              <Box>
                <Text
                  fontSize="sm"
                  fontWeight="bold"
                  borderBottom="1px"
                  borderColor="green.700"
                  mb={1}
                >
                  🧠 Memory Accessed
                </Text>
                <Box
                  whiteSpace="pre-wrap"
                  fontSize="xs"
                  overflowX="auto"
                  bg="black"
                  p={2}
                  border="1px"
                  borderColor="green.700"
                  borderRadius="md"
                >
                  {memory || '// No memory log yet'}
                </Box>
              </Box>
              <Box>
                <Text
                  fontSize="sm"
                  fontWeight="bold"
                  borderBottom="1px"
                  borderColor="green.700"
                  mb={1}
                >
                  🧪 Reasoning & Logs
                </Text>
                <Box
                  whiteSpace="pre-wrap"
                  fontSize="xs"
                  overflowX="auto"
                  bg="black"
                  p={2}
                  border="1px"
                  borderColor="green.700"
                  borderRadius="md"
                >
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
