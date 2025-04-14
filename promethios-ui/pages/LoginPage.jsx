import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  GridItem,
  Flex,
  Input,
  Button,
  Text,
  Heading,
  useToast,
  Image,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  InputGroup,
  InputRightElement,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { keyframes } from '@emotion/react';

// Animation keyframes
const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  // Animation style
  const animation = `${fadeIn} 1s ease-in`;

  // Check if already authenticated
  useEffect(() => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        navigate('/dashboard');
      }
    } catch (error) {
      console.log('Session validation error:', error);
    }
  }, [navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Easter egg check
      if (username.toUpperCase() === 'I AM PROMETHIOS') {
        // Flash system override effect
        document.body.style.backgroundColor = '#ff6700';
        setTimeout(() => {
          document.body.style.backgroundColor = '#000';
          // Set mock token and redirect
          try {
            localStorage.setItem('token', 'system-override-token');
            navigate('/dashboard');
          } catch (error) {
            console.log('Error setting override token:', error);
            setError('System override failed');
          }
        }, 500);
        return;
      }

      // Get environment variables with fallbacks
      const envUsername = import.meta.env.VITE_OPERATOR_USERNAME || '';
      const envPassword = import.meta.env.VITE_OPERATOR_PASSWORD || '';

      // Log to console if environment variables are missing
      if (!envUsername || !envPassword) {
        console.log('Warning: Missing environment variables for authentication');
      }

      if (username === envUsername && password === envPassword) {
        try {
          // Set token in localStorage with error handling
          localStorage.setItem('token', JSON.stringify({
            user: username,
            timestamp: Date.now()
          }));
          
          // Create default empty session if it doesn't exist
          try {
            const session = localStorage.getItem('session');
            if (!session) {
              localStorage.setItem('session', JSON.stringify({}));
              console.log('Created default empty session in localStorage');
            }
          } catch (error) {
            console.log('Error ensuring session exists:', error);
          }
          
          // Redirect to dashboard
          navigate('/dashboard');
        } catch (error) {
          console.log('Login error:', error);
          setError('Authentication error occurred');
        }
      } else {
        setError('Access Denied');
      }
    } catch (error) {
      console.log('Login process error:', error);
      setError('Authentication process failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box 
      bg="black" 
      minH="100vh" 
      w="100%" 
      sx={{ animation: animation }}
    >
      <Grid 
        templateColumns={{ base: "1fr", md: "1fr 1fr" }} 
        h="100vh"
      >
        {/* Left Panel - Logo and Slogan */}
        <GridItem>
          <Flex 
            direction="column" 
            justify="center" 
            align="center" 
            h="100%" 
            p={8}
          >
            <Box maxW="400px" mb={8}>
              <Image 
                src="/promethioslogo.png" 
                alt="PROMETHIOS" 
                w="100%" 
              />
            </Box>
            <Text 
              color="whiteAlpha.800" 
              fontSize={{ base: "lg", md: "xl" }} 
              textAlign="center"
              fontWeight="light"
              letterSpacing="wider"
            >
              The fire has been lit. Operator input required.
            </Text>
          </Flex>
        </GridItem>

        {/* Right Panel - Login Form */}
        <GridItem>
          <Flex 
            direction="column" 
            justify="center" 
            align="center" 
            h="100%" 
            p={8}
          >
            <Box 
              bg="gray.800" 
              p={8} 
              borderRadius="lg" 
              boxShadow="xl" 
              w={{ base: "90%", md: "70%" }}
              maxW="400px"
            >
              <VStack spacing={6}>
                <Heading size="lg" color="white" mb={2}>
                  Operator Login
                </Heading>
                
                {error && (
                  <Text color="red.400" textAlign="center">
                    {error}
                  </Text>
                )}
                
                <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                  <VStack spacing={4} align="flex-start" w="100%">
                    <FormControl isRequired>
                      <FormLabel color="whiteAlpha.900">Username</FormLabel>
                      <Input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter username"
                        bg="whiteAlpha.100"
                        color="white"
                        borderColor="whiteAlpha.300"
                        _hover={{ borderColor: "whiteAlpha.400" }}
                        _focus={{ borderColor: "blue.300", boxShadow: "0 0 0 1px #63B3ED" }}
                      />
                    </FormControl>
                    
                    <FormControl isRequired>
                      <FormLabel color="whiteAlpha.900">Password</FormLabel>
                      <InputGroup>
                        <Input
                          type={showPassword ? "text" : "password"}
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter password"
                          bg="whiteAlpha.100"
                          color="white"
                          borderColor="whiteAlpha.300"
                          _hover={{ borderColor: "whiteAlpha.400" }}
                          _focus={{ borderColor: "blue.300", boxShadow: "0 0 0 1px #63B3ED" }}
                        />
                        <InputRightElement>
                          <IconButton
                            aria-label={showPassword ? "Hide password" : "Show password"}
                            icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                            onClick={() => setShowPassword(!showPassword)}
                            variant="ghost"
                            colorScheme="whiteAlpha"
                            size="sm"
                          />
                        </InputRightElement>
                      </InputGroup>
                    </FormControl>
                    
                    <Button
                      type="submit"
                      colorScheme="blue"
                      w="100%"
                      mt={4}
                      isLoading={isLoading}
                      loadingText="Authenticating"
                    >
                      Access System
                    </Button>
                  </VStack>
                </form>
              </VStack>
            </Box>
          </Flex>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default LoginPage;
