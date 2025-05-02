import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  Input, 
  Button, 
  IconButton, 
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Textarea,
  useColorModeValue,
  Tooltip,
  Text,
  HStack,
  Spinner
} from '@chakra-ui/react';
import { 
  FaPaperPlane, 
  FaRobot, 
  FaChevronDown, 
  FaEraser, 
  FaRegClock
} from 'react-icons/fa';
import { useChatMemory } from './ChatMemoryContext';
import { routeMessage } from './AgentRouter';

/**
 * ChatInputBar Component
 * 
 * Input field for sending messages to agents with agent selection,
 * status indicators, and send button.
 */
const ChatInputBar = () => {
  const [message, setMessage] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('orchestrator');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentLoopId, setCurrentLoopId] = useState(`loop_${Date.now()}`);
  const textareaRef = useRef(null);
  const { addMessage, projectId } = useChatMemory();
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Agents available for selection
  const agents = [
    { id: 'orchestrator', name: 'Orchestrator', color: 'purple', icon: '🧠' },
    { id: 'ash', name: 'ASH', color: 'orange', icon: '🔥' },
    { id: 'sage', name: 'SAGE', color: 'green', icon: '🧙' },
    { id: 'skeptic', name: 'Skeptic', color: 'red', icon: '🤔' },
    { id: 'builder', name: 'Builder', color: 'blue', icon: '🛠️' }
  ];
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'inherit';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);
  
  // Handle message submission
  const handleSubmit = async () => {
    if (!message.trim()) return;
    
    // Create operator message
    const operatorMessage = {
      agent: 'operator',
      role: 'operator',
      message: message.trim(),
      loop_id: currentLoopId,
      project_id: projectId,
      timestamp: new Date().toISOString()
    };
    
    // Add operator message to chat
    addMessage(operatorMessage);
    
    // Clear input
    setMessage('');
    
    // Show typing indicator
    const typingIndicator = {
      agent: selectedAgent,
      role: 'typing',
      message: '',
      loop_id: currentLoopId,
      project_id: projectId,
      timestamp: new Date().toISOString()
    };
    addMessage(typingIndicator);
    
    try {
      setIsSubmitting(true);
      
      // Route message to appropriate endpoint
      const agentMessage = {
        agent: selectedAgent,
        role: 'operator',
        message: operatorMessage.message,
        loop_id: currentLoopId,
        project_id: projectId
      };
      
      const response = await routeMessage(agentMessage);
      
      // Remove typing indicator and add agent response
      setTimeout(() => {
        addMessage({
          agent: selectedAgent,
          role: 'agent',
          message: response.message || response.output || 'No response received',
          loop_id: currentLoopId,
          project_id: projectId,
          timestamp: new Date().toISOString()
        });
      }, 500);
      
      // Generate new loop ID for next conversation turn
      setCurrentLoopId(`loop_${Date.now()}`);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Remove typing indicator and add error message
      setTimeout(() => {
        addMessage({
          agent: selectedAgent,
          role: 'agent',
          message: `Error: ${error.message || 'Failed to get response'}`,
          loop_id: currentLoopId,
          project_id: projectId,
          timestamp: new Date().toISOString()
        });
      }, 500);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  // Parse @ mentions to change agent
  const handleInputChange = (e) => {
    const value = e.target.value;
    setMessage(value);
    
    // Check for @agent mentions
    const match = value.match(/@(\w+)/);
    if (match && match[1]) {
      const mentionedAgent = match[1].toLowerCase();
      const foundAgent = agents.find(a => a.id.toLowerCase() === mentionedAgent);
      
      if (foundAgent) {
        setSelectedAgent(foundAgent.id);
        // Remove the @mention from the message
        setMessage(value.replace(/@\w+\s?/, ''));
      }
    }
  };
  
  return (
    <Box
      p={3}
      borderTopWidth="1px"
      borderColor={borderColor}
      bg={bgColor}
      borderRadius="md"
    >
      <Flex direction="column">
        {/* Agent selection and controls */}
        <Flex justify="space-between" mb={2}>
          <Menu>
            <Tooltip label="Select agent">
              <MenuButton
                as={Button}
                rightIcon={<FaChevronDown />}
                leftIcon={<FaRobot />}
                size="sm"
                colorScheme={agents.find(a => a.id === selectedAgent)?.color || 'gray'}
              >
                {agents.find(a => a.id === selectedAgent)?.name || 'Select Agent'}
              </MenuButton>
            </Tooltip>
            <MenuList>
              {agents.map((agent) => (
                <MenuItem 
                  key={agent.id} 
                  onClick={() => setSelectedAgent(agent.id)}
                  icon={<Text>{agent.icon}</Text>}
                >
                  {agent.name}
                </MenuItem>
              ))}
            </MenuList>
          </Menu>
          
          <HStack>
            <Tooltip label="Clear input">
              <IconButton
                icon={<FaEraser />}
                size="sm"
                variant="ghost"
                onClick={() => setMessage('')}
                isDisabled={!message || isSubmitting}
                aria-label="Clear input"
              />
            </Tooltip>
            
            <Tooltip label="View message history">
              <IconButton
                icon={<FaRegClock />}
                size="sm"
                variant="ghost"
                aria-label="View history"
              />
            </Tooltip>
          </HStack>
        </Flex>
        
        {/* Input area */}
        <Flex>
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={`Message ${agents.find(a => a.id === selectedAgent)?.name || 'Agent'}...`}
            resize="none"
            rows={1}
            maxRows={5}
            mr={2}
            flexGrow={1}
            disabled={isSubmitting}
          />
          
          <Tooltip label="Send message (Ctrl+Enter)">
            <IconButton
              icon={isSubmitting ? <Spinner size="sm" /> : <FaPaperPlane />}
              colorScheme="blue"
              onClick={handleSubmit}
              isDisabled={!message.trim() || isSubmitting}
              aria-label="Send message"
            />
          </Tooltip>
        </Flex>
        
        {/* Typing hint */}
        <Text fontSize="xs" color="gray.500" mt={1}>
          Tip: Type @agent to switch agents (e.g., @sage, @ash)
        </Text>
      </Flex>
    </Box>
  );
};

export default ChatInputBar;
