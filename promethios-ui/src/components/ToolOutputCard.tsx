import React from 'react';
import { 
  Box, 
  Text, 
  useColorModeValue, 
  HStack, 
  Badge, 
  Button,
  Icon,
  useClipboard
} from '@chakra-ui/react';
import { FiCopy, FiCode, FiFileText, FiTerminal } from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ToolOutputCardProps {
  title: string;
  content: string;
  type: 'code' | 'text' | 'markdown' | 'terminal';
  language?: string;
  timestamp: Date;
}

const ToolOutputCard: React.FC<ToolOutputCardProps> = ({
  title,
  content,
  type,
  language = 'javascript',
  timestamp
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { hasCopied, onCopy } = useClipboard(content);
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Get icon based on type
  const getIcon = (type: string) => {
    switch(type) {
      case 'code': return FiCode;
      case 'text': return FiFileText;
      case 'markdown': return FiFileText;
      case 'terminal': return FiTerminal;
      default: return FiFileText;
    }
  };
  
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      p={4}
      mb={4}
      overflow="hidden"
    >
      <HStack mb={3} justify="space-between">
        <HStack>
          <Icon as={getIcon(type)} />
          <Text fontWeight="medium">{title}</Text>
          <Badge colorScheme={
            type === 'code' ? 'blue' : 
            type === 'terminal' ? 'gray' : 
            type === 'markdown' ? 'green' : 'purple'
          }>
            {type}
          </Badge>
        </HStack>
        <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
          {formatTime(timestamp)}
        </Text>
      </HStack>
      
      <Box
        borderWidth="1px"
        borderRadius="md"
        borderColor={borderColor}
        overflow="auto"
        maxH="300px"
        mb={2}
      >
        {type === 'code' && (
          <SyntaxHighlighter 
            language={language} 
            style={tomorrow}
            customStyle={{ margin: 0, borderRadius: '0.375rem' }}
          >
            {content}
          </SyntaxHighlighter>
        )}
        
        {type === 'terminal' && (
          <Box bg="black" p={3} fontFamily="monospace" fontSize="sm" color="white">
            {content}
          </Box>
        )}
        
        {(type === 'text' || type === 'markdown') && (
          <Box p={3} fontFamily="monospace" fontSize="sm" whiteSpace="pre-wrap">
            {content}
          </Box>
        )}
      </Box>
      
      <HStack justify="flex-end">
        <Button
          size="sm"
          leftIcon={<Icon as={FiCopy} />}
          onClick={onCopy}
        >
          {hasCopied ? 'Copied!' : 'Copy'}
        </Button>
      </HStack>
    </Box>
  );
};

export default ToolOutputCard;
