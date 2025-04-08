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
  Button
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
  const bg = useColorModeValue('gray.50', 'gray.800');
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
    <Box bg={bg} p={4} minH="100vh">
      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="2xl" fontWeight="bold">HAL Interface</Text>
        <Button colorScheme="red" onClick={() => {
          localStorage.removeItem('isAuthenticated');
          window.location.href = '/auth';
        }}>Logout</Button>
      </Flex>

      <Box mb={4}>
        <Flex align="center" mb={2}>
          <Text fontWeight="bold" mr={2}>Streaming</Text>
          <Input
            type="checkbox"
            isChecked={streaming}
            onChange={() => setStreaming(!streaming)}
            w="auto"
          />
          <Tooltip label="Toggle Debug Drawer">
            <IconButton
              ml={3}
              icon={<Text>{"</>"}</Text>}
              onClick={() => setShowDebug(!showDebug)}
              aria-label="Toggle Debug"
            />
          </Tooltip>
        </Flex>

        <Flex>
          <Input
            placeholder="Enter your task..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            mr={2}
          />
          <IconButton icon={<AttachmentIcon />} onClick={() => fileInputRef.current.click()} mr={2} />
          <Button onClick={handleSubmit}>Send</Button>
        </Flex>

        <input type="file" hidden ref={fileInputRef} onChange={handleUpload} />
      </Box>

      <Box ref={feedRef} maxH="400px" overflowY="auto" p={4} bg="gray.700" borderRadius="md">
        {messages.map((msg, i) => (
          <Box key={i} bg={msg.role === 'hal' ? 'blue.700' : 'gray.600'} color="white" p={3} mb={2} borderRadius="md">
            <strong>{msg.role.toUpperCase()}:</strong> {msg.content}
          </Box>
        ))}
        {showMemoryConfirm && (
          <Text mt={2} color="green.400" fontSize="sm">💾 Memory Logged</Text>
        )}
      </Box>

      <MemoryFeed memories={getAllMemories()} />

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
