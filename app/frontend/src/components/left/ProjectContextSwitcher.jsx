import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Select, 
  Text, 
  Flex, 
  Heading, 
  useColorModeValue,
  Button,
  Icon,
  Spinner,
  Tooltip,
  useToast
} from '@chakra-ui/react';
import { FaExchangeAlt, FaPlus, FaExclamationTriangle } from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * ProjectContextSwitcher Component
 * 
 * Allows operators to switch between different project contexts.
 * Connected to /api/projects/list endpoint for project data.
 */
const ProjectContextSwitcher = () => {
  const [selectedProject, setSelectedProject] = useState('');
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const accentColor = useColorModeValue('blue.500', 'blue.300');
  const toast = useToast();
  
  // Fetch projects from API
  const { 
    data: projectsData, 
    error, 
    loading, 
    refetch 
  } = useFetch('/api/projects/list', {}, {
    initialData: {
      projects: [
        { id: 'promethios-core', name: 'Promethios Core' },
        { id: 'cognitive-stability', name: 'Cognitive Stability' },
        { id: 'loop-hardening', name: 'Loop Hardening' },
        { id: 'ui-integration', name: 'UI Integration' }
      ],
      activeProject: 'promethios-core'
    },
    transformResponse: (data) => ({
      projects: Array.isArray(data.projects) ? data.projects : [],
      activeProject: data.activeProject || ''
    })
  });
  
  // Set selected project when data is loaded
  useEffect(() => {
    if (projectsData && projectsData.activeProject) {
      setSelectedProject(projectsData.activeProject);
    } else if (projectsData && projectsData.projects && projectsData.projects.length > 0) {
      setSelectedProject(projectsData.projects[0].id);
    }
  }, [projectsData]);
  
  const handleProjectChange = async (e) => {
    const newProjectId = e.target.value;
    setSelectedProject(newProjectId);
    
    try {
      // Call API to update active project
      const response = await fetch('/api/projects/set-active', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId: newProjectId }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to set active project: ${response.status}`);
      }
      
      toast({
        title: "Project context updated",
        description: `Switched to ${projectsData.projects.find(p => p.id === newProjectId)?.name || newProjectId}`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      // In a real implementation, this would update a global context
      // and potentially trigger data reloading for the new project
    } catch (err) {
      console.error('Error setting active project:', err);
      toast({
        title: "Failed to switch project",
        description: err.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleCreateProject = () => {
    // In a real implementation, this would open a modal or navigate to project creation page
    console.log('Create new project clicked');
  };
  
  return (
    <Box 
      p={4} 
      borderRadius="md" 
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
      position="relative"
    >
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px">
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px">
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Flex justifyContent="space-between" alignItems="center" mb={3}>
        <Heading size="sm">Project Context</Heading>
        <Button 
          size="xs" 
          leftIcon={<Icon as={FaPlus} />} 
          colorScheme="blue" 
          variant="ghost"
          onClick={handleCreateProject}
        >
          New
        </Button>
      </Flex>
      
      <Flex alignItems="center">
        <Icon as={FaExchangeAlt} color={accentColor} mr={2} />
        <Select 
          value={selectedProject} 
          onChange={handleProjectChange}
          size="md"
          variant="filled"
          isDisabled={loading || !projectsData || projectsData.projects.length === 0}
        >
          {projectsData && projectsData.projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </Select>
      </Flex>
      
      <Text fontSize="xs" mt={2} color="gray.500">
        All operations scoped to selected project
      </Text>
    </Box>
  );
};

export default ProjectContextSwitcher;
