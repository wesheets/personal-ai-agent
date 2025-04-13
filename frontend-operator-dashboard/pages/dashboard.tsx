import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Box, Flex, Grid, GridItem, useColorModeValue } from '@chakra-ui/react';

// Import components
import Sidebar from '../src/components/layout/Sidebar';
import AgentChatPanel from '../src/components/AgentChatPanel';
import AgentSandboxCard from '../src/components/AgentSandboxCard';
import ToolOutputCard from '../src/components/ToolOutputCard';
import CheckpointApprovalPanel from '../src/components/CheckpointApprovalPanel';
import InputUI from '../src/components/InputUI';

const Dashboard = () => {
  // Check if user is authenticated
  const isAuthenticated = localStorage.getItem('authToken') === 'operator-authenticated' || 
                          localStorage.getItem('authToken') === 'architect-special-access';
  
  // Redirect to splash page if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock data for demonstration
  const [activeAgent, setActiveAgent] = useState('hal9000');
  const [messages, setMessages] = useState([
    { sender: 'system', text: 'HAL 9000 initialized and ready.', timestamp: new Date() },
    { sender: 'agent', text: 'Hello, I am HAL 9000. How can I assist you today?', timestamp: new Date() },
    { sender: 'user', text: 'Can you search for information about quantum computing?', timestamp: new Date() },
    { sender: 'system', text: 'HAL ran tool: search.web', timestamp: new Date() },
    { sender: 'agent', text: 'I found several resources about quantum computing. Quantum computing is a type of computation that harnesses quantum mechanical phenomena. Would you like me to provide more specific information?', timestamp: new Date() }
  ]);

  // Agent sandbox data
  const agents = [
    { id: 'hal9000', name: 'HAL 9000', status: 'active', currentTask: 'Information retrieval', activeTools: ['search.web', 'memory.read'], color: 'blue' },
    { id: 'ash-xenomorph', name: 'ASH', status: 'idle', currentTask: 'None', activeTools: [], color: 'purple' },
    { id: 'nova', name: 'NOVA', status: 'processing', currentTask: 'Data analysis', activeTools: ['data.analyze', 'chart.create'], color: 'orange' }
  ];

  // Tool output data
  const toolOutputs = [
    { 
      id: 'tool1', 
      name: 'search.web', 
      output: '## Quantum Computing Results\n\n1. **Introduction to Quantum Computing** - IBM Research\n2. **Quantum Computing Applications** - Nature Journal\n3. **Quantum Supremacy Explained** - Google AI Blog\n\n```python\n# Example quantum algorithm\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure([0, 1], [0, 1])\n```', 
      timestamp: new Date() 
    }
  ];

  // Checkpoint data
  const checkpoints = [
    { id: 'cp1', title: 'Web Search Authorization', description: 'HAL 9000 requests permission to search external data sources for quantum computing information', status: 'pending', type: 'soft', timestamp: new Date() },
    { id: 'cp2', title: 'Data Analysis Plan', description: 'Review proposed analysis methodology for quantum computing research data', status: 'pending', type: 'hard', timestamp: new Date() }
  ];

  const handleSendMessage = (message) => {
    if (!message.trim()) return;
    
    // Add user message
    const userMessage = {
      sender: 'user',
      text: message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Simulate agent response
    setTimeout(() => {
      const systemMessage = {
        sender: 'system',
        text: `${agents[0].name} processing request...`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, systemMessage]);
      
      setTimeout(() => {
        const agentResponse = {
          sender: 'agent',
          text: `I've processed your request: "${message}". Is there anything specific you'd like to know about this topic?`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, agentResponse]);
      }, 1500);
    }, 500);
  };

  return (
    <Grid
      templateColumns={{ base: '1fr', md: '250px 1fr' }}
      h="100vh"
      bg={bgColor}
    >
      {/* Sidebar */}
      <GridItem display={{ base: 'none', md: 'block' }}>
        <Sidebar />
      </GridItem>
      
      {/* Main Content */}
      <GridItem colSpan={{ base: 1, md: 'auto' }} overflowY="auto">
        <Grid
          templateColumns={{ base: '1fr', lg: '1fr 300px' }}
          templateRows={{ base: 'auto 1fr auto', lg: '1fr auto' }}
          h="100vh"
          gap={4}
          p={4}
        >
          {/* Agent Chat Thread */}
          <GridItem rowSpan={1} overflowY="auto" bg="white" borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <Box p={4} h="100%">
              <AgentChatPanel />
            </Box>
          </GridItem>
          
          {/* Right Panel - Agent Sandbox and Checkpoints */}
          <GridItem rowSpan={2} colSpan={{ base: 1, lg: 1 }} display="flex" flexDirection="column" gap={4}>
            {/* Agent Sandbox Panel */}
            <Box flex="1" bg="white" p={4} borderRadius="lg" borderWidth="1px" borderColor={borderColor} overflowY="auto">
              <Box mb={4}>
                <h2 className="text-xl font-semibold mb-2">Agent Sandbox</h2>
                {agents.map(agent => (
                  <Box 
                    key={agent.id}
                    p={3}
                    mb={3}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor={agent.id === activeAgent ? `${agent.color}.500` : borderColor}
                    bg={agent.id === activeAgent ? `${agent.color}.50` : 'white'}
                    cursor="pointer"
                    onClick={() => setActiveAgent(agent.id)}
                  >
                    <Flex align="center" mb={2}>
                      <Box
                        bg={`${agent.color}.500`}
                        color="white"
                        borderRadius="full"
                        boxSize="24px"
                        fontSize="xs"
                        fontWeight="bold"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        mr={2}
                      >
                        {agent.name.charAt(0)}
                      </Box>
                      <Box>
                        <Box fontWeight="bold">{agent.name}</Box>
                        <Box fontSize="xs" color={agent.status === 'active' ? 'green.500' : agent.status === 'processing' ? 'orange.500' : 'gray.500'}>
                          {agent.status.toUpperCase()}
                        </Box>
                      </Box>
                    </Flex>
                    {agent.id === activeAgent && (
                      <>
                        <Box fontSize="sm" mb={1}>
                          <strong>Current Task:</strong> {agent.currentTask}
                        </Box>
                        {agent.activeTools.length > 0 && (
                          <Box fontSize="sm">
                            <strong>Active Tools:</strong> {agent.activeTools.join(', ')}
                          </Box>
                        )}
                      </>
                    )}
                  </Box>
                ))}
              </Box>
              
              {/* Tool Output Panel */}
              <Box>
                <h2 className="text-xl font-semibold mb-2">Tool Outputs</h2>
                {toolOutputs.map(tool => (
                  <Box 
                    key={tool.id}
                    p={3}
                    mb={3}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor={borderColor}
                    bg="gray.50"
                  >
                    <Box fontWeight="bold" mb={1}>{tool.name}</Box>
                    <Box 
                      p={2}
                      borderRadius="md"
                      bg="gray.100"
                      fontSize="sm"
                      fontFamily="monospace"
                      whiteSpace="pre-wrap"
                      overflowX="auto"
                    >
                      {tool.output}
                    </Box>
                    <Box fontSize="xs" color="gray.500" mt={1}>
                      {tool.timestamp.toLocaleTimeString()}
                    </Box>
                  </Box>
                ))}
              </Box>
            </Box>
            
            {/* Checkpoint Approval Panel */}
            <Box flex="1" bg="white" p={4} borderRadius="lg" borderWidth="1px" borderColor={borderColor} overflowY="auto">
              <h2 className="text-xl font-semibold mb-2">Checkpoints</h2>
              {checkpoints.map(checkpoint => (
                <Box 
                  key={checkpoint.id}
                  p={3}
                  mb={3}
                  borderRadius="md"
                  borderWidth="1px"
                  borderColor={checkpoint.type === 'hard' ? 'red.200' : 'yellow.200'}
                  bg={checkpoint.type === 'hard' ? 'red.50' : 'yellow.50'}
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <Box fontWeight="bold">{checkpoint.title}</Box>
                    <Box 
                      fontSize="xs" 
                      px={2} 
                      py={1} 
                      borderRadius="full" 
                      bg={checkpoint.type === 'hard' ? 'red.100' : 'yellow.100'}
                    >
                      {checkpoint.type.toUpperCase()}
                    </Box>
                  </Flex>
                  <Box fontSize="sm" mb={2}>{checkpoint.description}</Box>
                  <Flex justify="space-between" mt={2}>
                    <Box fontSize="xs" color="gray.500">
                      {checkpoint.timestamp.toLocaleTimeString()}
                    </Box>
                    <Flex>
                      <Box 
                        as="button"
                        fontSize="xs"
                        px={3}
                        py={1}
                        borderRadius="md"
                        bg="green.100"
                        color="green.700"
                        mr={2}
                        _hover={{ bg: 'green.200' }}
                      >
                        Approve
                      </Box>
                      <Box 
                        as="button"
                        fontSize="xs"
                        px={3}
                        py={1}
                        borderRadius="md"
                        bg="red.100"
                        color="red.700"
                        _hover={{ bg: 'red.200' }}
                      >
                        Reject
                      </Box>
                    </Flex>
                  </Flex>
                </Box>
              ))}
            </Box>
          </GridItem>
          
          {/* Input UI */}
          <GridItem colSpan={{ base: 1, lg: 1 }} bg="white" p={4} borderRadius="lg" borderWidth="1px" borderColor={borderColor}>
            <Flex>
              <Box flex="1" mr={2}>
                <input
                  type="text"
                  placeholder="Type your message here..."
                  className="w-full p-2 border border-gray-300 rounded"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSendMessage(e.target.value);
                      e.target.value = '';
                    }
                  }}
                />
              </Box>
              <Box 
                as="button"
                px={4}
                py={2}
                borderRadius="md"
                bg="blue.500"
                color="white"
                _hover={{ bg: 'blue.600' }}
                onClick={() => {
                  const input = document.querySelector('input');
                  handleSendMessage(input.value);
                  input.value = '';
                }}
              >
                Send
              </Box>
            </Flex>
          </GridItem>
        </Grid>
      </GridItem>
    </Grid>
  );
};

export default Dashboard;
