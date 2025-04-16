import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider, Flex } from '@chakra-ui/react';
import Dashboard from './pages/Dashboard';
import TestPage from './pages/TestPage';

const App: React.FC = () => {
  return (
    <ChakraProvider>
      <Router>
        <Flex minHeight="100vh">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Flex>
      </Router>
    </ChakraProvider>
  );
};

export default App;
