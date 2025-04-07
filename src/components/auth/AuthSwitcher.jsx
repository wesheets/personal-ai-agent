import React from 'react';
import { 
  Menu, 
  MenuButton, 
  MenuList, 
  MenuItem, 
  Button, 
  Avatar, 
  Text, 
  HStack, 
  Box, 
  useToast,
  useColorModeValue
} from '@chakra-ui/react';
import { ChevronDownIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';

const AuthSwitcher = ({ user, isAuthenticated }) => {
  const toast = useToast();
  const navigate = useNavigate();
  const menuBg = useColorModeValue('white', 'gray.800');
  const menuBorder = useColorModeValue('gray.200', 'gray.700');

  const handleLogout = async () => {
    try {
      // Call logout endpoint
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      // Clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('token_type');

      toast({
        title: 'Logged out successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Redirect to login page
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      
      // Even if the API call fails, clear local storage and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('token_type');
      navigate('/login');
    }
  };

  // If not authenticated, show login/register buttons
  if (!isAuthenticated) {
    return (
      <HStack spacing={2}>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => navigate('/login')}
        >
          Log In
        </Button>
        <Button 
          colorScheme="blue" 
          size="sm" 
          onClick={() => navigate('/register')}
        >
          Register
        </Button>
      </HStack>
    );
  }

  // If authenticated, show user menu with logout option
  return (
    <Menu>
      <MenuButton 
        as={Button} 
        rightIcon={<ChevronDownIcon />} 
        variant="ghost" 
        _hover={{ bg: 'gray.100' }}
      >
        <HStack>
          <Avatar 
            size="sm" 
            name={user?.email || 'User'} 
            src={user?.avatar} 
            bg="blue.500"
          />
          <Box display={{ base: 'none', md: 'block' }}>
            <Text fontSize="sm" fontWeight="medium">
              {user?.email || 'User'}
            </Text>
          </Box>
        </HStack>
      </MenuButton>
      <MenuList bg={menuBg} borderColor={menuBorder}>
        <MenuItem onClick={() => navigate('/profile')}>Profile</MenuItem>
        <MenuItem onClick={() => navigate('/settings')}>Settings</MenuItem>
        <MenuItem onClick={handleLogout} color="red.500">Logout</MenuItem>
      </MenuList>
    </Menu>
  );
};

export default AuthSwitcher;
