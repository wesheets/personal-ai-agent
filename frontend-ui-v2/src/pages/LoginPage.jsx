import React, { useState } from 'react';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Text,
  VStack
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  // Create flicker animation using Chakra's keyframes
  const flickerAnimation = keyframes`
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
  `;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (email === 'admin@promethios.ai' && password === 'ignite') {
        await login(email, password);
        navigate('/hal');
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
      console.error('Login error:', err);
    }
  };

  return (
    <Flex direction="column" align="center" justify="center" minH="100vh" bg="black" color="white">
      <Box
        w="300px"
        mb={8}
        animation={`${flickerAnimation} 4s infinite ease-in-out`}
        textAlign="center"
      >
        <img src="/promethioslogo.png" alt="Promethios Logo" style={{ maxWidth: '100%' }} />
      </Box>

      <Box bg="gray.900" p={8} borderRadius="md" boxShadow="lg" w={{ base: '90%', sm: '400px' }}>
        <VStack spacing={6}>
          <Heading size="lg" textAlign="center">
            Login to Promethios
          </Heading>

          {error && (
            <Text color="red.400" textAlign="center">
              {error}
            </Text>
          )}

          <form onSubmit={handleSubmit} style={{ width: '100%' }}>
            <VStack spacing={4} align="flex-start" w="100%">
              <FormControl isRequired>
                <FormLabel color="gray.300">Email</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@promethios.ai"
                  bg="gray.800"
                  border="1px"
                  borderColor="gray.700"
                  _hover={{ borderColor: 'blue.300' }}
                  _focus={{ borderColor: 'blue.500', boxShadow: '0 0 0 1px #3182ce' }}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel color="gray.300">Password</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  bg="gray.800"
                  border="1px"
                  borderColor="gray.700"
                  _hover={{ borderColor: 'blue.300' }}
                  _focus={{ borderColor: 'blue.500', boxShadow: '0 0 0 1px #3182ce' }}
                />
              </FormControl>

              <Button type="submit" colorScheme="blue" size="lg" w="100%" mt={4}>
                Login
              </Button>
            </VStack>
          </form>
        </VStack>
      </Box>

      <Text fontSize="xs" mt={10} opacity={0.2}>
        The fire was stolen for a reason.
      </Text>
    </Flex>
  );
};

export default LoginPage;
