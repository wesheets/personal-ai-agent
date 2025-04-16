import React, { useRef } from 'react';
import { Box, Input, Text, useColorModeValue } from '@chakra-ui/react';

const AgentFileUpload = ({ onFileUpload }) => {
  const fileInputRef = useRef(null);
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  const borderColor = useColorModeValue('gray.300', 'gray.600');

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  const handlePaste = (e) => {
    const items = e.clipboardData?.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].kind === 'file') {
          const file = items[i].getAsFile();
          onFileUpload(file);
          break;
        }
      }
    }
  };

  return (
    <Box
      p={4}
      bg={bgColor}
      borderRadius="md"
      border="2px dashed"
      borderColor={borderColor}
      textAlign="center"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onPaste={handlePaste}
      onClick={() => fileInputRef.current?.click()}
      cursor="pointer"
      mb={4}
    >
      <Text>Drop files here, click to browse, or paste from clipboard</Text>
      <Input type="file" ref={fileInputRef} onChange={handleFileChange} display="none" />
    </Box>
  );
};

export default AgentFileUpload;
