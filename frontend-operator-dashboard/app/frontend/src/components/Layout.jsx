import React from 'react';
import { 
  Box, 
  Flex, 
  useColorMode, 
  useColorModeValue, 
  IconButton,
  Container,
  Heading
} from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

// Simple sun/moon icons for theme toggle
const SunIcon = () => <Box as="span" fontSize="1.2em">☀️</Box>;
const MoonIcon = () => <Box as="span" fontSize="1.2em">🌙</Box>;

const Layout = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const headerBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Flex h="100vh" bg={bgColor}>
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main content area */}
      <Box ml="64" flex="1" display="flex" flexDirection="column" overflow="hidden">
        {/* Header */}
        <Flex
          as="header"
          align="center"
          justify="space-between"
          py={4}
          px={8}
          bg={headerBg}
          borderBottomWidth="1px"
          borderColor={borderColor}
          h="16"
        >
          <Heading size="md">Personal AI Agent System</Heading>
          
          <IconButton
            aria-label={`Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`}
            variant="ghost"
            onClick={toggleColorMode}
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          />
        </Flex>
        
        {/* Main content */}
        <Box flex="1" p={8} overflowY="auto">
          <Container maxW="container.xl" p={0}>
            <Outlet />
          </Container>
        </Box>
      </Box>
    </Flex>
  );
};

export default Layout;
