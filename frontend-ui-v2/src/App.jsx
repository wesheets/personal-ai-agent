import React from 'react';
import { Box, Flex, useColorMode, Text, Center } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import AgentChat from './components/AgentChat';
import AuthenticatedLayout from './components/AuthenticatedLayout';
import { useAuth } from './hooks/useAuth';

// Placeholder components for sidebar menu items
const Dashboard = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Dashboard - Coming Soon</Text>
  </Center>
);

const BuilderAgent = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Builder Agent - Coming Soon</Text>
  </Center>
);

const OpsAgent = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Ops Agent - Coming Soon</Text>
  </Center>
);

const ResearchAgent = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Research Agent - Coming Soon</Text>
  </Center>
);

const MemoryAgent = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Memory Agent - Coming Soon</Text>
  </Center>
);

const MemoryBrowser = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Memory Browser - Coming Soon</Text>
  </Center>
);

const ActivityFeed = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Activity Feed - Coming Soon</Text>
  </Center>
);

const AgentActivity = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Agent Activity - Coming Soon</Text>
  </Center>
);

const Settings = () => (
  <Center h="calc(100vh - 80px)" p={8}>
    <Text fontSize="2xl">Settings - Coming Soon</Text>
  </Center>
);

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated()) {
    return <Navigate to="/auth" />;
  }
  
  return (
    <AuthenticatedLayout>
      {children}
    </AuthenticatedLayout>
  );
};

function App() {
  const { colorMode } = useColorMode();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Routes>
        {/* Auth route */}
        <Route path="/auth" element={<LoginPage />} />
        
        {/* Protected routes - all wrapped with AuthenticatedLayout */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/builder" element={<ProtectedRoute><BuilderAgent /></ProtectedRoute>} />
        <Route path="/ops" element={<ProtectedRoute><OpsAgent /></ProtectedRoute>} />
        <Route path="/research" element={<ProtectedRoute><ResearchAgent /></ProtectedRoute>} />
        <Route path="/memory-agent" element={<ProtectedRoute><MemoryAgent /></ProtectedRoute>} />
        <Route path="/memory-browser" element={<ProtectedRoute><MemoryBrowser /></ProtectedRoute>} />
        <Route path="/activity-feed" element={<ProtectedRoute><ActivityFeed /></ProtectedRoute>} />
        <Route path="/agent-activity" element={<ProtectedRoute><AgentActivity /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        
        {/* HAL Agent Chat - default interface after authentication */}
        <Route path="/hal" element={<ProtectedRoute><AgentChat /></ProtectedRoute>} />
        
        {/* Root path redirect to dashboard if authenticated, otherwise to auth */}
        <Route 
          path="/" 
          element={
            <Navigate to="/hal" />
          } 
        />
        
        {/* Fallback for unknown routes */}
        <Route 
          path="*" 
          element={<Navigate to="/hal" />} 
        />
      </Routes>
    </Box>
  );
}

// Wrapped App with providers
const AppWithProviders = () => {
  return (
    <AuthProvider>
      <Router>
        <App />
      </Router>
    </AuthProvider>
  );
};

export default AppWithProviders;
