import React, { useState, useRef } from 'react';
import { Box, Flex, VStack, Text, useColorModeValue, Input, Button, Icon, useToast } from '@chakra-ui/react';
import { FiUpload, FiFile, FiX } from 'react-icons/fi';

/**
 * FileAttachmentHandler component
 * Handles file uploads with drag & drop functionality
 */
const FileAttachmentHandler = ({ onFileUpload }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const toast = useToast();
  
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const dragBgColor = useColorModeValue('blue.50', 'blue.900');
  
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) {
      setIsDragging(true);
    }
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };
  
  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };
  
  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList);
    setFiles([...files, ...newFiles]);
  };
  
  const removeFile = (index) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  };
  
  const uploadFiles = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    
    try {
      // In a real implementation, this would use FormData to upload files to the server
      // const formData = new FormData();
      // files.forEach(file => {
      //   formData.append('files', file);
      // });
      
      // const response = await fetch('/api/files/upload', {
      //   method: 'POST',
      //   body: formData
      // });
      
      // if (!response.ok) {
      //   throw new Error('Failed to upload files');
      // }
      
      // const data = await response.json();
      
      // Simulate successful upload
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Call the onFileUpload callback with the uploaded files
      if (onFileUpload) {
        onFileUpload(files);
      }
      
      toast({
        title: 'Files uploaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Clear the files list
      setFiles([]);
    } catch (error) {
      console.error('Error uploading files:', error);
      toast({
        title: 'Failed to upload files',
        description: error.message,
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  return (
    <Box>
      <Box
        border="2px dashed"
        borderColor={isDragging ? 'blue.400' : borderColor}
        borderRadius="md"
        p={4}
        bg={isDragging ? dragBgColor : bgColor}
        transition="all 0.2s"
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={openFileDialog}
        cursor="pointer"
        textAlign="center"
      >
        <Input
          type="file"
          multiple
          ref={fileInputRef}
          onChange={handleFileInput}
          display="none"
        />
        <Icon as={FiUpload} boxSize={6} mb={2} />
        <Text>
          {isDragging ? 'Drop files here' : 'Drag and drop files here, or click to select'}
        </Text>
      </Box>
      
      {files.length > 0 && (
        <VStack mt={4} spacing={2} align="stretch">
          {files.map((file, index) => (
            <Flex
              key={index}
              p={2}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={bgColor}
              align="center"
            >
              <Icon as={FiFile} mr={2} />
              <Text flex="1" fontSize="sm" isTruncated>
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </Text>
              <Icon
                as={FiX}
                cursor="pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(index);
                }}
              />
            </Flex>
          ))}
          
          <Button
            mt={2}
            colorScheme="blue"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              uploadFiles();
            }}
            isLoading={isUploading}
            loadingText="Uploading"
          >
            Upload {files.length} file{files.length !== 1 ? 's' : ''}
          </Button>
        </VStack>
      )}
    </Box>
  );
};

export default FileAttachmentHandler;
