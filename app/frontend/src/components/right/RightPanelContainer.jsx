import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel, 
  useColorModeValue,
  Icon,
  Flex,
  Text,
  Spinner,
  Tooltip
} from '@chakra-ui/react';
import { 
  FaFolder, 
  FaServer, 
  FaShieldAlt, 
  FaScroll, 
  FaChartLine,
  FaExclamationTriangle
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

// Import panel components
import FileTreePanel from './FileTreePanel';
import SystemHealthPanel from './SystemHealthPanel';
import RebuildStatusDisplay from './RebuildStatusDisplay';
import TrustScoreDisplay from './TrustScoreDisplay';
import LoopDriftIndex from './LoopDriftIndex';
import AuditLogViewer from './AuditLogViewer';
import MetricsVisualization from './MetricsVisualization';
import { LoadingCard } from '../LoadingStates';

/**
 * RightPanelContainer Component
 * 
 * A tabbed container that houses all diagnostic and system visibility tools.
 * Allows switching between different views: Files, System, Trust, Logs, and Metrics.
 */
const RightPanelContainer = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [projectId, setProjectId] = useState('');
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const tabBgColor = useColorModeValue('gray.50', 'gray.800');
  const activeTabColor = useColorModeValue('blue.500', 'blue.300');
  
  // Fetch current project context
  const { 
    data: projectData, 
    error, 
    loading 
  } = useFetch('/api/projects/active', {}, {
    refreshInterval: 30000, // Refresh every 30 seconds
    initialData: {
      projectId: 'promethios-core',
      name: 'Promethios Core'
    },
    transformResponse: (data) => ({
      projectId: data.projectId || 'promethios-core',
      name: data.name || 'Promethios Core'
    })
  });
  
  // Update project ID when data changes
  useEffect(() => {
    if (projectData && projectData.projectId) {
      setProjectId(projectData.projectId);
    }
  }, [projectData]);
  
  // Tab configuration
  const tabs = [
    { 
      name: 'Files', 
      icon: FaFolder, 
      component: FileTreePanel,
      description: 'File system explorer'
    },
    { 
      name: 'System', 
      icon: FaServer, 
      components: [SystemHealthPanel, RebuildStatusDisplay],
      description: 'System health and rebuild status'
    },
    { 
      name: 'Trust', 
      icon: FaShieldAlt, 
      components: [TrustScoreDisplay, LoopDriftIndex],
      description: 'Trust scores and loop drift metrics'
    },
    { 
      name: 'Logs', 
      icon: FaScroll, 
      component: AuditLogViewer,
      description: 'System audit logs'
    },
    { 
      name: 'Metrics', 
      icon: FaChartLine, 
      component: MetricsVisualization,
      description: 'Performance metrics visualization'
    }
  ];
  
  const handleTabChange = (index) => {
    setActiveTab(index);
  };
  
  // Render a single component or multiple components in a tab panel
  const renderTabContent = (tabConfig) => {
    if (loading) {
      return <LoadingCard message="Loading panel data..." />;
    }
    
    if (error) {
      return (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading data: {error}</Text>
        </Flex>
      );
    }
    
    // If tab has multiple components
    if (tabConfig.components) {
      return tabConfig.components.map((Component, idx) => (
        <Box key={idx} mb={idx < tabConfig.components.length - 1 ? 4 : 0}>
          <Component projectId={projectId} />
        </Box>
      ));
    }
    
    // If tab has a single component
    if (tabConfig.component) {
      const Component = tabConfig.component;
      return <Component projectId={projectId} />;
    }
    
    return <Text>No content available</Text>;
  };
  
  return (
    <Box 
      borderRadius="lg" 
      bg={bgColor} 
      borderWidth="1px" 
      borderColor={borderColor} 
      overflow="hidden"
      height="100%"
      position="relative"
    >
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px" zIndex={1}>
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px" zIndex={1}>
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Tabs 
        variant="enclosed" 
        colorScheme="blue" 
        onChange={handleTabChange} 
        index={activeTab}
        height="100%"
        display="flex"
        flexDirection="column"
      >
        <TabList bg={tabBgColor}>
          {tabs.map((tab, idx) => (
            <Tab 
              key={idx} 
              _selected={{ 
                color: activeTabColor, 
                borderBottomColor: activeTabColor,
                fontWeight: 'bold'
              }}
            >
              <Tooltip label={tab.description}>
                <Flex align="center">
                  <Icon as={tab.icon} mr={2} />
                  <Text display={{ base: 'none', md: 'block' }}>{tab.name}</Text>
                </Flex>
              </Tooltip>
            </Tab>
          ))}
        </TabList>
        
        <TabPanels flex="1" overflowY="auto">
          {tabs.map((tab, idx) => (
            <TabPanel key={idx} p={4} height="100%">
              {renderTabContent(tab)}
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default RightPanelContainer;
