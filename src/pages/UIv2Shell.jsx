import React from 'react';
import { Box, Heading, Text, Flex, Container, VStack, HStack, Button, useColorModeValue } from '@chakra-ui/react';
import { BrandLogo, BrandHeader, BrandFooter } from '../components/brand';

/**
 * UIv2Shell - The main shell component for the Promethios UI v2
 * This component serves as the entry point for the new UI system
 */
const UIv2Shell = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box minH="100vh" bg={bgColor} color={textColor}>
      <Container maxW="container.xl" p={0}>
        {/* Header */}
        <BrandHeader 
          title="Promethios UI v2" 
          subtitle="Full Agent OS Shell + Auth" 
        />
        
        {/* Main Content */}
        <Box py={10} px={4}>
          <VStack spacing={8} align="stretch">
            <Box textAlign="center">
              <Heading as="h1" size="2xl" mb={4}>
                Welcome to Promethios UI v2
              </Heading>
              <Text fontSize="xl">
                The scalable, multi-agent, user-authenticated system
              </Text>
            </Box>
            
            <Flex 
              direction={{ base: 'column', md: 'row' }} 
              gap={6} 
              justify="center"
              wrap="wrap"
            >
              {/* System Agents Section */}
              <Box 
                flex="1" 
                p={6} 
                borderWidth="1px" 
                borderRadius="lg" 
                borderColor={borderColor}
                shadow="md"
              >
                <Heading as="h2" size="lg" mb={4}>System Agents</Heading>
                <VStack align="stretch" spacing={4}>
                  <HStack p={3} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
                    <Box fontWeight="bold" flex="1">HAL</Box>
                    <Button size="sm" colorScheme="blue">Chat</Button>
                  </HStack>
                  <HStack p={3} bg={useColorModeValue('purple.50', 'purple.900')} borderRadius="md">
                    <Box fontWeight="bold" flex="1">ASH</Box>
                    <Button size="sm" colorScheme="purple">Chat</Button>
                  </HStack>
                </VStack>
              </Box>
              
              {/* Features Section */}
              <Box 
                flex="1" 
                p={6} 
                borderWidth="1px" 
                borderRadius="lg" 
                borderColor={borderColor}
                shadow="md"
              >
                <Heading as="h2" size="lg" mb={4}>Key Features</Heading>
                <VStack align="stretch" spacing={3}>
                  <Text>✅ JWT-based authentication</Text>
                  <Text>✅ Multi-agent support</Text>
                  <Text>✅ User-scoped memory</Text>
                  <Text>✅ File attachments</Text>
                  <Text>✅ Activity logging</Text>
                  <Text>✅ Responsive design</Text>
                </VStack>
              </Box>
            </Flex>
            
            {/* Implementation Status */}
            <Box 
              p={6} 
              borderWidth="1px" 
              borderRadius="lg" 
              borderColor={borderColor}
              bg={useColorModeValue('green.50', 'green.900')}
              shadow="md"
            >
              <Heading as="h2" size="lg" mb={4}>Implementation Status</Heading>
              <Text fontSize="lg">
                All features from GitHub Issue #1 have been successfully implemented with 10 feature branches and pull requests.
              </Text>
            </Box>
          </VStack>
        </Box>
        
        {/* Footer */}
        <BrandFooter />
      </Container>
    </Box>
  );
};

export default UIv2Shell;
