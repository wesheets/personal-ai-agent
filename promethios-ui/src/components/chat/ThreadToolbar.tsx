import React from 'react';
import { 
  Box, 
  Text, 
  useColorModeValue
} from '@chakra-ui/react';
import { FiFileText, FiFilePlus } from 'react-icons/fi';

interface ThreadToolbarProps {
  messageId: string;
  onMarkResolved: (messageId: string) => void;
  onSummarizeThread: (messageId: string) => void;
  onExportMarkdown: (messageId: string) => void;
  onExportPDF: (messageId: string) => void;
}

const ThreadToolbar: React.FC<ThreadToolbarProps> = ({
  messageId,
  onMarkResolved,
  onSummarizeThread,
  onExportMarkdown,
  onExportPDF
}) => {
  return (
    <Box>
      <Box
        as="button"
        onClick={() => onMarkResolved(messageId)}
        p={1}
        borderRadius="md"
        _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
        mr={2}
      >
        <Text fontSize="sm">Mark Resolved</Text>
      </Box>
      <Box
        as="button"
        onClick={() => onSummarizeThread(messageId)}
        p={1}
        borderRadius="md"
        _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
        mr={2}
      >
        <Text fontSize="sm">Summarize</Text>
      </Box>
      <Box
        as="button"
        onClick={() => onExportMarkdown(messageId)}
        p={1}
        borderRadius="md"
        _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
        mr={2}
      >
        <Box as={FiFileText} display="inline-block" mr={1} />
        <Text fontSize="sm" as="span">MD</Text>
      </Box>
      <Box
        as="button"
        onClick={() => onExportPDF(messageId)}
        p={1}
        borderRadius="md"
        _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
      >
        <Box as={FiFilePlus} display="inline-block" mr={1} />
        <Text fontSize="sm" as="span">PDF</Text>
      </Box>
    </Box>
  );
};

export default ThreadToolbar;
