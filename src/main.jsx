import React from 'react';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { BrowserRouter as Router } from 'react-router-dom';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext';
import theme from './theme';
import './index.css';

// SSR-compatible rendering
function renderApp() {
  // Only run client-side code in browser environment
  if (typeof window !== 'undefined') {
    const ReactDOM = require('react-dom/client');
    const rootElement = document.getElementById('root');
    
    if (rootElement) {
      ReactDOM.createRoot(rootElement).render(
        <React.StrictMode>
          <ColorModeScript initialColorMode={theme.config.initialColorMode} />
          <ChakraProvider theme={theme}>
            <Router>
              <AuthProvider>
                <App />
              </AuthProvider>
            </Router>
          </ChakraProvider>
        </React.StrictMode>
      );
    }
  }
}

renderApp();
