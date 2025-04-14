import React from 'react';
import { 
  Box, 
  Text, 
  useColorModeValue
} from '@chakra-ui/react';
import { Attachment } from '../../models/Message';
import MessageAttachment from './MessageAttachment';

interface AttachmentViewerProps {
  attachments: Attachment[];
}

const AttachmentViewer: React.FC<AttachmentViewerProps> = ({
  attachments
}) => {
  const [selectedAttachment, setSelectedAttachment] = React.useState<Attachment | null>(null);
  const [isOpen, setIsOpen] = React.useState(false);
  
  const handleOpen = (attachment: Attachment) => {
    setSelectedAttachment(attachment);
    setIsOpen(true);
  };
  
  // Render attachment content based on type
  const renderAttachmentContent = (attachment: Attachment) => {
    if (!attachment) return null;
    
    switch(attachment.type) {
      case 'image':
        return (
          <Text>Image: {attachment.name}</Text>
        );
      case 'tool_result':
      case 'memory_block':
        return (
          <Text>Tool result: {attachment.name}</Text>
        );
      case 'file':
      default:
        return (
          <Text>File: {attachment.name}</Text>
        );
    }
  };
  
  if (!attachments || attachments.length === 0) return null;
  
  return (
    <Box mt={2}>
      {attachments.map((attachment, index) => (
        <MessageAttachment 
          key={index}
          attachment={attachment}
          onOpen={handleOpen}
        />
      ))}
      
      {isOpen && selectedAttachment && (
        <Box 
          mt={2} 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor={useColorModeValue('gray.200', 'gray.700')}
        >
          {renderAttachmentContent(selectedAttachment)}
          <Box 
            as="button" 
            mt={2} 
            onClick={() => setIsOpen(false)}
            fontSize="sm"
            color="blue.500"
          >
            Close
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default AttachmentViewer;
