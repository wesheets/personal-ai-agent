import React, { useState } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Textarea, 
  Button, 
  FormControl,
  FormLabel,
  Input,
  useToast,
  Flex,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { memoryService } from '../services/api';

const MemoryUpload = () => {
  const [memoryContent, setMemoryContent] = useState('');
  const [memoryTitle, setMemoryTitle] = useState('');
  const [tags, setTags] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [file, setFile] = useState(null);
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleSubmit = async () => {
    if (!memoryContent.trim() && !file) {
      toast({
        title: 'Empty memory',
        description: 'Please enter memory content or upload a file',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const memoryData = {
        title: memoryTitle.trim() || 'Untitled Memory',
        content: memoryContent.trim(),
        tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        timestamp: new Date().toISOString()
      };

      // If there's a file, handle it differently
      if (file) {
        // In a real implementation, we would upload the file
        // For now, we'll just add the filename to the content
        memoryData.content += `\n\nAttached file: ${file.name}`;
      }

      await memoryService.createMemoryEntry(memoryData);
      
      toast({
        title: 'Memory created',
        description: 'Memory has been successfully stored',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Reset form
      setMemoryContent('');
      setMemoryTitle('');
      setTags('');
      setFile(null);
    } catch (error) {
      console.error('Error creating memory:', error);
      toast({
        title: 'Submission failed',
        description: 'Failed to store memory. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      p={4} 
      shadow="md" 
      bg={bgColor} 
      borderColor={borderColor}
    >
      <VStack spacing={4} align="stretch">
        <Text fontWeight="bold" fontSize="lg">Create Memory</Text>
        
        <FormControl>
          <FormLabel>Title (Optional)</FormLabel>
          <Input 
            value={memoryTitle}
            onChange={(e) => setMemoryTitle(e.target.value)}
            placeholder="Enter a title for this memory"
          />
        </FormControl>
        
        <FormControl isRequired>
          <FormLabel>Memory Content</FormLabel>
          <Textarea
            value={memoryContent}
            onChange={(e) => setMemoryContent(e.target.value)}
            placeholder="Enter memory content here..."
            size="md"
            rows={6}
            resize="vertical"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Tags (comma separated)</FormLabel>
          <Input 
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="tag1, tag2, tag3"
          />
        </FormControl>
        
        <Divider />
        
        <Text fontWeight="bold">Or Upload a File</Text>
        
        <FormControl>
          <FormLabel>File Upload</FormLabel>
          <Input
            type="file"
            onChange={handleFileChange}
            padding={1}
          />
          {file && (
            <Text mt={2} fontSize="sm">
              Selected file: {file.name} ({Math.round(file.size / 1024)} KB)
            </Text>
          )}
        </FormControl>
        
        <Flex justifyContent="flex-end">
          <Button
            colorScheme="purple"
            onClick={handleSubmit}
            isLoading={isSubmitting}
            loadingText="Submitting"
            isDisabled={(!memoryContent.trim() && !file) || isSubmitting}
          >
            Store Memory
          </Button>
        </Flex>
      </VStack>
    </Box>
  );
};

export default MemoryUpload;
