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
  useColorModeValue,
  Alert,
  AlertIcon,
  Heading,
  Tooltip,
  HStack,
  CircularProgress,
  CircularProgressLabel
} from '@chakra-ui/react';
import { controlService } from '../services/api';
import isEqual from 'lodash/isEqual';

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
  const [systemHeartbeat, setSystemHeartbeat] = useState({ status: 'unknown', lastBeat: null });
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

  // Fetch system status from API
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const response = await fetch('/api/system/status');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch system status: ${response.status}`);
        }
        
        const data = await response.json();
        
        setSystemHeartbeat({
          status: data.status || 'unknown',
          lastBeat: data.lastHeartbeat ? new Date(data.lastHeartbeat) : new Date(),
          activeTasks: data.activeTasks || 0,
          cpuUsage: data.cpuUsage || 0,
          memoryUsage: data.memoryUsage || 0
        });
        
        setInterruptSystemOffline(data.status === 'offline');
      } catch (err) {
        console.error('Error fetching system status:', err);
        // Don't set interrupt system offline here, as we'll check that separately
        
        // Set fallback heartbeat data
        setSystemHeartbeat(prev => ({
          ...prev,
          status: 'unknown',
          lastBeat: new Date()
        }));
      }
    };
    
    // Initial fetch
    fetchSystemStatus();
    
    // Set up polling for heartbeat updates
    const intervalId = setInterval(fetchSystemStatus, 10000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const fetchControlState = async () => {
      try {
        // Only show loading on initial fetch, not during polling updates
        if (activeTasks.length === 0) {
          setLoading(true);
        }
        
        // Try to fetch from the new API endpoint first
        try {
          const response = await fetch('/api/system/status');
          
          if (!response.ok) {
            throw new Error(`Failed to fetch system status: ${response.status}`);
          }
          
          const data = await response.json();
          
          // Update control mode if available in the response
          if (data.executionMode) {
            const newControlMode = { mode: data.executionMode };
            
            // Compare data before updating state to avoid unnecessary re-renders
            const modeChanged = !isEqual(prevControlModeRef.current, newControlMode);
            if (modeChanged) {
              prevControlModeRef.current = newControlMode;
              setControlMode(newControlMode);
            }
          }
          
          // Update tasks if available in the response
          if (Array.isArray(data.tasks)) {
            // Deep compare task state before updating to prevent unnecessary re-renders
            if (!isEqual(prevTaskStateRef.current, data.tasks)) {
              prevTaskStateRef.current = data.tasks;
              
              // Filter active tasks
              const active = data.tasks.filter(task => 
                task && task.status && 
                ['pending', 'in_progress', 'running'].includes(task.status.toLowerCase())
              );
              
              if (!isEqual(activeTasks, active)) {
                setActiveTasks(active);
              }
              
              setSystemState(prev => ({
                ...prev,
                tasks: data.tasks
              }));
            }
            
            setInterruptSystemOffline(false);
            setError(null);
          }
        } catch (err) {
          // If new API fails, fall back to original implementation
          console.warn('Falling back to original implementation:', err);
          
          // Original implementation
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
          const executionModeChanged = controlMode.mode !== systemState.executionMode;
          const tasksChanged = !isEqual(systemState.tasks, taskState.tasks);
          
          if (executionModeChanged || tasksChanged) {
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
      // Try new API endpoint first
      try {
        const response = await fetch('/api/system/mode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ mode }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to set mode: ${response.status}`);
        }
        
        setSystemState(prevState => ({
          ...prevState,
          executionMode: mode
        }));
        
        return;
      } catch (err) {
        console.warn('Falling back to original implementation for mode change:', err);
      }
      
      // Fall back to original implementation
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
      // Try new API endpoint first
      try {
        const endpoint = action === 'kill' ? '/api/system/task/kill' : '/api/system/task/restart';
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ taskId }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to ${action} task: ${response.status}`);
        }
        
        return;
      } catch (err) {
        console.warn(`Falling back to original implementation for ${action}:`, err);
      }
      
      // Fall back to original implementation
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
      // Try new API endpoint first
      try {
        const response = await fetch('/api/system/task/delegate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ taskId, agent: targetAgent }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to delegate task: ${response.status}`);
        }
        
        return;
      } catch (err) {
        console.warn('Falling back to original implementation for delegation:', err);
      }
      
      // Fall back to original implementation
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
      // Try new API endpoint first
      try {
        const response = await fetch('/api/system/task/edit-prompt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            taskId: selectedTask.task_id, 
            prompt: taskPrompt 
          }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to edit prompt: ${response.status}`);
        }
        
        onClose();
        setSelectedTask(null);
        setTaskPrompt('');
        return;
      } catch (err) {
        console.warn('Falling back to original implementation for prompt edit:', err);
      }
      
      // Fall back to original implementation
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

  // Get status color
  const getStatusColor = (status) => {
    if (!status || typeof status !== 'string') {
      return 'gray';
    }
    
    switch (status.toLowerCase()) {
      case 'online':
      case 'active':
        return 'green';
      case 'idle':
        return 'blue';
      case 'offline':
      case 'error':
        return 'red';
      case 'busy':
        return 'orange';
      case 'warning':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  // Format time since last heartbeat
  const formatTimeSince = (date) => {
    if (!date) return 'unknown';
    
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
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

  return (
    <Box minH="inherit">
      <Flex mb={4} justifyContent="space-between" alignItems="center">
        <Heading size="md">System Control</Heading>
        
        <HStack spacing={2}>
          <Text fontWeight="bold">Status:</Text>
          <Badge colorScheme={getStatusColor(systemHeartbeat.status)}>
            {systemHeartbeat.status || 'Unknown'}
          </Badge>
          
          <Tooltip label={systemHeartbeat.lastBeat ? systemHeartbeat.lastBeat.toLocaleString() : 'Unknown'}>
            <Text fontSize="sm" color="gray.500">
              {systemHeartbeat.lastBeat ? formatTimeSince(systemHeartbeat.lastBeat) : 'unknown'}
            </Text>
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* System metrics */}
      <Flex mb={4} justifyContent="space-between" gap={4}>
        <Box 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          flex="1"
          bg={bgColor}
        >
          <Flex alignItems="center" justifyContent="space-between">
            <Text fontSize="sm" fontWeight="medium">Active Tasks</Text>
            <Badge colorScheme="blue" fontSize="md">
              {systemHeartbeat.activeTasks || memoizedTasks.length || 0}
            </Badge>
          </Flex>
        </Box>
        
        <Box 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          flex="1"
          bg={bgColor}
        >
          <Flex alignItems="center" justifyContent="space-between">
            <Text fontSize="sm" fontWeight="medium">CPU Usage</Text>
            <CircularProgress 
              value={systemHeartbeat.cpuUsage || 0} 
              color="green.400" 
              size="40px"
            >
              <CircularProgressLabel>{systemHeartbeat.cpuUsage || 0}%</CircularProgressLabel>
            </CircularProgress>
          </Flex>
        </Box>
        
        <Box 
          p={3} 
          borderWidth="1px" 
          borderRadius="md" 
          flex="1"
          bg={bgColor}
        >
          <Flex alignItems="center" justifyContent="space-between">
            <Text fontSize="sm" fontWeight="medium">Memory</Text>
            <CircularProgress 
              value={systemHeartbeat.memoryUsage || 0} 
              color="purple.400" 
              size="40px"
            >
              <CircularProgressLabel>{systemHeartbeat.memoryUsage || 0}%</CircularProgressLabel>
            </CircularProgress>
          </Flex>
        </Box>
      </Flex>
      
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
      
      {error && (
        <Alert status="error" mb={4} borderRadius="md">
          <AlertIcon />
          {error}
        </Alert>
      )}
      
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
      
      <Heading size="sm" mb={3}>Active Tasks</Heading>
      
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
          py={8}
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
