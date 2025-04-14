import React from 'react';
import { Box, Flex, useColorModeValue } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * LogoutButton component
 * Handles user logout with proper redirect to login page
 */
const LogoutButton = ({ children }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    // Clear token from localStorage
    localStorage.removeItem('token');
    
    // Redirect to login page
    navigate('/login', { replace: true });
  };
  
  return (
    <Box onClick={handleLogout} cursor="pointer">
      {children}
    </Box>
  );
};

export default LogoutButton;
