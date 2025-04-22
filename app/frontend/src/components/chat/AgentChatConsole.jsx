import React, { useEffect, useRef } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Flex, 
  useColorModeValue, 
  Heading,
  Divider,
  Button,
  IconButton,
  Tooltip,
  HStack
} from '@chakra-ui/react';
import { FaExpandAlt, FaCompress, FaDownload, FaBrain } from 'react-icons/fa';
import { ChatMemoryProvider, useChatMemory } from './ChatMemoryContext';
import MessageBubble from './MessageBubble';
import ChatInputBar from './ChatInputBar';

/**
 * AgentChatConsole Component
 * 
 * Main chat window for Operator ↔ Agent interactions.
 * Displays conversational message thread scoped by project_id.
 */
const AgentChatConsole = ({ projectId = 'promethios-core' }) => {
  const { messages, changeProject } = useChatMemory();
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const [expanded, setExpanded] = React.useState(false);
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Set project context
  useEffect(() => {
    changeProject(projectId);
  }, [projectId, changeProject]);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Toggle expanded view
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  // Export chat history
  const exportChatHistory = () => {
    try {
      const chatData = JSON.stringify(messages, null, 2);
      const blob = new Blob([chatData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_history_${projectId}_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting chat history:', error);
    }
  };
  
  // View full loop trace
  const viewFullLoopTrace = (loopId) => {
    console.log(`Viewing full loop trace for ${loopId}`);
    // This would open a sidebar or modal with the full loop trace
    // Implementation depends on the existing UI components
  };
  
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      bg={bgColor}
      borderColor={borderColor}
      shadow="sm"
      height={expanded ? "calc(100vh - 100px)" : "500px"}
      display="flex"
      flexDirection="column"
      transition="height 0.3s ease"
      position={expanded ? "fixed" : "relative"}
      top={expanded ? "50px" : "auto"}
      left={expanded ? "0" : "auto"}
      right={expanded ? "0" : "auto"}
      zIndex={expanded ? "1000" : "1"}
      width={expanded ? "100%" : "auto"}
    >
      {/* Header */}
      <Flex 
        p={3} 
        borderBottomWidth="1px" 
        borderColor={borderColor}
        justify="space-between"
        align="center"
      >
        <Heading size="md" display="flex" alignItems="center">
          <Box as="span" mr={2}>💬</Box>
          Agent Chat
        </Heading>
        
        <HStack spacing={2}>
          <Tooltip label="Export chat history">
            <IconButton
              icon={<FaDownload />}
              size="sm"
              variant="ghost"
              onClick={exportChatHistory}
              aria-label="Export chat"
            />
          </Tooltip>
          
          <Tooltip label={expanded ? "Minimize" : "Expand"}>
            <IconButton
              icon={expanded ? <FaCompress /> : <FaExpandAlt />}
              size="sm"
              variant="ghost"
              onClick={toggleExpanded}
              aria-label={expanded ? "Minimize" : "Expand"}
            />
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Messages container */}
      <Box 
        flex="1" 
        overflowY="auto" 
        p={4}
        ref={chatContainerRef}
      >
        {messages.length === 0 ? (
          <Flex 
            direction="column" 
            align="center" 
            justify="center" 
            height="100%"
            color="gray.500"
            textAlign="center"
            p={6}
          >
            <Box as="span" fontSize="4xl" mb={4}>🧠</Box>
            <Text fontSize="lg" fontWeight="bold">
              Start a conversation with Promethios
            </Text>
            <Text fontSize="sm" mt={2}>
              Select an agent and type a message to begin
            </Text>
            <Divider my={4} />
            <VStack spacing={2} align="stretch" width="100%" maxW="400px">
              <Button 
                leftIcon={<FaBrain />} 
                size="sm" 
                variant="outline"
                justifyContent="flex-start"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "What can you help me with today?";
                    textarea.focus();
                  }
                }}
              >
                What can you help me with?
              </Button>
              <Button 
                leftIcon={<FaBrain />} 
                size="sm" 
                variant="outline"
                justifyContent="flex-start"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "Explain the current project status";
                    textarea.focus();
                  }
                }}
              >
                Explain the current project status
              </Button>
              <Button 
                leftIcon={<FaBrain />} 
                size="sm" 
                variant="outline"
                justifyContent="flex-start"
                onClick={() => {
                  const textarea = document.querySelector('textarea');
                  if (textarea) {
                    textarea.value = "Analyze the latest memory entries";
                    textarea.focus();
                  }
                }}
              >
                Analyze the latest memory entries
              </Button>
            </VStack>
          </Flex>
        ) : (
          <VStack spacing={2} align="stretch">
            {messages.map((msg, index) => (
              <MessageBubble
                key={`${msg.id || index}`}
                agent={msg.agent}
                role={msg.role}
                message={msg.message}
                timestamp={msg.timestamp}
                loop_id={msg.loop_id}
                tags={msg.tags}
              />
            ))}
            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>
      
      {/* Input bar */}
      <ChatInputBar />
    </Box>
  );
};

/**
 * Wrapped AgentChatConsole with ChatMemoryProvider
 */
const AgentChatConsoleWithProvider = (props) => (
  <ChatMemoryProvider>
    <AgentChatConsole {...props} />
  </ChatMemoryProvider>
);

export default AgentChatConsoleWithProvider;
