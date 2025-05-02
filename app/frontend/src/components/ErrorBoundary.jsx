import React, { Component } from 'react';
import { 
  Box, 
  Alert, 
  AlertIcon, 
  AlertTitle, 
  AlertDescription, 
  Button,
  Code,
  VStack,
  Collapse,
  useDisclosure
} from '@chakra-ui/react';

/**
 * ErrorDetails component to show/hide detailed error information
 */
const ErrorDetails = ({ error, componentStack }) => {
  const { isOpen, onToggle } = useDisclosure();
  
  return (
    <VStack align="stretch" mt={4}>
      <Button size="sm" onClick={onToggle} colorScheme="blue" variant="outline">
        {isOpen ? 'Hide Details' : 'Show Details'}
      </Button>
      
      <Collapse in={isOpen} animateOpacity>
        <Box 
          mt={2} 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          bg="gray.50" 
          _dark={{ bg: 'gray.800' }}
          overflowX="auto"
        >
          <VStack align="stretch" spacing={3}>
            {error && (
              <Box>
                <strong>Error:</strong>
                <Code display="block" whiteSpace="pre-wrap" p={2} mt={1}>
                  {error.toString()}
                </Code>
              </Box>
            )}
            
            {componentStack && (
              <Box>
                <strong>Component Stack:</strong>
                <Code display="block" whiteSpace="pre-wrap" p={2} mt={1}>
                  {componentStack}
                </Code>
              </Box>
            )}
          </VStack>
        </Box>
      </Collapse>
    </VStack>
  );
};

/**
 * ErrorBoundary component to catch JavaScript errors in child components
 * and display a fallback UI instead of crashing the whole application
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
    
    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }
  
  handleReset = () => {
    this.setState({ 
      hasError: false,
      error: null,
      errorInfo: null
    });
    
    // Call onReset callback if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  }

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { fallback, children } = this.props;
    
    if (hasError) {
      // If a custom fallback is provided, use it
      if (fallback) {
        return typeof fallback === 'function' 
          ? fallback(error, errorInfo, this.handleReset)
          : fallback;
      }
      
      // Otherwise, use the default fallback UI
      return (
        <Box 
          p={4} 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor="red.300"
          bg="red.50"
          _dark={{ bg: 'red.900', borderColor: 'red.700' }}
        >
          <Alert 
            status="error" 
            variant="subtle" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            textAlign="center" 
            borderRadius="md"
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Component Error
            </AlertTitle>
            <AlertDescription maxWidth="sm">
              An error occurred while rendering this component.
            </AlertDescription>
          </Alert>
          
          <ErrorDetails 
            error={error} 
            componentStack={errorInfo?.componentStack} 
          />
          
          <Button 
            mt={4} 
            colorScheme="red" 
            onClick={this.handleReset}
            size="sm"
          >
            Try Again
          </Button>
        </Box>
      );
    }

    // If there's no error, render children normally
    return children;
  }
}

export default ErrorBoundary;
