// src/pages/LoginPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Button, Flex, Heading, Input, Text, VStack, useToast } from '@chakra-ui/react'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const toast = useToast()

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const operatorUsername = import.meta.env.VITE_OPERATOR_USERNAME || 'admin'
    const operatorPassword = import.meta.env.VITE_OPERATOR_PASSWORD || 'password'
    
    if (username === operatorUsername && password === operatorPassword) {
      // Set auth in localStorage or context
      localStorage.setItem('isAuthenticated', 'true')
      
      // Show success toast
      toast({
        title: 'Login successful',
        description: 'Welcome, Operator.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      
      // Redirect to dashboard
      navigate('/dashboard')
    } else {
      setError('Invalid operator credentials')
    }
  }

  return (
    <Flex 
      direction="column" 
      align="center" 
      justify="center" 
      minH="100vh" 
      bg="black" 
      color="white"
      p={4}
    >
      <Box 
        w={["90%", "80%", "60%", "450px"]} 
        p={8} 
        borderRadius="md" 
        bg="gray.900" 
        boxShadow="lg"
      >
        <VStack spacing={6}>
          <Heading size="lg" textAlign="center">Promethios Operator Interface</Heading>
          
          <Text fontSize="md" color="orange.400" textAlign="center" fontStyle="italic">
            The fire has been lit. Operator input required.
          </Text>
          
          {error && <Text color="red.400" fontSize="sm">{error}</Text>}
          
          <form onSubmit={handleSubmit} style={{ width: '100%' }}>
            <VStack spacing={4} w="100%">
              <Input
                placeholder="Operator ID"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                bg="gray.800"
                border="none"
                _focus={{ borderColor: "orange.400" }}
              />
              
              <Input
                type="password"
                placeholder="Access Code"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                bg="gray.800"
                border="none"
                _focus={{ borderColor: "orange.400" }}
              />
              
              <Button 
                type="submit" 
                w="100%" 
                colorScheme="orange" 
                variant="solid"
                _hover={{ bg: "orange.500" }}
              >
                Authenticate
              </Button>
            </VStack>
          </form>
        </VStack>
      </Box>
      
      <Text fontSize="xs" mt={10} opacity={0.3}>
        Promethios Orchestration System v10.0
      </Text>
    </Flex>
  )
}
