import React from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  Text, 
  Icon, 
  Drawer, 
  DrawerOverlay, 
  DrawerContent, 
  DrawerCloseButton, 
  DrawerHeader, 
  DrawerBody,
  useColorMode,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiHome, 
  FiTool, 
  FiServer, 
  FiSearch, 
  FiDatabase, 
  FiFolder, 
  FiSettings,
  FiMenu
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';

// Navigation items configuration
const navItems = [
  { name: 'Dashboard', icon: FiHome, path: '/' },
  { name: 'Builder Agent', icon: FiTool, path: '/builder' },
  { name: 'Ops Agent', icon: FiServer, path: '/ops' },
  { name: 'Research Agent', icon: FiSearch, path: '/research' },
  { name: 'Memory Agent', icon: FiDatabase, path: '/memory' },
  { name: 'Memory Browser', icon: FiFolder, path: '/memory-browser' },
  { name: 'Settings', icon: FiSettings, path: '/settings' },
];

// NavItem component for both desktop and mobile
const NavItem = ({ icon, children, path, isActive, onClick }) => {
  const { colorMode } = useColorMode();
  
  return (
    <Link to={path} style={{ textDecoration: 'none', width: '100%' }} onClick={onClick}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? (colorMode === 'light' ? 'brand.100' : 'brand.900') : 'transparent'}
        color={isActive ? (colorMode === 'light' ? 'brand.800' : 'brand.200') : (colorMode === 'light' ? 'gray.600' : 'gray.300')}
        _hover={{
          bg: colorMode === 'light' ? 'brand.50' : 'brand.800',
          color: colorMode === 'light' ? 'brand.800' : 'brand.200',
        }}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
          />
        )}
        {children}
      </Flex>
    </Link>
  );
};

// Sidebar component with responsive design
const Sidebar = ({ isOpen, onClose }) => {
  const { colorMode } = useColorMode();
  const location = useLocation();
  const { isOpen: isMobileOpen, onOpen: onMobileOpen, onClose: onMobileClose } = useDisclosure();
  
  // Desktop sidebar
  const DesktopSidebar = (
    <Box
      as="nav"
      pos="fixed"
      top="0"
      left="0"
      zIndex="sticky"
      h="full"
      pb="10"
      overflowX="hidden"
      overflowY="auto"
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
      borderRight="1px"
      borderRightColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
      w="60"
      display={{ base: 'none', md: 'block' }}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold" color={colorMode === 'light' ? 'brand.500' : 'brand.300'}>
          Manus
        </Text>
      </Flex>
      <VStack spacing={0} align="stretch">
        {navItems.map((item) => (
          <NavItem 
            key={item.name} 
            icon={item.icon} 
            path={item.path}
            isActive={location.pathname === item.path}
          >
            {item.name}
          </NavItem>
        ))}
      </VStack>
    </Box>
  );

  // Mobile sidebar (Drawer)
  const MobileSidebar = (
    <>
      <Flex
        ml={{ base: 0, md: 60 }}
        px={{ base: 4, md: 4 }}
        height="20"
        alignItems="center"
        bg={colorMode === 'light' ? 'white' : 'gray.900'}
        borderBottomWidth="1px"
        borderBottomColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
        justifyContent={{ base: 'space-between', md: 'flex-end' }}
        display={{ base: 'flex', md: 'none' }}
      >
        <Icon
          as={FiMenu}
          display={{ base: 'flex', md: 'none' }}
          onClick={onMobileOpen}
          cursor="pointer"
          boxSize={6}
        />
        <Text fontSize="2xl" fontWeight="bold" color={colorMode === 'light' ? 'brand.500' : 'brand.300'}>
          Manus
        </Text>
      </Flex>

      <Drawer
        isOpen={isMobileOpen}
        placement="left"
        onClose={onMobileClose}
        returnFocusOnClose={false}
        onOverlayClick={onMobileClose}
      >
        <DrawerOverlay />
        <DrawerContent bg={colorMode === 'light' ? 'white' : 'gray.800'}>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            Manus
          </DrawerHeader>
          <DrawerBody p={0}>
            <VStack spacing={0} align="stretch">
              {navItems.map((item) => (
                <NavItem 
                  key={item.name} 
                  icon={item.icon} 
                  path={item.path}
                  isActive={location.pathname === item.path}
                  onClick={onMobileClose}
                >
                  {item.name}
                </NavItem>
              ))}
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );

  return (
    <>
      {DesktopSidebar}
      {MobileSidebar}
    </>
  );
};

export default Sidebar;
