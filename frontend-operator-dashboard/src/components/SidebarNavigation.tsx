import React, { useState } from 'react';
import {
  Box,
  Flex,
  Text,
  Icon,
  VStack,
  HStack,
  useColorModeValue,
  Divider,
  Badge,
  Collapse,
  Button,
  Link as ChakraLink
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { 
  FiChevronDown, 
  FiChevronUp, 
  FiCpu, 
  FiTarget, 
  FiTool, 
  FiCheckSquare, 
  FiArchive,
  FiAlertTriangle
} from 'react-icons/fi';

interface SidebarNavigationProps {
  // Props can be extended as needed
}

const SidebarNavigation: React.FC<SidebarNavigationProps> = () => {
  const [expandedSections, setExpandedSections] = useState({
    agents: true,
    goals: false,
    tools: false,
    checkpoints: false,
    archives: false
  });
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.100', 'gray.700');
  
  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section]
    });
  };
  
  // Mock data - would be replaced with actual data from API
  const mockAgents = [
    { id: 'hal', name: 'HAL', status: 'executing', type: 'system' },
    { id: 'ash', name: 'ASH', status: 'idle', type: 'system' },
    { id: 'nova', name: 'NOVA', status: 'paused', type: 'system' }
  ];
  
  const mockGoals = [
    { id: 'goal-1', name: 'Build React Dashboard', status: 'in_progress' },
    { id: 'goal-2', name: 'Research API Integration', status: 'pending' }
  ];
  
  const mockTools = [
    { id: 'tool-1', name: 'search.web', category: 'research' },
    { id: 'tool-2', name: 'code.generate', category: 'development' },
    { id: 'tool-3', name: 'copy.write', category: 'content' }
  ];
  
  const mockCheckpoints = [
    { id: 'cp-1', name: 'Verify API Schema', agent: 'hal', type: 'hard' },
    { id: 'cp-2', name: 'Review Content Draft', agent: 'nova', type: 'soft' }
  ];
  
  const mockArchives = [
    { id: 'arch-1', name: 'Legacy System Migration', date: '2025-03-15' },
    { id: 'arch-2', name: 'Q1 Performance Report', date: '2025-04-01' }
  ];
  
  // Helper function to get status color
  const getStatusColor = (status: string) => {
    switch(status) {
      case 'executing': return 'green';
      case 'in_progress': return 'green';
      case 'paused': return 'orange';
      case 'idle': return 'gray';
      case 'pending': return 'blue';
      default: return 'gray';
    }
  };
  
  // Helper function to get checkpoint type color
  const getCheckpointTypeColor = (type: string) => {
    return type === 'hard' ? 'red' : 'yellow';
  };

  return (
    <Box
      as="nav"
      h="100%"
      bg={bgColor}
      borderRightWidth="1px"
      borderColor={borderColor}
      w="100%"
      overflowY="auto"
    >
      <VStack spacing={0} align="stretch">
        {/* Agents Section */}
        <Box>
          <Button
            variant="ghost"
            width="full"
            justifyContent="space-between"
            onClick={() => toggleSection('agents')}
            py={3}
            borderRadius={0}
          >
            <HStack>
              <Icon as={FiCpu} />
              <Text fontWeight="medium">Agents</Text>
            </HStack>
            <Icon as={expandedSections.agents ? FiChevronUp : FiChevronDown} />
          </Button>
          
          <Collapse in={expandedSections.agents} animateOpacity>
            <VStack align="stretch" pl={6} pr={2} pb={2}>
              {mockAgents.map((agent) => (
                <ChakraLink 
                  as={Link} 
                  to={`/agent/${agent.id}`} 
                  key={agent.id}
                  _hover={{ textDecoration: 'none' }}
                >
                  <HStack
                    py={2}
                    px={2}
                    borderRadius="md"
                    _hover={{ bg: hoverBgColor }}
                    transition="all 0.2s"
                  >
                    <Text fontSize="sm">{agent.name}</Text>
                    <Badge 
                      size="sm" 
                      colorScheme={getStatusColor(agent.status)}
                      ml="auto"
                    >
                      {agent.status}
                    </Badge>
                  </HStack>
                </ChakraLink>
              ))}
            </VStack>
          </Collapse>
        </Box>
        
        <Divider />
        
        {/* Goals/Threads Section */}
        <Box>
          <Button
            variant="ghost"
            width="full"
            justifyContent="space-between"
            onClick={() => toggleSection('goals')}
            py={3}
            borderRadius={0}
          >
            <HStack>
              <Icon as={FiTarget} />
              <Text fontWeight="medium">Goals / Threads</Text>
            </HStack>
            <Icon as={expandedSections.goals ? FiChevronUp : FiChevronDown} />
          </Button>
          
          <Collapse in={expandedSections.goals} animateOpacity>
            <VStack align="stretch" pl={6} pr={2} pb={2}>
              {mockGoals.map((goal) => (
                <ChakraLink 
                  as={Link} 
                  to={`/goal/${goal.id}`} 
                  key={goal.id}
                  _hover={{ textDecoration: 'none' }}
                >
                  <HStack
                    py={2}
                    px={2}
                    borderRadius="md"
                    _hover={{ bg: hoverBgColor }}
                    transition="all 0.2s"
                  >
                    <Text fontSize="sm" noOfLines={1}>{goal.name}</Text>
                    <Badge 
                      size="sm" 
                      colorScheme={getStatusColor(goal.status)}
                      ml="auto"
                    >
                      {goal.status}
                    </Badge>
                  </HStack>
                </ChakraLink>
              ))}
            </VStack>
          </Collapse>
        </Box>
        
        <Divider />
        
        {/* Tools Section */}
        <Box>
          <Button
            variant="ghost"
            width="full"
            justifyContent="space-between"
            onClick={() => toggleSection('tools')}
            py={3}
            borderRadius={0}
          >
            <HStack>
              <Icon as={FiTool} />
              <Text fontWeight="medium">Tools</Text>
            </HStack>
            <Icon as={expandedSections.tools ? FiChevronUp : FiChevronDown} />
          </Button>
          
          <Collapse in={expandedSections.tools} animateOpacity>
            <VStack align="stretch" pl={6} pr={2} pb={2}>
              {mockTools.map((tool) => (
                <ChakraLink 
                  as={Link} 
                  to={`/tool/${tool.id}`} 
                  key={tool.id}
                  _hover={{ textDecoration: 'none' }}
                >
                  <HStack
                    py={2}
                    px={2}
                    borderRadius="md"
                    _hover={{ bg: hoverBgColor }}
                    transition="all 0.2s"
                  >
                    <Text fontSize="sm">{tool.name}</Text>
                    <Badge 
                      size="sm" 
                      colorScheme="blue"
                      variant="outline"
                      ml="auto"
                    >
                      {tool.category}
                    </Badge>
                  </HStack>
                </ChakraLink>
              ))}
            </VStack>
          </Collapse>
        </Box>
        
        <Divider />
        
        {/* Checkpoints Section */}
        <Box>
          <Button
            variant="ghost"
            width="full"
            justifyContent="space-between"
            onClick={() => toggleSection('checkpoints')}
            py={3}
            borderRadius={0}
          >
            <HStack>
              <Icon as={FiCheckSquare} />
              <Text fontWeight="medium">Checkpoints</Text>
              {mockCheckpoints.length > 0 && (
                <Badge colorScheme="red" ml={1}>
                  {mockCheckpoints.length}
                </Badge>
              )}
            </HStack>
            <Icon as={expandedSections.checkpoints ? FiChevronUp : FiChevronDown} />
          </Button>
          
          <Collapse in={expandedSections.checkpoints} animateOpacity>
            <VStack align="stretch" pl={6} pr={2} pb={2}>
              {mockCheckpoints.map((checkpoint) => (
                <ChakraLink 
                  as={Link} 
                  to={`/checkpoint/${checkpoint.id}`} 
                  key={checkpoint.id}
                  _hover={{ textDecoration: 'none' }}
                >
                  <HStack
                    py={2}
                    px={2}
                    borderRadius="md"
                    _hover={{ bg: hoverBgColor }}
                    transition="all 0.2s"
                  >
                    <Icon 
                      as={FiAlertTriangle} 
                      color={`${getCheckpointTypeColor(checkpoint.type)}.500`}
                      mr={1}
                    />
                    <Text fontSize="sm" noOfLines={1}>{checkpoint.name}</Text>
                    <Badge 
                      size="sm" 
                      colorScheme="purple"
                      ml="auto"
                    >
                      {checkpoint.agent}
                    </Badge>
                  </HStack>
                </ChakraLink>
              ))}
            </VStack>
          </Collapse>
        </Box>
        
        <Divider />
        
        {/* Archives Section */}
        <Box>
          <Button
            variant="ghost"
            width="full"
            justifyContent="space-between"
            onClick={() => toggleSection('archives')}
            py={3}
            borderRadius={0}
          >
            <HStack>
              <Icon as={FiArchive} />
              <Text fontWeight="medium">Archives</Text>
            </HStack>
            <Icon as={expandedSections.archives ? FiChevronUp : FiChevronDown} />
          </Button>
          
          <Collapse in={expandedSections.archives} animateOpacity>
            <VStack align="stretch" pl={6} pr={2} pb={2}>
              {mockArchives.map((archive) => (
                <ChakraLink 
                  as={Link} 
                  to={`/archive/${archive.id}`} 
                  key={archive.id}
                  _hover={{ textDecoration: 'none' }}
                >
                  <HStack
                    py={2}
                    px={2}
                    borderRadius="md"
                    _hover={{ bg: hoverBgColor }}
                    transition="all 0.2s"
                  >
                    <Text fontSize="sm" noOfLines={1}>{archive.name}</Text>
                    <Text 
                      fontSize="xs" 
                      color="gray.500"
                      ml="auto"
                    >
                      {archive.date}
                    </Text>
                  </HStack>
                </ChakraLink>
              ))}
            </VStack>
          </Collapse>
        </Box>
      </VStack>
    </Box>
  );
};

export default SidebarNavigation;
