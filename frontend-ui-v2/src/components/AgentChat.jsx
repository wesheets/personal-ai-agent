import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  Input,
  Text,
  Textarea,
  VStack,
  IconButton,
  Tooltip,
  useColorMode,
  useColorModeValue,
  Button,
  Heading
} from '@chakra-ui/react';
import { AttachmentIcon, CloseIcon } from '@chakra-ui/icons';
import TerminalDrawer from './TerminalDrawer';
import { useAgentDebug } from '../hooks/useAgentDebug';
import AgentFileUpload from './AgentFileUpload';
import { createMemory } from '../api/memorySchema';
import { useMemoryStore } from '../hooks/useMemoryStore';
import MemoryFeed from './MemoryFeed';

const AgentChat = () => {
  const { colorMode } = useColorMode();
  const bg = useColorModeValue('gray.50', 'gray.900');
  const feedBg = useColorModeValue('gray.100', 'gray.800');
  const msgBg = useColorModeValue('white', 'gray.700');
  const halMsgBg = useColorModeValue('blue.50', 'blue.900');
  const fileInputRef = useRef(null);
  const feedRef = useRef(null);

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(true);
  const [showDebug, setShowDebug] = useState(false);
  const [showMemoryConfirm, setShowMemoryConfirm] = useState(false);

  const { payload, memory, logs, logPayload, logMemory, logThoughts, resetDebug } = useAgentDebug();
  const { memories, addMemory, getAllMemories } = useMemoryStore();

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight);
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const taskPayload = { task_name: 'HAL', task_goal: input, streaming };
    logPayload(taskPayload);

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const res = await fetch('/api/delegate-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskPayload)
    });

    if (!res.ok || !res.body) return;

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let agentMsg = '';
    setMessages(prev => [...prev, { role: 'hal', content: '' }]);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      agentMsg += decoder.decode(value);
      setMessages(prev => prev.map((m, i) => i === prev.length - 1 ? { ...m, content: agentMsg } : m));
    }

    const memoryEntry = createMemory({
      content: input,
      type: 'task',
      agent: 'HAL',
      tags: ['hal', 'task']
    });
    addMemory(memoryEntry);
    setShowMemoryConfirm(true);
    logMemory(agentMsg);
  };

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('File uploaded:', file.name);
    }
  };

  return (
    <Box bg={bg} h="calc(100vh - 80px)" display="flex" flexDirection="column">
      <Flex justify="space-between" align="center" p={4} borderBottom="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <Heading size="lg">HAL Interface</Heading>
        <Button colorScheme="red" size="sm" onClick={() => {
          localStorage.removeItem('isAuthenticated');
          window.location.href = '/auth';
        }}>Logout</Button>
      </Flex>

      <Flex p={4} align="center" borderBottom="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <Text fontWeight="bold" mr={4}>Streaming</Text>
        <Input
          type="checkbox"
          isChecked={streaming}
          onChange={() => setStreaming(!streaming)}
          w="auto"
        />
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

      <Box flex="1" overflow="hidden" display="flex" flexDirection="column" p={4}>
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
            <Box 
              key={i} 
              bg={msg.role === 'hal' ? halMsgBg : msgBg} 
              color={colorMode === 'light' ? 'gray.800' : 'white'} 
              p={4} 
              mb={3} 
              borderRadius="lg"
              boxShadow="sm"
            >
              <Text fontWeight="bold" mb={1}>{msg.role.toUpperCase()}:</Text> 
              <Text>{msg.content}</Text>
            </Box>
          ))}
          {showMemoryConfirm && (
            <Text mt={2} color="green.400" fontSize="sm">💾 Memory Logged</Text>
          )}
        </Box>

        <Flex>
          <Input
            placeholder="Enter your task..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            mr={2}
            bg={colorMode === 'light' ? 'white' : 'gray.700'}
            border="1px"
            borderColor={colorMode === 'light' ? 'gray.300' : 'gray.600'}
            _focus={{
              borderColor: 'blue.500',
              boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)'
            }}
          />
          <IconButton 
            icon={<AttachmentIcon />} 
            onClick={() => fileInputRef.current.click()} 
            mr={2}
            aria-label="Attach file"
          />
          <Button 
            onClick={handleSubmit}
            colorScheme="blue"
          >
            Send
          </Button>
        </Flex>

        <input type="file" hidden ref={fileInputRef} onChange={handleUpload} />
      </Box>

      <Box p={4} borderTop="1px" borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}>
        <Text fontWeight="bold" mb={2}>Memory Feed</Text>
        <MemoryFeed memories={getAllMemories()} />
      </Box>

      {showDebug && (
        <TerminalDrawer
          open={showDebug}
          onClose={() => setShowDebug(false)}
          payload={payload}
          memory={memory}
          logs={logs}
        />
      )}
    </Box>
  );
};

export default AgentChat;
