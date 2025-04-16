import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  HStack,
  Text,
  Badge,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { FiCpu, FiGrid } from 'react-icons/fi';

interface SidebarProps {
  activeAgent: string;
  onSelectAgent: (agentId: string) => void;
  onSelectThread: (threadId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeAgent, onSelectAgent, onSelectThread }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', '#1F2937');

  // Mock data for agents
  const agents = [
    { id: 'orchestrator', name: 'Orchestrator', type: 'system', color: 'purple' },
    { id: 'hal', name: 'HAL', type: 'agent', color: 'blue' },
    { id: 'ash', name: 'ASH', type: 'agent', color: 'teal' },
    { id: 'nova', name: 'NOVA', type: 'agent', color: 'orange' }
  ];

  // Mock data for threads
  const threads = [
    { id: 'thread_1', title: 'React State Management', agentId: 'hal', messageCount: 6 },
    { id: 'thread_2', title: 'API Integration', agentId: 'nova', messageCount: 3 },
    { id: 'thread_3', title: 'UI Component Library', agentId: 'ash', messageCount: 4 }
  ];

  // Mock data for tools
  const tools = [
    { id: 'tool_1', name: 'Web Search', category: 'research' },
    { id: 'tool_2', name: 'Code Generator', category: 'development' },
    { id: 'tool_3', name: 'Data Analyzer', category: 'analysis' }
  ];

  // Mock data for checkpoints
  const checkpoints = [
    { id: 'checkpoint_1', name: 'Research Complete', status: 'pending' },
    { id: 'checkpoint_2', name: 'Design Approved', status: 'approved' },
    { id: 'checkpoint_3', name: 'Implementation Started', status: 'active' }
  ];

  return (
    <Box
      h="100%"
      w="260px" // Exactly 260px as specified
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
    >
      <VStack align="stretch" spacing={0} h="100%">
        <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
          <Heading size="md">Promethios</Heading>
        </Box>

        <Box overflowY="auto" flex="1" p={2}>
          <Accordion defaultIndex={[0, 1]} allowMultiple>
            {/* System Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    🧠 SYSTEM
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <VStack align="stretch" spacing={1}>
                  <Box
                    key="orchestrator"
                    p={2}
                    borderRadius="6px" // 6px radius as specified
                    cursor="pointer"
                    bg={activeAgent === 'orchestrator' ? 'purple.50' : 'transparent'}
                    _hover={{ bg: hoverBg }}
                    onClick={() => onSelectAgent('orchestrator')}
                  >
                    <HStack>
                      <Icon as={FiGrid} color="purple.500" />
                      <Text fontSize="16px">Orchestrator</Text>
                      <Badge colorScheme="purple" variant="subtle" size="sm">
                        System
                      </Badge>
                    </HStack>
                  </Box>
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Agents Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    👤 AGENTS
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <VStack align="stretch" spacing={1}>
                  {agents
                    .filter((agent) => agent.id !== 'orchestrator')
                    .map((agent) => (
                      <Box
                        key={agent.id}
                        p={2}
                        borderRadius="6px" // 6px radius as specified
                        cursor="pointer"
                        bg={activeAgent === agent.id ? `${agent.color}.50` : 'transparent'}
                        _hover={{ bg: hoverBg }}
                        onClick={() => onSelectAgent(agent.id)}
                      >
                        <HStack>
                          <Icon as={FiCpu} color={`${agent.color}.500`} />
                          <Text fontSize="16px">{agent.name}</Text>
                        </HStack>
                      </Box>
                    ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Goals/Threads Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    📌 Goals / Threads
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <VStack align="stretch" spacing={1}>
                  {threads.map((thread) => (
                    <Box
                      key={thread.id}
                      p={2}
                      borderRadius="6px" // 6px radius as specified
                      cursor="pointer"
                      _hover={{ bg: hoverBg }}
                      onClick={() => onSelectThread(thread.id)}
                    >
                      <Text fontSize="16px" fontWeight="medium">
                        {thread.title}
                      </Text>
                      <HStack fontSize="xs" color={useColorModeValue('gray.600', 'gray.400')}>
                        <Text>{thread.agentId}</Text>
                        <Text>•</Text>
                        <Text>{thread.messageCount} messages</Text>
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Tools Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    🧰 Tools
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <VStack align="stretch" spacing={1}>
                  {tools.map((tool) => (
                    <Box
                      key={tool.id}
                      p={2}
                      borderRadius="6px" // 6px radius as specified
                      cursor="pointer"
                      _hover={{ bg: hoverBg }}
                    >
                      <Text fontSize="16px">{tool.name}</Text>
                      <Badge size="sm" colorScheme="gray" variant="subtle">
                        {tool.category}
                      </Badge>
                    </Box>
                  ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Checkpoints Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    ⏳ Checkpoints
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <VStack align="stretch" spacing={1}>
                  {checkpoints.map((checkpoint) => (
                    <Box
                      key={checkpoint.id}
                      p={2}
                      borderRadius="6px" // 6px radius as specified
                      cursor="pointer"
                      _hover={{ bg: hoverBg }}
                    >
                      <Text fontSize="16px">{checkpoint.name}</Text>
                      <Badge
                        size="sm"
                        colorScheme={
                          checkpoint.status === 'approved'
                            ? 'green'
                            : checkpoint.status === 'active'
                              ? 'blue'
                              : 'yellow'
                        }
                      >
                        {checkpoint.status}
                      </Badge>
                    </Box>
                  ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>

            {/* Archives Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    🗄 Archives
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <Text fontSize="16px" color={useColorModeValue('gray.600', 'gray.400')}>
                  No archived threads
                </Text>
              </AccordionPanel>
            </AccordionItem>

            {/* Settings Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    ⚙️ Settings
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <Text fontSize="16px" color={useColorModeValue('gray.600', 'gray.400')}>
                  System settings
                </Text>
              </AccordionPanel>
            </AccordionItem>

            {/* Help Section */}
            <AccordionItem border="none">
              <AccordionButton py={2} px={1}>
                <HStack flex="1" textAlign="left">
                  <Text fontWeight="medium" fontSize="16px">
                    🆘 Help
                  </Text>
                </HStack>
                <AccordionIcon />
              </AccordionButton>
              <AccordionPanel pb={4} pt={0} px={1}>
                <Text fontSize="16px" color={useColorModeValue('gray.600', 'gray.400')}>
                  Documentation and support
                </Text>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar;
