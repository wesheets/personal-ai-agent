import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  HStack,
  useColorModeValue,
  Button,
  Icon,
  Input,
  Progress,
  IconButton,
  useToast,
  Tooltip
} from '@chakra-ui/react';
import { 
  FiUpload, 
  FiFile, 
  FiImage, 
  FiFileText, 
  FiX, 
  FiPaperclip,
  FiCheck,
  FiAlertCircle
} from 'react-icons/fi';
import { useDropzone } from 'react-dropzone';

const FileAttachmentHandler = ({ 
  onFileUpload, 
  onFileRemove,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedFileTypes = {
    'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
  }
}) => {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadStatus, setUploadStatus] = useState({});
  const fileInputRef = useRef(null);
  const toast = useToast();
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  
  // Handle file drop
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(file => {
        const errorMessage = file.errors[0]?.message || 'File not accepted';
        toast({
          title: 'File rejected',
          description: `${file.file.name}: ${errorMessage}`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      });
    }
    
    // Handle accepted files
    if (acceptedFiles.length > 0) {
      // Check if adding these files would exceed the max files limit
      if (files.length + acceptedFiles.length > maxFiles) {
        toast({
          title: 'Too many files',
          description: `You can only upload a maximum of ${maxFiles} files at once.`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }
      
      // Add files with additional metadata
      const newFiles = acceptedFiles.map(file => ({
        id: `file-${Date.now()}-${file.name}`,
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
      }));
      
      setFiles(prevFiles => [...prevFiles, ...newFiles]);
      
      // Initialize upload progress and status for new files
      const newProgress = { ...uploadProgress };
      const newStatus = { ...uploadStatus };
      
      newFiles.forEach(file => {
        newProgress[file.id] = 0;
        newStatus[file.id] = 'pending';
      });
      
      setUploadProgress(newProgress);
      setUploadStatus(newStatus);
      
      // Start uploading files
      newFiles.forEach(file => {
        uploadFile(file);
      });
    }
  }, [files, maxFiles, uploadProgress, uploadStatus, toast]);
  
  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    maxSize,
    maxFiles: maxFiles - files.length
  });
  
  // Handle file upload
  const uploadFile = async (file) => {
    // Update status to uploading
    setUploadStatus(prev => ({ ...prev, [file.id]: 'uploading' }));
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file.file);
      
      // Create upload request
      const xhr = new XMLHttpRequest();
      
      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(prev => ({ ...prev, [file.id]: progress }));
        }
      });
      
      // Handle upload completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          // Upload successful
          setUploadStatus(prev => ({ ...prev, [file.id]: 'success' }));
          
          // Parse response
          const response = JSON.parse(xhr.responseText);
          
          // Call onFileUpload callback with file info and response
          if (onFileUpload) {
            onFileUpload({
              ...file,
              url: response.url,
              path: response.path
            });
          }
        } else {
          // Upload failed
          setUploadStatus(prev => ({ ...prev, [file.id]: 'error' }));
          
          toast({
            title: 'Upload failed',
            description: `Failed to upload ${file.name}. Please try again.`,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        }
      });
      
      // Handle upload error
      xhr.addEventListener('error', () => {
        setUploadStatus(prev => ({ ...prev, [file.id]: 'error' }));
        
        toast({
          title: 'Upload failed',
          description: `Failed to upload ${file.name}. Please try again.`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      });
      
      // Open connection and send request
      xhr.open('POST', '/api/files/upload', true);
      xhr.send(formData);
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus(prev => ({ ...prev, [file.id]: 'error' }));
      
      toast({
        title: 'Upload failed',
        description: `Failed to upload ${file.name}. Please try again.`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  // Handle file removal
  const handleRemoveFile = (fileId) => {
    const fileToRemove = files.find(file => file.id === fileId);
    
    // Remove file from state
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
    
    // Remove progress and status
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
    
    setUploadStatus(prev => {
      const newStatus = { ...prev };
      delete newStatus[fileId];
      return newStatus;
    });
    
    // Call onFileRemove callback
    if (onFileRemove && fileToRemove) {
      onFileRemove(fileToRemove);
    }
    
    // Revoke object URL for image previews
    if (fileToRemove && fileToRemove.preview) {
      URL.revokeObjectURL(fileToRemove.preview);
    }
  };
  
  // Handle manual file selection
  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };
  
  // Get file icon based on file type
  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) {
      return FiImage;
    } else if (fileType === 'application/pdf') {
      return FiFileText;
    } else {
      return FiFile;
    }
  };
  
  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  // Get status icon based on upload status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <Icon as={FiCheck} color="green.500" />;
      case 'error':
        return <Icon as={FiAlertCircle} color="red.500" />;
      case 'uploading':
        return null; // Progress bar will be shown
      default:
        return null;
    }
  };
  
  return (
    <Box>
      {/* Dropzone */}
      <Box
        {...getRootProps()}
        p={4}
        borderWidth="2px"
        borderRadius="md"
        borderStyle="dashed"
        borderColor={isDragActive ? 'blue.500' : borderColor}
        bg={isDragActive ? 'blue.50' : bgColor}
        _hover={{ bg: hoverBg }}
        cursor="pointer"
        transition="all 0.2s"
        textAlign="center"
      >
        <input {...getInputProps()} />
        
        <VStack spacing={2}>
          <Icon as={FiUpload} boxSize={8} color={isDragActive ? 'blue.500' : 'gray.500'} />
          
          <Text fontWeight="medium">
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </Text>
          
          <Text fontSize="sm" color="gray.500">
            or
          </Text>
          
          <Button
            size="sm"
            leftIcon={<FiPaperclip />}
            onClick={handleFileSelect}
            colorScheme="blue"
            variant="outline"
          >
            Browse files
          </Button>
          
          <Input
            type="file"
            ref={fileInputRef}
            display="none"
            multiple
            onChange={(e) => {
              const fileList = e.target.files;
              if (fileList) {
                const filesArray = Array.from(fileList);
                onDrop(filesArray, []);
              }
              // Reset input value to allow selecting the same file again
              e.target.value = '';
            }}
          />
          
          <Text fontSize="xs" color="gray.500">
            Max file size: {formatFileSize(maxSize)} | Max files: {maxFiles}
          </Text>
        </VStack>
      </Box>
      
      {/* File list */}
      {files.length > 0 && (
        <VStack mt={4} spacing={2} align="stretch">
          {files.map((file) => (
            <HStack
              key={file.id}
              p={2}
              borderWidth="1px"
              borderRadius="md"
              borderColor={borderColor}
              bg={bgColor}
            >
              <Icon as={getFileIcon(file.type)} boxSize={5} color="blue.500" />
              
              <VStack spacing={1} align="stretch" flex={1}>
                <HStack justifyContent="space-between">
                  <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                    {file.name}
                  </Text>
                  
                  <Text fontSize="xs" color="gray.500">
                    {formatFileSize(file.size)}
                  </Text>
                </HStack>
                
                {uploadStatus[file.id] === 'uploading' && (
                  <Progress
                    value={uploadProgress[file.id]}
                    size="xs"
                    colorScheme="blue"
                    borderRadius="full"
                  />
                )}
              </VStack>
              
              {getStatusIcon(uploadStatus[file.id])}
              
              <Tooltip label="Remove file">
                <IconButton
                  icon={<FiX />}
                  size="xs"
                  variant="ghost"
                  colorScheme="red"
                  aria-label="Remove file"
                  onClick={() => handleRemoveFile(file.id)}
                />
              </Tooltip>
            </HStack>
          ))}
        </VStack>
      )}
    </Box>
  );
};

export default FileAttachmentHandler;
