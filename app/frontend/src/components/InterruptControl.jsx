<<<<<<< HEAD
import React, { useState, useEffect } from 'react';
import isEqual from 'lodash.isequal';
import { controlService, goalsService } from '../services/api';

// Component for controlling agent execution with interrupt capabilities
const InterruptControl = () => {
  const [systemState, setSystemState] = useState({
    executionMode: 'auto', // 'auto', 'manual', 'paused'
    activeAgents: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskPrompt, setTaskPrompt] = useState('');
  const [activeTasks, setActiveTasks] = useState([]);

  useEffect(() => {
    // Function to fetch system state and active tasks
    const fetchSystemState = async () => {
      try {
        setLoading(true);
        
        // Fetch system control mode
        const controlModeData = await controlService.getControlMode();
        
        // Fetch active tasks
        const tasksData = await goalsService.getTaskState();
        
        setSystemState({
          executionMode: controlModeData.mode,
          activeAgents: controlModeData.active_agents || []
        });
        
        setActiveTasks(tasksData.tasks || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch system state');
        setLoading(false);
        console.error('Error fetching system state:', err);
      }
    };

    // Initial fetch
    fetchSystemState();
    
    // Set up polling for real-time updates (every 3 seconds)
    const intervalId = setInterval(fetchSystemState, 3000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Handle system execution mode change
=======
import React, { useState, useEffect, useRef } from 'react';
import isEqual from 'lodash.isequal';
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

  const lastTaskStateRef = useRef(null);
  const renderCountRef = useRef(0);
  const lastTasksRef = useRef([]);
  const lastModeRef = useRef('');

  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
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
            typeof window.or.getTaskState === "function"
          ) {
            const fetchedTaskState = await window.or.getTaskState();

            if (!isEqual(fetchedTaskState, lastTaskStateRef.current)) {
              if (process.env.NODE_ENV === "development") {
                console.log('Task state changed, updating state');
              }
              lastTaskStateRef.current = JSON.parse(JSON.stringify(fetchedTaskState));
              taskState = fetchedTaskState;
            } else {
              if (process.env.NODE_ENV === "development") {
                console.log('Task state unchanged, skipping update');
              }
              taskState = lastTaskStateRef.current;
            }
          } else {
            if (process.env.NODE_ENV === "development") {
              console.warn("window.or.getTaskState is not defined or not a function. Using fallback.");
            }
          }
        } catch (err) {
          if (process.env.NODE_ENV === "development") {
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
        if (process.env.NODE_ENV === "development") {
          console.error('Error fetching control state:', err);
        }
      }
    };

    fetchControlState();
    const intervalId = setInterval(fetchControlState, 3000);
    return () => clearInterval(intervalId);
  }, []);

>>>>>>> manus-ui-restore
  const handleModeChange = async (mode) => {
    try {
      await controlService.setControlMode(mode);
      setSystemState(prev => ({
        ...prev,
        executionMode: mode
      }));
    } catch (err) {
<<<<<<< HEAD
      setError(`Failed to change execution mode to ${mode}`);
      console.error('Error changing execution mode:', err);
    }
  };

  // Handle task kill/restart
  const handleTaskAction = async (taskId, action) => {
    try {
      if (action === 'kill') {
        await goalsService.killTask(taskId);
      } else if (action === 'restart') {
        await goalsService.restartTask(taskId);
      }
      // State will be updated on next polling cycle
    } catch (err) {
      setError(`Failed to ${action} task ${taskId}`);
      console.error(`Error ${action} task:`, err);
    }
  };

  // Handle task redirection to another agent
  const handleTaskRedirect = async (taskId, targetAgent) => {
    try {
      await controlService.delegateTask(taskId, targetAgent);
      // State will be updated on next polling cycle
    } catch (err) {
      setError(`Failed to redirect task ${taskId} to ${targetAgent}`);
      console.error('Error redirecting task:', err);
    }
  };

  // Handle task prompt editing (Manual Mode only)
  const handlePromptEdit = async () => {
    if (!selectedTask) return;
    
    try {
      await controlService.editTaskPrompt(selectedTask.task_id, taskPrompt);
      
      // Reset form
      setSelectedTask(null);
      setTaskPrompt('');
    } catch (err) {
      setError(`Failed to edit prompt for task ${selectedTask.task_id}`);
      console.error('Error editing task prompt:', err);
    }
  };

  // Open task prompt editor
  const openPromptEditor = (task) => {
    setSelectedTask(task);
    setTaskPrompt(task.prompt || '');
  };

  if (loading) {
    return <div className="loading">Loading control panel...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="interrupt-control">
      {/* System execution mode controls */}
      <div className="control-panel">
        <h3>Execution Control</h3>
        <div className="control-buttons">
          <button 
            className={`btn ${systemState.executionMode === 'auto' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => handleModeChange('auto')}
          >
            <i className="fas fa-play"></i> Auto Mode
          </button>
          
          <button 
            className={`btn ${systemState.executionMode === 'manual' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => handleModeChange('manual')}
          >
            <i className="fas fa-user"></i> Manual Mode
          </button>
          
          <button 
            className={`btn ${systemState.executionMode === 'paused' ? 'btn-warning' : 'btn-secondary'}`}
            onClick={() => handleModeChange('paused')}
          >
            <i className="fas fa-pause"></i> Pause All
          </button>
        </div>
      </div>
      
      {/* Active tasks control */}
      <div className="tasks-control">
        <h3>Active Tasks</h3>
        {activeTasks.length > 0 ? (
          <div className="task-list">
            {activeTasks.map((task) => (
              <div key={task.task_id} className="task-control-item">
                <div className="task-info">
                  <h4>{task.title}</h4>
                  <div className="task-meta">
                    <span>Status: {task.status}</span>
                    <span>Agent: {task.assigned_agent || 'Unassigned'}</span>
                  </div>
                </div>
                
                <div className="task-actions">
                  {/* Kill/restart task */}
                  <button 
                    className="btn btn-warning"
                    onClick={() => handleTaskAction(task.task_id, task.status === 'in_progress' ? 'kill' : 'restart')}
                    disabled={task.status === 'completed'}
                  >
                    <i className={`fas ${task.status === 'in_progress' ? 'fa-stop' : 'fa-redo'}`}></i>
                    {task.status === 'in_progress' ? ' Kill' : ' Restart'}
                  </button>
                  
                  {/* Redirect task */}
                  <div className="redirect-control">
                    <select 
                      onChange={(e) => handleTaskRedirect(task.task_id, e.target.value)}
                      disabled={task.status === 'completed'}
                    >
                      <option value="">Redirect to...</option>
                      {systemState.activeAgents.map((agent) => (
                        <option key={agent} value={agent}>{agent}</option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Edit prompt (Manual Mode only) */}
                  {systemState.executionMode === 'manual' && (
                    <button 
                      className="btn btn-secondary"
                      onClick={() => openPromptEditor(task)}
                      disabled={task.status === 'completed'}
                    >
                      <i className="fas fa-edit"></i> Edit Prompt
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">No active tasks found</div>
        )}
      </div>
      
      {/* Prompt editor modal (Manual Mode only) */}
      {selectedTask && (
        <div className="prompt-editor-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Edit Task Prompt</h3>
              <button className="close-btn" onClick={() => setSelectedTask(null)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="task-info">
                <p><strong>Task:</strong> {selectedTask.title}</p>
                <p><strong>ID:</strong> {selectedTask.task_id}</p>
              </div>
              
              <div className="prompt-form">
                <label htmlFor="taskPrompt">Task Prompt:</label>
                <textarea
                  id="taskPrompt"
                  value={taskPrompt}
                  onChange={(e) => setTaskPrompt(e.target.value)}
                  rows={10}
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectedTask(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handlePromptEdit}>Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </div>
=======
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
>>>>>>> manus-ui-restore
  );
};

export default InterruptControl;
