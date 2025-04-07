import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  Link,
  useColorModeValue,
  FormErrorMessage,
  Container,
  Alert,
  AlertIcon,
  AlertDescription,
  Spinner,
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * LoginPage - Public login page that is always accessible
 * This component handles user authentication and redirects to the dashboard on success
 * Enhanced with failsafe protection to prevent lockout
 */
const LoginPage = ({ isRegister = false }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [nameError, setNameError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, isAuthenticated, loading } = useAuth();

  const bgColor = useColorModeValue('white', 'gray.800');
  const boxBgColor = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Check for redirect path on component mount
  useEffect(() => {
    // If user is already authenticated, redirect to dashboard or saved redirect path
    if (isAuthenticated && !loading) {
      const redirectPath = sessionStorage.getItem('redirectAfterLogin') || '/dashboard';
      navigate(redirectPath, { replace: true });
      // Clear the stored redirect path
      sessionStorage.removeItem('redirectAfterLogin');
    }
  }, [isAuthenticated, loading, navigate]);

  const validateForm = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');
    setNameError('');

    if (!email) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Email is invalid');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    }

    if (isRegister && !name) {
      setNameError('Name is required');
      isValid = false;
    }

    return isValid;
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      if (isRegister) {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
      
      // Note: Navigation is handled in the auth context after successful login/register
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading spinner while auth state is being determined
  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minH="100vh"
        bg={bgColor}
      >
        <Spinner size="xl" color="blue.500" />
      </Box>
    );
  }

  return (
    <Box minH="100vh" bg={bgColor} color={textColor} py={10}>
      <Container maxW="lg">
        <VStack spacing={8} align="center">
          <Box 
            alignItems="center" 
            justifyContent="center"
            bg="blue.500"
            color="white"
            borderRadius="md"
            boxSize="60px"
            fontSize="2xl"
            fontWeight="bold"
            display="flex"
          >
            P
          </Box>
          
          <Heading as="h1" size="xl">Promethios UI v2</Heading>
          
          <Box 
            w="full" 
            bg={boxBgColor} 
            p={8} 
            borderRadius="lg" 
            boxShadow="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <VStack spacing={6} align="stretch">
              <Heading as="h2" size="lg" textAlign="center">
                {isRegister ? 'Register' : 'Login'}
              </Heading>
              
              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <form onSubmit={handleAuth}>
                <VStack spacing={4}>
                  {isRegister && (
                    <FormControl isInvalid={!!nameError}>
                      <FormLabel>Name</FormLabel>
                      <Input 
                        type="text" 
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your Name"
                      />
                      <FormErrorMessage>{nameError}</FormErrorMessage>
                    </FormControl>
                  )}
                  
                  <FormControl isInvalid={!!emailError}>
                    <FormLabel>Email</FormLabel>
                    <Input 
                      type="email" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your.email@example.com"
                    />
                    <FormErrorMessage>{emailError}</FormErrorMessage>
                  </FormControl>
                  
                  <FormControl isInvalid={!!passwordError}>
                    <FormLabel>Password</FormLabel>
                    <Input 
                      type="password" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="******"
                    />
                    <FormErrorMessage>{passwordError}</FormErrorMessage>
                  </FormControl>
                  
                  <Button 
                    type="submit" 
                    colorScheme="blue" 
                    size="lg" 
                    width="full"
                    isLoading={isLoading}
                    loadingText={isRegister ? "Registering" : "Logging in"}
                  >
                    {isRegister ? 'Register' : 'Login'}
                  </Button>
                </VStack>
              </form>
              
              <Text textAlign="center">
                {isRegister ? 'Already have an account?' : 'Don\'t have an account?'}{' '}
                <Link as={RouterLink} to={isRegister ? '/login' : '/register'} color="blue.500">
                  {isRegister ? 'Login' : 'Register'}
                </Link>
              </Text>
            </VStack>
          </Box>
          
          <Text fontSize="sm" color="gray.500">
            Promethios UI v2 &copy; {new Date().getFullYear()} | All rights reserved
          </Text>
        </VStack>
      </Container>
    </Box>
  );
};

export default LoginPage;
