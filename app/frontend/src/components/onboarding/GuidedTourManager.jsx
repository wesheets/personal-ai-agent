import React, { useState, useEffect } from 'react';
import Joyride, { STATUS } from 'react-joyride';
import { useToast, useColorModeValue, Button, Box, Flex, Icon } from '@chakra-ui/react';
import { FaMapMarkedAlt, FaPlay, FaPause, FaStop } from 'react-icons/fa';
import tourRegistry from '../../config/TourStepRegistry.json';

/**
 * GuidedTourManager Component
 * 
 * Manages guided tours using the TourStepRegistry and react-joyride.
 * Provides options to restart, skip, complete, or resume tours.
 * 
 * @param {Object} props
 * @param {string} props.tourId - ID of the tour to run from TourStepRegistry (default: 'main')
 * @param {boolean} props.autoStart - Whether to start the tour automatically (default: false)
 * @param {function} props.onComplete - Callback when tour is completed
 * @param {function} props.onSkip - Callback when tour is skipped
 * @param {boolean} props.showControls - Whether to show tour controls (default: true)
 */
const GuidedTourManager = ({ 
  tourId = 'main', 
  autoStart = false, 
  onComplete, 
  onSkip,
  showControls = true
}) => {
  const [runTour, setRunTour] = useState(autoStart);
  const [tourSteps, setTourSteps] = useState([]);
  const [stepIndex, setStepIndex] = useState(0);
  const [tourData, setTourData] = useState(null);
  
  const toast = useToast();
  const tooltipBg = useColorModeValue('blue.700', 'blue.900');
  const tooltipColor = useColorModeValue('white', 'gray.100');
  const controlsBg = useColorModeValue('white', 'gray.800');
  const controlsBorder = useColorModeValue('gray.200', 'gray.700');
  
  // Load tour data from registry
  useEffect(() => {
    if (tourRegistry.tours && tourRegistry.tours[tourId]) {
      setTourData(tourRegistry.tours[tourId]);
      
      // Transform steps to Joyride format
      const steps = tourRegistry.tours[tourId].steps.map(step => ({
        target: step.target,
        content: (
          <Box>
            <Box fontWeight="bold" fontSize="lg" mb={1}>{step.title}</Box>
            <Box mb={step.sageQuote ? 3 : 0}>{step.content}</Box>
            {step.sageQuote && (
              <Box fontStyle="italic" fontSize="sm" color="gray.300" mt={2} borderLeft="2px solid" borderColor="blue.400" pl={2}>
                "{step.sageQuote}"
              </Box>
            )}
          </Box>
        ),
        placement: step.position || 'center',
        disableBeacon: true
      }));
      
      setTourSteps(steps);
    } else {
      console.error(`Tour with ID "${tourId}" not found in registry`);
      toast({
        title: 'Tour not found',
        description: `Could not find tour "${tourId}" in the registry.`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }, [tourId, toast]);
  
  // Check for saved tour progress in localStorage
  useEffect(() => {
    const savedProgress = localStorage.getItem(`promethios_tour_${tourId}`);
    if (savedProgress) {
      try {
        const { lastStep, completed } = JSON.parse(savedProgress);
        if (!completed && lastStep > 0) {
          setStepIndex(lastStep);
          
          // Only auto-resume if explicitly set or user was more than halfway
          if (autoStart || lastStep > (tourSteps.length / 2)) {
            setRunTour(true);
            toast({
              title: 'Tour resumed',
              description: 'Resuming your previous tour from where you left off.',
              status: 'info',
              duration: 3000,
              isClosable: true,
            });
          }
        }
      } catch (e) {
        console.error('Error parsing saved tour progress', e);
      }
    }
  }, [tourId, tourSteps.length, toast, autoStart]);
  
  // Save progress to localStorage
  const saveTourProgress = (index, completed = false) => {
    localStorage.setItem(`promethios_tour_${tourId}`, JSON.stringify({
      lastStep: index,
      completed
    }));
  };
  
  // Handle tour callbacks
  const handleJoyrideCallback = (data) => {
    const { action, index, status, type } = data;
    
    // Save progress on step changes
    if (type === 'step:after' && action === 'next') {
      saveTourProgress(index + 1);
      setStepIndex(index + 1);
    }
    
    // Handle tour completion
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
      
      if (status === STATUS.FINISHED) {
        saveTourProgress(tourSteps.length, true);
        toast({
          title: 'Tour completed',
          description: 'You have completed the guided tour!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        if (onComplete) onComplete();
      } else if (status === STATUS.SKIPPED) {
        saveTourProgress(index);
        if (onSkip) onSkip();
      }
    }
  };
  
  // Start tour
  const startTour = () => {
    setRunTour(true);
    toast({
      title: 'Tour started',
      description: tourData?.title || 'Starting guided tour',
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };
  
  // Pause tour
  const pauseTour = () => {
    setRunTour(false);
    saveTourProgress(stepIndex);
    toast({
      title: 'Tour paused',
      description: 'Your progress has been saved. You can resume later.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };
  
  // Reset tour
  const resetTour = () => {
    setStepIndex(0);
    setRunTour(true);
    toast({
      title: 'Tour restarted',
      description: 'Starting the tour from the beginning.',
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };
  
  return (
    <>
      <Joyride
        steps={tourSteps}
        run={runTour}
        stepIndex={stepIndex}
        continuous
        showProgress
        showSkipButton
        callback={handleJoyrideCallback}
        styles={{
          options: {
            primaryColor: '#3182CE', // blue.500
            zIndex: 1000,
          },
          tooltip: {
            backgroundColor: tooltipBg,
            color: tooltipColor,
            borderRadius: '8px',
          },
          buttonNext: {
            backgroundColor: '#3182CE', // blue.500
          },
          buttonBack: {
            color: '#3182CE', // blue.500
          }
        }}
        locale={{
          last: 'Finish',
          skip: 'Skip tour'
        }}
      />
      
      {showControls && (
        <Box
          position="fixed"
          bottom="20px"
          right="20px"
          zIndex="900"
          bg={controlsBg}
          borderRadius="md"
          boxShadow="md"
          border="1px solid"
          borderColor={controlsBorder}
          p={2}
        >
          <Flex align="center">
            <Icon as={FaMapMarkedAlt} mr={2} color="blue.500" />
            {!runTour ? (
              <Button 
                size="sm" 
                leftIcon={<FaPlay />} 
                colorScheme="blue" 
                onClick={startTour}
                mr={1}
              >
                {stepIndex > 0 ? 'Resume Tour' : 'Start Tour'}
              </Button>
            ) : (
              <Button 
                size="sm" 
                leftIcon={<FaPause />} 
                colorScheme="yellow" 
                onClick={pauseTour}
                mr={1}
              >
                Pause
              </Button>
            )}
            <Button 
              size="sm" 
              leftIcon={<FaStop />} 
              variant="ghost" 
              onClick={resetTour}
            >
              Restart
            </Button>
          </Flex>
        </Box>
      )}
    </>
  );
};

export default GuidedTourManager;
