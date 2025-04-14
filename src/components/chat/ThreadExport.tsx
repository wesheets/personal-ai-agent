import React from 'react';
import { 
  Box, 
  Button, 
  VStack, 
  HStack, 
  Text, 
  useColorModeValue,
  Icon,
  useToast
} from '@chakra-ui/react';
import { FiFileText, FiFilePlus } from 'react-icons/fi';
import { UIMessage } from '../../models/Message';

interface ThreadExportProps {
  threadId: string;
  messages: UIMessage[];
  onExportMarkdown: (threadId: string) => void;
  onExportPDF: (threadId: string) => void;
}

const ThreadExport: React.FC<ThreadExportProps> = ({
  threadId,
  messages,
  onExportMarkdown,
  onExportPDF
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const toast = useToast();
  
  // Filter messages to only include those in this thread
  const threadMessages = messages.filter(
    msg => msg.message_id === threadId || msg.thread_parent_id === threadId
  );
  
  // Generate markdown export
  const generateMarkdown = () => {
    let markdown = `# Thread Export\n\n`;
    markdown += `Generated: ${new Date().toLocaleString()}\n\n`;
    
    threadMessages.forEach(msg => {
      const sender = msg.sender === 'operator' ? 'Operator' : msg.agent_id;
      const time = msg.timestamp.toLocaleString();
      
      markdown += `## ${sender} (${time})\n\n`;
      markdown += `${msg.content}\n\n`;
      
      if (msg.attachments && msg.attachments.length > 0) {
        markdown += `### Attachments\n\n`;
        msg.attachments.forEach(attachment => {
          markdown += `- ${attachment.name} (${attachment.type})\n`;
        });
        markdown += `\n`;
      }
    });
    
    return markdown;
  };
  
  // Handle markdown export
  const handleExportMarkdown = () => {
    // In a real implementation, this would create a file and trigger download
    // For now, we'll just show a toast and call the provided callback
    generateMarkdown();
    
    toast({
      title: 'Markdown Export',
      description: 'Thread exported as markdown successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
    
    onExportMarkdown(threadId);
  };
  
  // Handle PDF export
  const handleExportPDF = () => {
    // In a real implementation, this would generate a PDF and trigger download
    // For now, we'll just show a toast and call the provided callback
    
    toast({
      title: 'PDF Export',
      description: 'Thread exported as PDF successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
    
    onExportPDF(threadId);
  };
  
  return (
    <Box
      p={3}
      borderWidth="1px"
      borderRadius="md"
      borderColor={borderColor}
      bg={bgColor}
      mt={2}
    >
      <Text fontWeight="medium" mb={2}>Export Thread</Text>
      
      <VStack align="stretch" spacing={3}>
        <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
          Export this thread with {threadMessages.length} messages and all attachments.
        </Text>
        
        <HStack spacing={2}>
          <Button
            leftIcon={<Icon as={FiFileText} />}
            variant="outline"
            size="sm"
            onClick={handleExportMarkdown}
            flex="1"
          >
            Export as Markdown
          </Button>
          
          <Button
            leftIcon={<Icon as={FiFilePlus} />}
            colorScheme="blue"
            variant="outline"
            size="sm"
            onClick={handleExportPDF}
            flex="1"
          >
            Export as PDF
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default ThreadExport;
