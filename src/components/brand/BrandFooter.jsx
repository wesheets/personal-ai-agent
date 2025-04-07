import React from 'react';
import { Box, Flex, Text, useColorModeValue, Button, Icon } from '@chakra-ui/react';
import { FiInfo } from 'react-icons/fi';

const BrandFooter = ({ showVersion = true, ...props }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');
  
  const version = 'v2.0.0'; // Version should be dynamically pulled from package.json in a real implementation
  const currentYear = new Date().getFullYear();
  
  return (
    <Box
      as="footer"
      py={4}
      px={6}
      bg={bgColor}
      borderTopWidth="1px"
      borderColor={borderColor}
      {...props}
    >
      <Flex 
        direction={{ base: 'column', md: 'row' }}
        justify="space-between"
        align={{ base: 'center', md: 'center' }}
        maxW="container.xl"
        mx="auto"
        gap={2}
      >
        <Text fontSize="sm" color={textColor}>
          &copy; {currentYear} Promethios AI. All rights reserved.
        </Text>
        
        <Flex align="center" gap={4}>
          <Button 
            as="a" 
            href="https://docs.promethios.ai" 
            target="_blank"
            variant="ghost" 
            size="sm"
            colorScheme="brand"
          >
            Documentation
          </Button>
          
          <Button 
            as="a" 
            href="https://promethios.ai/privacy" 
            target="_blank"
            variant="ghost" 
            size="sm"
            colorScheme="brand"
          >
            Privacy Policy
          </Button>
          
          <Button 
            as="a" 
            href="https://promethios.ai/terms" 
            target="_blank"
            variant="ghost" 
            size="sm"
            colorScheme="brand"
          >
            Terms of Service
          </Button>
        </Flex>
        
        {showVersion && (
          <Flex align="center">
            <Icon as={FiInfo} color={textColor} mr={1} />
            <Text fontSize="xs" color={textColor}>
              {version}
            </Text>
          </Flex>
        )}
      </Flex>
    </Box>
  );
};

export default BrandFooter;
