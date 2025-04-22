import React, { useState, useEffect } from 'react';
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
  Radio,
  RadioGroup,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import {
  FiEdit,
  FiFlag,
  FiRefreshCw,
  FiCheck,
  FiX,
  FiAlertTriangle,
  FiInfo,
  FiSave,
} from 'react-icons/fi';

/**
 * ReflectionRetractionPanel Component
 * 
 * Modal/dialogue for retracting or editing reflections, triggered via:
 * - Misalignment alert
 * - Trust breakdown
 * - Manual Operator action
 * 
 * Provides options to:
 * - Edit reflection
 * - Flag as flawed
 * - Trigger replanning by Orchestrator or SAGE
 */
const ReflectionRetractionPanel = ({ 
  isOpen, 
  onClose, 
  reflection = null,
  onRetract = () => {},
  onReplan = () => {},
  triggerSource = 'manual' // 'manual', 'misalignment', 'trust_breakdown'
}) => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const alertBgColor = useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)');
  
  // Toast for notifications
  const toast = useToast();
  
  // State for form
  const [formData, setFormData] = useState({
    loop_id: '',
    agent: '',
    original_reflection: '',
    revised_reflection: '',
    reason: 'operator_override',
    replan_required: true,
    flag_as_flawed: true,
  });
  
  // State for form submission
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Update form data when reflection changes
  useEffect(() => {
    if (reflection) {
      setFormData({
        loop_id: reflection.loop_id || '',
        agent: reflection.agent || '',
        original_reflection: reflection.content || '',
        revised_reflection: reflection.content || '',
        reason: 'operator_override',
        replan_required: true,
        flag_as_flawed: true,
      });
    }
  }, [reflection]);
  
  // Update reason based on trigger source
  useEffect(() => {
    if (triggerSource === 'misalignment') {
      setFormData(prev => ({ ...prev, reason: 'misalignment' }));
    } else if (triggerSource === 'trust_breakdown') {
      setFormData(prev => ({ ...prev, reason: 'contradiction' }));
    }
  }, [triggerSource]);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };
  
  // Handle radio button changes
  const handleRadioChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Validate form
      if (!formData.revised_reflection.trim()) {
        throw new Error('Revised reflection cannot be empty');
      }
      
      // Prepare retraction data
      const retractionData = {
        loop_id: formData.loop_id,
        agent: formData.agent,
        original_reflection: formData.original_reflection,
        revised_reflection: formData.revised_reflection,
        reason: formData.reason,
        timestamp: new Date().toISOString(),
        status: formData.replan_required ? 'pending' : 'revised',
        flag_as_flawed: formData.flag_as_flawed,
      };
      
      // Call retraction handler
      await onRetract(retractionData);
      
      // If replanning is required, call replan handler
      if (formData.replan_required) {
        await onReplan(retractionData);
      }
      
      // Show success toast
      toast({
        title: 'Reflection retracted',
        description: formData.replan_required ? 'Replanning has been triggered.' : 'Reflection has been revised.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Close modal
      onClose();
    } catch (error) {
      // Show error toast
      toast({
        title: 'Error',
        description: error.message || 'Failed to retract reflection',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Get alert variant based on trigger source
  const getAlertProps = () => {
    switch (triggerSource) {
      case 'misalignment':
        return {
          status: 'error',
          title: 'Belief Misalignment Detected',
          description: 'This reflection violates one or more anchored beliefs.',
          icon: <FiAlertTriangle />,
        };
      case 'trust_breakdown':
        return {
          status: 'warning',
          title: 'Trust Breakdown Detected',
          description: 'This reflection contradicts previous agent statements or beliefs.',
          icon: <FiAlertTriangle />,
        };
      default:
        return {
          status: 'info',
          title: 'Manual Reflection Retraction',
          description: 'You are manually retracting or editing this reflection.',
          icon: <FiInfo />,
        };
    }
  };
  
  const alertProps = getAlertProps();
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>Reflection Retraction</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            <VStack spacing={4} align="stretch">
              {/* Alert based on trigger source */}
              <Alert status={alertProps.status} borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>{alertProps.title}</AlertTitle>
                  <AlertDescription>
                    {alertProps.description}
                  </AlertDescription>
                </Box>
              </Alert>
              
              {/* Loop and Agent Info */}
              <Flex gap={4}>
                <FormControl isReadOnly>
                  <FormLabel>Loop ID</FormLabel>
                  <Input
                    value={formData.loop_id}
                    fontFamily="mono"
                  />
                </FormControl>
                
                <FormControl isReadOnly>
                  <FormLabel>Agent</FormLabel>
                  <Input
                    value={formData.agent}
                  />
                </FormControl>
              </Flex>
              
              {/* Original Reflection */}
              <FormControl isReadOnly>
                <FormLabel>Original Reflection</FormLabel>
                <Textarea
                  value={formData.original_reflection}
                  rows={4}
                  bg={alertBgColor}
                />
              </FormControl>
              
              {/* Revised Reflection */}
              <FormControl isRequired>
                <FormLabel>Revised Reflection</FormLabel>
                <Textarea
                  name="revised_reflection"
                  value={formData.revised_reflection}
                  onChange={handleInputChange}
                  placeholder="Enter the revised reflection"
                  rows={4}
                />
              </FormControl>
              
              <Divider />
              
              {/* Retraction Reason */}
              <FormControl>
                <FormLabel>Retraction Reason</FormLabel>
                <RadioGroup
                  value={formData.reason}
                  onChange={(value) => handleRadioChange('reason', value)}
                >
                  <HStack spacing={4} wrap="wrap">
                    <Radio value="misalignment">Belief Misalignment</Radio>
                    <Radio value="drift">Belief Drift</Radio>
                    <Radio value="operator_override">Operator Override</Radio>
                    <Radio value="contradiction">Contradiction</Radio>
                  </HStack>
                </RadioGroup>
              </FormControl>
              
              {/* Flag as Flawed */}
              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">
                  Flag as Flawed
                </FormLabel>
                <Switch
                  name="flag_as_flawed"
                  isChecked={formData.flag_as_flawed}
                  onChange={handleInputChange}
                  colorScheme="red"
                />
              </FormControl>
              
              {/* Replan Required */}
              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">
                  Trigger Replanning
                </FormLabel>
                <Switch
                  name="replan_required"
                  isChecked={formData.replan_required}
                  onChange={handleInputChange}
                  colorScheme="blue"
                />
              </FormControl>
              
              {formData.replan_required && (
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Replanning will be triggered</AlertTitle>
                    <AlertDescription>
                      This will restart the loop with the revised reflection and updated context.
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
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
              isLoading={isSubmitting}
            >
              Retract & {formData.replan_required ? 'Replan' : 'Revise'}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

/**
 * ReflectionRetractionTrigger Component
 * 
 * Button or icon that triggers the ReflectionRetractionPanel
 */
export const ReflectionRetractionTrigger = ({ 
  reflection, 
  triggerSource = 'manual',
  buttonProps = {},
  iconOnly = false,
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
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
  
  // Handle replanning
  const handleReplan = async (retractionData) => {
    // In a real implementation, this would call an API
    console.log('Triggering replan for reflection:', retractionData);
    
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000);
    });
  };
  
  if (iconOnly) {
    return (
      <>
        <IconButton
          icon={<FiEdit />}
          aria-label="Retract reflection"
          onClick={onOpen}
          {...buttonProps}
        />
        <ReflectionRetractionPanel
          isOpen={isOpen}
          onClose={onClose}
          reflection={reflection}
          onRetract={handleRetract}
          onReplan={handleReplan}
          triggerSource={triggerSource}
        />
      </>
    );
  }
  
  return (
    <>
      <Button
        leftIcon={<FiEdit />}
        onClick={onOpen}
        {...buttonProps}
      >
        Retract Reflection
      </Button>
      <ReflectionRetractionPanel
        isOpen={isOpen}
        onClose={onClose}
        reflection={reflection}
        onRetract={handleRetract}
        onReplan={handleReplan}
        triggerSource={triggerSource}
      />
    </>
  );
};

export default ReflectionRetractionPanel;
