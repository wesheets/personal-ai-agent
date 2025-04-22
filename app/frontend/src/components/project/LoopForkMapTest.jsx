import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
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
  HStack,
  Badge
} from '@chakra-ui/react';
import LoopForkMap from './LoopForkMap';

/**
 * Test component for LoopForkMap
 * 
 * This component demonstrates the LoopForkMap functionality
 * with sample project data and interaction handlers.
 */
const LoopForkMapTest = () => {
  const [selectedProjectId, setSelectedProjectId] = useState('project-123');
  const [selectedLoopId, setSelectedLoopId] = useState(null);
  const toast = useToast();

  // Handle loop selection
  const handleLoopSelect = (loopId) => {
    setSelectedLoopId(loopId);
    toast({
      title: 'Loop Selected',
      description: `Selected loop: ${loopId}`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  // Sample projects for testing
  const sampleProjects = [
    { id: 'project-123', name: 'Memory System Development' },
    { id: 'project-456', name: 'Cognitive Loop Optimization' },
    { id: 'project-789', name: 'Belief System Integration' },
  ];

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Loop Fork Map Test</Heading>
          <Text>
            This test component demonstrates the LoopForkMap functionality with sample project data.
            You can select different projects and interact with the fork map to see how it behaves.
          </Text>
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <FormControl mb={4}>
            <FormLabel>Select Project</FormLabel>
            <Select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
            >
              {sampleProjects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name} ({project.id})
                </option>
              ))}
            </Select>
          </FormControl>

          {selectedLoopId && (
            <Alert status="info" mb={4}>
              <AlertIcon />
              <Box>
                <AlertTitle>Loop Selected</AlertTitle>
                <AlertDescription>
                  Selected loop ID: <Code>{selectedLoopId}</Code>
                </AlertDescription>
              </Box>
            </Alert>
          )}

          <Button
            mb={4}
            onClick={() => setSelectedLoopId(null)}
            isDisabled={!selectedLoopId}
          >
            Clear Selection
          </Button>
        </Box>

        <Divider />

        <Box height="800px">
          <LoopForkMap 
            projectId={selectedProjectId} 
            onLoopSelect={handleLoopSelect} 
          />
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The fork map visualizes how loops branch, merge, and diverge</Text>
            <Text>• Different edge styles indicate fork types:</Text>
            <HStack ml={4}>
              <Badge colorScheme="orange">Orange</Badge>
              <Text>- Active forks</Text>
            </HStack>
            <HStack ml={4}>
              <Badge colorScheme="purple">Purple</Badge>
              <Text>- Merged forks</Text>
            </HStack>
            <HStack ml={4}>
              <Badge colorScheme="gray">Gray (dashed)</Badge>
              <Text>- Skipped forks</Text>
            </HStack>
            <Text>• The graph is interactive - you can zoom, pan, and rearrange nodes</Text>
            <Text>• Toggle between vertical (top-down) and horizontal (left-right) layouts</Text>
            <Text>• Filter options allow hiding skipped or merged loops</Text>
            <Text>• Clicking on a node would typically open the LoopTraceViewer in a real implementation</Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default LoopForkMapTest;
