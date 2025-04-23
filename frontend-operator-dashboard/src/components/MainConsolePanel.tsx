import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  useColorModeValue,
  Input,
  Button,
  Icon,
  Switch,
  FormControl,
  FormLabel,
  Tooltip
} from '@chakra-ui/react';
import { FiSend, FiRefreshCw, FiCpu } from 'react-icons/fi';
import { ReflectionMessage } from '../schemas/reflectionMessage.schema';

interface MainConsolePanelProps {
  loopId: string;
  projectId: string;
  onSendMessage: (message: string) => void;
  onSendReflection: (reflectionMessage: ReflectionMessage) => void;
  isLoading?: boolean;
}

const MainConsolePanel: React.FC<MainConsolePanelProps> = ({
  loopId,
  projectId,
  onSendMessage,
  onSendReflection,
  isLoading = false
}) => {
  const [message, setMessage] = useState('');
  const [reflectionMode, setReflectionMode] = useState(false);
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    if (reflectionMode) {
      const reflectionMessage: ReflectionMessage = {
        loop_id: loopId,
        project_id: projectId,
        prompt: message,
        initiator: 'operator'
      };
      onSendReflection(reflectionMessage);
    } else {
      onSendMessage(message);
    }
    
    setMessage('');
  };
  
  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      borderColor={borderColor} 
      bg={bgColor} 
      p={4} 
      position="sticky" 
      bottom={0}
      width="100%"
      zIndex={1}
    >
      <form onSubmit={handleSubmit}>
        <VStack spacing={3}>
          <HStack width="100%" justifyContent="space-between">
            <Text fontWeight="bold">Console</Text>
            <HStack>
              <FormControl display="flex" alignItems="center" width="auto">
                <FormLabel htmlFor="reflection-mode" mb="0" fontSize="sm">
                  <Tooltip label="Toggle between normal planning mode and reflection mode">
                    <HStack spacing={1} cursor="help">
                      <Icon as={FiCpu} />
                      <Text>Reflection Mode</Text>
                    </HStack>
                  </Tooltip>
                </FormLabel>
                <Switch 
                  id="reflection-mode" 
                  colorScheme="purple"
                  isChecked={reflectionMode}
                  onChange={() => setReflectionMode(!reflectionMode)}
                />
              </FormControl>
            </HStack>
          </HStack>
          
          <HStack width="100%">
            <Input
              placeholder={reflectionMode ? "Enter prompt for self-reflection..." : "Enter message..."}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              borderColor={borderColor}
              _focus={{ borderColor: reflectionMode ? 'purple.500' : 'blue.500' }}
              _hover={{ borderColor: reflectionMode ? 'purple.400' : 'blue.400' }}
              borderWidth="2px"
              borderRadius="md"
              bg={useColorModeValue('white', 'gray.700')}
              disabled={isLoading}
            />
            <Button
              type="submit"
              colorScheme={reflectionMode ? "purple" : "blue"}
              isLoading={isLoading}
              loadingText="Sending"
              leftIcon={<Icon as={reflectionMode ? FiRefreshCw : FiSend} />}
              disabled={!message.trim() || isLoading}
            >
              {reflectionMode ? "Reflect" : "Send"}
            </Button>
          </HStack>
          
          {reflectionMode && (
            <Box 
              width="100%" 
              p={2} 
              borderRadius="md" 
              bg={useColorModeValue('purple.50', 'purple.900')}
              fontSize="xs"
            >
              <Text fontWeight="medium">Reflection Mode Active</Text>
              <Text>Input will be sent to Promethios' reflective cognition endpoints.</Text>
            </Box>
          )}
        </VStack>
      </form>
    </Box>
  );
};

export default MainConsolePanel;
