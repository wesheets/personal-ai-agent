import React, { useState } from 'react';
import { Box, Flex, Grid, GridItem, useColorModeValue, useDisclosure, Button, Icon } from '@chakra-ui/react';
import ErrorBoundary from './ErrorBoundary';
import { LoadingCard } from './LoadingStates';
import UIZoneSchema from '../config/ui/UIZoneSchema.json';

// Import existing components
import AgentPanel from './AgentPanel';
import GoalLoopVisualization from './GoalLoopVisualization';
import MemoryViewer from './MemoryViewer';

// Import new components as they're created
// LEFT zone components
import OperatorHUDBar from './left/OperatorHUDBar';
import ProjectContextSwitcher from './left/ProjectContextSwitcher';
import OrchestratorModePanel from './left/OrchestratorModePanel';
import PermissionsManager from './left/PermissionsManager';
import AgentChatConsole from './left/AgentChatConsole';

// CENTER zone components
import LoopDebugger from './center/LoopDebugger';
import WhatIfSimulator from './center/WhatIfSimulator';
import BeliefsExplorer from './center/BeliefsExplorer';

// Import Memory Query and Reflection Trace components
import MemoryQueryConsole from './memory/MemoryQueryConsole';
import LoopTraceViewer from './memory/LoopTraceViewer';
import ReflectionHistoryPanel from './memory/ReflectionHistoryPanel';

// RIGHT zone components
import RightPanelContainer from './right/RightPanelContainer';
import FileTreePanel from './right/FileTreePanel';
import SystemHealthPanel from './right/SystemHealthPanel';
import MetricsVisualization from './right/MetricsVisualization';
import RebuildStatusDisplay from './right/RebuildStatusDisplay';
import AuditLogViewer from './right/AuditLogViewer';
import TrustScoreDisplay from './right/TrustScoreDisplay';
import ContradictionDisplay from './right/ContradictionDisplay';
import LoopDriftIndex from './right/LoopDriftIndex';

// MODAL components are loaded dynamically when needed
import { useModalContext } from '../hooks/useModalContext';

// Import onboarding components
import SageTooltip from './onboarding/SageTooltip';
import OnboardingPane from './onboarding/OnboardingPane';
import GuidedTourManager from './onboarding/GuidedTourManager';
import { FaQuestionCircle, FaMapMarkedAlt } from 'react-icons/fa';

// Component mapping for dynamic rendering
const componentMap = {
  // LEFT zone
  OperatorHUDBar,
  ProjectContextSwitcher,
  OrchestratorModePanel,
  AgentPanel,
  PermissionsManager,
  AgentChatConsole,
  
  // CENTER zone
  GoalLoopVisualization,
  MemoryViewer,
  LoopDebugger,
  WhatIfSimulator,
  BeliefsExplorer,
  LoopTraceViewer, // Added new component
  
  // RIGHT zone
  RightPanelContainer,
  FileTreePanel,
  SystemHealthPanel,
  MetricsVisualization,
  RebuildStatusDisplay,
  AuditLogViewer,
  TrustScoreDisplay,
  ContradictionDisplay,
  LoopDriftIndex,
  
  // MODAL zone
  MemoryQueryConsole, // Added new component
  ReflectionHistoryPanel, // Added new component
  OnboardingPane
};

const DashboardLayout = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const { activeModal, openModal } = useModalContext();
  
  // Onboarding state
  const [showTour, setShowTour] = useState(false);
  const [activeTour, setActiveTour] = useState('main');
  const { isOpen: isOnboardingOpen, onOpen: onOpenOnboarding, onClose: onCloseOnboarding } = useDisclosure();
  
  // Check if this is the first visit
  React.useEffect(() => {
    const isFirstVisit = localStorage.getItem('promethios_first_visit') === null;
    if (isFirstVisit) {
      // Set first visit flag
      localStorage.setItem('promethios_first_visit', 'false');
      // Show onboarding pane
      onOpenOnboarding();
      // Start tour after a short delay
      setTimeout(() => {
        setActiveTour('newUser');
        setShowTour(true);
      }, 1000);
    }
  }, [onOpenOnboarding]);

  const renderComponent = (componentName) => {
    const Component = componentMap[componentName];
    if (!Component) {
      console.warn(`Component ${componentName} not found in component map`);
      return <Box p={4}>Component {componentName} not implemented yet</Box>;
    }
    
    // Wrap component with SageTooltip if it has tooltip data
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
    <Box bg={bgColor} minH="100vh">
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
              {renderComponent(activeModal)}
            </ErrorBoundary>
          </Box>
        </Box>
      )}
      
      {/* Onboarding Pane */}
      <OnboardingPane 
        isOpen={isOnboardingOpen} 
        onClose={onCloseOnboarding} 
      />
      
      {/* Help Button */}
      <Box
        position="fixed"
        bottom="80px"
        right="20px"
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
      
      {/* Memory Query Button */}
      <Box
        position="fixed"
        bottom="20px"
        left="20px"
        zIndex="900"
      >
        <Button
          colorScheme="purple"
          onClick={() => openModal('MemoryQueryConsole')}
          size="md"
          boxShadow="md"
        >
          Memory Query
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
  );
};

export default DashboardLayout;
