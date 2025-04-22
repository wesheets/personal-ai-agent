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
  Code
} from '@chakra-ui/react';
import ProjectTimelineViewer from './ProjectTimelineViewer';

/**
 * Test component for ProjectTimelineViewer
 * 
 * This component demonstrates the ProjectTimelineViewer functionality
 * with sample project data and interaction handlers.
 */
const ProjectTimelineViewerTest = () => {
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
          <Heading size="lg" mb={4}>Project Timeline Viewer Test</Heading>
          <Text>
            This test component demonstrates the ProjectTimelineViewer functionality with sample project data.
            You can select different projects and interact with the timeline to see how it behaves.
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
          <ProjectTimelineViewer 
            projectId={selectedProjectId} 
            onLoopSelect={handleLoopSelect} 
          />
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The timeline supports both vertical and horizontal orientations</Text>
            <Text>• Forks are visually indicated with branch icons and indentation</Text>
            <Text>• Trust scores and drift indices are color-coded for quick assessment</Text>
            <Text>• Time filters allow focusing on recent changes</Text>
            <Text>• Agent filters help track contributions from specific agents</Text>
            <Text>• Clicking on a loop node would typically open the LoopTraceViewer in a real implementation</Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default ProjectTimelineViewerTest;
