import React, { useState } from 'react';
import {
  Box,
  Flex,
  Input,
  Button,
  Icon,
  useColorModeValue,
  Tooltip,
  IconButton
} from '@chakra-ui/react';
import { FiSend, FiPaperclip, FiMic, FiCode } from 'react-icons/fi';

const InputUI = ({ onSendMessage }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const inputBgColor = useColorModeValue('gray.50', 'gray.700');
  
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    if (!isTyping && e.target.value) {
      setIsTyping(true);
    } else if (isTyping && !e.target.value) {
      setIsTyping(false);
    }
  };

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      p={4}
      bg={bgColor}
      borderTopWidth="1px"
      borderColor={borderColor}
      zIndex={10}
      ml={{ base: 0, md: '240px' }} // Adjust based on sidebar width
    >
      <Flex 
        maxW="1200px" 
        mx="auto"
        alignItems="center"
        boxShadow="sm"
        borderRadius="lg"
        p={2}
        bg={bgColor}
      >
        <Tooltip label="Attach file">
          <IconButton
            variant="ghost"
            colorScheme="blue"
            aria-label="Attach file"
            icon={<FiPaperclip />}
            mr={1}
          />
        </Tooltip>
        
        <Tooltip label="Voice input">
          <IconButton
            variant="ghost"
            colorScheme="blue"
            aria-label="Voice input"
            icon={<FiMic />}
            mr={1}
          />
        </Tooltip>
        
        <Tooltip label="Code snippet">
          <IconButton
            variant="ghost"
            colorScheme="blue"
            aria-label="Code snippet"
            icon={<FiCode />}
            mr={2}
          />
        </Tooltip>
        
        <Input
          flex="1"
          placeholder="Type your message here..."
          value={inputMessage}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          bg={inputBgColor}
          borderColor={borderColor}
          borderRadius="md"
          _focus={{ 
            borderColor: 'blue.400',
            boxShadow: '0 0 0 1px var(--chakra-colors-blue-400)'
          }}
          size="md"
        />
        
        <Button
          ml={2}
          colorScheme="blue"
          onClick={handleSendMessage}
          isDisabled={!inputMessage.trim()}
          leftIcon={<FiSend />}
          size="md"
        >
          Send
        </Button>
      </Flex>
      
      {/* Typing indicator */}
      {isTyping && (
        <Box 
          position="absolute" 
          bottom="100%" 
          left="50%" 
          transform="translateX(-50%)"
          bg="blue.500"
          color="white"
          fontSize="xs"
          py={1}
          px={3}
          borderRadius="full"
          mb={2}
        >
          Message to HAL
        </Box>
      )}
    </Box>
  );
};

export default InputUI;
