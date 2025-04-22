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
  Badge,
  Switch
} from '@chakra-ui/react';
import BeliefChangeLog from './BeliefChangeLog';

/**
 * Test component for BeliefChangeLog
 * 
 * This component demonstrates the BeliefChangeLog functionality
 * with sample project data and interaction handlers.
 */
const BeliefChangeLogTest = () => {
  const [selectedProjectId, setSelectedProjectId] = useState('project-123');
  const toast = useToast();

  // Sample projects for testing
  const sampleProjects = [
    { id: 'project-123', name: 'Memory System Development' },
    { id: 'project-456', name: 'Cognitive Loop Optimization' },
    { id: 'project-789', name: 'Belief System Integration' },
  ];

  // Handle rollback notification
  const handleRollback = (beliefId, version) => {
    toast({
      title: 'Rollback Initiated',
      description: `Rolling back belief ${beliefId} to version ${version}`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Belief Change Log Test</Heading>
          <Text>
            This test component demonstrates the BeliefChangeLog functionality with sample project data.
            You can select different projects and interact with the belief change log to see how it behaves.
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
        </Box>

        <Divider />

        <Box height="800px">
          <BeliefChangeLog 
            projectId={selectedProjectId} 
          />
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The belief change log tracks how beliefs evolve over time</Text>
            <Text>• Change types are color-coded:</Text>
            <HStack ml={4}>
              <Badge colorScheme="green">Added</Badge>
              <Text>- New beliefs</Text>
            </HStack>
            <HStack ml={4}>
              <Badge colorScheme="blue">Modified</Badge>
              <Text>- Updated beliefs</Text>
            </HStack>
            <HStack ml={4}>
              <Badge colorScheme="red">Deprecated</Badge>
              <Text>- Removed beliefs</Text>
            </HStack>
            <Text>• The accordion view groups beliefs by ID for easy navigation</Text>
            <Text>• Version history shows all changes with timestamps and authoring agents</Text>
            <Text>• Diff view highlights specific changes between versions</Text>
            <Text>• Rollback functionality allows reverting to previous versions</Text>
            <Text>• Filters allow focusing on specific time ranges, agents, or change types</Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default BeliefChangeLogTest;
