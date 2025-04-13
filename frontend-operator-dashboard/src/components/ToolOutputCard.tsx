import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  useColorModeValue,
  Grid,
  GridItem,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Icon,
  Image,
  Link as ChakraLink
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { FiSend, FiCode, FiCopy, FiDownload } from 'react-icons/fi';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomOneDark, atomOneLight } from 'react-syntax-highlighter/dist/esm/styles/hljs';

interface ToolOutputCardProps {
  output: {
    id: string;
    toolName: string;
    content: string;
    language?: string;
    timestamp: Date;
    memoryId?: string;
  };
}

const ToolOutputCard: React.FC<ToolOutputCardProps> = ({ output }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const codeStyle = useColorModeValue(atomOneLight, atomOneDark);
  
  // Determine if content is code
  const isCode = !!output.language;
  
  // Function to copy content to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(output.content);
    // Could add a toast notification here
  };
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
      mb={4}
    >
      <Flex 
        justify="space-between" 
        align="center" 
        bg={useColorModeValue('gray.50', 'gray.700')} 
        p={3}
        borderBottomWidth="1px"
        borderColor={borderColor}
      >
        <HStack>
          <Icon as={FiCode} />
          <Text fontWeight="medium">{output.toolName}</Text>
        </HStack>
        <HStack>
          <Text fontSize="xs" color="gray.500">
            {formatTime(output.timestamp)}
          </Text>
          <Button 
            size="xs" 
            leftIcon={<FiCopy />} 
            variant="ghost" 
            onClick={copyToClipboard}
          >
            Copy
          </Button>
          {output.memoryId && (
            <ChakraLink as={Link} to={`/memory/${output.memoryId}`}>
              <Button size="xs" leftIcon={<FiDownload />} variant="ghost">
                Memory
              </Button>
            </ChakraLink>
          )}
        </HStack>
      </Flex>
      
      <Box p={isCode ? 0 : 4} maxH="400px" overflowY="auto">
        {isCode ? (
          <SyntaxHighlighter 
            language={output.language} 
            style={codeStyle}
            customStyle={{ margin: 0, borderRadius: 0 }}
          >
            {output.content}
          </SyntaxHighlighter>
        ) : (
          <Text whiteSpace="pre-wrap">{output.content}</Text>
        )}
      </Box>
    </Box>
  );
};

export default ToolOutputCard;
