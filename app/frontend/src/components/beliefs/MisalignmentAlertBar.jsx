import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  CloseButton,
  Button,
  HStack,
  VStack,
  Text,
  Collapse,
  useColorModeValue,
  Flex,
  Badge,
  Divider,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Code,
} from '@chakra-ui/react';
import { 
  FiAlertTriangle, 
  FiCheck, 
  FiX, 
  FiRefreshCw, 
  FiInfo,
  FiChevronDown,
  FiChevronUp
} from 'react-icons/fi';

/**
 * MisalignmentAlertBar Component
 * 
 * Renders an alert bar when a loop or reflection violates an anchored belief.
 * Provides options to reflect again, replan, or approve override.
 */
const MisalignmentAlertBar = () => {
  // Color mode values
  const alertBgColor = useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)');
  const alertBorderColor = useColorModeValue('red.200', 'red.800');
  const codeBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // State for alerts
  const [alerts, setAlerts] = useState([]);
  const [expandedAlerts, setExpandedAlerts] = useState({});
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  // Modal controls
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Mock data for development - would be replaced with real data in production
  useEffect(() => {
    // Simulating alerts for development purposes
    const mockAlerts = [
      {
        id: 'alert_001',
        belief_id: 'life_tree_intent_001',
        belief_content: 'The system should prioritize emotional safety over technical completeness.',
        agent_involved: 'SAGE',
        loop_id: 'loop_289',
        drift_score: 0.84,
        timestamp: new Date().toISOString(),
        violation_content: 'Proceeding with technical implementation despite user expressing discomfort with the approach.',
        status: 'active'
      }
    ];
    
    // In a real implementation, this would subscribe to a real-time alert system
    const alertListener = () => {
      // This would be replaced with actual event listeners
    };
    
    // Initialize with mock data
    setAlerts(mockAlerts);
    
    // Cleanup function
    return () => {
      // This would clean up real event listeners
    };
  }, []);
  
  // Toggle alert expansion
  const toggleAlertExpansion = (alertId) => {
    setExpandedAlerts(prev => ({
      ...prev,
      [alertId]: !prev[alertId]
    }));
  };
  
  // Handle dismissing an alert
  const handleDismissAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };
  
  // Handle reflecting again
  const handleReflectAgain = (alert) => {
    // In a real implementation, this would trigger a re-reflection process
    console.log('Triggering re-reflection for loop:', alert.loop_id);
    
    // Update alert status
    setAlerts(prev => 
      prev.map(a => 
        a.id === alert.id 
          ? { ...a, status: 'reflecting' } 
          : a
      )
    );
    
    // Simulate reflection process
    setTimeout(() => {
      setAlerts(prev => 
        prev.map(a => 
          a.id === alert.id 
            ? { ...a, status: 'resolved', resolution: 'reflected' } 
            : a
        )
      );
    }, 2000);
  };
  
  // Handle replanning
  const handleReplan = (alert) => {
    // In a real implementation, this would trigger a replanning process
    console.log('Triggering replanning for loop:', alert.loop_id);
    
    // Update alert status
    setAlerts(prev => 
      prev.map(a => 
        a.id === alert.id 
          ? { ...a, status: 'replanning' } 
          : a
      )
    );
    
    // Simulate replanning process
    setTimeout(() => {
      setAlerts(prev => 
        prev.map(a => 
          a.id === alert.id 
            ? { ...a, status: 'resolved', resolution: 'replanned' } 
            : a
        )
      );
    }, 2000);
  };
  
  // Handle approving override
  const handleApproveOverride = (alert) => {
    // Set selected alert and open modal
    setSelectedAlert(alert);
    onOpen();
  };
  
  // Confirm override approval
  const confirmOverride = () => {
    if (!selectedAlert) return;
    
    // In a real implementation, this would log the override and update the system
    console.log('Override approved for alert:', selectedAlert.id);
    
    // Update alert status
    setAlerts(prev => 
      prev.map(a => 
        a.id === selectedAlert.id 
          ? { ...a, status: 'resolved', resolution: 'override_approved' } 
          : a
      )
    );
    
    // Close modal
    onClose();
    setSelectedAlert(null);
  };
  
  // If no alerts, don't render anything
  if (alerts.length === 0) {
    return null;
  }
  
  return (
    <>
      <Box width="100%" position="sticky" top="0" zIndex="1000">
        {alerts.map(alert => (
          <Box
            key={alert.id}
            mb={2}
            borderWidth="1px"
            borderRadius="md"
            borderColor={alertBorderColor}
            bg={alertBgColor}
            overflow="hidden"
            boxShadow="md"
          >
            <Alert 
              status="error" 
              variant="solid" 
              borderRadius="0"
              alignItems="flex-start"
            >
              <AlertIcon boxSize="20px" mt={1} />
              <Flex direction="column" flex="1">
                <Flex justify="space-between" align="center" width="100%">
                  <AlertTitle fontSize="md">
                    Possible Misalignment Detected
                  </AlertTitle>
                  <HStack>
                    {alert.status === 'active' && (
                      <>
                        <Button
                          size="sm"
                          leftIcon={<FiRefreshCw />}
                          colorScheme="blue"
                          variant="ghost"
                          onClick={() => handleReflectAgain(alert)}
                        >
                          Reflect Again
                        </Button>
                        <Button
                          size="sm"
                          leftIcon={<FiRefreshCw />}
                          colorScheme="purple"
                          variant="ghost"
                          onClick={() => handleReplan(alert)}
                        >
                          Replan
                        </Button>
                        <Button
                          size="sm"
                          leftIcon={<FiCheck />}
                          colorScheme="green"
                          variant="ghost"
                          onClick={() => handleApproveOverride(alert)}
                        >
                          Approve
                        </Button>
                      </>
                    )}
                    {alert.status === 'reflecting' && (
                      <Badge colorScheme="blue" variant="subtle" px={2} py={1}>
                        Reflecting...
                      </Badge>
                    )}
                    {alert.status === 'replanning' && (
                      <Badge colorScheme="purple" variant="subtle" px={2} py={1}>
                        Replanning...
                      </Badge>
                    )}
                    {alert.status === 'resolved' && (
                      <Badge colorScheme="green" variant="subtle" px={2} py={1}>
                        Resolved
                      </Badge>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleAlertExpansion(alert.id)}
                    >
                      {expandedAlerts[alert.id] ? <FiChevronUp /> : <FiChevronDown />}
                    </Button>
                    <CloseButton 
                      size="sm" 
                      onClick={() => handleDismissAlert(alert.id)} 
                    />
                  </HStack>
                </Flex>
                <AlertDescription fontSize="sm" mt={1}>
                  <Text>
                    Agent <Badge colorScheme="blue">{alert.agent_involved}</Badge> in loop <Badge>{alert.loop_id}</Badge> has a drift score of <Badge colorScheme="red">{alert.drift_score.toFixed(2)}</Badge>
                  </Text>
                </AlertDescription>
              </Flex>
            </Alert>
            
            <Collapse in={expandedAlerts[alert.id]} animateOpacity>
              <Box p={4} bg={useColorModeValue('white', 'gray.800')}>
                <VStack align="stretch" spacing={3}>
                  <Box>
                    <Text fontWeight="bold" fontSize="sm">Anchored Belief:</Text>
                    <Text fontSize="sm" pl={2} borderLeftWidth="2px" borderColor="blue.500">
                      {alert.belief_content}
                    </Text>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold" fontSize="sm">Violation Content:</Text>
                    <Code p={2} borderRadius="md" fontSize="sm" width="100%" bg={codeBgColor}>
                      {alert.violation_content}
                    </Code>
                  </Box>
                  
                  <Divider />
                  
                  <Flex justify="space-between" align="center">
                    <Text fontSize="xs" color="gray.500">
                      Detected at {new Date(alert.timestamp).toLocaleTimeString()}
                    </Text>
                    
                    {alert.status === 'resolved' && alert.resolution && (
                      <Badge colorScheme={
                        alert.resolution === 'reflected' ? 'blue' :
                        alert.resolution === 'replanned' ? 'purple' :
                        'green'
                      }>
                        {alert.resolution === 'reflected' ? 'Reflected' :
                         alert.resolution === 'replanned' ? 'Replanned' :
                         'Override Approved'}
                      </Badge>
                    )}
                  </Flex>
                </VStack>
              </Box>
            </Collapse>
          </Box>
        ))}
      </Box>
      
      {/* Override Confirmation Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm Override</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            <VStack align="stretch" spacing={4}>
              <Alert status="warning" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>Warning</AlertTitle>
                  <AlertDescription>
                    You are about to override a belief misalignment alert. This action will be logged.
                  </AlertDescription>
                </Box>
              </Alert>
              
              {selectedAlert && (
                <>
                  <Box>
                    <Text fontWeight="bold">Anchored Belief:</Text>
                    <Text pl={2} borderLeftWidth="2px" borderColor="blue.500" mt={1}>
                      {selectedAlert.belief_content}
                    </Text>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold">Agent:</Text>
                    <Text>{selectedAlert.agent_involved}</Text>
                  </Box>
                  
                  <Box>
                    <Text fontWeight="bold">Loop ID:</Text>
                    <Text>{selectedAlert.loop_id}</Text>
                  </Box>
                </>
              )}
            </VStack>
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="red" onClick={confirmOverride}>
              Confirm Override
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default MisalignmentAlertBar;
