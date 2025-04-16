import React, { useState, useEffect } from 'react';
import { Box, Flex, useDisclosure, useColorModeValue } from '@chakra-ui/react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ActivityLogTray from '../ActivityLogTray';

/**
 * AppLayout - Main layout component for authenticated pages
 * Includes sidebar, header, and content area
 */
const AppLayout = ({ children, activePage }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const location = useLocation();

  const bgColor = useColorModeValue('gray.50', 'gray.900');

  const handleSidebarToggle = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  // Extract agent ID from URL if present
  const getAgentIdFromPath = () => {
    const path = location.pathname;
    if (path.startsWith('/chat/')) {
      return path.split('/').pop();
    }
    if (path.startsWith('/agent/')) {
      return path.split('/').pop();
    }
    return null;
  };

  const agentId = getAgentIdFromPath();

  return (
    <Flex h="100vh" flexDirection="column">
      {/* Mobile Sidebar Overlay */}
      {isMobileSidebarOpen && (
        <Box
          position="fixed"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="blackAlpha.600"
          zIndex="overlay"
          display={{ base: 'block', md: 'none' }}
          onClick={() => setIsMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Box
        display={{ base: isMobileSidebarOpen ? 'block' : 'none', md: 'block' }}
        w={{ base: 'full', md: '250px' }}
        position="fixed"
        h="full"
        zIndex="sticky"
      >
        <Sidebar />
      </Box>

      {/* Main Content Area */}
      <Flex direction="column" flex="1" ml={{ base: 0, md: '250px' }} transition="margin-left 0.3s">
        {/* Header */}
        <Header onSidebarToggle={handleSidebarToggle}>
          {/* Activity Log Tray */}
          <ActivityLogTray agentId={agentId} />
        </Header>

        {/* Page Content */}
        <Box as="main" flex="1" p={6} bg={bgColor} overflowY="auto">
          {children}
        </Box>
      </Flex>
    </Flex>
  );
};

export default AppLayout;
