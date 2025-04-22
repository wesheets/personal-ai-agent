import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Select,
  FormControl,
  FormLabel,
  useToast,
  Container,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Radio,
  RadioGroup,
  Stack
} from '@chakra-ui/react';
import LoopRepairLog from './LoopRepairLog';

/**
 * Test component for LoopRepairLog
 * 
 * This component demonstrates the LoopRepairLog functionality
 * with sample repair history data and filtering options.
 */
const LoopRepairLogTest = () => {
  const [timeFilter, setTimeFilter] = useState('week');
  const [viewMode, setViewMode] = useState('timeline');
  const toast = useToast();

  // Handle refresh
  const handleRefresh = () => {
    toast({
      title: 'Refreshing Data',
      description: 'Fetching the latest repair history...',
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Loop Repair Log Test</Heading>
          <Text>
            This test component demonstrates the LoopRepairLog functionality with sample repair history data.
            You can filter the data and switch between timeline and table views to see how the component behaves.
          </Text>
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Test Controls</Heading>
          
          <HStack spacing={8} mb={4} wrap="wrap">
            <FormControl maxW="200px">
              <FormLabel>Time Filter</FormLabel>
              <Select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
              >
                <option value="all">All Time</option>
                <option value="hour">Past Hour</option>
                <option value="day">Past Day</option>
                <option value="week">Past Week</option>
              </Select>
            </FormControl>
            
            <FormControl maxW="200px">
              <FormLabel>View Mode</FormLabel>
              <RadioGroup value={viewMode} onChange={setViewMode}>
                <Stack direction="row">
                  <Radio value="timeline">Timeline</Radio>
                  <Radio value="table">Table</Radio>
                </Stack>
              </RadioGroup>
            </FormControl>
            
            <Box pt={8}>
              <Button
                colorScheme="blue"
                onClick={handleRefresh}
              >
                Refresh Data
              </Button>
            </Box>
          </HStack>
          
          <Alert status="info" mb={4}>
            <AlertIcon />
            <Box>
              <AlertTitle>Test Configuration</AlertTitle>
              <AlertDescription>
                <Text>Time Filter: <Code>{timeFilter}</Code></Text>
                <Text>View Mode: <Code>{viewMode}</Code></Text>
                <Text mt={2} fontSize="sm">
                  The component is using mock data for demonstration purposes. In a production environment, it would fetch real repair history from the API.
                </Text>
              </AlertDescription>
            </Box>
          </Alert>
        </Box>

        <Divider />

        <Box>
          <Heading size="md" mb={4}>Loop Repair Log</Heading>
          <LoopRepairLog />
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The LoopRepairLog shows a history of failed loops, repair paths, and outcomes</Text>
            <Text>• Two visualization options are available: timeline and table views</Text>
            <Text>• Filtering capabilities include time period, agent, repair type, and outcome</Text>
            <Text>• Clicking on a repair entry opens a detailed modal with before/after metrics</Text>
            <Text>• The component automatically refreshes data every 30 seconds</Text>
            <Text>• Color coding indicates repair types and outcomes for quick visual assessment</Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default LoopRepairLogTest;
