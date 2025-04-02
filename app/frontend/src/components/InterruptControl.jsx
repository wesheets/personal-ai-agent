import React, { useState, useEffect, useMemo } from 'react';
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
  Divider,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { controlService } from '../services/api';
import isEqual from 'lodash/isEqual';

// Initialize window.or and getTaskState at the module level
// This ensures it happens before any component rendering
(function initializeGlobalOrchestrator() {
  try {
    if (typeof window !== 'undefined') {
      if (!window.or) {
        console.warn("⚠️ window.or not found, creating empty object");
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        console.warn("⚠️ Injecting mock getTaskState into window.or at module level");
        window.or.getTaskState = async () => {
          console.warn("🛑 Mock getTaskState invoked – returning empty array");
          return { tasks: [] };
        };
      } else {
        console.log("✅ getTaskState exists and is safe to use at module level");
      }
    }
  } catch (err) {
    console.error("🔥 Error initializing global orchestrator:", err);
  }
})();

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
  const [interruptSystemOffline, setInterruptSystemOffline] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Double-check window.or.getTaskState on component mount as a safety measure
  useEffect(() => {
    try {
      if (!window.or) {
        console.warn("⚠️ window.or still not found after module init, creating empty object");
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        console.warn("⚠️ Re-injecting mock getTaskState into window.or");
        window.or.getTaskState = async () => {
          console.warn("🛑 Mock getTaskState invoked – returning empty array");
          return { tasks: [] };
        };
      } else {
        console.log("✅ getTaskState exists and is safe to use in component");
      }
    } catch (err) {
      console.error("🔥 Error in component getTaskState check:", err);
      setInterruptSystemOffline(true);
    }
  }, []);

  useEffect(() => {
    const fetchControlState = async () => {
      try {
        // Only show loading on initial fetch, not during polling updates
        if (activeTasks.length === 0 && systemState.executionMode === 'auto') {
          setLoading(true);
        }
        
        const controlMode = await controlService.getControlMode();

        // Strict guard for or.getTaskState fallback logic with retry
        let taskState = { tasks: [] };

        try {
          // Extra defensive check before calling
          if (typeof window.or?.getTaskState !== "function") {
            console.warn("⚠️ getTaskState still not a function before fetch attempt");
            throw new Error("getTaskState is not available");
          }
          
          const res = await window.or.getTaskState();
          if (!isEqual(taskState, res)) {
            taskState = res;
          }
          if (process.env.NODE_ENV === "development") {
            console.log("✅ Successfully fetched task state:", taskState);
          }
          setInterruptSystemOffline(false);
        } catch (err) {
          console.warn("Error while calling window.or.getTaskState:", err);
          setInterruptSystemOffline(true);
          
          // Implement retry logic with exponential backoff
          if (retryCount < 3) {
            const timeout = Math.pow(2, retryCount) * 1000;
            console.log(`⏱️ Retrying in ${timeout/1000} seconds...`);
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, timeout);
          }
        }

        // Compare data before updating state to avoid unnecessary re-renders
        const modeChanged = controlMode.mode !== systemState.executionMode;
        const tasksChanged = !isEqual(taskState.tasks, activeTasks);
        
        if (modeChanged) {
          setSystemState(prevState => ({
            ...prevState,
            executionMode: controlMode.mode || 'auto'
          }));
        }

        if (tasksChanged) {
          setActiveTasks(taskState.tasks || []);
        }
        
        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch control state');
        setLoading(false);
        console.error('Error fetching control state:', err);
      }
    };

    fetchControlState();
    // Set up polling for real-time updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchControlState, 5000);
    return () => clearInterval(intervalId);
  }, [retryCount]); // Re-run when retryCount changes

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

  const handleTaskRedirect = async (taskId, targetAgent) => {
    if (!targetAgent) return;
    try {
      await controlService.delegateTask(taskId, targetAgent);
    } catch (err) {
      console.error(`Error redirecting task ${taskId} to ${targetAgent}:`, err);
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
      console.error(`Error editing prompt for task ${selectedTask.task_id}:`, err);
    }
  };

  // Memoize the tasks list to prevent unnecessary re-renders
  const memoizedTasks = useMemo(() => activeTasks, [activeTasks]);

  if (loading) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading control panel...</Text>
        </Flex>
      </Box>
    );
  }

  if (error) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Text fontSize="lg" color="red.500">{error}</Text>
      </Box>
    );
  }

  return (
    <Box minH="inherit">
      {interruptSystemOffline && (
        <Alert status="warning" variant="left-accent" mb={4}>
          <AlertIcon />
          Interrupt system offline – retrying soon
        </Alert>
      )}
      
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

      <Box p={4} borderWidth="1px" borderRadius="lg" bg={bgColor} borderColor={borderColor} minH="120px">
        <Heading size="md" mb={4}>Active Tasks</Heading>
        {memoizedTasks.length > 0 ? (
          <VStack spacing={4} align="stretch" divider={<Divider />}>
            {memoizedTasks.filter(task => task).map((task) => (
              <Box key={task?.task_id || `task-${Math.random()}`} p={3} borderWidth="1px" borderRadius="md">
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                  <Text fontWeight="bold">{task?.title || 'Untitled Task'}</Text>
                  <Badge colorScheme={task?.status === 'in_progress' ? 'blue' : 'yellow'}>
                    {task?.status || 'unknown'}
                  </Badge>
                </Flex>
                <Text fontSize="sm" mb={3}>
                  Agent: {task?.assigned_agent || 'Unassigned'}
                </Text>
                <Flex gap={2} wrap="wrap">
                  <Button 
                    size="sm"
                    colorScheme="yellow"
                    onClick={() => handleTaskAction(task?.task_id, task?.status === 'in_progress' ? 'kill' : 'restart')}
                    isDisabled={task?.status === 'completed'}
                  >
                    {task?.status === 'in_progress' ? 'Kill' : 'Restart'}
                  </Button>
                  <Select 
                    size="sm"
                    placeholder="Redirect to..."
                    onChange={(e) => handleTaskRedirect(task?.task_id, e.target.value)}
                    isDisabled={task?.status === 'completed'}
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
                      isDisabled={task?.status === 'completed'}
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
            minH="inherit"
            display="flex"
            alignItems="center"
            justifyContent="center"
            borderWidth="1px" 
            borderRadius="md" 
            borderStyle="dashed" 
            borderColor={borderColor}
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
