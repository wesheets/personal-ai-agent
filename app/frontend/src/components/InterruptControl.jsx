import React, { useState, useEffect, useMemo, useRef } from 'react';
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
  FormControl,
  FormLabel,
  Textarea,
  useDisclosure,
  useColorModeValue
} from '@chakra-ui/react';
import { controlService } from '../services/api';
import isEqual from 'lodash/isEqual';

// This ensures it happens before any component rendering
(function initializeGlobalOrchestrator() {
  try {
    if (typeof window !== 'undefined') {
      if (!window.or) {
        console.warn("⚠️ window.or not found, creating empty object");
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        if (process.env.NODE_ENV === "development") {
          console.warn("⚠️ Injecting mock getTaskState into window.or at module level");
        }
        window.or.getTaskState = async () => {
          if (process.env.NODE_ENV === "development") {
            console.warn("🛑 Mock getTaskState invoked – returning empty array");
          }
          return { tasks: [] };
        };
      } else if (process.env.NODE_ENV === "development") {
        console.log("✅ getTaskState exists and is safe to use at module level");
      }
    }
  } catch (err) {
    if (process.env.NODE_ENV === "development") {
      console.error("🔥 Error initializing global orchestrator:", err);
    }
  }
})();

const InterruptControl = () => {
  const [systemState, setSystemState] = useState({
    executionMode: 'auto',
    tasks: []
  });
  const [controlMode, setControlMode] = useState({ mode: 'auto' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [interruptSystemOffline, setInterruptSystemOffline] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskPrompt, setTaskPrompt] = useState('');
  const [activeTasks, setActiveTasks] = useState([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Add refs to store previous values for comparison
  const prevTaskStateRef = useRef(null);
  const prevControlModeRef = useRef(null);

  // Diagnostic DOM logging to detect component redraws
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("InterruptControl component rendered/redrawn");
    }
  });

  // Double-check window.or.getTaskState on component mount as a safety measure
  useEffect(() => {
    try {
      if (!window.or) {
        if (process.env.NODE_ENV === "development") {
          console.warn("⚠️ window.or still not found after module init, creating empty object");
        }
        window.or = {};
      }

      if (typeof window.or.getTaskState !== "function") {
        if (process.env.NODE_ENV === "development") {
          console.warn("⚠️ Re-injecting mock getTaskState into window.or");
        }
        window.or.getTaskState = async () => {
          if (process.env.NODE_ENV === "development") {
            console.warn("🛑 Mock getTaskState invoked – returning empty array");
          }
          return { tasks: [] };
        };
      } else if (process.env.NODE_ENV === "development") {
        console.log("✅ getTaskState exists and is safe to use in component");
      }
    } catch (err) {
      if (process.env.NODE_ENV === "development") {
        console.error("🔥 Error in component getTaskState check:", err);
      }
      setInterruptSystemOffline(true);
    }
  }, []);

  useEffect(() => {
    const fetchControlState = async () => {
      try {
        // Only show loading on initial fetch, not during polling updates
        if (activeTasks.length === 0) {
          setLoading(true);
        }
        
        const res = await controlService.getControlMode();
        
        // Compare data before updating state to avoid unnecessary re-renders
        const modeChanged = !isEqual(prevControlModeRef.current, res.data);
        if (modeChanged) {
          prevControlModeRef.current = res.data;
          setControlMode(res.data);
        }
        
        // Strict guard for or.getTaskState fallback logic with retry
        let taskState = { tasks: [] };

        try {
          // Extra defensive check before calling
          if (typeof window.or?.getTaskState !== "function") {
            if (process.env.NODE_ENV === "development") {
              console.warn("⚠️ getTaskState still not a function before fetch attempt");
            }
            throw new Error("getTaskState is not available");
          }
          
          const res = await window.or.getTaskState();
          
          // Deep compare task state before updating to prevent unnecessary re-renders
          if (!isEqual(prevTaskStateRef.current, res)) {
            prevTaskStateRef.current = res;
            taskState = res;
            if (process.env.NODE_ENV === "development") {
              console.log("✅ Successfully fetched task state:", taskState);
            }
          }
          setInterruptSystemOffline(false);
        } catch (err) {
          console.warn("Error while calling window.or.getTaskState:", err);
          setInterruptSystemOffline(true);
          
          // Implement retry logic with exponential backoff
          if (retryCount < 3) {
            const timeout = Math.pow(2, retryCount) * 1000;
            if (process.env.NODE_ENV === "development") {
              console.log(`⏱️ Retrying in ${timeout/1000} seconds...`);
            }
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, timeout);
          }
        }

        // Compare data before updating state to avoid unnecessary re-renders
        const modeChanged = controlMode.mode !== systemState.executionMode;
        const tasksChanged = !isEqual(systemState.tasks, taskState.tasks);
        
        if (modeChanged || tasksChanged) {
          setSystemState({
            executionMode: controlMode.mode,
            tasks: taskState.tasks || []
          });
          
          // Filter active tasks
          const active = (taskState.tasks || []).filter(task => 
            task && task.status && 
            ['pending', 'in_progress', 'running'].includes(task.status.toLowerCase())
          );
          
          if (!isEqual(activeTasks, active)) {
            setActiveTasks(active);
          }
        }
        
        if (loading) {
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch control state');
        setLoading(false);
        if (process.env.NODE_ENV === "development") {
          console.error('Error fetching control state:', err);
        }
      }
    };

    fetchControlState();
    // Set up polling for real-time updates (every 5 seconds as requested)
    const intervalId = setInterval(fetchControlState, 5000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [retryCount]);

  const handleModeChange = async (mode) => {
    try {
      await controlService.setControlMode(mode);
      setSystemState(prevState => ({
        ...prevState,
        executionMode: mode
      }));
    } catch (err) {
      if (process.env.NODE_ENV === "development") {
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
      if (process.env.NODE_ENV === "development") {
        console.error(`Error performing ${action} on task ${taskId}:`, err);
      }
    }
  };

  const handleTaskRedirect = async (taskId, targetAgent) => {
    if (!targetAgent) return;
    try {
      await controlService.delegateTask(taskId, targetAgent);
    } catch (err) {
      if (process.env.NODE_ENV === "development") {
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
      if (process.env.NODE_ENV === "development") {
        console.error(`Error editing prompt for task ${selectedTask.task_id}:`, err);
      }
    }
  };

  // Memoize the tasks list to prevent unnecessary re-renders
  const memoizedTasks = useMemo(() => activeTasks, [activeTasks]);

  if (loading) {
    return (
      <Box minH="inherit" display="flex" alignItems="center" justifyContent="center">
        <Flex direction="column" align="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading control state...</Text>
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
      <Flex mb={4} justifyContent="space-between" alignItems="center">
        <Text fontWeight="bold">Execution Mode:</Text>
        <Select 
          value={systemState.executionMode} 
          onChange={(e) => handleModeChange(e.target.value)}
          width="auto"
          ml={2}
        >
          <option value="auto">Automatic</option>
          <option value="manual">Manual</option>
          <option value="paused">Paused</option>
        </Select>
      </Flex>
      
      {interruptSystemOffline && (
        <Box 
          mb={4} 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          borderColor="orange.200"
          bg="orange.50"
          _dark={{ bg: "orange.900", borderColor: "orange.700" }}
        >
          <Text fontSize="sm">
            Interrupt system is offline. Some task control features may be unavailable.
          </Text>
        </Box>
      )}
      
      {memoizedTasks.length > 0 ? (
        <VStack spacing={4} align="stretch">
          {memoizedTasks.map((task) => (
            <Box 
              key={task?.task_id || `task-${Math.random()}`} 
              borderWidth="1px" 
              borderRadius="lg" 
              p={4} 
              shadow="sm" 
              bg={bgColor} 
              borderColor={borderColor}
            >
              <Flex justifyContent="space-between" alignItems="center" mb={3}>
                <Text fontWeight="bold">{task?.title || 'Untitled Task'}</Text>
                <Badge colorScheme={
                  task?.status === 'in_progress' ? 'blue' : 
                  task?.status === 'pending' ? 'yellow' : 'gray'
                }>
                  {task?.status || 'Unknown'}
                </Badge>
              </Flex>
              
              <Text fontSize="sm" mb={3}>{task?.description || 'No description'}</Text>
              
              <Flex gap={2} wrap="wrap">
                <Button 
                  size="sm" 
                  colorScheme="red" 
                  onClick={() => handleTaskAction(task.task_id, 'kill')}
                >
                  Kill
                </Button>
                
                <Button 
                  size="sm" 
                  colorScheme="blue" 
                  onClick={() => handleTaskAction(task.task_id, 'restart')}
                >
                  Restart
                </Button>
                
                <Button 
                  size="sm" 
                  colorScheme="purple" 
                  onClick={() => openPromptEditor(task)}
                >
                  Edit Prompt
                </Button>
                
                <Select 
                  size="sm" 
                  placeholder="Delegate to..." 
                  width="auto" 
                  onChange={(e) => {
                    if (e.target.value) {
                      handleTaskRedirect(task.task_id, e.target.value);
                      e.target.value = '';
                    }
                  }}
                >
                  <option value="assistant">Assistant</option>
                  <option value="researcher">Researcher</option>
                  <option value="coder">Coder</option>
                </Select>
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
          <Text color="gray.500">No active tasks</Text>
        </Box>
      )}
      
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Edit Task Prompt</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>Prompt</FormLabel>
              <Textarea 
                value={taskPrompt} 
                onChange={(e) => setTaskPrompt(e.target.value)} 
                rows={10}
              />
            </FormControl>
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
