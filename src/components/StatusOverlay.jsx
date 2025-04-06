import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  Badge,
  useColorMode,
  Fade,
  HStack,
  Icon,
  Tooltip
} from '@chakra-ui/react';
import { FiCheckCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';
import DEBUG_MODE from '../config/debug';

/**
 * StatusOverlay Component
 * 
 * A toast-like component that displays API status information
 * Helps debug connection issues and request cancellations
 */
const StatusOverlay = () => {
  const { colorMode } = useColorMode();
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');
  const [visible, setVisible] = useState(false);
  
  // Monitor fetch requests to detect cancellations
  useEffect(() => {
    if (!DEBUG_MODE) return; // Only run in debug mode
    
    const originalFetch = window.fetch;
    let activeRequests = 0;
    
    // Override fetch to track requests
    window.fetch = function(...args) {
      activeRequests++;
      console.debug(`📡 API Request started (${activeRequests} active)`);
      
      // Show stable status after successful requests
      setStatus('pending');
      setMessage(`API Request in progress (${activeRequests} active)`);
      setVisible(true);
      
      return originalFetch.apply(this, args)
        .then(response => {
          activeRequests = Math.max(0, activeRequests - 1);
          
          if (response.ok) {
            setStatus('success');
            setMessage(`📡 API Stable – ${response.status} ${response.statusText}`);
          } else {
            setStatus('error');
            setMessage(`API Error: ${response.status} ${response.statusText}`);
          }
          
          // Auto-hide success messages after 3 seconds
          if (response.ok) {
            setTimeout(() => {
              setVisible(false);
            }, 3000);
          }
          
          return response;
        })
        .catch(error => {
          activeRequests = Math.max(0, activeRequests - 1);
          
          if (error.name === 'AbortError') {
            setStatus('warning');
            setMessage('⚠️ Request canceled – poll loop likely active');
            console.warn('⚠️ Request canceled – poll loop likely active', error);
          } else {
            setStatus('error');
            setMessage(`API Error: ${error.message}`);
            console.error('API Error:', error);
          }
          
          throw error;
        });
    };
    
    return () => {
      // Restore original fetch when component unmounts
      window.fetch = originalFetch;
    };
  }, []);
  
  // Don't render anything if not visible or not in debug mode
  if (!visible || !DEBUG_MODE) return null;
  
  // Determine styling based on status
  const getBgColor = () => {
    switch (status) {
      case 'success':
        return colorMode === 'light' ? 'green.50' : 'green.900';
      case 'error':
        return colorMode === 'light' ? 'red.50' : 'red.900';
      case 'warning':
        return colorMode === 'light' ? 'yellow.50' : 'yellow.900';
      default:
        return colorMode === 'light' ? 'blue.50' : 'blue.900';
    }
  };
  
  const getBorderColor = () => {
    switch (status) {
      case 'success':
        return colorMode === 'light' ? 'green.200' : 'green.700';
      case 'error':
        return colorMode === 'light' ? 'red.200' : 'red.700';
      case 'warning':
        return colorMode === 'light' ? 'yellow.200' : 'yellow.700';
      default:
        return colorMode === 'light' ? 'blue.200' : 'blue.700';
    }
  };
  
  const getIcon = () => {
    switch (status) {
      case 'success':
        return FiCheckCircle;
      case 'error':
      case 'warning':
        return FiAlertTriangle;
      default:
        return FiInfo;
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case 'success':
        return 'Success';
      case 'error':
        return 'Error';
      case 'warning':
        return 'Warning';
      case 'pending':
        return 'Pending';
      default:
        return 'Info';
    }
  };
  
  return (
    <Fade in={visible}>
      <Box
        position="fixed"
        bottom="20px"
        right="20px"
        zIndex={9999}
        p={3}
        borderRadius="md"
        bg={getBgColor()}
        borderWidth="1px"
        borderColor={getBorderColor()}
        boxShadow="md"
        maxW="400px"
      >
        <HStack spacing={2} align="center">
          <Icon as={getIcon()} />
          <Badge colorScheme={
            status === 'success' ? 'green' :
            status === 'error' ? 'red' :
            status === 'warning' ? 'yellow' : 'blue'
          }>
            {getStatusText()}
          </Badge>
          <Text fontSize="sm">{message}</Text>
        </HStack>
      </Box>
    </Fade>
  );
};

export default StatusOverlay;
