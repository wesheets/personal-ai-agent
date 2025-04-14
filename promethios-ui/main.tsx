import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import './index.css';
import App from './App';
import { AuthProvider } from './context/AuthContext';

// Get the container element
const container = document.getElementById('root');

// Create a root
const root = createRoot(container!);

// Render the app with all required providers
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ChakraProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ChakraProvider>
    </BrowserRouter>
  </React.StrictMode>
);
