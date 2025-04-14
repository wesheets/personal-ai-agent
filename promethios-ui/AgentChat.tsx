import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Textarea, Button, Flex, Text, Badge, VStack, HStack, Spinner, useColorModeValue, Collapse } from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons';
import { Instruction } from '../backend/instruction_engine';

// Agent name to backend ID mapping
const agentNameMap: Record<string, string> = {
  "ReflectionAgent": "LifeTree",
  "CADBuilderAgent": "SiteGen",
  "DreamAgent": "NEUREAL",
  "HAL": "hal"
};

interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system' | 'orchestrator';
  content: string;
  instruction?: Instruction;
  isExpanded?: boolean;
}

const AgentChat: React.FC = () => {
  // Get agentId from URL params
  const { agentId } = useParams<{ agentId: string }>();
  const resolvedAgentId = agentNameMap[agentId || ''] || agentId || 'core-forge';
  
  // State for agent data
  const [agent, setAgent] = useState<any>(null);
  const [agentLoading, setAgentLoading] = useState<boolean>(true);
  const [agentError, setAgentError] = useState<string | null>(null);
  
  // Persist conversationHistory as an array of user and assistant messages
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [streaming, setStreaming] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const feedRef = useRef<HTMLDivElement>(null);
  const [debugOpen, setDebugOpen] = useState<boolean>(false);
  const navigate = useNavigate();
  
  // AbortController for fetch requests
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Retry counter for API calls
  const [retryCount, setRetryCount] = useState<number>(0);
  const maxRetries = 1; // Maximum number of retries

  // Fetch agent data
  useEffect(() => {
    const fetchAgentData = async () => {
      setAgentLoading(true);
      setAgentError(null);
      
      try {
        const response = await fetch(`/api/agent/${resolvedAgentId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch agent data: ${response.status}`);
        }
        
        const data = await response.json();
        setAgent(data);
      } catch (error: any) {
        console.error('Error fetching agent data:', error);
        setAgentError(error.message);
        // Fallback agent data
        setAgent({
          id: resolvedAgentId,
          name: resolvedAgentId
        });
      } finally {
        setAgentLoading(false);
      }
    };
    
    if (resolvedAgentId) {
      fetchAgentData();
    }
  }, [resolvedAgentId]);

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    // Scope conversation history to specific agent
    const historyKey = `chat_history_${resolvedAgentId}`;
    const savedHistory = localStorage.getItem(historyKey);
    if (savedHistory) {
      try {
        setMessages(JSON.parse(savedHistory));
      } catch (e) {
        console.error(`Failed to parse saved conversation history for ${resolvedAgentId}:`, e);
      }
    } else {
      // Clear messages if no history exists for this agent
      setMessages([]);
    }
  }, [resolvedAgentId]);

  // Save conversation history to localStorage whenever it changes
  useEffect(() => {
    if (messages.length > 0 && resolvedAgentId) {
      const historyKey = `chat_history_${resolvedAgentId}`;
      localStorage.setItem(historyKey, JSON.stringify(messages));
    }
  }, [messages, resolvedAgentId]);

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight);
  }, [messages]);

  const makeApiRequest = async (endpoint: string, body: any, signal: AbortSignal) => {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal
    });
    
    // Handle API failures (502, 504, etc.)
    if (response.status === 502 || response.status === 504) {
      throw new Error('UNAVAILABLE');
    }

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    
    return response;
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setRetryCount(0); // Reset retry counter on new submission

    // Cancel any ongoing requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    const userMessage: Message = { role: 'user', content: input };
    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setInput('');

    // Check if this is an onboarding request for HAL
    if (resolvedAgentId.toLowerCase() === 'hal' && 
        input.toLowerCase().includes('onboarding')) {
      // Add orchestrator message with instruction
      const instruction: Instruction = {
        instruction_id: 'inst_' + Math.random().toString(36).substring(2, 15),
        goal_id: 'goal_' + Math.random().toString(36).substring(2, 15),
        agent_id: 'hal',
        task_summary: 'Complete onboarding process',
        tools_required: ['file_read', 'file_write', 'shell_exec'],
        expected_outputs: [
          { type: 'memory', tag: 'tool_usage', required: true },
          { type: 'reflection', tag: 'onboarding_thoughts', required: true },
          { type: 'checkpoint', tag: 'agent_onboarding_complete', required: true }
        ],
        loop_enforcement: 2,
        allow_retry: true,
        escalate_on_failure: true,
        status: 'pending',
        last_updated: new Date()
      };
      
      const orchestratorMessage: Message = {
        role: 'orchestrator',
        content: 'Instruction assigned to HAL: Complete onboarding process',
        instruction,
        isExpanded: false
      };
      
      setMessages(prev => [...prev, orchestratorMessage]);
      setTimeout(() => setLoading(false), 1000);
      return;
    }

    const makeRequest = async (isRetry = false) => {
      try {
        // Use delegate-stream endpoint for streaming responses
        const endpoint = streaming ? '/api/agent/delegate-stream' : '/api/agent/delegate';
        const requestBody = {
          agent_id: resolvedAgentId,
          prompt: input,
          history: updatedHistory // Pass full conversation history with every prompt
        };
        
        if (streaming) {
          // Handle streaming response
          const response = await makeApiRequest(endpoint, requestBody, signal);
          
          const reader = response.body!.getReader();
          const decoder = new TextDecoder();
          let responseText = '';
          
          // Create a placeholder for the streaming response
          const assistantMessageId = Date.now();
          setMessages(prev => [...prev, { 
            id: assistantMessageId,
            role: 'assistant', 
            content: '' 
          }]);

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            responseText += chunk;
            
            // Update the message with the accumulated text
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: responseText } 
                : msg
            ));
          }

          // Finalize the message without the temporary ID
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { role: 'assistant', content: responseText } 
              : msg
          ));
        } else {
          // Handle non-streaming response
          const res = await makeApiRequest(endpoint, requestBody, signal);
          const data = await res.json();

          const assistantMessage: Message = {
            role: 'assistant',
            content: data.message || '[No response]'
          };

          // Append GPT response to history array before next message
          setMessages(prev => [...prev, assistantMessage]);
        }

        setMessages(prev => [...prev, { role: 'system', content: '💾 Memory Logged' }]);
        
        // Reset retry counter on success
        setRetryCount(0);
      } catch (error: any) {
        console.error('Error during chat:', error);
        
        // Handle retry logic for unavailable agent
        if (error.message === 'UNAVAILABLE' && retryCount < maxRetries && !isRetry) {
          console.log(`Retrying request (${retryCount + 1}/${maxRetries})...`);
          setRetryCount(prev => prev + 1);
          
          // Add a retry message
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ Connection issue. Retrying...` }
          ]);
          
          // Wait a moment before retrying
          setTimeout(() => makeRequest(true), 1500);
          return;
        }
        
        // Special handling for unavailable agent
        if (error.message === 'UNAVAILABLE' || error.name === 'AbortError') {
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ This agent is temporarily unavailable. Please try again or switch agents.` }
          ]);
        } else {
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ Agent response failed. Try again or switch agents.` }
          ]);
        }
        
        // Reset retry counter on final failure
        setRetryCount(0);
      } finally {
        if (isRetry || retryCount >= maxRetries) {
          setLoading(false);
          abortControllerRef.current = null;
        }
      }
    };
    
    // Start the request process
    await makeRequest();
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/auth');
  };

  const clearHistory = () => {
    setMessages([]);
    if (resolvedAgentId) {
      const historyKey = `chat_history_${resolvedAgentId}`;
      localStorage.removeItem(historyKey);
    }
  };

  const toggleInstructionExpand = (index: number) => {
    setMessages(prev => 
      prev.map((msg, i) => 
        i === index ? { ...msg, isExpanded: !msg.isExpanded } : msg
      )
    );
  };

  // Render instruction details in a collapsible card
  const renderInstructionCard = (instruction: Instruction, isExpanded: boolean, index: number) => {
    const bgColor = useColorModeValue('gray.50', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');
    
    return (
      <Box 
        mt={2} 
        p={3} 
        bg={bgColor} 
        borderRadius="md" 
        borderWidth="1px" 
        borderColor={borderColor}
      >
        <Flex 
          justifyContent="space-between" 
          alignItems="center" 
          onClick={() => toggleInstructionExpand(index)}
          cursor="pointer"
        >
          <Text fontWeight="bold">Instruction: {instruction.task_summary}</Text>
          {isExpanded ? <ChevronUpIcon /> : <ChevronDownIcon />}
        </Flex>
        
        <Collapse in={isExpanded} animateOpacity>
          <VStack align="start" mt={3} spacing={2}>
            <HStack>
              <Text fontWeight="semibold" fontSize="sm">Goal ID:</Text>
              <Text fontSize="sm" fontFamily="monospace">{instruction.goal_id}</Text>
            </HStack>
            
            <HStack>
              <Text fontWeight="semibold" fontSize="sm">Agent:</Text>
              <Text fontSize="sm">{instruction.agent_id}</Text>
            </HStack>
            
            <Box width="100%">
              <Text fontWeight="semibold" fontSize="sm">Tools Required:</Text>
              <Flex flexWrap="wrap" gap={1} mt={1}>
                {instruction.tools_required.map((tool: string, i: number) => (
                  <Badge key={i} colorScheme="blue">{tool}</Badge>
                ))}
              </Flex>
            </Box>
            
            <Box width="100%">
              <Text fontWeight="semibold" fontSize="sm">Expected Outputs:</Text>
              <VStack align="start" mt={1} spacing={1}>
                {instruction.expected_outputs.map((output: any, i: number) => (
                  <HStack key={i}>
                    <Badge colorScheme={output.required ? "red" : "gray"}>
                      {output.required ? "required" : "optional"}
                    </Badge>
                    <Text fontSize="sm">{output.type}: {output.tag}</Text>
                  </HStack>
                ))}
              </VStack>
            </Box>
            
            <HStack>
              <Text fontWeight="semibold" fontSize="sm">Status:</Text>
              <Badge colorScheme={
                instruction.status === 'complete' ? 'green' : 
                instruction.status === 'failed' ? 'red' : 
                instruction.status === 'in_progress' ? 'blue' : 'gray'
              }>
                {instruction.status}
              </Badge>
            </HStack>
          </VStack>
        </Collapse>
      </Box>
    );
  };

  // Show loading spinner while agent is being fetched
  if (agentLoading) {
    return (
      <Flex flexDirection="column" height="100vh" alignItems="center" justifyContent="center">
        <Spinner size="xl" color="blue.500" mb={4} />
        <Text color="gray.600">Loading agent...</Text>
      </Flex>
    );
  }

  // Show error state if agent fetch failed
  if (agentError && !agent) {
    return (
      <Flex flexDirection="column" height="100vh" alignItems="center" justifyContent="center">
        <Box bg="red.100" border="1px" borderColor="red.400" color="red.700" px={4} py={3} borderRadius="md" maxWidth="md">
          <Text fontWeight="bold">Error!</Text>
          <Text> Failed to load agent. Please try again later.</Text>
        </Box>
      </Flex>
    );
  }

  return (
    <Flex flexDirection="column" height="100vh">
      <Flex p={2} justifyContent="space-between" alignItems="center" borderBottomWidth="1px">
        <Flex alignItems="center">
          <Text fontWeight="bold" mr={2}>
            {agent?.name || resolvedAgentId}
          </Text>
          <Badge fontSize="xs" bg="gray.200" px={2} py={1} borderRadius="md">
            {resolvedAgentId}
          </Badge>
        </Flex>
        <Flex gap={2}>
          <Button
            onClick={clearHistory}
            size="sm"
            colorScheme="gray"
          >
            Clear History
          </Button>
          <Button
            onClick={handleLogout}
            size="sm"
            colorScheme="red"
          >
            Logout
          </Button>
        </Flex>
      </Flex>

      <Box ref={feedRef} flex="1" overflowY="auto" p={4}>
        {messages.length === 0 ? (
          <Flex textAlign="center" color="gray.500" mt={10} justifyContent="center">
            <Text>Start a new conversation with {agent?.name || resolvedAgentId}</Text>
          </Flex>
        ) : (
          messages.map((msg, i) => (
            <Box key={i} my={2} textAlign={msg.role === 'user' ? 'right' : 'left'}>
              <Box
                display="inline-block"
                px={4}
                py={2}
                borderRadius="xl"
                bg={
                  msg.role === 'user'
                    ? 'blue.600'
                    : msg.role === 'system'
                      ? 'gray.500'
                      : msg.role === 'orchestrator'
                        ? 'purple.500'
                        : 'gray.200'
                }
                color={
                  msg.role === 'user' || msg.role === 'system' || msg.role === 'orchestrator'
                    ? 'white'
                    : 'black'
                }
                maxWidth="80%"
              >
                <Text fontWeight="bold">
                  {msg.role === 'user' 
                    ? 'You' 
                    : msg.role === 'assistant' 
                      ? (agent?.name || 'ASSISTANT') 
                      : msg.role === 'orchestrator'
                        ? 'ORCHESTRATOR'
                        : msg.role.toUpperCase()}:
                </Text> 
                <Text>{msg.content}</Text>
                
                {/* Render instruction card for orchestrator messages with instructions */}
                {msg.role === 'orchestrator' && msg.instruction && 
                  renderInstructionCard(msg.instruction, !!msg.isExpanded, i)}
              </Box>
            </Box>
          ))
        )}
      </Box>

      <Flex p={4} borderTopWidth="1px" alignItems="center" gap={2}>
        <Button
          onClick={() => setDebugOpen(!debugOpen)}
          size="sm"
          variant="outline"
        >
          &lt;/&gt;
        </Button>
        <Button
          onClick={() => setStreaming(!streaming)}
          size="sm"
          variant="outline"
        >
          {streaming ? 'Streaming ON' : 'Streaming OFF'}
        </Button>
        <Textarea
          flex="1"
          borderRadius="md"
          p={2}
          rows={2}
          placeholder="Enter your task..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        <Button
          onClick={handleSubmit}
          isDisabled={loading}
          colorScheme={loading ? 'gray' : 'blue'}
        >
          {loading ? (
            <Flex alignItems="center">
              <Spinner size="sm" mr={2} />
              <Text>Thinking...</Text>
            </Flex>
          ) : (
            'Send'
          )}
        </Button>
      </Flex>
    </Flex>
  );
};

export default AgentChat;
