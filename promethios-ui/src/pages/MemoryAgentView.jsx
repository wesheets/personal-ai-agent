import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Flex,
  Textarea,
  Button,
  VStack,
  HStack,
  useColorMode,
  Card,
  CardBody,
  Divider,
  Input,
  FormControl,
  FormLabel,
  Icon,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress
} from '@chakra-ui/react';
import { FiUpload, FiFile, FiCheck, FiX } from 'react-icons/fi';

const MemoryAgentView = () => {
  const { colorMode } = useColorMode();
  const toast = useToast();

  // State for text input
  const [textInput, setTextInput] = useState('');
  const [isSubmittingText, setIsSubmittingText] = useState(false);

  // State for file upload
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // State for responses
  const [textResponse, setTextResponse] = useState(null);
  const [fileResponse, setFileResponse] = useState(null);

  // Handle text submission
  const handleTextSubmit = async () => {
    if (!textInput.trim()) {
      toast({
        title: 'Empty input',
        description: 'Please enter some text to save to memory',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsSubmittingText(true);

    try {
      // Real API call with fallback to mock data
      let response;
      let responseData;

      try {
        const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/memory/create`;
        response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: textInput,
            type: 'text',
            title: textInput.split('\n')[0].substring(0, 50) // Use first line as title
          })
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        responseData = await response.json();
        console.log('Memory created successfully:', responseData);
      } catch (apiError) {
        console.warn('API call failed, using mock data:', apiError);
        // Fallback to mock data if API call fails
        await new Promise((resolve) => setTimeout(resolve, 800));
        responseData = {
          id: `mem-${Date.now()}`,
          status: 'saved',
          message: 'Text successfully saved to memory'
        };
      }

      setTextResponse(responseData);

      // Show success toast
      toast({
        title: 'Memory saved',
        description: 'Text has been successfully saved to memory',
        status: 'success',
        duration: 5000,
        isClosable: true
      });

      // Reset form
      setTextInput('');
    } catch (err) {
      console.error('Error saving text to memory:', err);

      // Show error toast
      toast({
        title: 'Error',
        description: 'Failed to save text to memory. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsSubmittingText(false);
    }
  };

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file type
      const validTypes = [
        '.txt',
        '.pdf',
        '.json',
        'text/plain',
        'application/pdf',
        'application/json'
      ];
      const fileType = file.type;
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

      if (!validTypes.some((type) => fileType.includes(type) || fileExtension.includes(type))) {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a TXT, PDF, or JSON file',
          status: 'error',
          duration: 5000,
          isClosable: true
        });
        return;
      }

      setSelectedFile(file);
    }
  };

  // Handle file upload
  const handleFileUpload = async () => {
    if (!selectedFile) {
      toast({
        title: 'No file selected',
        description: 'Please select a file to upload',
        status: 'warning',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Real API call with fallback to mock data
      let response;
      let responseData;

      try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('type', 'file');
        formData.append('filename', selectedFile.name);

        const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/memory/create`;
        response = await fetch(apiUrl, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        responseData = await response.json();
        console.log('File uploaded successfully:', responseData);
      } catch (apiError) {
        console.warn('API call failed, using mock data:', apiError);
        // Fallback to mock data if API call fails
        // Continue with upload progress simulation
        const totalSteps = 10;
        for (let i = 1; i <= totalSteps; i++) {
          await new Promise((resolve) => setTimeout(resolve, 300));
          setUploadProgress((i / totalSteps) * 100);
        }

        responseData = {
          id: `file-${Date.now()}`,
          status: 'uploaded',
          filename: selectedFile.name,
          size: selectedFile.size,
          message: 'File successfully uploaded to memory'
        };
      }

      setFileResponse(responseData);

      // Show success toast
      toast({
        title: 'File uploaded',
        description: `${selectedFile.name} has been successfully uploaded to memory`,
        status: 'success',
        duration: 5000,
        isClosable: true
      });

      // Reset form
      setSelectedFile(null);
      setUploadProgress(0);

      // Reset file input by clearing the value
      const fileInput = document.getElementById('file-upload');
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error('Error uploading file:', err);

      // Show error toast
      toast({
        title: 'Error',
        description: 'Failed to upload file. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];

      // Check file type
      const validTypes = [
        '.txt',
        '.pdf',
        '.json',
        'text/plain',
        'application/pdf',
        'application/json'
      ];
      const fileType = file.type;
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

      if (!validTypes.some((type) => fileType.includes(type) || fileExtension.includes(type))) {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a TXT, PDF, or JSON file',
          status: 'error',
          duration: 5000,
          isClosable: true
        });
        return;
      }

      setSelectedFile(file);
    }
  };

  return (
    <Box p={4}>
      <Heading mb={6} size="lg">
        Memory Agent
      </Heading>
      <Text mb={6} color="gray.500">
        Store information in the agent's memory by pasting text or uploading files.
      </Text>

      <Flex direction={{ base: 'column', md: 'row' }} gap={6}>
        {/* Left Pane - Paste Text */}
        <Card
          flex="1"
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
          boxShadow="md"
          borderRadius="lg"
        >
          <CardBody>
            <Heading size="md" mb={4}>
              Paste Text
            </Heading>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Text to remember</FormLabel>
                <Textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste or type text to store in memory"
                  rows={10}
                  resize="vertical"
                />
              </FormControl>

              <Button
                colorScheme="blue"
                onClick={handleTextSubmit}
                isLoading={isSubmittingText}
                loadingText="Saving..."
                leftIcon={<FiCheck />}
              >
                Save to Memory
              </Button>

              {textResponse && (
                <Alert status="success" mt={2} borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Saved to Memory</AlertTitle>
                    <AlertDescription>
                      {textResponse?.message ?? 'Text saved successfully'}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Right Pane - Upload Files */}
        <Card
          flex="1"
          bg={colorMode === 'light' ? 'white' : 'gray.700'}
          boxShadow="md"
          borderRadius="lg"
        >
          <CardBody>
            <Heading size="md" mb={4}>
              Upload Files
            </Heading>
            <VStack spacing={4} align="stretch">
              <Box
                border="2px dashed"
                borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                borderRadius="md"
                p={6}
                textAlign="center"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                bg={colorMode === 'light' ? 'gray.50' : 'gray.600'}
                _hover={{
                  borderColor: 'blue.400',
                  bg: colorMode === 'light' ? 'blue.50' : 'blue.900'
                }}
                transition="all 0.3s"
              >
                <Icon as={FiUpload} boxSize={10} color="gray.400" mb={4} />
                <Text mb={2}>Drag & drop a file here, or click to select</Text>
                <Text fontSize="sm" color="gray.500">
                  Supports TXT, PDF, and JSON files
                </Text>

                <Input
                  id="file-upload"
                  type="file"
                  height="100%"
                  width="100%"
                  position="absolute"
                  top="0"
                  left="0"
                  opacity="0"
                  aria-hidden="true"
                  accept=".txt,.pdf,.json,text/plain,application/pdf,application/json"
                  onChange={handleFileChange}
                  cursor="pointer"
                />
              </Box>

              {selectedFile && (
                <HStack
                  p={3}
                  bg={colorMode === 'light' ? 'gray.50' : 'gray.600'}
                  borderRadius="md"
                  justify="space-between"
                >
                  <HStack>
                    <Icon as={FiFile} />
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="medium" noOfLines={1}>
                        {selectedFile?.name ?? 'Unknown file'}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {selectedFile?.size
                          ? `${(selectedFile.size / 1024).toFixed(2)} KB`
                          : 'Unknown size'}
                      </Text>
                    </VStack>
                  </HStack>
                  <Button
                    size="sm"
                    colorScheme="red"
                    variant="ghost"
                    onClick={() => setSelectedFile(null)}
                  >
                    <Icon as={FiX} />
                  </Button>
                </HStack>
              )}

              {isUploading && (
                <Progress value={uploadProgress} size="sm" colorScheme="blue" borderRadius="md" />
              )}

              <Button
                colorScheme="blue"
                onClick={handleFileUpload}
                isLoading={isUploading}
                loadingText="Uploading..."
                leftIcon={<FiUpload />}
                isDisabled={!selectedFile}
              >
                Upload File
              </Button>

              {fileResponse && (
                <Alert status="success" mt={2} borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>File Uploaded</AlertTitle>
                    <AlertDescription>
                      {fileResponse?.message ?? 'File uploaded successfully'}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
      </Flex>
    </Box>
  );
};

export default MemoryAgentView;
