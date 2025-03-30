import { Box, Flex, Text, VStack, Link, Icon, Divider } from '@chakra-ui/react'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { FaHome, FaTools, FaServer, FaSearch, FaBrain, FaCog } from 'react-icons/fa'

const Sidebar = () => {
  const location = useLocation()
  
  const NavItem = ({ icon, children, to }: { icon: React.ElementType; children: React.ReactNode; to: string }) => {
    const isActive = location.pathname === to
    
    return (
      <Link
        as={RouterLink}
        to={to}
        style={{ textDecoration: 'none' }}
        _focus={{ boxShadow: 'none' }}
      >
        <Flex
          align="center"
          p="4"
          mx="4"
          borderRadius="lg"
          role="group"
          cursor="pointer"
          bg={isActive ? 'brand.500' : 'transparent'}
          color={isActive ? 'white' : 'gray.600'}
          _hover={{
            bg: 'brand.400',
            color: 'white',
          }}
          _dark={{
            color: isActive ? 'white' : 'gray.200',
            _hover: {
              bg: 'brand.600',
            },
          }}
        >
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
          />
          {children}
        </Flex>
      </Link>
    )
  }

  return (
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
      bg="white"
      _dark={{ bg: 'gray.800' }}
      borderRight="1px"
      borderRightColor="gray.200"
      w={{ base: 'full', md: 60 }}
      display={{ base: 'none', md: 'block' }}
      pt="20"
    >
      <VStack spacing={1} align="stretch">
        <NavItem icon={FaHome} to="/">
          Dashboard
        </NavItem>
        
        <Box px="4" py="2" mt="4">
          <Text fontSize="xs" fontWeight="semibold" textTransform="uppercase" color="gray.500" _dark={{ color: 'gray.400' }}>
            Agents
          </Text>
        </Box>
        
        <NavItem icon={FaTools} to="/agent/builder">
          Builder Agent
        </NavItem>
        <NavItem icon={FaServer} to="/agent/ops">
          Ops Agent
        </NavItem>
        <NavItem icon={FaSearch} to="/agent/research">
          Research Agent
        </NavItem>
        <NavItem icon={FaBrain} to="/agent/memory">
          Memory Agent
        </NavItem>
        
        <Divider my="2" />
        
        <Box px="4" py="2">
          <Text fontSize="xs" fontWeight="semibold" textTransform="uppercase" color="gray.500" _dark={{ color: 'gray.400' }}>
            System
          </Text>
        </Box>
        
        <NavItem icon={FaBrain} to="/memory">
          Memory Browser
        </NavItem>
        <NavItem icon={FaCog} to="/settings">
          Settings
        </NavItem>
      </VStack>
    </Box>
  )
}

export default Sidebar
