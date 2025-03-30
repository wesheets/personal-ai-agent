import React from 'react';
import { ChakraProvider, Box, VStack, Heading, Text } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <ChakraProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
