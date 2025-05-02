import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  Text,
  Heading,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Divider,
  useToast
} from '@chakra-ui/react';
import useFetch from '../hooks/useFetch';
import { LoadingSpinner } from './LoadingStates';
import ErrorBoundary from './ErrorBoundary';

/**
 * IntegrationTester component
 * 
 * Tests all API integrations and reports their status
 */
const IntegrationTester = () => {
  const toast = useToast();
  const [testResults, setTestResults] = useState({});
  const [isRunningTests, setIsRunningTests] = useState(false);
  
  // Define the endpoints to test
  const endpoints = [
    { name: 'Agent List', url: '/api/agent/list', method: 'GET' },
    { name: 'System Status', url: '/api/system/status', method: 'GET' },
    { name: 'Memory Read', url: '/api/memory/read', method: 'GET' },
    { name: 'Loop Plan', url: '/api/loop/plan', method: 'GET' }
  ];
  
  // Function to test a single endpoint
  const testEndpoint = async (endpoint) => {
    try {
      const response = await fetch(endpoint.url, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      return {
        success: response.ok,
        status: response.status,
        statusText: response.statusText,
        data: data,
        error: null
      };
    } catch (error) {
      return {
        success: false,
        status: 'Error',
        statusText: error.message,
        data: null,
        error: error.message
      };
    }
  };
  
  // Function to run all tests
  const runAllTests = async () => {
    setIsRunningTests(true);
    const results = {};
    
    for (const endpoint of endpoints) {
      setTestResults(prev => ({
        ...prev,
        [endpoint.name]: { status: 'Testing...', success: null }
      }));
      
      const result = await testEndpoint(endpoint);
      
      results[endpoint.name] = result;
      
      setTestResults(prev => ({
        ...prev,
        [endpoint.name]: result
      }));
      
      // Show toast for each test result
      toast({
        title: `${endpoint.name} Test ${result.success ? 'Passed' : 'Failed'}`,
        description: result.success 
          ? `Successfully connected to ${endpoint.url}`
          : `Failed to connect to ${endpoint.url}: ${result.error || result.statusText}`,
        status: result.success ? 'success' : 'error',
        duration: 5000,
        isClosable: true,
      });
      
      // Add a small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setIsRunningTests(false);
  };
  
  return (
    <Box>
      <Heading size="md" mb={4}>Integration Test Dashboard</Heading>
      
      <Button 
        colorScheme="blue" 
        onClick={runAllTests} 
        isLoading={isRunningTests}
        loadingText="Running Tests"
        mb={6}
      >
        Run All Tests
      </Button>
      
      <VStack spacing={4} align="stretch">
        {endpoints.map(endpoint => (
          <Box 
            key={endpoint.name}
            p={4}
            borderWidth="1px"
            borderRadius="md"
            borderColor={
              testResults[endpoint.name]?.success === true ? 'green.300' :
              testResults[endpoint.name]?.success === false ? 'red.300' :
              'gray.200'
            }
          >
            <Heading size="sm" mb={2}>{endpoint.name}</Heading>
            <Text fontSize="sm" mb={2}>
              <strong>Endpoint:</strong> {endpoint.url} ({endpoint.method})
            </Text>
            
            {testResults[endpoint.name] ? (
              <>
                <Text fontSize="sm" mb={2}>
                  <strong>Status:</strong> {
                    testResults[endpoint.name].success === true ? 'Success' :
                    testResults[endpoint.name].success === false ? 'Failed' :
                    'Testing...'
                  }
                </Text>
                
                {testResults[endpoint.name].status && (
                  <Text fontSize="sm" mb={2}>
                    <strong>Response:</strong> {testResults[endpoint.name].status} {testResults[endpoint.name].statusText}
                  </Text>
                )}
                
                {testResults[endpoint.name].error && (
                  <Alert status="error" mt={2} mb={2} size="sm">
                    <AlertIcon />
                    {testResults[endpoint.name].error}
                  </Alert>
                )}
                
                {testResults[endpoint.name].data && (
                  <Box mt={2}>
                    <Divider mb={2} />
                    <Text fontSize="sm" mb={1}><strong>Response Data:</strong></Text>
                    <Code 
                      p={2} 
                      borderRadius="md" 
                      fontSize="xs"
                      whiteSpace="pre-wrap"
                      overflowX="auto"
                      display="block"
                      maxHeight="200px"
                      overflowY="auto"
                    >
                      {JSON.stringify(testResults[endpoint.name].data, null, 2)}
                    </Code>
                  </Box>
                )}
              </>
            ) : (
              <Text fontSize="sm" color="gray.500">Not tested yet</Text>
            )}
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

/**
 * TestPage component
 * 
 * Wrapper component with error boundary for the integration tester
 */
const TestPage = () => (
  <Box p={6} maxW="1200px" mx="auto">
    <Heading mb={6}>UI Integration Tests</Heading>
    
    <ErrorBoundary>
      <IntegrationTester />
    </ErrorBoundary>
  </Box>
);

export default TestPage;
