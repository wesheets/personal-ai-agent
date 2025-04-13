import React, { useState } from 'react';
import {
  Box,
  Flex,
  Input,
  Button,
  Icon,
  useColorModeValue,
  HStack
} from '@chakra-ui/react';
import { FiSend, FiPaperclip } from 'react-icons/fi';

interface InputUIProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

const InputUI: React.FC<InputUIProps> = ({ onSendMessage, isLoading = false }) => {
  const [inputMessage, setInputMessage] = useState('');
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
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
      <Flex maxW="1200px" mx="auto">
        <Button
          variant="ghost"
          mr={2}
          aria-label="Attach file"
        >
          <Icon as={FiPaperclip} />
        </Button>
        <Input
          flex="1"
          placeholder="Type your message here..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          bg={useColorModeValue('white', 'gray.700')}
          borderColor={borderColor}
        />
        <Button
          ml={2}
          colorScheme="blue"
          onClick={handleSendMessage}
          isDisabled={!inputMessage.trim() || isLoading}
          isLoading={isLoading}
          leftIcon={<FiSend />}
        >
          Send
        </Button>
      </Flex>
    </Box>
  );
};

export default InputUI;
