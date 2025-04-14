// src/components/AgentChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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

const AgentChat = () => {
  const { agentId } = useParams();
  const finalAgentId = agentId || "core-forge";
  
  // Agent names mapping
  const agentNames = {
    "core-forge": "Core.Forge",
    "hal": "HAL",
    "ash-xenomorph": "Ash",
    "ops-agent": "Ops Agent",
  };
  
  // Get agent display name
  const getAgentDisplayName = () => {
    return agentNames[finalAgentId] || finalAgentId.charAt(0).toUpperCase() + finalAgentId.slice(1);
  };
  
  const agentName = getAgentDisplayName();
  
  const { colorMode } = useColorMode();
  const bg = useColorModeValue('gray.50', 'gray.900');
  const feedBg = useColorModeValue('gray.100', 'gray.800');
  const msgBg = useColorModeValue('white', 'gray.700');
  const agentMsgBg = useColorModeValue('blue.50', 'blue.900');
  
  const [messages, setMessages] = useState(() => {
    const stored = localStorage.getItem(`chat_history_${finalAgentId}`);
    return stored ? JSON.parse(stored) : [];
  });
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(`chat_history_${finalAgentId}`, JSON.stringify(messages));
  }, [messages, finalAgentId]);
  
  // Create a unique threadId for this conversation
  const threadId = useRef(Date.now().toString());
  
  const [showDebug, setShowDebug] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showMemoryConfirm, setShowMemoryConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const { logPayload, logs, memory, payload } = useAgentDebug();
  const { addMemory, getAllMemories, memories } = useMemoryStore();
  const { isTraining } = useAgentTraining();
  
  const [input, setInput] = useState('');
  const feedRef = useRef();
  
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
  
  const handleMemorize = () => {
    if (messages.length > 0) {
      const lastUserMessage = messages.filter(m => m.role === 'user').pop();
      const lastAgentMessage = messages.filter(m => m.role === finalAgentId).pop();
      
      if (lastUserMessage && lastAgentMessage) {
        const memory = createMemory(
          lastUserMessage.content,
          lastAgentMessage.content,
          finalAgentId
        );
        addMemory(memory);
        setShowMemoryConfirm(true);
        setTimeout(() => setShowMemoryConfirm(false), 2000);
      }
    }
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
        agent_id: finalAgentId
      };
      logPayload(taskPayload);
      
      // Call API with proper parameters
      const response = await fetch('/api/delegate-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: finalAgentId,
          prompt: input,
          history: messages.map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          threadId: threadId.current
        })
      });
      
      if (!response.ok) {
        throw new Error(`API call failed with status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let responseText = '';
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        responseText += chunk;
        
        // Update the UI with the streaming response
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          
          if (lastMessage && lastMessage.role === finalAgentId) {
            lastMessage.content = responseText;
            return [...newMessages];
          } else {
            return [...newMessages, { role: finalAgentId, content: responseText }];
          }
        });
      }
      
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: finalAgentId, content: `Error: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box height="100vh" display="flex" flexDirection="column">
      <Flex
        bg={colorMode === 'light' ? 'blue.600' : 'blue.900'}
        color="white"
        p={4}
        justifyContent="space-between"
        alignItems="center"
      >
        <Heading size="md">{agentName}</Heading>
        <Tooltip label="Debug View" placement="bottom">
          <IconButton
            icon={<span>🧠</span>}
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
            <Box key={i} bg={msg.role === finalAgentId ? agentMsgBg : msgBg} color={colorMode === 'light' ? 'gray.800' : 'white'} p={4} mb={3} borderRadius="lg" boxShadow="sm">
              <Text fontWeight="bold" mb={1}>{msg.role === finalAgentId ? agentName : msg.role.toUpperCase()}:</Text>
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
