import React, { useState } from 'react';
import { Box, Button, Flex, Heading, Text } from '@chakra-ui/react';
import OnboardingPane from './OnboardingPane';

/**
 * Test component for OnboardingPane
 * This component demonstrates how to use the OnboardingPane component
 */
const OnboardingPaneTest = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [initialTab, setInitialTab] = useState('about');
  
  const openPane = (tab = 'about') => {
    setInitialTab(tab);
    setIsOpen(true);
  };
  
  return (
    <Box p={4}>
      <Heading size="md" mb={4}>OnboardingPane Test</Heading>
      
      <Text mb={4}>
        Click the buttons below to open the OnboardingPane with different initial tabs.
      </Text>
      
      <Flex gap={4} mb={6}>
        <Button colorScheme="blue" onClick={() => openPane('about')}>
          What is Promethios?
        </Button>
        
        <Button colorScheme="green" onClick={() => openPane('loops')}>
          What is a loop?
        </Button>
        
        <Button colorScheme="purple" onClick={() => openPane('agents')}>
          How to talk to agents?
        </Button>
      </Flex>
      
      <OnboardingPane 
        isOpen={isOpen} 
        onClose={() => setIsOpen(false)} 
        initialTab={initialTab} 
      />
    </Box>
  );
};

export default OnboardingPaneTest;
