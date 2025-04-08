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

// Import HAL UI and Auth components
import AgentChat from './components/AgentChat';
import LoginPage from './pages/LoginPage';
import { isAuthenticated, logout } from './hooks/useAuth';

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
        <Box fontSize="3xl" mr={3}>
          {agentData.icon}
        </Box>
        <Box>
          <Box fontSize="2xl" fontWeight="bold">
            {agentData.name}
          </Box>
          <Box color="gray.500">Status: {agentData.status}</Box>
        </Box>
      </Flex>

      <Box mb={6}>{agentData.description}</Box>

      <Box p={4} borderWidth="1px" borderRadius="lg">
        <Box fontWeight="bold" mb={3}>
          Chat Interface
        </Box>
        <Box bg="gray.100" p={4} borderRadius="md" height="300px" mb={4}>
          {/* Chat messages would appear here */}
          <Box textAlign="center" color="gray.500" mt="120px">
            No messages yet. Start a conversation with {agentData.name}.
          </Box>
        </Box>

        <Flex>
          <Box flex="1" mr={3}>
            <Box
              as="input"
              w="100%"
              p={2}
              borderWidth="1px"
              borderRadius="md"
              placeholder={`Message ${agentData.name}...`}
            />
          </Box>
          <Box
            as="button"
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

// Layout component for authenticated routes
const AuthenticatedLayout = ({ children }) => {
  const { colorMode } = useColorMode();
  const navigate = React.useCallback(() => {
    // This is a simplified version - in a real app, you'd use useNavigate from react-router-dom
    window.location.href = '/auth';
  }, []);

  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Flex direction="column" h="100vh">
        {/* Top navigation area with color mode toggle and logout */}
        <Flex
          as="header"
          position="fixed"
          w="full"
          zIndex="1000"
          bg={colorMode === 'light' ? 'white' : 'gray.800'}
          boxShadow="sm"
          justifyContent="space-between"
          p={2}
        >
          <Box></Box> {/* Empty box for spacing */}
          <Flex>
            <Box
              as="button"
              mr={4}
              px={3}
              py={1}
              borderRadius="md"
              bg="red.500"
              color="white"
              _hover={{ bg: 'red.600' }}
              onClick={() => {
                logout();
                navigate();
              }}
            >
              Logout
            </Box>
            <ColorModeToggle />
          </Flex>
        </Flex>

        {/* Sidebar navigation */}
        <Sidebar />

        {/* Main content area */}
        <Box ml={{ base: 0, md: '60' }} p="4" pt="20">
          {children}
        </Box>
      </Flex>
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
              <Routes>
                {/* Auth route */}
                <Route path="/auth" element={<LoginPage />} />

                {/* Root path redirect based on auth status */}
                <Route
                  path="/"
                  element={isAuthenticated() ? <Navigate to="/hal" /> : <Navigate to="/auth" />}
                />

                {/* HAL Agent Chat - default interface after authentication */}
                <Route
                  path="/hal"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <AgentChat />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />

                {/* Default route redirects to dashboard */}
                <Route
                  path="/dashboard"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <Dashboard />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />

                {/* Agent chat routes */}
                <Route
                  path="/chat/:agentId"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <AgentChatView />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />

                {/* Existing routes with authentication */}
                <Route
                  path="/builder"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <BuilderAgent />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/ops"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <OpsAgent />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/research"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <ResearchAgent />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/memory"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <MemoryAgentView />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/memory-browser"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <MemoryBrowser />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/activity"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <MainActivityFeed />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/agent-activity"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <AgentActivityPage />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/settings"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <SettingsPage />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />
                <Route
                  path="/agents"
                  element={
                    isAuthenticated() ? (
                      <AuthenticatedLayout>
                        <ErrorBoundary>
                          <AgentListPage />
                        </ErrorBoundary>
                      </AuthenticatedLayout>
                    ) : (
                      <Navigate to="/auth" />
                    )
                  }
                />

                {/* Fallback for unknown routes */}
                <Route
                  path="*"
                  element={isAuthenticated() ? <Navigate to="/hal" /> : <Navigate to="/auth" />}
                />
              </Routes>
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
