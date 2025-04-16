import React, { useState, useEffect } from 'react';
import { Box, Flex, VStack, Text, useColorModeValue, useToast } from '@chakra-ui/react';
import FileAttachmentHandler from './FileAttachmentHandler';

/**
 * MemoryUserScoping component
 * Handles memory logs scoped by user_id and agent_id
 */
const MemoryUserScoping = ({ agentId, userId }) => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');

  // Load memories when component mounts or when agentId/userId changes
  useEffect(() => {
    if (agentId) {
      loadMemories();
    }
  }, [agentId, userId]);

  const loadMemories = async () => {
    setLoading(true);

    try {
      // In a real implementation, this would fetch memories from the API
      // const response = await fetch(`/api/memory/agent-${agentId}?user_id=${userId}`);
      // if (!response.ok) {
      //   throw new Error('Failed to load memories');
      // }
      // const data = await response.json();
      // setMemories(data.memories);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock memories data
      const mockMemories = [
        {
          id: 1,
          content: 'User asked about quantum computing principles',
          timestamp: new Date(Date.now() - 2 * 60 * 60000),
          type: 'conversation'
        },
        {
          id: 2,
          content: 'User uploaded research paper on neural networks',
          timestamp: new Date(Date.now() - 1 * 24 * 60 * 60000),
          type: 'file'
        },
        {
          id: 3,
          content: 'Discussion about machine learning algorithms',
          timestamp: new Date(Date.now() - 3 * 24 * 60 * 60000),
          type: 'conversation'
        }
      ];

      setMemories(mockMemories);
    } catch (error) {
      console.error('Error loading memories:', error);
      toast({
        title: 'Failed to load memories',
        description: error.message,
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files) => {
    try {
      // In a real implementation, this would upload files and add them to memory
      // const formData = new FormData();
      // files.forEach(file => {
      //   formData.append('files', file);
      // });
      // formData.append('agent_id', agentId);
      // formData.append('user_id', userId);

      // const response = await fetch('/api/memory/upload', {
      //   method: 'POST',
      //   body: formData
      // });

      // if (!response.ok) {
      //   throw new Error('Failed to upload files to memory');
      // }

      // Simulate successful upload
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Add new memory entries for uploaded files
      const newMemories = files.map((file, index) => ({
        id: Date.now() + index,
        content: `File uploaded: ${file.name}`,
        timestamp: new Date(),
        type: 'file'
      }));

      setMemories((prev) => [...newMemories, ...prev]);

      toast({
        title: 'Files added to memory',
        description: `${files.length} file(s) successfully added to agent memory`,
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (error) {
      console.error('Error uploading files to memory:', error);
      toast({
        title: 'Failed to add files to memory',
        description: error.message,
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Box>
      <Box mb={6}>
        <Text fontWeight="bold" mb={2}>
          Add to Agent Memory
        </Text>
        <FileAttachmentHandler onFileUpload={handleFileUpload} />
      </Box>

      <Box>
        <Text fontWeight="bold" mb={2}>
          Memory Logs
        </Text>
        {loading ? (
          <Text>Loading memories...</Text>
        ) : memories.length === 0 ? (
          <Text>No memories found for this agent</Text>
        ) : (
          <VStack spacing={3} align="stretch">
            {memories.map((memory) => (
              <Box
                key={memory.id}
                p={3}
                borderWidth="1px"
                borderRadius="md"
                borderColor={borderColor}
                bg={bgColor}
              >
                <Flex justify="space-between" mb={1}>
                  <Text fontWeight="bold">
                    {memory.type === 'file' ? '📎 File Upload' : '💬 Conversation'}
                  </Text>
                  <Text fontSize="sm" color="gray.500">
                    {formatTimestamp(memory.timestamp)}
                  </Text>
                </Flex>
                <Text>{memory.content}</Text>
              </Box>
            ))}
          </VStack>
        )}
      </Box>
    </Box>
  );
};

export default MemoryUserScoping;
