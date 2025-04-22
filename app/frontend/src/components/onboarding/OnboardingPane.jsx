import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Image,
  List,
  ListItem,
  ListIcon,
  Divider,
  useColorModeValue,
  CloseButton,
  Collapse,
  Icon
} from '@chakra-ui/react';
import { FaCheckCircle, FaInfoCircle, FaLightbulb, FaQuestionCircle } from 'react-icons/fa';

/**
 * OnboardingPane Component
 * 
 * Floating right-side pane or modal that introduces users to Promethios concepts.
 * Includes tabs for "What is Promethios?", "What is a loop?", and "How do I talk to an agent?"
 * 
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether the pane is open
 * @param {function} props.onClose - Function to call when closing the pane
 * @param {string} props.initialTab - Initial tab to show (default: 'about')
 */
const OnboardingPane = ({ isOpen = true, onClose, initialTab = 'about' }) => {
  const [tabIndex, setTabIndex] = useState(
    initialTab === 'about' ? 0 : initialTab === 'loops' ? 1 : initialTab === 'agents' ? 2 : 0
  );
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headingColor = useColorModeValue('blue.600', 'blue.300');
  const textColor = useColorModeValue('gray.700', 'gray.300');
  
  if (!isOpen) return null;
  
  return (
    <Box
      position="fixed"
      right="0"
      top="0"
      height="100vh"
      width={{ base: "100%", md: "450px" }}
      bg={bgColor}
      borderLeft="1px solid"
      borderColor={borderColor}
      boxShadow="-4px 0 10px rgba(0, 0, 0, 0.1)"
      zIndex="1000"
      overflowY="auto"
      transition="all 0.3s ease"
    >
      <Flex justify="space-between" align="center" p={4} borderBottom="1px solid" borderColor={borderColor}>
        <Heading size="md" color={headingColor}>Promethios Guide</Heading>
        <CloseButton onClick={onClose} />
      </Flex>
      
      <Tabs isFitted variant="enclosed" index={tabIndex} onChange={setTabIndex}>
        <TabList mb="1em" borderBottom="1px solid" borderColor={borderColor}>
          <Tab>What is Promethios?</Tab>
          <Tab>What is a loop?</Tab>
          <Tab>How to talk to agents?</Tab>
        </TabList>
        
        <TabPanels>
          {/* What is Promethios? */}
          <TabPanel>
            <Box p={2}>
              <Heading size="md" mb={4} color={headingColor}>Welcome to Promethios</Heading>
              <Text mb={4} color={textColor}>
                Promethios is a cognitive operating system that helps you think, create, and solve problems. 
                It's designed to be an extension of your own cognitive abilities, providing tools for deeper 
                reasoning and more effective problem-solving.
              </Text>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3} color={headingColor}>Key Features</Heading>
              <List spacing={3} mb={4}>
                <ListItem>
                  <ListIcon as={FaCheckCircle} color="green.500" />
                  <Text as="span" fontWeight="bold">Cognitive Loops</Text>: Break down complex problems into manageable steps
                </ListItem>
                <ListItem>
                  <ListIcon as={FaCheckCircle} color="green.500" />
                  <Text as="span" fontWeight="bold">Specialized Agents</Text>: Delegate tasks to agents with different cognitive strengths
                </ListItem>
                <ListItem>
                  <ListIcon as={FaCheckCircle} color="green.500" />
                  <Text as="span" fontWeight="bold">Memory System</Text>: Store and retrieve information across sessions
                </ListItem>
                <ListItem>
                  <ListIcon as={FaCheckCircle} color="green.500" />
                  <Text as="span" fontWeight="bold">Orchestrator Modes</Text>: Control the depth vs. speed of thinking
                </ListItem>
              </List>
              
              <Divider my={4} />
              
              <Box bg="blue.50" p={4} borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
                <Flex align="center" mb={2}>
                  <Icon as={FaLightbulb} color="blue.500" mr={2} />
                  <Text fontWeight="bold" color="blue.700">SAGE Wisdom</Text>
                </Flex>
                <Text fontStyle="italic" color="blue.700">
                  "Promethios is not just a tool, but a partner in your cognitive journey. 
                  The more you engage with it, the more it adapts to your thinking patterns and needs."
                </Text>
              </Box>
              
              <Button colorScheme="blue" mt={6} onClick={() => setTabIndex(1)}>
                Learn About Loops →
              </Button>
            </Box>
          </TabPanel>
          
          {/* What is a loop? */}
          <TabPanel>
            <Box p={2}>
              <Heading size="md" mb={4} color={headingColor}>Understanding Cognitive Loops</Heading>
              <Text mb={4} color={textColor}>
                Cognitive loops are the fundamental thinking units in Promethios. They represent how the system 
                breaks down complex tasks into manageable steps, similar to how human thought processes work.
              </Text>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3} color={headingColor}>Loop Components</Heading>
              <List spacing={3} mb={4}>
                <ListItem>
                  <ListIcon as={FaInfoCircle} color="blue.500" />
                  <Text as="span" fontWeight="bold">Goal</Text>: The objective the loop aims to achieve
                </ListItem>
                <ListItem>
                  <ListIcon as={FaInfoCircle} color="blue.500" />
                  <Text as="span" fontWeight="bold">Context</Text>: Relevant information and constraints
                </ListItem>
                <ListItem>
                  <ListIcon as={FaInfoCircle} color="blue.500" />
                  <Text as="span" fontWeight="bold">Steps</Text>: Individual cognitive actions to take
                </ListItem>
                <ListItem>
                  <ListIcon as={FaInfoCircle} color="blue.500" />
                  <Text as="span" fontWeight="bold">Reflection</Text>: Evaluation of progress and adjustments
                </ListItem>
              </List>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3} color={headingColor}>Loop Visualization</Heading>
              <Text mb={4} color={textColor}>
                In the Goal Loop Visualization panel, you can see how Promethios is thinking about your request. 
                Each loop represents a distinct cognitive process, and you can explore how they connect and build 
                upon each other.
              </Text>
              
              <Box bg="blue.50" p={4} borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
                <Flex align="center" mb={2}>
                  <Icon as={FaLightbulb} color="blue.500" mr={2} />
                  <Text fontWeight="bold" color="blue.700">SAGE Wisdom</Text>
                </Flex>
                <Text fontStyle="italic" color="blue.700">
                  "The path of thought becomes visible when we map the journey of understanding. 
                  By observing loops, you gain insight into not just what Promethios thinks, but how it thinks."
                </Text>
              </Box>
              
              <Flex justify="space-between" mt={6}>
                <Button variant="outline" colorScheme="blue" onClick={() => setTabIndex(0)}>
                  ← Back to Overview
                </Button>
                <Button colorScheme="blue" onClick={() => setTabIndex(2)}>
                  Learn About Agents →
                </Button>
              </Flex>
            </Box>
          </TabPanel>
          
          {/* How do I talk to an agent? */}
          <TabPanel>
            <Box p={2}>
              <Heading size="md" mb={4} color={headingColor}>Communicating with Agents</Heading>
              <Text mb={4} color={textColor}>
                Promethios features multiple specialized agents, each with different cognitive strengths. 
                You can communicate with them through the Agent Chat Console or delegate specific tasks 
                through the Agent Panel.
              </Text>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3} color={headingColor}>Using the Chat Console</Heading>
              <List spacing={3} mb={4}>
                <ListItem>
                  <ListIcon as={FaQuestionCircle} color="purple.500" />
                  <Text as="span" fontWeight="bold">Direct Messages</Text>: Type your question or request in the chat input
                </ListItem>
                <ListItem>
                  <ListIcon as={FaQuestionCircle} color="purple.500" />
                  <Text as="span" fontWeight="bold">Agent Selection</Text>: Choose a specific agent from the dropdown or use @ mentions
                </ListItem>
                <ListItem>
                  <ListIcon as={FaQuestionCircle} color="purple.500" />
                  <Text as="span" fontWeight="bold">Markdown Support</Text>: Format your messages using markdown syntax
                </ListItem>
                <ListItem>
                  <ListIcon as={FaQuestionCircle} color="purple.500" />
                  <Text as="span" fontWeight="bold">File Sharing</Text>: Attach files by dragging them into the chat area
                </ListItem>
              </List>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3} color={headingColor}>Agent Types</Heading>
              <List spacing={3} mb={4}>
                <ListItem>
                  <Text as="span" fontWeight="bold">Orchestrator</Text>: Coordinates complex tasks and manages other agents
                </ListItem>
                <ListItem>
                  <Text as="span" fontWeight="bold">Sage</Text>: Provides wisdom, reflection, and philosophical insights
                </ListItem>
                <ListItem>
                  <Text as="span" fontWeight="bold">Builder</Text>: Creates and implements technical solutions
                </ListItem>
                <ListItem>
                  <Text as="span" fontWeight="bold">Researcher</Text>: Gathers and analyzes information
                </ListItem>
                <ListItem>
                  <Text as="span" fontWeight="bold">Skeptic</Text>: Challenges assumptions and identifies potential issues
                </ListItem>
              </List>
              
              <Box bg="blue.50" p={4} borderRadius="md" borderLeft="4px solid" borderColor="blue.500">
                <Flex align="center" mb={2}>
                  <Icon as={FaLightbulb} color="blue.500" mr={2} />
                  <Text fontWeight="bold" color="blue.700">SAGE Wisdom</Text>
                </Flex>
                <Text fontStyle="italic" color="blue.700">
                  "Through dialogue, we bridge the gap between human intention and machine understanding. 
                  Be clear in your requests, but don't hesitate to explore and refine your questions through conversation."
                </Text>
              </Box>
              
              <Flex justify="space-between" mt={6}>
                <Button variant="outline" colorScheme="blue" onClick={() => setTabIndex(1)}>
                  ← Back to Loops
                </Button>
                <Button colorScheme="green" onClick={onClose}>
                  Start Using Promethios
                </Button>
              </Flex>
            </Box>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default OnboardingPane;
