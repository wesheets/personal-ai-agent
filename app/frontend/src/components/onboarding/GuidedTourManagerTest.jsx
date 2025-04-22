import React, { useState } from 'react';
import { Box, Button, Flex, Heading, Text, VStack, useColorModeValue } from '@chakra-ui/react';
import GuidedTourManager from './GuidedTourManager';

/**
 * Test component for GuidedTourManager
 * This component demonstrates how to use the GuidedTourManager component
 */
const GuidedTourManagerTest = () => {
  const [activeTour, setActiveTour] = useState(null);
  const [showControls, setShowControls] = useState(true);
  const [autoStart, setAutoStart] = useState(false);
  
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleComplete = () => {
    console.log('Tour completed');
    setActiveTour(null);
  };
  
  const handleSkip = () => {
    console.log('Tour skipped');
    setActiveTour(null);
  };
  
  return (
    <Box p={4}>
      <Heading size="md" mb={4}>GuidedTourManager Test</Heading>
      
      <Text mb={4}>
        Select a tour to start and configure its behavior.
      </Text>
      
      <Flex gap={4} mb={6} flexWrap="wrap">
        <Button 
          colorScheme="blue" 
          onClick={() => {
            setActiveTour('main');
            setAutoStart(true);
          }}
        >
          Start Main Tour
        </Button>
        
        <Button 
          colorScheme="green" 
          onClick={() => {
            setActiveTour('newUser');
            setAutoStart(true);
          }}
        >
          Start New User Tour
        </Button>
        
        <Button 
          colorScheme="purple" 
          onClick={() => {
            setActiveTour('advancedFeatures');
            setAutoStart(true);
          }}
        >
          Start Advanced Features Tour
        </Button>
      </Flex>
      
      <Box 
        p={4} 
        bg={bgColor} 
        borderRadius="md" 
        borderWidth="1px" 
        borderColor={borderColor}
        mb={6}
      >
        <Heading size="sm" mb={3}>Tour Configuration</Heading>
        <VStack align="start" spacing={3}>
          <Button 
            size="sm" 
            colorScheme={showControls ? "green" : "red"} 
            onClick={() => setShowControls(!showControls)}
          >
            {showControls ? "Hide Controls" : "Show Controls"}
          </Button>
          
          <Button 
            size="sm" 
            colorScheme="red" 
            onClick={() => setActiveTour(null)}
            isDisabled={!activeTour}
          >
            Stop Active Tour
          </Button>
        </VStack>
      </Box>
      
      {/* Mock UI elements for tour targets */}
      <Box 
        p={4} 
        bg={bgColor} 
        borderRadius="md" 
        borderWidth="1px" 
        borderColor={borderColor}
      >
        <Heading size="sm" mb={3}>Mock UI Elements (Tour Targets)</Heading>
        <Flex gap={4} flexWrap="wrap">
          <Box id="OperatorHUDBar" p={3} bg="blue.100" borderRadius="md" width="200px">
            OperatorHUDBar
          </Box>
          
          <Box id="ProjectContextSwitcher" p={3} bg="green.100" borderRadius="md" width="200px">
            ProjectContextSwitcher
          </Box>
          
          <Box id="OrchestratorModePanel" p={3} bg="purple.100" borderRadius="md" width="200px">
            OrchestratorModePanel
          </Box>
          
          <Box id="AgentPanel" p={3} bg="yellow.100" borderRadius="md" width="200px">
            AgentPanel
          </Box>
          
          <Box id="AgentChatConsole" p={3} bg="red.100" borderRadius="md" width="200px">
            AgentChatConsole
          </Box>
          
          <Box id="GoalLoopVisualization" p={3} bg="teal.100" borderRadius="md" width="200px">
            GoalLoopVisualization
          </Box>
          
          <Box id="MemoryViewer" p={3} bg="orange.100" borderRadius="md" width="200px">
            MemoryViewer
          </Box>
          
          <Box id="RightPanelContainer" p={3} bg="cyan.100" borderRadius="md" width="200px">
            RightPanelContainer
          </Box>
        </Flex>
      </Box>
      
      {/* Render the GuidedTourManager if a tour is active */}
      {activeTour && (
        <GuidedTourManager
          tourId={activeTour}
          autoStart={autoStart}
          onComplete={handleComplete}
          onSkip={handleSkip}
          showControls={showControls}
        />
      )}
    </Box>
  );
};

export default GuidedTourManagerTest;
