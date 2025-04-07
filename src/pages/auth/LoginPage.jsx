import React, { useState } from 'react';
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
  useToast, 
  InputGroup, 
  InputRightElement, 
  IconButton,
  Container,
  Flex,
  Image
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Convert email/password to FormData for OAuth2 compatibility
      const formData = new FormData();
      formData.append('username', email); // OAuth2 uses 'username' field
      formData.append('password', password);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store token in localStorage
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('token_type', data.token_type);

      toast({
        title: 'Login successful',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Redirect to dashboard
      navigate('/');
    } catch (error) {
      toast({
        title: 'Login failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.md" py={10}>
      <Flex direction="column" align="center">
        <Box mb={8} textAlign="center">
          <Image 
            src="/static/promethios-logo.png" 
            alt="Promethios Logo" 
            maxW="200px" 
            mb={4}
            fallbackSrc="https://via.placeholder.com/200x80?text=Promethios"
          />
          <Heading as="h1" size="xl" mb={2}>
            Welcome to Promethios
          </Heading>
          <Text fontSize="lg" color="gray.600">
            Log in to access your AI agents
          </Text>
        </Box>

        <Box 
          p={8} 
          width="100%" 
          maxW="400px" 
          borderWidth={1} 
          borderRadius="lg" 
          boxShadow="lg"
        >
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <FormControl id="email" isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                />
              </FormControl>

              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowPassword(!showPassword)}
                      variant="ghost"
                      size="sm"
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                mt={4}
                isLoading={isLoading}
                loadingText="Logging in"
              >
                Log In
              </Button>
            </VStack>
          </form>

          <Text mt={6} textAlign="center">
            Don't have an account?{' '}
            <Link color="blue.500" href="/register">
              Register
            </Link>
          </Text>
        </Box>
      </Flex>
    </Container>
  );
};

export default LoginPage;
