import React from 'react';
import {
  Box,
  Input,
  Button,
  HStack,
  Icon,
  Text,
  useColorModeValue,
  VStack,
  Image,
  CloseButton
} from '@chakra-ui/react';
import { FiSend, FiPaperclip } from 'react-icons/fi';

interface InputUIProps {
  onSendMessage: (content: string, files?: File[]) => void;
  placeholder?: string;
  isReplyMode?: boolean;
  replyToName?: string;
  onCancelReply?: () => void;
}

const InputUI: React.FC<InputUIProps> = ({
  onSendMessage,
  placeholder = 'Type a message...',
  isReplyMode = false,
  replyToName,
  onCancelReply
}) => {
  const [inputValue, setInputValue] = React.useState('');
  const [files, setFiles] = React.useState<File[]>([]);
  const [filePreviewUrls, setFilePreviewUrls] = React.useState<string[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  // Handle key press (Enter to send, Shift+Enter for newline)
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...newFiles]);

      // Generate preview URLs
      const newPreviewUrls = newFiles.map((file) => {
        if (file.type.startsWith('image/')) {
          return URL.createObjectURL(file);
        }
        return '';
      });

      setFilePreviewUrls((prev) => [...prev, ...newPreviewUrls]);
    }
  };

  // Handle file drop
  const handleDrop = React.useCallback((e: React.DragEvent) => {
    e.preventDefault();

    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      setFiles((prev) => [...prev, ...newFiles]);

      // Generate preview URLs
      const newPreviewUrls = newFiles.map((file) => {
        if (file.type.startsWith('image/')) {
          return URL.createObjectURL(file);
        }
        return '';
      });

      setFilePreviewUrls((prev) => [...prev, ...newPreviewUrls]);
    }
  }, []);

  // Handle drag over
  const handleDragOver = React.useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  // Handle file removal
  const handleRemoveFile = (index: number) => {
    // Revoke object URL to prevent memory leaks
    if (filePreviewUrls[index]) {
      URL.revokeObjectURL(filePreviewUrls[index]);
    }

    setFiles((prev) => prev.filter((_, i) => i !== index));
    setFilePreviewUrls((prev) => prev.filter((_, i) => i !== index));
  };

  // Handle send message
  const handleSendMessage = () => {
    if (inputValue.trim() || files.length > 0) {
      onSendMessage(inputValue, files.length > 0 ? files : undefined);
      setInputValue('');
      setFiles([]);

      // Revoke all object URLs
      filePreviewUrls.forEach((url) => {
        if (url) URL.revokeObjectURL(url);
      });
      setFilePreviewUrls([]);

      if (isReplyMode && onCancelReply) {
        onCancelReply();
      }
    }
  };

  // Handle file button click
  const handleFileButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <Box
      p={3}
      borderWidth="1px"
      borderRadius="lg"
      bg={useColorModeValue('white', 'gray.800')}
      borderColor={useColorModeValue('gray.200', 'gray.700')}
      position="sticky"
      bottom={0}
      width="100%"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      {isReplyMode && (
        <Box
          mb={2}
          p={2}
          borderRadius="md"
          bg={useColorModeValue('blue.50', 'blue.900')}
          fontSize="sm"
        >
          <HStack justify="space-between">
            <Text>Replying to {replyToName}</Text>
            {onCancelReply && (
              <Button size="xs" variant="ghost" onClick={onCancelReply}>
                Cancel
              </Button>
            )}
          </HStack>
        </Box>
      )}

      <HStack>
        <Input
          placeholder={placeholder}
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          mr={2}
          flex={1}
        />
        <Button onClick={handleFileButtonClick} variant="ghost" mr={2}>
          <Icon as={FiPaperclip} />
        </Button>
        <Button
          colorScheme="blue"
          onClick={handleSendMessage}
          isDisabled={!inputValue.trim() && files.length === 0}
          leftIcon={<Icon as={FiSend} />}
        >
          Send
        </Button>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileSelect}
          multiple
        />
      </HStack>

      {/* File previews */}
      {files.length > 0 && (
        <VStack align="stretch" mt={2} spacing={2}>
          <Text fontSize="sm" fontWeight="medium">
            Attachments:
          </Text>
          <HStack flexWrap="wrap" gap={2}>
            {files.map((file, index) => (
              <Box
                key={index}
                position="relative"
                borderWidth="1px"
                borderRadius="md"
                p={2}
                width="100px"
              >
                {filePreviewUrls[index] ? (
                  <Image
                    src={filePreviewUrls[index]}
                    alt={file.name}
                    maxH="60px"
                    objectFit="contain"
                    mb={1}
                  />
                ) : (
                  <Box
                    height="60px"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    bg={useColorModeValue('gray.100', 'gray.700')}
                    mb={1}
                    borderRadius="md"
                  >
                    <Text fontSize="xs">{file.type.split('/')[0]}</Text>
                  </Box>
                )}
                <Text fontSize="xs" noOfLines={1} title={file.name}>
                  {file.name}
                </Text>
                <CloseButton
                  size="sm"
                  position="absolute"
                  top={0}
                  right={0}
                  onClick={() => handleRemoveFile(index)}
                />
              </Box>
            ))}
          </HStack>
        </VStack>
      )}
    </Box>
  );
};

export default InputUI;
