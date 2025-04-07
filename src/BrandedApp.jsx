import React from 'react';
import { ChakraProvider, CSSReset } from '@chakra-ui/react';
import { BrowserRouter as Router } from 'react-router-dom';
import brandTheme from './theme/brandTheme';
import { AuthProvider } from './context/AuthContext';
import App from './App';

const PrometheiosProvider = ({ children }) => {
  return (
    <ChakraProvider theme={brandTheme}>
      <CSSReset />
      <AuthProvider>
        <Router>
          {children}
        </Router>
      </AuthProvider>
    </ChakraProvider>
  );
};

const BrandedApp = () => {
  return (
    <PrometheiosProvider>
      <App />
    </PrometheiosProvider>
  );
};

export default BrandedApp;
