import React from 'react';
import { 
  Box, 
  Grid, 
  GridItem, 
  Heading, 
  Text, 
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Flex
} from '@chakra-ui/react';
import ErrorBoundary from './ErrorBoundary';
import { LoadingCard } from './LoadingStates';
import AgentPanel from './AgentPanel';
import GoalLoopVisualization from './GoalLoopVisualization';
import InterruptControl from './InterruptControl';
import MemoryViewer from './MemoryViewer';

/**
 * DashboardLayout component
 * 
 * Main layout for the dashboard that integrates all UI components
 * with proper error boundaries and consistent styling
 */
const DashboardLayout = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  return (
    <Box bg={bgColor} minH="100vh" p={4}>
      <Heading as="h1" size="xl" mb={6}>Promethios Control Dashboard</Heading>
      
      <Grid 
        templateColumns={{ base: "1fr", lg: "repeat(2, 1fr)" }}
        templateRows={{ base: "auto", lg: "auto" }}
        gap={6}
      >
        {/* Agent Panel */}
        <GridItem colSpan={1} rowSpan={1}>
          <Box 
            p={4} 
            borderRadius="lg" 
            bg={cardBgColor} 
            borderWidth="1px"
            borderColor={borderColor}
            shadow="sm"
            height="100%"
          >
            <ErrorBoundary
              fallback={(error) => (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Agent Panel Error</AlertTitle>
                    <AlertDescription>
                      Failed to load agent panel: {error.message}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            >
              <AgentPanel />
            </ErrorBoundary>
          </Box>
        </GridItem>
        
        {/* Interrupt Control */}
        <GridItem colSpan={1} rowSpan={1}>
          <Box 
            p={4} 
            borderRadius="lg" 
            bg={cardBgColor} 
            borderWidth="1px"
            borderColor={borderColor}
            shadow="sm"
            height="100%"
          >
            <ErrorBoundary
              fallback={(error) => (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Interrupt Control Error</AlertTitle>
                    <AlertDescription>
                      Failed to load interrupt control: {error.message}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            >
              <InterruptControl />
            </ErrorBoundary>
          </Box>
        </GridItem>
        
        {/* Goal Loop Visualization */}
        <GridItem colSpan={{ base: 1, lg: 2 }} rowSpan={1}>
          <Box 
            p={4} 
            borderRadius="lg" 
            bg={cardBgColor} 
            borderWidth="1px"
            borderColor={borderColor}
            shadow="sm"
          >
            <ErrorBoundary
              fallback={(error) => (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Goal Loop Visualization Error</AlertTitle>
                    <AlertDescription>
                      Failed to load goal loop visualization: {error.message}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            >
              <GoalLoopVisualization />
            </ErrorBoundary>
          </Box>
        </GridItem>
        
        {/* Memory Viewer */}
        <GridItem colSpan={{ base: 1, lg: 2 }} rowSpan={1}>
          <Box 
            p={4} 
            borderRadius="lg" 
            bg={cardBgColor} 
            borderWidth="1px"
            borderColor={borderColor}
            shadow="sm"
          >
            <ErrorBoundary
              fallback={(error) => (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Memory Viewer Error</AlertTitle>
                    <AlertDescription>
                      Failed to load memory viewer: {error.message}
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            >
              <MemoryViewer />
            </ErrorBoundary>
          </Box>
        </GridItem>
      </Grid>
      
      <Flex justify="center" mt={8} mb={4}>
        <Text fontSize="sm" color="gray.500">
          Promethios Control Dashboard v1.0.2 • {new Date().getFullYear()}
        </Text>
      </Flex>
    </Box>
  );
};

export default DashboardLayout;
