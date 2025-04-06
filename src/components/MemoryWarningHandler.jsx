import React, { useEffect } from 'react';
import { useToast, Box, Alert, AlertIcon, AlertTitle, AlertDescription, CloseButton } from '@chakra-ui/react';

/**
 * MemoryWarningHandler Component
 * 
 * This component handles warnings from the memory API and displays them as toasts
 * or alerts to the user. It can be included in any component that makes memory API calls.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.apiResponse - The API response object that might contain warnings
 * @param {boolean} props.showAlert - Whether to show an alert in addition to a toast
 * @param {function} props.onClose - Callback when alert is closed
 */
const MemoryWarningHandler = ({ apiResponse, showAlert = false, onClose = () => {} }) => {
  const toast = useToast();
  
  useEffect(() => {
    // Check if the API response contains a warning
    if (apiResponse?.metadata?.warning) {
      const warning = apiResponse.metadata.warning;
      
      // Show toast notification
      toast({
        title: 'Memory System Warning',
        description: warning,
        status: 'warning',
        duration: 8000,
        isClosable: true,
        position: 'top-right',
      });
      
      // Log the warning to console
      console.warn(`[Memory Warning] ${warning}`);
    }
  }, [apiResponse, toast]);
  
  // If showAlert is true and there's a warning, show an alert box
  if (showAlert && apiResponse?.metadata?.warning) {
    return (
      <Box my={4}>
        <Alert status="warning" variant="left-accent">
          <AlertIcon />
          <Box flex="1">
            <AlertTitle>Memory System Warning</AlertTitle>
            <AlertDescription display="block">
              {apiResponse.metadata.warning}
              <br />
              <Box as="span" fontSize="sm" mt={1}>
                The system is operating in degraded mode. Some memory features may be limited.
              </Box>
            </AlertDescription>
          </Box>
          <CloseButton position="absolute" right="8px" top="8px" onClick={onClose} />
        </Alert>
      </Box>
    );
  }
  
  // If no warning or showAlert is false, render nothing
  return null;
};

export default MemoryWarningHandler;
