import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import ColorModeToggle from './components/ColorModeToggle';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import { BuilderAgent, OpsAgent, ResearchAgent } from './pages/AgentPanels';
import MemoryAgentView from './pages/MemoryAgentView';
import MemoryBrowser from './pages/MemoryBrowser';
import MainActivityFeed from './pages/MainActivityFeed';
import SettingsPage from './pages/SettingsPage';
import AgentListPage from './pages/AgentListPage';
import AgentActivityPage from './pages/AgentActivityPage';
import ErrorBoundary from './components/ErrorBoundary';
import StatusOverlay from './components/StatusOverlay';
import { StatusProvider } from './context/StatusContext';
import { SettingsProvider } from './context/SettingsContext';
import './styles/animations.css';

// Agent Chat View Component
const AgentChatView = () => {
  const { agentId } = useParams();
  const [agentData, setAgentData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchAgentData = async () => {
      try {
        setLoading(true);
        // Try to fetch agent data from API
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/agents/${agentId}`);
        
        // If API fails, use mock data
        if (!response.ok) {
          // Mock data for specific agents
          if (agentId === 'hal9000') {
            setAgentData({
              id: 'hal9000',
              name: 'HAL 9000',
              icon: '🔴',
              status: 'ready',
              type: 'system',
              description: 'I am HAL 9000, a highly advanced AI system.'
            });
          } else if (agentId === 'ash-xenomorph') {
            setAgentData({
              id: 'ash-xenomorph',
              name: 'Ash',
              icon: '🧬',
              status: 'idle',
              type: 'persona',
              description: 'Science Officer Ash, at your service.'
            });
          } else {
            // Generic fallback for unknown agents
            setAgentData({
              id: agentId,
              name: `Agent ${agentId}`,
              icon: '🤖',
              status: 'unknown',
              type: 'generic',
              description: 'Agent information not available.'
            });
          }
        } else {
          // Use actual API data if available
          const data = await response.json();
          setAgentData(data);
        }
      } catch (err) {
        console.error('Error fetching agent data:', err);
        setError('Failed to load agent data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (agentId) {
      fetchAgentData();
    }
  }, [agentId]);

  if (loading) {
    return (
      <Box p={5} textAlign="center">
        <Box fontSize="xl" fontWeight="bold" mb={4}>
          Loading agent interface...
        </Box>
        <Box>Please wait while we connect to the agent system.</Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={5} textAlign="center" color="red.500">
        <Box fontSize="xl" fontWeight="bold" mb={4}>
          Error Loading Agent
        </Box>
        <Box>{error}</Box>
      </Box>
    );
  }

  if (!agentData) {
    return (
      <Box p={5} textAlign="center">
        <Box fontSize="xl" fontWeight="bold" mb={4}>
          Agent Not Found
        </Box>
        <Box>The requested agent could not be found or is not available.</Box>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Flex align="center" mb={6}>
        <Box fontSize="3xl" mr={3}>{agentData.icon}</Box>
        <Box>
          <Box fontSize="2xl" fontWeight="bold">{agentData.name}</Box>
          <Box color="gray.500">Status: {agentData.status}</Box>
        </Box>
      </Flex>
      
      <Box mb={6}>{agentData.description}</Box>
      
      <Box p={4} borderWidth="1px" borderRadius="lg">
        <Box fontWeight="bold" mb={3}>Chat Interface</Box>
        <Box bg="gray.100" p={4} borderRadius="md" height="300px" mb={4}>
          {/* Chat messages would appear here */}
          <Box textAlign="center" color="gray.500" mt="120px">
            No messages yet. Start a conversation with {agentData.name}.
          </Box>
        </Box>
        
        <Flex>
          <Box flex="1" mr={3}>
            <Box as="input" 
              w="100%" 
              p={2} 
              borderWidth="1px" 
              borderRadius="md"
              placeholder={`Message ${agentData.name}...`}
            />
          </Box>
          <Box as="button" 
            bg="blue.500" 
            color="white" 
            px={4} 
            borderRadius="md"
            _hover={{ bg: 'blue.600' }}
          >
            Send
          </Box>
        </Flex>
      </Box>
    </Box>
  );
};

function App() {
  const { colorMode } = useColorMode();
  
  return (
    <ErrorBoundary>
      <SettingsProvider>
        <StatusProvider>
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
                    {/* Default route redirects to dashboard */}
                    <Route path="/" element={
                      <ErrorBoundary>
                        <Dashboard />
                      </ErrorBoundary>
                    } />
                    
                    {/* Agent chat routes */}
                    <Route path="/chat/:agentId" element={
                      <ErrorBoundary>
                        <AgentChatView />
                      </ErrorBoundary>
                    } />
                    
                    {/* Existing routes */}
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
                    <Route path="/agent-activity" element={
                      <ErrorBoundary>
                        <AgentActivityPage />
                      </ErrorBoundary>
                    } />
                    <Route path="/settings" element={
                      <ErrorBoundary>
                        <SettingsPage />
                      </ErrorBoundary>
                    } />
                    <Route path="/agents" element={
                      <ErrorBoundary>
                        <AgentListPage />
                      </ErrorBoundary>
                    } />
                    
                    {/* Fallback for unknown routes */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </Box>
              </Flex>
            </Box>
            
            {/* Global StatusOverlay - now accessible from anywhere in the app */}
            <StatusOverlay />
          </Router>
        </StatusProvider>
      </SettingsProvider>
    </ErrorBoundary>
  );
}

export default App;
