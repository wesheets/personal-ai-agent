import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ColorModeToggle from './components/ColorModeToggle';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import { BuilderAgent, OpsAgent, ResearchAgent } from './pages/AgentPanels';
import MemoryAgentView from './pages/MemoryAgentView';
import MemoryBrowser from './pages/MemoryBrowser';
import MainActivityFeed from './pages/MainActivityFeed';
import SettingsPage from './pages/SettingsPage';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const { colorMode } = useColorMode();
  
  return (
    <ErrorBoundary>
      <Router>
        <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
          <Flex direction="column" h="100vh">
            {/* Top navigation area with color mode toggle */}
            <Flex 
              as="header" 
              position="fixed" 
              w="full" 
              zIndex="1000"
              bg={colorMode === 'light' ? 'white' : 'gray.800'}
              boxShadow="sm"
              justifyContent="flex-end"
              p={2}
            >
              <ColorModeToggle />
            </Flex>
            
            {/* Sidebar navigation */}
            <Sidebar />
            
            {/* Main content area */}
            <Box ml={{ base: 0, md: '60' }} p="4" pt="20">
              <Routes>
                <Route path="/" element={
                  <ErrorBoundary>
                    <Dashboard />
                  </ErrorBoundary>
                } />
                <Route path="/builder" element={
                  <ErrorBoundary>
                    <BuilderAgent />
                  </ErrorBoundary>
                } />
                <Route path="/ops" element={
                  <ErrorBoundary>
                    <OpsAgent />
                  </ErrorBoundary>
                } />
                <Route path="/research" element={
                  <ErrorBoundary>
                    <ResearchAgent />
                  </ErrorBoundary>
                } />
                <Route path="/memory" element={
                  <ErrorBoundary>
                    <MemoryAgentView />
                  </ErrorBoundary>
                } />
                <Route path="/memory-browser" element={
                  <ErrorBoundary>
                    <MemoryBrowser />
                  </ErrorBoundary>
                } />
                <Route path="/activity" element={
                  <ErrorBoundary>
                    <MainActivityFeed />
                  </ErrorBoundary>
                } />
                <Route path="/settings" element={
                  <ErrorBoundary>
                    <SettingsPage />
                  </ErrorBoundary>
                } />
              </Routes>
            </Box>
          </Flex>
        </Box>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
