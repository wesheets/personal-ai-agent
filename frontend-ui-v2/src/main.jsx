import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import App from './App.jsx';
import theme from './theme';
import './index.css';

// Simple wrapper to ensure React mounts properly
const AppWrapper = () => {
  return (
    <React.StrictMode>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <ChakraProvider theme={theme}>
        <App />
      </ChakraProvider>
    </React.StrictMode>
  );
};

// Mount the application with error handling
try {
  const rootElement = document.getElementById('root');
  if (rootElement) {
    ReactDOM.createRoot(rootElement).render(<AppWrapper />);
    console.log('React application successfully mounted');
  } else {
    console.error('Root element not found in the DOM');
  }
} catch (error) {
  console.error('Error mounting React application:', error);
}
