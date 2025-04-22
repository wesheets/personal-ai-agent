import React from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Heading,
  Code,
  UnorderedList,
  ListItem,
  Divider
} from '@chakra-ui/react';

/**
 * Right Panel Components Documentation
 * 
 * This document provides an overview of the RIGHT zone components for the Promethios UI.
 * It includes details about the RightPanelContainer and all individual components that
 * are mounted inside it.
 */

const RightPanelDocumentation = () => {
  return (
    <Box p={8}>
      <Heading as="h1" size="xl" mb={6}>RIGHT Zone Components Documentation</Heading>
      
      <Text mb={4}>
        The RIGHT zone of the Promethios UI contains diagnostic and system visibility tools
        organized in a tabbed container. This document provides an overview of the components
        and their functionality.
      </Text>
      
      <Divider my={6} />
      
      <Heading as="h2" size="lg" mb={4}>RightPanelContainer</Heading>
      <Text mb={4}>
        The RightPanelContainer is the main container component that houses all diagnostic tools
        in a tabbed interface. It allows operators to switch between different views: Files, System,
        Trust, Logs, and Metrics.
      </Text>
      
      <Heading as="h3" size="md" mb={2}>Features</Heading>
      <UnorderedList mb={4}>
        <ListItem>Tabbed interface with icon and text labels</ListItem>
        <ListItem>Project-aware via projectId state</ListItem>
        <ListItem>Responsive design for both desktop and mobile</ListItem>
        <ListItem>Error handling and loading states</ListItem>
        <ListItem>Tooltips for tab descriptions</ListItem>
      </UnorderedList>
      
      <Heading as="h3" size="md" mb={2}>API Integration</Heading>
      <Text mb={2}>
        The RightPanelContainer fetches the current project context from:
      </Text>
      <Code p={2} mb={4} display="block">
        /api/projects/active
      </Code>
      
      <Divider my={6} />
      
      <Heading as="h2" size="lg" mb={4}>Individual Components</Heading>
      
      <VStack align="stretch" spacing={6}>
        {/* FileTreePanel */}
        <Box>
          <Heading as="h3" size="md" mb={2}>FileTreePanel</Heading>
          <Text mb={2}>
            Displays a hierarchical file tree for the current project with expandable folders
            and file size information.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/files/tree?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Expandable folder structure</ListItem>
            <ListItem>File size formatting</ListItem>
            <ListItem>Folder/file icons</ListItem>
            <ListItem>Hover effects for better UX</ListItem>
          </UnorderedList>
        </Box>
        
        {/* SystemHealthPanel */}
        <Box>
          <Heading as="h3" size="md" mb={2}>SystemHealthPanel</Heading>
          <Text mb={2}>
            Displays system health metrics including CPU, memory, network, and service status.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/system/health?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Resource usage visualization (CPU, memory, disk, network)</ListItem>
            <ListItem>Service status with uptime information</ListItem>
            <ListItem>System alerts with severity indicators</ListItem>
            <ListItem>Color-coded status indicators</ListItem>
          </UnorderedList>
        </Box>
        
        {/* RebuildStatusDisplay */}
        <Box>
          <Heading as="h3" size="md" mb={2}>RebuildStatusDisplay</Heading>
          <Text mb={2}>
            Displays the status of system rebuilds and cognitive restructuring processes.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/rebuild/status?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Active rebuild progress tracking</ListItem>
            <ListItem>Recent rebuilds history</ListItem>
            <ListItem>Rebuild schedule information</ListItem>
            <ListItem>Manual rebuild trigger</ListItem>
          </UnorderedList>
        </Box>
        
        {/* TrustScoreDisplay */}
        <Box>
          <Heading as="h3" size="md" mb={2}>TrustScoreDisplay</Heading>
          <Text mb={2}>
            Displays trust scores and reliability metrics for the cognitive system.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/trust/scores?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Overall trust score visualization</ListItem>
            <ListItem>Trust categories breakdown</ListItem>
            <ListItem>Recent trust-related events</ListItem>
            <ListItem>Trend indicators for each metric</ListItem>
          </UnorderedList>
        </Box>
        
        {/* LoopDriftIndex */}
        <Box>
          <Heading as="h3" size="md" mb={2}>LoopDriftIndex</Heading>
          <Text mb={2}>
            Displays cognitive loop drift metrics and anomalies.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/loop/drift?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Overall drift index visualization</ListItem>
            <ListItem>Drift metrics table with thresholds</ListItem>
            <ListItem>Detected anomalies with severity indicators</ListItem>
            <ListItem>Historical drift visualization</ListItem>
          </UnorderedList>
        </Box>
        
        {/* AuditLogViewer */}
        <Box>
          <Heading as="h3" size="md" mb={2}>AuditLogViewer</Heading>
          <Text mb={2}>
            Displays system audit logs with filtering and search capabilities.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/audit/logs?projectId={'{projectId}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Log search functionality</ListItem>
            <ListItem>Filtering by log type and severity</ListItem>
            <ListItem>Color-coded severity indicators</ListItem>
            <ListItem>Log export functionality</ListItem>
            <ListItem>Pagination information</ListItem>
          </UnorderedList>
        </Box>
        
        {/* MetricsVisualization */}
        <Box>
          <Heading as="h3" size="md" mb={2}>MetricsVisualization</Heading>
          <Text mb={2}>
            Displays system performance metrics and visualizations.
          </Text>
          <Heading as="h4" size="sm" mb={1}>API Endpoint</Heading>
          <Code p={2} mb={2} display="block">
            /api/metrics?projectId={'{projectId}'}&timeRange={'{timeRange}'}&type={'{metricType}'}
          </Code>
          <Heading as="h4" size="sm" mb={1}>Features</Heading>
          <UnorderedList>
            <ListItem>Performance, cognitive, and operational metrics</ListItem>
            <ListItem>Time range selection</ListItem>
            <ListItem>Bar chart visualizations for trends</ListItem>
            <ListItem>Metrics export functionality</ListItem>
            <ListItem>Trend indicators for each metric</ListItem>
          </UnorderedList>
        </Box>
      </VStack>
      
      <Divider my={6} />
      
      <Heading as="h2" size="lg" mb={4}>Integration</Heading>
      <Text mb={4}>
        The RIGHT zone components are integrated into the Promethios UI through the UIZoneSchema.json
        configuration. The RightPanelContainer is the only component directly referenced in the schema,
        and it dynamically loads the individual components based on the selected tab.
      </Text>
      
      <Heading as="h3" size="md" mb={2}>Schema Configuration</Heading>
      <Code p={2} mb={4} display="block">
        {`{
  "zones": {
    "RIGHT": [
      "RightPanelContainer"
    ]
  }
}`}
      </Code>
      
      <Heading as="h3" size="md" mb={2}>Component Dependencies</Heading>
      <Text mb={2}>
        All components depend on the following shared utilities:
      </Text>
      <UnorderedList mb={4}>
        <ListItem>useFetch hook for API integration</ListItem>
        <ListItem>Chakra UI for styling and components</ListItem>
        <ListItem>React Icons for iconography</ListItem>
      </UnorderedList>
      
      <Divider my={6} />
      
      <Heading as="h2" size="lg" mb={4}>Best Practices</Heading>
      <UnorderedList mb={4}>
        <ListItem>All components should use the useFetch hook for API integration</ListItem>
        <ListItem>Include proper error handling and loading states</ListItem>
        <ListItem>Make components project-aware via projectId parameter</ListItem>
        <ListItem>Follow schema compliance as specified in the requirements</ListItem>
        <ListItem>Use Chakra UI components for consistent styling</ListItem>
        <ListItem>Implement responsive design for both desktop and mobile</ListItem>
      </UnorderedList>
    </Box>
  );
};

export default RightPanelDocumentation;
