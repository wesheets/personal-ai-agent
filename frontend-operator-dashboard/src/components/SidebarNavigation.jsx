import React, { useState } from 'react';
import {
  Box,
  Flex,
  VStack,
  Text,
  Icon,
  Divider,
  useColorModeValue,
  Collapse,
  Image,
  Badge
} from '@chakra-ui/react';
import { 
  FiUsers, 
  FiTarget, 
  FiTool, 
  FiCheckSquare, 
  FiArchive,
  FiChevronDown,
  FiChevronRight,
  FiCpu,
  FiMessageSquare,
  FiSettings,
  FiHelpCircle,
  FiBriefcase,
  FiGrid
} from 'react-icons/fi';
import orchestratorAgent from '../data/orchestratorAgent';

const SidebarNavigation = () => {
  const [openSections, setOpenSections] = useState({
    agents: true,
    goals: false,
    tools: false,
    checkpoints: false,
    archives: false
  });
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.100', 'gray.700');
  const activeBgColor = useColorModeValue('blue.50', 'blue.900');
  const activeTextColor = useColorModeValue('blue.600', 'blue.200');
  
  const toggleSection = (section) => {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const NavSection = ({ title, icon, isOpen, children, onToggle }) => (
    <Box mb={2}>
      <Flex
        py={2}
        px={4}
        alignItems="center"
        cursor="pointer"
        borderRadius="md"
        _hover={{ bg: hoverBgColor }}
        onClick={onToggle}
      >
        <Icon as={icon} mr={3} />
        <Text fontWeight="medium">{title}</Text>
        <Icon 
          as={isOpen ? FiChevronDown : FiChevronRight} 
          ml="auto" 
          transition="all 0.2s"
        />
      </Flex>
      <Collapse in={isOpen} animateOpacity>
        <VStack 
          align="stretch" 
          pl={8} 
          mt={1} 
          spacing={1}
        >
          {children}
        </VStack>
      </Collapse>
    </Box>
  );
  
  const NavItem = ({ text, icon, isActive = false, color, isSystem = false }) => (
    <Flex
      py={2}
      px={4}
      alignItems="center"
      borderRadius="md"
      cursor="pointer"
      bg={isActive ? activeBgColor : 'transparent'}
      color={isActive ? activeTextColor : 'inherit'}
      _hover={{ bg: isActive ? activeBgColor : hoverBgColor }}
    >
      {icon && (
        <Box position="relative" mr={3}>
          <Icon as={icon} color={color ? `${color}.500` : undefined} />
          {isSystem && (
            <Box 
              position="absolute" 
              bottom="-2px" 
              right="-2px" 
              w="6px" 
              h="6px" 
              borderRadius="full" 
              bg={color ? `${color}.500` : "purple.500"} 
            />
          )}
        </Box>
      )}
      <Text fontSize="sm">{text}</Text>
      {isSystem && (
        <Badge ml={2} colorScheme={color || "purple"} fontSize="xs" variant="subtle">
          System
        </Badge>
      )}
    </Flex>
  );

  return (
    <Box
      h="100%"
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
    >
      {/* Logo Header */}
      <Flex 
        p={4} 
        borderBottomWidth="1px" 
        borderColor={borderColor}
        alignItems="center"
        justifyContent="center"
      >
        <Image 
          src="/promethioslogo.png" 
          alt="Promethios Logo" 
          maxW="150px"
          mx="auto"
        />
      </Flex>
      
      {/* Navigation Sections */}
      <VStack 
        align="stretch" 
        p={3} 
        spacing={0}
        overflowY="auto"
        maxH="calc(100vh - 100px)"
        css={{
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            width: '6px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: useColorModeValue('gray.300', 'gray.600'),
            borderRadius: '24px',
          },
        }}
      >
        {/* Agents Section */}
        <NavSection 
          title="Agents" 
          icon={FiUsers} 
          isOpen={openSections.agents}
          onToggle={() => toggleSection('agents')}
        >
          {/* Orchestrator - System Agent */}
          <NavItem 
            text="Orchestrator" 
            icon={FiGrid} 
            color="purple" 
            isSystem={true} 
          />
          <NavItem text="HAL" icon={FiCpu} isActive={true} color="blue" />
          <NavItem text="ASH" icon={FiCpu} color="teal" />
          <NavItem text="NOVA" icon={FiCpu} color="orange" />
          <NavItem text="All Agents" icon={FiUsers} />
        </NavSection>
        
        {/* Goals/Threads Section */}
        <NavSection 
          title="Goals / Threads" 
          icon={FiTarget} 
          isOpen={openSections.goals}
          onToggle={() => toggleSection('goals')}
        >
          <NavItem text="Active Goals" icon={FiTarget} />
          <NavItem text="Completed Goals" icon={FiCheckSquare} />
          <NavItem text="Conversation Threads" icon={FiMessageSquare} />
        </NavSection>
        
        {/* Tools Section */}
        <NavSection 
          title="Tools" 
          icon={FiTool} 
          isOpen={openSections.tools}
          onToggle={() => toggleSection('tools')}
        >
          <NavItem text="Search Tools" />
          <NavItem text="Code Tools" />
          <NavItem text="Content Tools" />
          <NavItem text="Data Tools" />
          <NavItem text="Tool Registry" />
        </NavSection>
        
        {/* Checkpoints Section */}
        <NavSection 
          title="Checkpoints" 
          icon={FiCheckSquare} 
          isOpen={openSections.checkpoints}
          onToggle={() => toggleSection('checkpoints')}
        >
          <NavItem text="Pending Approvals" />
          <NavItem text="Approval History" />
          <NavItem text="Checkpoint Settings" />
        </NavSection>
        
        {/* Archives Section */}
        <NavSection 
          title="Archives" 
          icon={FiArchive} 
          isOpen={openSections.archives}
          onToggle={() => toggleSection('archives')}
        >
          <NavItem text="Memory Archive" />
          <NavItem text="Tool Outputs" />
          <NavItem text="System Logs" />
        </NavSection>
        
        <Divider my={4} />
        
        {/* Bottom Items */}
        <NavItem text="Settings" icon={FiSettings} />
        <NavItem text="Help" icon={FiHelpCircle} />
      </VStack>
    </Box>
  );
};

export default SidebarNavigation;
