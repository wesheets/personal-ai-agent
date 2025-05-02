import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useDisclosure,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiEdit } from 'react-icons/fi';
import LoopRevisionLog from './revision/LoopRevisionLog';
import ReflectionRetractionPanel, { ReflectionRetractionTrigger } from './revision/ReflectionRetractionPanel';
import { useReplanTrigger } from '../logic/ReplanTrigger';

/**
 * RevisionDashboard Component
 * 
 * Integrates the loop revision and reflection retraction components
 * into a unified dashboard interface.
 */
const RevisionDashboard = () => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // State for selected reflection
  const [selectedReflection, setSelectedReflection] = useState(null);
  
  // Modal controls
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Replan trigger hook
  const {
    isReplanning,
    status: replanStatus,
    message: replanMessage,
    triggerReplan,
  } = useReplanTrigger({
    onComplete: (result) => {
      console.log('Replan completed:', result);
      // In a real implementation, this would update the UI or trigger a refresh
    },
  });
  
  // Handle retraction
  const handleRetract = async (retractionData) => {
    // In a real implementation, this would call an API
    console.log('Retracting reflection:', retractionData);
    
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000);
    });
  };
  
  // Handle replan
  const handleReplan = async (retractionData) => {
    // Use the replan trigger hook
    return triggerReplan({
      revised_from_loop_id: retractionData.loop_id,
      agent: retractionData.agent,
      reason: retractionData.reason,
      revised_reflection: retractionData.revised_reflection,
      project_id: 'life_tree', // In a real implementation, this would be dynamic
    });
  };
  
  return (
    <Box
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      boxShadow="sm"
    >
      <Tabs variant="enclosed">
        <TabList>
          <Tab>Revision Log</Tab>
          <Tab>Retraction Tools</Tab>
        </TabList>
        
        <TabPanels>
          {/* Revision Log Tab */}
          <TabPanel p={0}>
            <LoopRevisionLog />
          </TabPanel>
          
          {/* Retraction Tools Tab */}
          <TabPanel>
            <Box p={4}>
              <Heading size="md" mb={4}>Reflection Retraction Tools</Heading>
              
              <Flex direction="column" gap={4}>
                <Box>
                  <Heading size="sm" mb={2}>Manual Retraction</Heading>
                  <ReflectionRetractionTrigger
                    reflection={{
                      loop_id: 'loop_demo',
                      agent: 'OPERATOR',
                      content: 'This is a sample reflection that can be retracted.',
                    }}
                    triggerSource="manual"
                    buttonProps={{
                      colorScheme: 'blue',
                      size: 'md',
                    }}
                  />
                </Box>
                
                <Box>
                  <Heading size="sm" mb={2}>Misalignment Retraction</Heading>
                  <ReflectionRetractionTrigger
                    reflection={{
                      loop_id: 'loop_misalign',
                      agent: 'SAGE',
                      content: 'This reflection violates anchored beliefs and should be retracted.',
                    }}
                    triggerSource="misalignment"
                    buttonProps={{
                      colorScheme: 'red',
                      size: 'md',
                    }}
                  />
                </Box>
                
                <Box>
                  <Heading size="sm" mb={2}>Trust Breakdown Retraction</Heading>
                  <ReflectionRetractionTrigger
                    reflection={{
                      loop_id: 'loop_trust',
                      agent: 'HAL',
                      content: 'This reflection contradicts previous statements and should be retracted.',
                    }}
                    triggerSource="trust_breakdown"
                    buttonProps={{
                      colorScheme: 'yellow',
                      size: 'md',
                    }}
                  />
                </Box>
              </Flex>
            </Box>
          </TabPanel>
        </TabPanels>
      </Tabs>
      
      {/* Retraction Panel (if opened from elsewhere) */}
      <ReflectionRetractionPanel
        isOpen={isOpen}
        onClose={onClose}
        reflection={selectedReflection}
        onRetract={handleRetract}
        onReplan={handleReplan}
        triggerSource="manual"
      />
    </Box>
  );
};

export default RevisionDashboard;
