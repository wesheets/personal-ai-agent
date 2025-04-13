import React from 'react';
import {
  Box,
  Flex,
  Text,
  Badge,
  useColorModeValue,
  Icon,
  Tooltip,
  Button,
  HStack,
  Code,
  useClipboard
} from '@chakra-ui/react';
import { FiClock, FiCopy, FiCode, FiFileText, FiDatabase } from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import PropTypes from 'prop-types';

const ToolOutputCard = ({ output }) => {
  const { hasCopied, onCopy } = useClipboard(output.content);
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const codeBgColor = useColorModeValue('gray.50', 'gray.900');
  
  // Determine if content is code
  const isCode = !!output.language;
  
  // Determine if content is markdown
  const isMarkdown = output.content.includes('#') || 
                    output.content.includes('*') || 
                    output.content.includes('```');
  
  // Get tool icon
  const getToolIcon = (toolName) => {
    if (toolName.includes('code')) return FiCode;
    if (toolName.includes('search')) return FiFileText;
    if (toolName.includes('data')) return FiDatabase;
    return FiCode;
  };
  
  // Format timestamp
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Box
      mb={4}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
      boxShadow="sm"
    >
      {/* Tool header */}
      <Flex 
        justify="space-between" 
        align="center" 
        p={3} 
        borderBottomWidth="1px" 
        borderColor={borderColor}
      >
        <Flex align="center">
          <Icon as={getToolIcon(output.toolName)} mr={2} />
          <Text fontWeight="bold">{output.toolName}</Text>
        </Flex>
        
        <HStack spacing={2}>
          {output.memoryId && (
            <Tooltip label="Saved to memory">
              <Badge colorScheme="purple" variant="subtle">
                Memory
              </Badge>
            </Tooltip>
          )}
          
          <Flex align="center">
            <Icon as={FiClock} size="sm" mr={1} />
            <Text fontSize="xs" color="gray.500">
              {formatTime(output.timestamp)}
            </Text>
          </Flex>
          
          <Tooltip label={hasCopied ? "Copied!" : "Copy to clipboard"}>
            <Button 
              size="xs" 
              variant="ghost" 
              onClick={onCopy}
              aria-label="Copy to clipboard"
            >
              <Icon as={FiCopy} />
            </Button>
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Tool content */}
      <Box p={3}>
        {isCode ? (
          <Box borderRadius="md" overflow="hidden">
            <SyntaxHighlighter
              language={output.language}
              style={atomDark}
              customStyle={{ margin: 0, borderRadius: '0.375rem' }}
            >
              {output.content}
            </SyntaxHighlighter>
          </Box>
        ) : isMarkdown ? (
          <Box 
            p={3} 
            bg={codeBgColor} 
            borderRadius="md" 
            fontSize="sm" 
            whiteSpace="pre-wrap"
            sx={{
              'h1, h2, h3, h4, h5, h6': {
                fontWeight: 'bold',
                marginTop: '0.5rem',
                marginBottom: '0.5rem'
              },
              'h1': { fontSize: 'xl' },
              'h2': { fontSize: 'lg' },
              'h3': { fontSize: 'md' },
              'ul, ol': {
                paddingLeft: '1rem',
                marginBottom: '0.5rem'
              },
              'code': {
                bg: 'gray.700',
                padding: '0.1rem 0.3rem',
                borderRadius: '0.2rem',
                fontFamily: 'monospace'
              },
              'pre': {
                bg: 'gray.800',
                padding: '0.5rem',
                borderRadius: '0.3rem',
                overflow: 'auto',
                marginBottom: '0.5rem'
              }
            }}
          >
            {output.content}
          </Box>
        ) : (
          <Text whiteSpace="pre-wrap">{output.content}</Text>
        )}
      </Box>
    </Box>
  );
};

// Define prop types
ToolOutputCard.propTypes = {
  output: PropTypes.shape({
    id: PropTypes.string.isRequired,
    toolName: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    language: PropTypes.string,
    timestamp: PropTypes.instanceOf(Date).isRequired,
    memoryId: PropTypes.string
  }).isRequired
};

export default ToolOutputCard;
