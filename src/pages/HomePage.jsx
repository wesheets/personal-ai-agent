import React from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  HStack, 
  Text, 
  Icon, 
  useColorModeValue,
  Divider,
  Heading,
  Button,
  SimpleGrid
} from '@chakra-ui/react';
import { FiMessageCircle, FiUsers, FiActivity, FiSettings } from 'react-icons/fi';
import AppShell from '../components/layout/AppShell';
import PageHeader from '../components/layout/PageHeader';
import DashboardStats from '../components/layout/DashboardStats';
import AgentCard from '../components/layout/AgentCard';
import ActivityFeed from '../components/layout/ActivityFeed';
import ContentLayout from '../components/layout/ContentLayout';

// Sample data for demonstration
const sampleAgents = [
  {
    name: 'HAL',
    description: 'General purpose assistant for everyday tasks and questions.',
    status: 'idle',
    isSystem: true,
    lastActive: '2 hours ago'
  },
  {
    name: 'ASH',
    description: 'Advanced security handler for sensitive operations and security monitoring.',
    status: 'active',
    isSystem: true,
    lastActive: '5 minutes ago'
  },
  {
    name: 'Research Agent',
    description: 'Specialized in research tasks, data analysis, and information gathering.',
    status: 'idle',
    isSystem: false,
    lastActive: 'Yesterday'
  },
  {
    name: 'Code Assistant',
    description: 'Helps with programming tasks, code reviews, and technical documentation.',
    status: 'busy',
    isSystem: false,
    lastActive: '3 days ago'
  }
];

const sampleActivities = [
  {
    title: 'Security scan completed',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    agent: { name: 'ASH' },
    type: 'success',
    message: 'No security issues found in the system.'
  },
  {
    title: 'New message received',
    timestamp: new Date(Date.now() - 1000 * 60 * 120), // 2 hours ago
    agent: { name: 'HAL' },
    type: 'message',
    message: 'User requested information about climate change data.'
  },
  {
    title: 'System update available',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
    type: 'info',
    message: 'A new system update is available. Please restart the application to apply.'
  }
];

const HomePage = () => {
  return (
    <AppShell>
      <PageHeader
        title="Dashboard"
        subtitle="Welcome to Promethios OS"
        icon={FiActivity}
        status={{ type: 'success', text: 'System Operational' }}
      />
      
      <VStack spacing={8} align="stretch">
        {/* Stats Section */}
        <Box>
          <DashboardStats />
        </Box>
        
        {/* Agents Section */}
        <ContentLayout
          title="Your Agents"
          subtitle="Access your AI assistants"
          actions={
            <Button leftIcon={<FiUsers />} colorScheme="blue">
              View All Agents
            </Button>
          }
        >
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={4}>
            {sampleAgents.map((agent, index) => (
              <AgentCard
                key={index}
                {...agent}
                onClick={() => console.log(`Clicked on ${agent.name}`)}
              />
            ))}
          </SimpleGrid>
        </ContentLayout>
        
        {/* Activity Section */}
        <ContentLayout
          title="Recent Activity"
          subtitle="Latest updates and notifications"
          actions={
            <Button leftIcon={<FiActivity />} colorScheme="blue" variant="outline">
              View All Activity
            </Button>
          }
        >
          <Box mt={4}>
            <ActivityFeed activities={sampleActivities} />
          </Box>
        </ContentLayout>
      </VStack>
    </AppShell>
  );
};

export default HomePage;
