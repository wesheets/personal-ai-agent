import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Spinner, 
  Badge, 
  Button,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Textarea,
  useDisclosure,
  useColorModeValue,
  Heading,
  Divider
} from '@chakra-ui/react';
import { controlService } from '../services/api';

const InterruptControl = () => {
  const [systemState, setSystemState] = useState({
    executionMode: 'auto',
    activeAgents: ['builder', 'research', 'memory', 'ops']
  });
  const [activeTasks, setActiveTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskPrompt, setTaskPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    // Function to fetch system control state
    const fetchControlState = async () => {
      try {
        setLoading(true);
        const controlMode = await controlService.getControlMode();
        
        // Safe fallback logic for getTaskState
        let taskState = [];
        
        if (typeof window !== "undefined" && window.or && typeof window.or.getTaskState === "function") {
          try {
            taskState = await window.or.getTaskState();
          } catch (err) {
            console.warn("getTaskState threw an error:", err);
          }
        } else {
          console.warn("getTaskState not available – using fallback");
        }
        
        setSystemState(prevState => ({
          ...prevState,
          executionMode: controlMode.mode || 'auto'
        }));
        
        setActiveTasks(taskState.tasks || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch control state');
        setLoading(false);
        console.error('Error fetching control state:', err);
      }
    };

    // Initial fetch
    fetchControlState();

    // Set up polling for real-time updates (every 3 seconds)
    const intervalId = setInterval(fetchControlState, 3000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Handle execution mode change
  const handleModeChange = async (mode) => {
    try {
      await controlService.setControlMode(mode);
      setSystemState(prevState => ({
        ...prevState,
        executionMode: mode
      }));
    } catch (err) {
      console.error(`Error setting mode to ${mode}:`, err);
    }
  };

  // Handle task actions (kill/restart)
  const handleTaskAction = async (taskId, action) => {
    try {
      if (action === 'kill') {
        await controlService.killTask(taskId);
      } else if (action === 'restart') {
        await controlService.restartTask(taskId);
      }
    } catch (err) {
      console.error(`Error performing ${action} on task ${taskId}:`, err);
    }
  };

  // Handle task redirection to another agent
  const handleTaskRedirect = async (taskId, targetAgent) => {
    if (!targetAgent) return;
    
    try {
      await controlService.delegateTask(taskId, targetAgent);
    } catch (err) {
      console.error(`Error redirecting task ${taskId} to ${targetAgent}:`, err);
    }
  };

  // Open prompt editor modal
  const openPromptEditor = (task) => {
    setSelectedTask(task);
    setTaskPrompt(task.prompt || '');
    onOpen();
  };

  // Handle prompt edit submission
  const handlePromptEdit = async () => {
    try {
      await controlService.editTaskPrompt(selectedTask.task_id, taskPrompt);
      onClose();
      setSelectedTask(null);
      setTaskPrompt('');
    } catch (err) {
      console.error(`Error editing prompt for task ${selectedTask.task_id}:`, err);
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading control panel...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} color="red.500">
        <Text fontSize="lg">{error}</Text>
      </Box>
    );
  }

  return (
    <Box>
      {/* System execution mode controls */}
      <Box 
        mb={6} 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        bg={bgColor} 
        borderColor={borderColor}
      >
        <Heading size="md" mb={4}>Execution Control</Heading>
        <Flex gap={3}>
          <Button 
            colorScheme={systemState.executionMode === 'auto' ? 'blue' : 'gray'}
            onClick={() => handleModeChange('auto')}
            flex="1"
          >
            Auto Mode
          </Button>
          
          <Button 
            colorScheme={systemState.executionMode === 'manual' ? 'blue' : 'gray'}
            onClick={() => handleModeChange('manual')}
            flex="1"
          >
            Manual Mode
          </Button>
          
          <Button 
            colorScheme={systemState.executionMode === 'paused' ? 'yellow' : 'gray'}
            onClick={() => handleModeChange('paused')}
            flex="1"
          >
            Pause All
          </Button>
        </Flex>
      </Box>
      
      {/* Active tasks control */}
      <Box 
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        bg={bgColor} 
        borderColor={borderColor}
      >
        <Heading size="md" mb={4}>Active Tasks</Heading>
        {activeTasks.length > 0 ? (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {activeTasks.map((task) => (
              <Box 
                key={task.task_id} 
                p={3} 
                borderWidth="1px" 
                borderRadius="md"
              >
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="bold">{task.title}</Text>
                  <Badge colorScheme={task.status === 'in_progress' ? 'blue' : 'yellow'}>
                    {task.status}
                  </Badge>
                </Flex>
                
                <Text fontSize="sm" mb={3}>
                  Agent: {task.assigned_agent || 'Unassigned'}
                </Text>
                
                <Flex gap={2} wrap="wrap">
                  {/* Kill/restart task */}
                  <Button 
                    size="sm"
                    colorScheme="yellow"
                    onClick={() => handleTaskAction(task.task_id, task.status === 'in_progress' ? 'kill' : 'restart')}
                    isDisabled={task.status === 'completed'}
                  >
                    {task.status === 'in_progress' ? 'Kill' : 'Restart'}
                  </Button>
                  
                  {/* Redirect task */}
                  <Select 
                    size="sm"
                    placeholder="Redirect to..."
                    onChange={(e) => handleTaskRedirect(task.task_id, e.target.value)}
                    isDisabled={task.status === 'completed'}
                    maxW="200px"
                  >
                    {systemState.activeAgents.map((agent) => (
                      <option key={agent} value={agent}>{agent}</option>
                    ))}
                  </Select>
                  
                  {/* Edit prompt (Manual Mode only) */}
                  {systemState.executionMode === 'manual' && (
                    <Button 
                      size="sm"
                      colorScheme="blue"
                      onClick={() => openPromptEditor(task)}
                      isDisabled={task.status === 'completed'}
                    >
                      Edit Prompt
                    </Button>
                  )}
                </Flex>
              </Box>
            ))}
          </VStack>
        ) : (
          <Box 
            textAlign="center" 
            py={6} 
            borderWidth="1px" 
            borderRadius="md" 
            borderStyle="dashed"
            borderColor={borderColor}
          >
            <Text color="gray.500">No active tasks found</Text>
          </Box>
        )}
      </Box>
      
      {/* Prompt editor modal (Manual Mode only) */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Edit Task Prompt</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {selectedTask && (
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontWeight="bold">Task:</Text>
                  <Text>{selectedTask.title}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">ID:</Text>
                  <Text fontSize="sm">{selectedTask.task_id}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="bold" mb={2}>Task Prompt:</Text>
                  <Textarea
                    value={taskPrompt}
                    onChange={(e) => setTaskPrompt(e.target.value)}
                    rows={10}
                  />
                </Box>
              </VStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handlePromptEdit}>
              Save Changes
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default InterruptControl;
