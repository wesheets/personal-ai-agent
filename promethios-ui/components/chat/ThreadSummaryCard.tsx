import React from 'react';
import { Box, Flex, Text, Badge, useColorModeValue, Button, HStack, Icon } from '@chakra-ui/react';
import { FiFileText, FiDownload, FiCheck } from 'react-icons/fi';
import { ThreadSummary } from '../../models/Message';

interface ThreadSummaryCardProps {
  threadId: string;
  summary: ThreadSummary;
  onExportMarkdown: (threadId: string) => void;
  onExportPDF: (threadId: string) => void;
  onMarkResolved: (threadId: string) => void;
}

const ThreadSummaryCard: React.FC<ThreadSummaryCardProps> = ({
  threadId,
  summary,
  onExportMarkdown,
  onExportPDF,
  onMarkResolved
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleString([], { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  return (
    <Box
      borderWidth="1px"
      borderRadius="md"
      p={4}
      bg={bgColor}
      borderColor={borderColor}
      borderLeftWidth="3px"
      borderLeftColor="purple.500"
      mb={4}
    >
      <Flex justifyContent="space-between" alignItems="center" mb={2}>
        <HStack>
          <Icon as={FiFileText} color="purple.500" />
          <Text fontWeight="medium">Thread Summary</Text>
        </HStack>
        <Badge colorScheme="purple" variant="subtle">
          Generated {formatTime(summary.generated_at)}
        </Badge>
      </Flex>
      
      <Text mb={4} fontStyle="italic">
        {summary.summary}
      </Text>
      
      <HStack justifyContent="flex-end" spacing={2}>
        <Button
          size="sm"
          leftIcon={<FiCheck />}
          variant="ghost"
          onClick={() => onMarkResolved(threadId)}
        >
          Mark Resolved
        </Button>
        <Button
          size="sm"
          leftIcon={<FiDownload />}
          variant="outline"
          onClick={() => onExportMarkdown(threadId)}
        >
          Export .md
        </Button>
        <Button
          size="sm"
          leftIcon={<FiDownload />}
          colorScheme="blue"
          variant="outline"
          onClick={() => onExportPDF(threadId)}
        >
          Export PDF
        </Button>
      </HStack>
    </Box>
  );
};

export default ThreadSummaryCard;
