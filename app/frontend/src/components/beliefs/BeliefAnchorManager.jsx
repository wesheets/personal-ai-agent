import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  HStack,
  Heading,
  Text,
  useColorModeValue,
  IconButton,
  Badge,
  Flex,
  Switch,
  Select,
  Divider,
  useToast,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
} from '@chakra-ui/react';
import { 
  FiPlus, 
  FiTrash2, 
  FiEdit2, 
  FiLock, 
  FiUnlock, 
  FiAlertTriangle,
  FiSave,
  FiInfo
} from 'react-icons/fi';

/**
 * BeliefAnchorManager Component
 * 
 * Allows operators to define, manage, and anchor core beliefs that the system should adhere to.
 * Provides UI for defining beliefs, tagging them as critical/soft/deprecated, and setting drift thresholds.
 */
const BeliefAnchorManager = () => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headerBgColor = useColorModeValue('gray.50', 'gray.700');
  const criticalBadgeBg = useColorModeValue('red.100', 'red.900');
  const softBadgeBg = useColorModeValue('blue.100', 'blue.900');
  const deprecatedBadgeBg = useColorModeValue('gray.100', 'gray.700');
  
  // Toast for notifications
  const toast = useToast();
  
  // Modal controls
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // State for beliefs
  const [beliefs, setBeliefs] = useState([]);
  const [currentBelief, setCurrentBelief] = useState({
    belief_id: '',
    content: '',
    critical: false,
    project_id: '',
    agent_origin: '',
    drift_threshold: 0.7
  });
  const [isEditing, setIsEditing] = useState(false);
  const [editIndex, setEditIndex] = useState(-1);
  const [globalDriftThreshold, setGlobalDriftThreshold] = useState(0.7);
  
  // Load beliefs from storage on component mount
  useEffect(() => {
    const loadBeliefs = async () => {
      try {
        // In a real implementation, this would fetch from an API or local storage
        const storedBeliefs = localStorage.getItem('anchored_beliefs');
        if (storedBeliefs) {
          setBeliefs(JSON.parse(storedBeliefs));
        }
      } catch (error) {
        console.error('Failed to load beliefs:', error);
        toast({
          title: 'Failed to load beliefs',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      }
    };
    
    loadBeliefs();
  }, [toast]);
  
  // Save beliefs to storage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('anchored_beliefs', JSON.stringify(beliefs));
    } catch (error) {
      console.error('Failed to save beliefs:', error);
    }
  }, [beliefs]);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCurrentBelief({
      ...currentBelief,
      [name]: type === 'checkbox' ? checked : value,
    });
  };
  
  // Handle drift threshold change
  const handleDriftThresholdChange = (value) => {
    setCurrentBelief({
      ...currentBelief,
      drift_threshold: value,
    });
  };
  
  // Handle global drift threshold change
  const handleGlobalDriftThresholdChange = (value) => {
    setGlobalDriftThreshold(value);
    // In a real implementation, this would update a global setting
  };
  
  // Generate a unique ID for new beliefs
  const generateBeliefId = useCallback(() => {
    const prefix = currentBelief.project_id ? 
      `${currentBelief.project_id}_belief_` : 
      'belief_';
    const randomId = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    return `${prefix}${randomId}`;
  }, [currentBelief.project_id]);
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!currentBelief.content.trim()) {
      toast({
        title: 'Belief content is required',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    if (isEditing && editIndex >= 0) {
      // Update existing belief
      const updatedBeliefs = [...beliefs];
      updatedBeliefs[editIndex] = currentBelief;
      setBeliefs(updatedBeliefs);
      
      toast({
        title: 'Belief updated',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } else {
      // Add new belief
      const newBelief = {
        ...currentBelief,
        belief_id: currentBelief.belief_id || generateBeliefId(),
        last_violated_loop: null,
        drift_score: 0,
      };
      
      setBeliefs([...beliefs, newBelief]);
      
      toast({
        title: 'Belief added',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    }
    
    // Reset form
    setCurrentBelief({
      belief_id: '',
      content: '',
      critical: false,
      project_id: '',
      agent_origin: '',
      drift_threshold: 0.7
    });
    setIsEditing(false);
    setEditIndex(-1);
    onClose();
  };
  
  // Handle editing a belief
  const handleEdit = (index) => {
    setCurrentBelief(beliefs[index]);
    setIsEditing(true);
    setEditIndex(index);
    onOpen();
  };
  
  // Handle deleting a belief
  const handleDelete = (index) => {
    const updatedBeliefs = [...beliefs];
    updatedBeliefs.splice(index, 1);
    setBeliefs(updatedBeliefs);
    
    toast({
      title: 'Belief deleted',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };
  
  // Handle toggling a belief's critical status
  const handleToggleCritical = (index) => {
    const updatedBeliefs = [...beliefs];
    updatedBeliefs[index].critical = !updatedBeliefs[index].critical;
    setBeliefs(updatedBeliefs);
  };
  
  // Handle toggling a belief's deprecated status
  const handleToggleDeprecated = (index) => {
    const updatedBeliefs = [...beliefs];
    updatedBeliefs[index].deprecated = !updatedBeliefs[index].deprecated;
    setBeliefs(updatedBeliefs);
  };
  
  // Reset the form for adding a new belief
  const handleAddNew = () => {
    setCurrentBelief({
      belief_id: '',
      content: '',
      critical: false,
      project_id: '',
      agent_origin: '',
      drift_threshold: 0.7
    });
    setIsEditing(false);
    setEditIndex(-1);
    onOpen();
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
      {/* Header */}
      <Box bg={headerBgColor} px={6} py={4}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Belief Anchor Manager</Heading>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            size="sm"
            onClick={handleAddNew}
          >
            Add Belief
          </Button>
        </Flex>
      </Box>
      
      {/* Global Settings */}
      <Box p={6} borderBottomWidth="1px" borderColor={borderColor}>
        <Heading size="sm" mb={4}>Global Settings</Heading>
        <FormControl>
          <FormLabel>Default Drift Threshold</FormLabel>
          <Flex align="center">
            <Slider
              aria-label="drift-threshold"
              defaultValue={globalDriftThreshold}
              min={0.1}
              max={1}
              step={0.05}
              onChange={handleGlobalDriftThresholdChange}
              flex="1"
              mr={4}
              colorScheme="blue"
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb boxSize={6}>
                <Box color="blue.500" as={FiAlertTriangle} />
              </SliderThumb>
              <SliderMark
                value={globalDriftThreshold}
                textAlign="center"
                bg="blue.500"
                color="white"
                mt="-10"
                ml="-5"
                w="12"
                fontSize="sm"
                borderRadius="md"
              >
                {globalDriftThreshold.toFixed(2)}
              </SliderMark>
            </Slider>
            <Text width="60px" textAlign="right">
              {globalDriftThreshold.toFixed(2)}
            </Text>
          </Flex>
          <Text fontSize="sm" color="gray.500" mt={1}>
            Sets the default sensitivity for detecting belief drift
          </Text>
        </FormControl>
      </Box>
      
      {/* Beliefs Table */}
      <Box p={6} overflowX="auto">
        {beliefs.length > 0 ? (
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Belief</Th>
                <Th>Status</Th>
                <Th>Project</Th>
                <Th>Threshold</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {beliefs.map((belief, index) => (
                <Tr key={belief.belief_id}>
                  <Td>
                    <Text noOfLines={2}>{belief.content}</Text>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      {belief.critical && (
                        <Badge bg={criticalBadgeBg} px={2} borderRadius="full">
                          Critical
                        </Badge>
                      )}
                      {!belief.critical && !belief.deprecated && (
                        <Badge bg={softBadgeBg} px={2} borderRadius="full">
                          Soft
                        </Badge>
                      )}
                      {belief.deprecated && (
                        <Badge bg={deprecatedBadgeBg} px={2} borderRadius="full">
                          Deprecated
                        </Badge>
                      )}
                    </HStack>
                  </Td>
                  <Td>{belief.project_id || '-'}</Td>
                  <Td>{belief.drift_threshold.toFixed(2)}</Td>
                  <Td>
                    <HStack spacing={1}>
                      <Tooltip label="Edit">
                        <IconButton
                          icon={<FiEdit2 />}
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit(index)}
                          aria-label="Edit belief"
                        />
                      </Tooltip>
                      <Tooltip label={belief.critical ? "Mark as non-critical" : "Mark as critical"}>
                        <IconButton
                          icon={belief.critical ? <FiUnlock /> : <FiLock />}
                          size="sm"
                          variant="ghost"
                          onClick={() => handleToggleCritical(index)}
                          aria-label={belief.critical ? "Mark as non-critical" : "Mark as critical"}
                        />
                      </Tooltip>
                      <Tooltip label={belief.deprecated ? "Restore" : "Deprecate"}>
                        <IconButton
                          icon={<FiAlertTriangle />}
                          size="sm"
                          variant="ghost"
                          colorScheme={belief.deprecated ? "gray" : "yellow"}
                          onClick={() => handleToggleDeprecated(index)}
                          aria-label={belief.deprecated ? "Restore" : "Deprecate"}
                        />
                      </Tooltip>
                      <Tooltip label="Delete">
                        <IconButton
                          icon={<FiTrash2 />}
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => handleDelete(index)}
                          aria-label="Delete belief"
                        />
                      </Tooltip>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        ) : (
          <Box textAlign="center" py={10}>
            <Text color="gray.500">No beliefs defined yet</Text>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="blue"
              size="sm"
              mt={4}
              onClick={handleAddNew}
            >
              Add Your First Belief
            </Button>
          </Box>
        )}
      </Box>
      
      {/* Add/Edit Belief Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <form onSubmit={handleSubmit}>
            <ModalHeader>
              {isEditing ? 'Edit Belief' : 'Add New Belief'}
            </ModalHeader>
            <ModalCloseButton />
            
            <ModalBody>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>Belief ID</FormLabel>
                  <Input
                    name="belief_id"
                    value={currentBelief.belief_id}
                    onChange={handleInputChange}
                    placeholder="Auto-generated if left blank"
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Belief Content</FormLabel>
                  <Textarea
                    name="content"
                    value={currentBelief.content}
                    onChange={handleInputChange}
                    placeholder="Enter the belief statement"
                    rows={4}
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Project ID</FormLabel>
                  <Input
                    name="project_id"
                    value={currentBelief.project_id}
                    onChange={handleInputChange}
                    placeholder="e.g., life_tree"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Agent Origin</FormLabel>
                  <Select
                    name="agent_origin"
                    value={currentBelief.agent_origin}
                    onChange={handleInputChange}
                    placeholder="Select agent"
                  >
                    <option value="SAGE">SAGE</option>
                    <option value="HAL">HAL</option>
                    <option value="NOVA">NOVA</option>
                    <option value="CRITIC">CRITIC</option>
                    <option value="OPERATOR">OPERATOR</option>
                  </Select>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Critical Belief</FormLabel>
                  <Switch
                    name="critical"
                    isChecked={currentBelief.critical}
                    onChange={handleInputChange}
                    colorScheme="red"
                  />
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Critical beliefs trigger immediate alerts when violated
                  </Text>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Drift Threshold</FormLabel>
                  <Flex align="center">
                    <Slider
                      aria-label="drift-threshold"
                      value={currentBelief.drift_threshold}
                      min={0.1}
                      max={1}
                      step={0.05}
                      onChange={handleDriftThresholdChange}
                      flex="1"
                      mr={4}
                      colorScheme="blue"
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb boxSize={6}>
                        <Box color="blue.500" as={FiAlertTriangle} />
                      </SliderThumb>
                    </Slider>
                    <Text width="60px" textAlign="right">
                      {currentBelief.drift_threshold.toFixed(2)}
                    </Text>
                  </Flex>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Lower values increase sensitivity to belief violations
                  </Text>
                </FormControl>
              </VStack>
            </ModalBody>
            
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button
                type="submit"
                leftIcon={<FiSave />}
                colorScheme="blue"
              >
                {isEditing ? 'Update' : 'Save'}
              </Button>
            </ModalFooter>
          </form>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default BeliefAnchorManager;
