import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Flex,
  Image,
  Text,
  Input,
  Button,
  FormControl,
  FormLabel,
  VStack,
  Heading,
  useColorModeValue,
  FormErrorMessage,
  useToast
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const pulse = keyframes`
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
`;

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  // Animation states
  const [showSlogan, setShowSlogan] = useState(false);
  
  useEffect(() => {
    // Show slogan with delay for animation effect
    const timer = setTimeout(() => {
      setShowSlogan(true);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    // Check for easter egg
    if (username.toLowerCase() === 'i am promethios' && password === '') {
      // Special easter egg message
      localStorage.setItem('specialAccess', 'true');
      localStorage.setItem('authToken', 'architect-special-access');
      
      toast({
        title: "Special Access Granted",
        description: "Welcome, Architect.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
      return;
    }
    
    // Check against environment variables
    const validUsername = import.meta.env.VITE_OPERATOR_USERNAME || 'admin';
    const validPassword = import.meta.env.VITE_OPERATOR_PASSWORD || 'securekey';
    
    setTimeout(() => {
      if (username === validUsername && password === validPassword) {
        // Store session in localStorage
        localStorage.setItem('authToken', 'operator-authenticated');
        localStorage.setItem('username', username);
        
        toast({
          title: "Access Granted",
          description: "Welcome to Promethios Operator Dashboard.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        
        // Route to dashboard
        navigate('/dashboard');
      } else {
        setError('Access Denied: Invalid operator credentials');
        setIsLoading(false);
      }
    }, 800); // Simulate authentication delay
  };

  // Colors
  const bgColor = "black";
  const cardBgColor = "gray.900";
  const borderColor = "gray.700";
  const inputBgColor = "gray.800";
  const buttonBgColor = "blue.600";
  const buttonHoverColor = "blue.500";
  const textColor = "white";
  const labelColor = "gray.300";
  const errorColor = "red.500";
  const sloganColor = "gray.400";
  const footerColor = "whiteAlpha.300";

  return (
    <Box 
      bg={bgColor} 
      minH="100vh" 
      color={textColor}
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      px={4}
    >
      {/* Logo with animation */}
      <Box 
        mb={8} 
        animation={`${fadeIn} 1s ease-in`}
        maxW="300px"
        w="full"
      >
        <Image 
          src="/promethioslogo.png" 
          alt="Promethios Logo" 
          mx="auto"
          w="full"
        />
      </Box>
      
      {/* Title and slogan with animation */}
      <VStack mb={8} spacing={2} textAlign="center">
        <Heading 
          size="xl" 
          fontWeight="bold"
          animation={`${fadeIn} 1.2s ease-in`}
        >
          Promethios Operator Dashboard
        </Heading>
        
        <Text 
          color={sloganColor} 
          fontSize="md"
          opacity={showSlogan ? 1 : 0}
          animation={showSlogan ? `${pulse} 4s infinite` : undefined}
          transition="opacity 0.5s"
        >
          The fire has been lit. Operator input required.
        </Text>
      </VStack>
      
      {/* Login form with animation */}
      <Box 
        bg={cardBgColor}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        p={8}
        maxW="400px"
        w="full"
        animation={`${fadeIn} 1.5s ease-in`}
        boxShadow="0 4px 12px rgba(0, 0, 0, 0.5)"
      >
        <form onSubmit={handleSubmit}>
          <VStack spacing={4}>
            <Heading size="md" textAlign="center" mb={2}>
              Operator Authentication
            </Heading>
            
            {error && (
              <Text color={errorColor} fontSize="sm" textAlign="center">
                {error}
              </Text>
            )}
            
            <FormControl isRequired>
              <FormLabel color={labelColor}>Username</FormLabel>
              <Input
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                bg={inputBgColor}
                borderColor={borderColor}
                _hover={{ borderColor: 'gray.600' }}
                _focus={{ borderColor: 'blue.400', boxShadow: '0 0 0 1px blue.400' }}
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel color={labelColor}>Password</FormLabel>
              <Input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                bg={inputBgColor}
                borderColor={borderColor}
                _hover={{ borderColor: 'gray.600' }}
                _focus={{ borderColor: 'blue.400', boxShadow: '0 0 0 1px blue.400' }}
              />
            </FormControl>
            
            <Button
              type="submit"
              colorScheme="blue"
              bg={buttonBgColor}
              _hover={{ bg: buttonHoverColor }}
              size="lg"
              width="full"
              mt={4}
              isLoading={isLoading}
              loadingText="Authenticating"
            >
              Access System
            </Button>
          </VStack>
        </form>
      </Box>
      
      {/* Footer text with animation */}
      <Text 
        fontSize="xs" 
        color={footerColor} 
        mt={12}
        animation={`${fadeIn} 2s ease-in`}
      >
        The fire was stolen for a reason.
      </Text>
    </Box>
  );
};

export default LoginPage;
