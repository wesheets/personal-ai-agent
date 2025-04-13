import React, { useState } from 'react';
import {
  Box,
  Grid,
  GridItem,
  Flex,
  useColorModeValue,
  Image,
  Link as ChakraLink,
  VStack
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import SidebarNavigation from '../components/SidebarNavigation';
import AgentChat from '../components/AgentChat';
import AgentSandboxCard from '../components/AgentSandboxCard';
import ToolOutputCard from '../components/ToolOutputCard';
import CheckpointApprovalPanel from '../components/CheckpointApprovalPanel';
import InputUI from '../components/InputUI';

const Dashboard = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Mock data for agent sandbox cards
  const agents = [
    {
      id: 'hal',
      name: 'HAL',
      status: 'executing',
      activeTask: 'Researching React state management',
      lastMemoryEntry: 'Found 5 articles about Redux vs Context API',
      tools: ['search.web', 'code.generate', 'copy.write'],
      reflection: 'Current task requires deep technical knowledge. Will focus on practical examples.'
    },
    {
      id: 'ash',
      name: 'ASH',
      status: 'idle',
      activeTask: 'Waiting for new instructions',
      lastMemoryEntry: 'Completed API documentation task',
      tools: ['code.review', 'api.test', 'docs.generate'],
      reflection: 'Ready for next assignment. Previous task completed with 98% accuracy.'
    },
    {
      id: 'nova',
      name: 'NOVA',
      status: 'paused',
      activeTask: 'Content generation for blog post',
      lastMemoryEntry: 'Draft created, awaiting operator approval',
      tools: ['copy.write', 'image.generate', 'seo.analyze'],
      reflection: 'Content draft needs technical review before proceeding.'
    }
  ];
  
  // Mock data for tool outputs
  const toolOutputs = [
    {
      id: 'tool1',
      toolName: 'search.web',
      content: 'Found 5 relevant articles about React state management:\n1. "Redux vs Context API" - React Docs\n2. "When to use Redux" - Medium\n3. "State Management in 2025" - Dev.to\n4. "Context API Best Practices" - LogRocket\n5. "Redux Toolkit Overview" - Redux Docs',
      timestamp: new Date(Date.now() - 1000 * 60 * 10),
      memoryId: 'mem123'
    },
    {
      id: 'tool2',
      toolName: 'code.generate',
      content: 'import { createContext, useContext, useState } from "react";\n\nconst StateContext = createContext();\n\nexport const StateProvider = ({ children }) => {\n  const [count, setCount] = useState(0);\n  \n  const increment = () => setCount(prev => prev + 1);\n  const decrement = () => setCount(prev => prev - 1);\n  \n  return (\n    <StateContext.Provider value={{ count, increment, decrement }}>\n      {children}\n    </StateContext.Provider>\n  );\n};\n\nexport const useStateContext = () => useContext(StateContext);',
      language: 'javascript',
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
      memoryId: 'mem456'
    }
  ];
  
  // Handle sending a message
  const handleSendMessage = (message) => {
    console.log('Message sent:', message);
    // In a real implementation, this would add the message to the chat
  };

  return (
    <Box bg={bgColor} minH="100vh" pb="80px"> {/* Add padding to bottom for input UI */}
      {/* Header with logo */}
      <Flex 
        as="header" 
        position="fixed" 
        w="full" 
        zIndex="1000"
        bg={useColorModeValue('white', 'gray.800')}
        boxShadow="sm"
        p={2}
        borderBottomWidth="1px"
        borderColor={borderColor}
      >
        <ChakraLink as={Link} to="/dashboard">
          <Image 
            src="/promethioslogo.png" 
            alt="Promethios Logo" 
            maxW={{ base: "80px", md: "120px" }}
            transition="all 0.2s"
            _hover={{ transform: 'scale(1.05)' }}
          />
        </ChakraLink>
      </Flex>
      
      {/* Main content with 3-panel layout */}
      <Grid
        templateColumns={{ base: "1fr", md: "240px 1fr 300px" }}
        gap={4}
        pt="70px" // Space for header
        px={4}
        maxW="1800px"
        mx="auto"
      >
        {/* Left Panel: Sidebar Navigation */}
        <GridItem display={{ base: 'none', md: 'block' }}>
          <Box position="sticky" top="70px" maxH="calc(100vh - 70px)" overflowY="auto">
            <SidebarNavigation />
          </Box>
        </GridItem>
        
        {/* Center Panel: Agent Chat Thread */}
        <GridItem>
          <Box maxH="calc(100vh - 150px)" overflowY="auto">
            <AgentChat agentId="hal" />
          </Box>
        </GridItem>
        
        {/* Right Panel: Agent Sandbox Cards & Tool Output */}
        <GridItem>
          <Box position="sticky" top="70px" maxH="calc(100vh - 70px)" overflowY="auto">
            <VStack spacing={4} align="stretch">
              {/* Agent Sandbox Cards */}
              <Box>
                {agents.map(agent => (
                  <AgentSandboxCard key={agent.id} agent={agent} />
                ))}
              </Box>
              
              {/* Checkpoint Approval Panel */}
              <CheckpointApprovalPanel />
              
              {/* Tool Output Cards */}
              <Box>
                {toolOutputs.map(output => (
                  <ToolOutputCard key={output.id} output={output} />
                ))}
              </Box>
            </VStack>
          </Box>
        </GridItem>
      </Grid>
      
      {/* Fixed Input UI at bottom */}
      <InputUI onSendMessage={handleSendMessage} />
    </Box>
  );
};

export default Dashboard;
