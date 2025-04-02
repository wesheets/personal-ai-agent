import React, { useState, useEffect, useRef } from 'react';
<<<<<<< HEAD
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  Spinner, 
  Badge, 
=======
import isEqual from 'lodash.isequal';
import {
  Box,
  VStack,
  Text,
  Flex,
  Spinner,
  Badge,
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
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
import isEqual from 'lodash/isEqual';

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

  // Add refs for tracking previous state and render count
  const lastTaskStateRef = useRef(null);
  const renderCountRef = useRef(0);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const lastTasksRef = useRef([]);
  const lastModeRef = useRef('');

  useEffect(() => {
    // Increment render counter for diagnostic purposes
    renderCountRef.current += 1;
    
    if (process.env.NODE_ENV === "development") {
      console.log(`InterruptControl render count: ${renderCountRef.current}`);
    }
  });

  useEffect(() => {
    const fetchControlState = async () => {
      try {
        setLoading(true);
        const controlMode = await controlService.getControlMode();

        let taskState = { tasks: [] };
        try {
          if (
            typeof window !== "undefined" &&
            window.or &&
            Object.prototype.hasOwnProperty.call(window.or, "getTaskState") &&
            typeof window.or.getTaskState === "function"
          ) {
            const fetchedTaskState = await window.or.getTaskState();
            
            // Only update if data has changed (deep comparison)
            if (!isEqual(fetchedTaskState, lastTaskStateRef.current)) {
              if (process.env.NODE_ENV === "development") {
                console.log('Task state changed, updating state');
              }
              lastTaskStateRef.current = JSON.parse(JSON.stringify(fetchedTaskState));
              taskState = fetchedTaskState;
            } else if (process.env.NODE_ENV === "development") {
              console.log('Task state unchanged, skipping update');
              taskState = lastTaskStateRef.current;
            }
          } else {
<<<<<<< HEAD
            if (process.env.NODE_ENV === "development") {
=======
            if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
              console.warn("window.or.getTaskState is not defined or not a function. Using fallback.");
            }
          }
        } catch (err) {
<<<<<<< HEAD
          if (process.env.NODE_ENV === "development") {
=======
          if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
            console.warn("Error while calling window.or.getTaskState:", err);
          }
        }

        if (!isEqual(lastModeRef.current, controlMode.mode)) {
          setSystemState(prev => ({
            ...prev,
            executionMode: controlMode.mode || 'auto'
          }));
          lastModeRef.current = controlMode.mode;
        }

        if (!isEqual(lastTasksRef.current, taskState.tasks)) {
          setActiveTasks(taskState.tasks || []);
          lastTasksRef.current = JSON.parse(JSON.stringify(taskState.tasks));
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch control state');
        setLoading(false);
<<<<<<< HEAD
        if (process.env.NODE_ENV === "development") {
=======
        if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
          console.error('Error fetching control state:', err);
        }
      }
    };

    fetchControlState();
    const intervalId = setInterval(fetchControlState, 3000);
    return () => clearInterval(intervalId);
  }, []);

  const handleModeChange = async (mode) => {
    try {
      await controlService.setControlMode(mode);
      setSystemState(prev => ({
        ...prev,
        executionMode: mode
      }));
    } catch (err) {
<<<<<<< HEAD
      if (process.env.NODE_ENV === "development") {
=======
      if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
        console.error(`Error setting mode to ${mode}:`, err);
      }
    }
  };

  const handleTaskAction = async (taskId, action) => {
    try {
      if (action === 'kill') {
        await controlService.killTask(taskId);
      } else if (action === 'restart') {
        await controlService.restartTask(taskId);
      }
    } catch (err) {
<<<<<<< HEAD
      if (process.env.NODE_ENV === "development") {
=======
      if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
        console.error(`Error performing ${action} on task ${taskId}:`, err);
      }
    }
  };

  const handleTaskRedirect = async (taskId, targetAgent) => {
    if (!targetAgent) return;
    try {
      await controlService.delegateTask(taskId, targetAgent);
    } catch (err) {
<<<<<<< HEAD
      if (process.env.NODE_ENV === "development") {
=======
      if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
        console.error(`Error redirecting task ${taskId} to ${targetAgent}:`, err);
      }
    }
  };

  const openPromptEditor = (task) => {
    setSelectedTask(task);
    setTaskPrompt(task.prompt || '');
    onOpen();
  };

  const handlePromptEdit = async () => {
    try {
      await controlService.editTaskPrompt(selectedTask.task_id, taskPrompt);
      onClose();
      setSelectedTask(null);
      setTaskPrompt('');
    } catch (err) {
<<<<<<< HEAD
      if (process.env.NODE_ENV === "development") {
=======
      if (process.env.NODE_ENV === 'development') {
>>>>>>> 6b2ed86 (Fix: Final layout deduplication + visual stability across polling components)
        console.error(`Error editing prompt for task ${selectedTask.task_id}:`, err);
      }
    }
  };

  if (loading) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} minH="inherit">
          <Spinner size="xl" />
          <Text mt={4}>Loading control panel...</Text>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
        <Box textAlign="center" py={10} color="red.500" minH="inherit">
          <Text fontSize="lg">{error}</Text>
        </Box>
      </Box>
    );
  }

  return (
    <Box h="100%" minH="300px" overflow="hidden" w="full" display="flex" flexDir="column" justifyContent="flex-start">
      <Box mb={6} p={4} borderWidth="1px" borderRadius="lg" bg={bgColor} borderColor={borderColor}>
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

      <Box p={4} borderWidth="1px" borderRadius="lg" bg={bgColor} borderColor={borderColor}>
        <Heading size="md" mb={4}>Active Tasks</Heading>
        {activeTasks.length > 0 ? (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {activeTasks.map((task) => (
              <Box key={task.task_id} p={3} borderWidth="1px" borderRadius="md">
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
                  <Button
                    size="sm"
                    colorScheme="yellow"
                    onClick={() => handleTaskAction(task.task_id, task.status === 'in_progress' ? 'kill' : 'restart')}
                    isDisabled={task.status === 'completed'}
                  >
                    {task.status === 'in_progress' ? 'Kill' : 'Restart'}
                  </Button>
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
            minH="inherit"
          >
            <Text color="gray.500">No active tasks found</Text>
          </Box>
        )}
      </Box>

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
            <Button variant="ghost" mr={3} onClick={onClose}>Cancel</Button>
            <Button colorScheme="blue" onClick={handlePromptEdit}>Save Changes</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default InterruptControl;
