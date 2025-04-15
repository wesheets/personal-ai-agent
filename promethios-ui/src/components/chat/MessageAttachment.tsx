import React from 'react';
import { 
  Box, 
  Text, 
  Badge, 
  useColorModeValue,
  Icon,
  HStack
} from '@chakra-ui/react';
import { FiPaperclip, FiFile, FiImage, FiCode } from 'react-icons/fi';
import { Attachment } from '../../models/Message';

interface MessageAttachmentProps {
  attachment: Attachment;
  onOpen: (attachment: Attachment) => void;
}

const MessageAttachment: React.FC<MessageAttachmentProps> = ({
  attachment,
  onOpen
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Get icon based on attachment type
  const getIcon = (type: string) => {
    if (type === 'file') return FiFile;
    if (type === 'image') return FiImage;
    if (type === 'tool_result') return FiCode;
    if (type === 'memory_block') return FiCode;
    return FiPaperclip;
  };
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <Box
      mt={2}
      p={2}
      borderWidth="1px"
      borderRadius="md"
      borderColor={borderColor}
      bg={bgColor}
      cursor="pointer"
      _hover={{ bg: useColorModeValue('gray.100', 'gray.600') }}
      onClick={() => onOpen(attachment)}
    >
      <HStack spacing={2}>
        <Icon as={getIcon(attachment.type)} />
        <Text fontSize="sm" fontWeight="medium">{attachment.name}</Text>
        <Badge size="sm" colorScheme="blue" variant="subtle">
          {attachment.type}
        </Badge>
        <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
          {formatTime(attachment.timestamp)}
        </Text>
      </HStack>
    </Box>
  );
};

export default MessageAttachment;
