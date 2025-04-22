import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Grid,
  GridItem,
  Button,
  Icon,
  useColorModeValue,
  useDisclosure,
} from '@chakra-ui/react';
import { FaTools, FaHistory, FaQuestionCircle, FaMapMarkedAlt, FaExclamationTriangle } from 'react-icons/fa';
import { AutoRouterProvider } from '../context/AutoRouterContext';
import { UIZoneSchema } from '../schemas/UIZoneSchema';
import ErrorBoundary from './ErrorBoundary';
import SageTooltip from './SageTooltip';
import OnboardingPane from './OnboardingPane';
import GuidedTourManager from './GuidedTourManager';
import MisalignmentAlertBar from './beliefs/MisalignmentAlertBar';
import ContradictionIntegration from './ContradictionIntegration';

/**
 * DashboardLayout Component
 * 
 * Main layout component for the Promethios dashboard.
 * Organizes UI components into zones based on UIZoneSchema.
 */
const DashboardLayout = () => {
  // Color mode values
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // State for modal and tour
  const [activeModal, setActiveModal] = useState(null);
  const [activeTour, setActiveTour] = useState('main');
  const [showTour, setShowTour] = useState(false);
  
  // Onboarding disclosure
  const { isOpen: isOnboardingOpen, onOpen: onOpenOnboarding, onClose: onCloseOnboarding } = useDisclosure();
  
  // Open modal
  const openModal = (componentName) => {
    setActiveModal(componentName);
  };
  
  // Close modal
  const closeModal = () => {
    setActiveModal(null);
  };
  
  // Render component based on name
  const renderComponent = (componentName) => {
    // Map component names to actual components
    const componentMap = {
      // Add your component mappings here
      ContradictionDisplay: ContradictionIntegration,
      // Other components...
    };
    
    // Get component from map or use a placeholder
    const Component = componentMap[componentName] || (() => <div>Component: {componentName}</div>);
    
    // Render component with error boundary and tooltip
    return (
      <Box
        p={4}
        borderRadius="lg"
        bg={cardBgColor}
        borderWidth="1px"
        borderColor={borderColor}
        shadow="sm"
        mb={4}
        height="100%"
        id={componentName}
      >
        <ErrorBoundary>
          <SageTooltip componentId={componentName} showIcon={false} usePopover={true}>
            <Component />
          </SageTooltip>
        </ErrorBoundary>
      </Box>
    );
  };
  return (
    <AutoRouterProvider>
      <Box bg={bgColor} minH="100vh">
        {/* Misalignment Alert Bar - Global placement */}
        <MisalignmentAlertBar />
        
        <Grid
          templateColumns={{ base: '1fr', md: '300px 1fr 300px' }}
          templateAreas={{
            base: `"left" "center" "right"`,
            md: `"left center right"`
          }}
          gap={2}
          height="100vh"
        >
          {/* LEFT Zone */}
          <GridItem area="left" overflowY="auto" p={2} maxH="100vh">
            {UIZoneSchema.zones.LEFT.map((componentName) => (
              <Box key={componentName} mb={4}>
                {renderComponent(componentName)}
              </Box>
            ))}
          </GridItem>
          {/* CENTER Zone */}
          <GridItem area="center" overflowY="auto" p={2} maxH="100vh">
            {UIZoneSchema.zones.CENTER.map((componentName) => (
              <Box key={componentName} mb={4}>
                {renderComponent(componentName)}
              </Box>
            ))}
          </GridItem>
          {/* RIGHT Zone */}
          <GridItem area="right" overflowY="auto" p={2} maxH="100vh">
            {/* Add ContradictionDisplay to the RIGHT zone */}
            <Box mb={4}>
              {renderComponent('ContradictionDisplay')}
            </Box>
            {UIZoneSchema.zones.RIGHT.map((componentName) => (
              <Box key={componentName} mb={4}>
                {renderComponent(componentName)}
              </Box>
            ))}
          </GridItem>
        </Grid>
        {/* MODAL Zone - Rendered conditionally */}
        {activeModal && (
          <Box
            position="fixed"
            top={0}
            left={0}
            right={0}
            bottom={0}
            bg="rgba(0, 0, 0, 0.7)"
            zIndex={1000}
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Box
              width="80%"
              maxWidth="1200px"
              maxHeight="80vh"
              overflowY="auto"
              bg={cardBgColor}
              borderRadius="lg"
              p={6}
            >
              <ErrorBoundary>
                {/* Modal content will be rendered here */}
              </ErrorBoundary>
            </Box>
          </Box>
        )}
        
        {/* Onboarding Pane */}
        <OnboardingPane 
          isOpen={isOnboardingOpen} 
          onClose={onCloseOnboarding} 
        />
        
        {/* Loop Repair Log Button */}
        <Box
          position="fixed"
          bottom="200px"
          right="20px"
          zIndex="900"
        >
          <Button
            leftIcon={<Icon as={FaTools} />}
            colorScheme="red"
            onClick={() => openModal('LoopRepairLog')}
            size="md"
            boxShadow="md"
          >
            Repair Log
          </Button>
        </Box>
        
        {/* Belief Change Log Button */}
        <Box
          position="fixed"
          bottom="140px"
          right="20px"
          zIndex="900"
        >
          <Button
            leftIcon={<Icon as={FaHistory} />}
            colorScheme="purple"
            onClick={() => openModal('BeliefChangeLog')}
            size="md"
            boxShadow="md"
          >
            Belief Changes
          </Button>
        </Box>
        
        {/* Contradiction Log Button */}
        <Box
          position="fixed"
          bottom="80px"
          right="20px"
          zIndex="900"
        >
          <Button
            leftIcon={<Icon as={FaExclamationTriangle} />}
            colorScheme="orange"
            onClick={() => openModal('ContradictionDisplay')}
            size="md"
            boxShadow="md"
          >
            Contradictions
          </Button>
        </Box>
        
        {/* Help Button */}
        <Box
          position="fixed"
          bottom="80px"
          right="180px"
          zIndex="900"
        >
          <Button
            leftIcon={<Icon as={FaQuestionCircle} />}
            colorScheme="blue"
            onClick={onOpenOnboarding}
            size="md"
            boxShadow="md"
          >
            Help
          </Button>
        </Box>
        
        {/* Tour Button */}
        <Box
          position="fixed"
          bottom="20px"
          right="20px"
          zIndex="900"
        >
          <Button
            leftIcon={<Icon as={FaMapMarkedAlt} />}
            colorScheme="teal"
            onClick={() => {
              setActiveTour('main');
              setShowTour(true);
            }}
            size="md"
            boxShadow="md"
          >
            Take Tour
          </Button>
        </Box>
        
        {/* Guided Tour Manager */}
        {showTour && (
          <GuidedTourManager
            tourId={activeTour}
            autoStart={true}
            onComplete={() => setShowTour(false)}
            onSkip={() => setShowTour(false)}
            showControls={true}
          />
        )}
      </Box>
    </AutoRouterProvider>
  );
};
export default DashboardLayout;
