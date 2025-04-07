import React from 'react';
import { 
  Box, 
  Flex, 
  useColorMode, 
  useColorModeValue,
  Container,
  Heading,
  Text,
  Image,
  HStack,
  VStack,
  Icon,
  Divider
} from '@chakra-ui/react';
import { FiHome, FiUsers, FiMessageSquare, FiActivity, FiSettings } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import AuthSwitcher from '../auth/AuthSwitcher';
import ColorModeToggle from '../ColorModeToggle';

const AppShell = ({ children }) => {
  const { colorMode } = useColorMode();
  const { user, isAuthenticated } = useAuth();
  
  // Color mode values
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const headerBg = useColorModeValue('white', 'gray.800');
  const sidebarBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box minH="100vh" bg={bgColor}>
      {/* Header */}
      <Flex
        as="header"
        position="fixed"
        w="full"
        zIndex="1000"
        bg={headerBg}
        boxShadow="sm"
        h="16"
        alignItems="center"
        justifyContent="space-between"
        px={4}
        borderBottomWidth="1px"
        borderColor={borderColor}
      >
        <HStack spacing={4}>
          <Image
            src="/static/promethios-logo.png"
            alt="Promethios Logo"
            h="8"
            fallbackSrc="https://via.placeholder.com/120x30?text=Promethios"
          />
          <Heading size="md" display={{ base: 'none', md: 'block' }}>
            Promethios OS
          </Heading>
        </HStack>
        
        <HStack spacing={4}>
          <AuthSwitcher user={user} isAuthenticated={isAuthenticated} />
          <ColorModeToggle />
        </HStack>
      </Flex>
      
      {/* Main content with sidebar */}
      <Flex pt="16" h="calc(100vh - 4rem)">
        {/* Sidebar - only shown when authenticated */}
        {isAuthenticated && (
          <Box
            as="nav"
            position="fixed"
            left={0}
            w="64"
            h="calc(100vh - 4rem)"
            bg={sidebarBg}
            borderRightWidth="1px"
            borderColor={borderColor}
            py={6}
            overflowY="auto"
            display={{ base: 'none', md: 'block' }}
          >
            <VStack spacing={1} align="stretch" px={4}>
              <NavItem icon={FiHome} label="Dashboard" href="/" />
              <NavItem icon={FiUsers} label="Agents" href="/agents" />
              <NavItem icon={FiMessageSquare} label="Chat" href="/chat" />
              <NavItem icon={FiActivity} label="Activity" href="/activity" />
              
              <Divider my={4} />
              
              <Text px={3} fontSize="xs" fontWeight="bold" color="gray.500" mb={2}>
                SYSTEM AGENTS
              </Text>
              <NavItem label="HAL" href="/agent/hal" isAgent />
              <NavItem label="ASH" href="/agent/ash" isAgent />
              
              <Divider my={4} />
              
              <NavItem icon={FiSettings} label="Settings" href="/settings" />
            </VStack>
          </Box>
        )}
        
        {/* Main content area */}
        <Box
          as="main"
          flex={1}
          ml={{ base: 0, md: isAuthenticated ? '64' : 0 }}
          p={4}
          overflowY="auto"
        >
          <Container maxW="container.xl" py={4}>
            {children}
          </Container>
        </Box>
      </Flex>
    </Box>
  );
};

// Navigation item component
const NavItem = ({ icon, label, href, isActive, isAgent = false }) => {
  const activeColor = useColorModeValue('blue.500', 'blue.300');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const color = useColorModeValue('gray.700', 'gray.200');
  
  return (
    <Box
      as="a"
      href={href}
      px={3}
      py={2}
      borderRadius="md"
      color={isActive ? activeColor : color}
      fontWeight={isActive ? 'bold' : 'medium'}
      _hover={{ bg: hoverBg, textDecoration: 'none' }}
      display="flex"
      alignItems="center"
    >
      {icon && <Icon as={icon} mr={3} boxSize={5} />}
      {isAgent && (
        <Box 
          w={5} 
          h={5} 
          borderRadius="full" 
          bg={label === 'HAL' ? 'red.500' : 'purple.500'} 
          mr={3} 
          display="flex" 
          alignItems="center" 
          justifyContent="center"
        >
          <Text fontSize="xs" color="white" fontWeight="bold">
            {label.charAt(0)}
          </Text>
        </Box>
      )}
      {label}
    </Box>
  );
};

export default AppShell;
