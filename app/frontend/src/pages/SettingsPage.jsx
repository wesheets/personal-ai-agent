import React from 'react';
import { 
  Box, 
  Heading, 
  VStack,
  FormControl,
  FormLabel,
  Switch,
  Select,
  Input,
  Button,
  Text,
  Divider,
  useColorModeValue,
  Card,
  CardHeader,
  CardBody
} from '@chakra-ui/react';

const SettingsPage = () => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>Settings</Heading>
      
      <VStack spacing={6} align="stretch" maxW="container.md">
        <Card borderColor={borderColor} shadow="md">
          <CardHeader>
            <Heading size="md">General Settings</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-refresh" mb="0">
                  Auto-refresh Activity Feed
                </FormLabel>
                <Switch id="auto-refresh" defaultChecked />
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="notifications" mb="0">
                  Enable Notifications
                </FormLabel>
                <Switch id="notifications" defaultChecked />
              </FormControl>
              
              <FormControl>
                <FormLabel>Refresh Interval (seconds)</FormLabel>
                <Select defaultValue="5">
                  <option value="3">3 seconds</option>
                  <option value="5">5 seconds</option>
                  <option value="10">10 seconds</option>
                  <option value="30">30 seconds</option>
                </Select>
              </FormControl>
            </VStack>
          </CardBody>
        </Card>
        
        <Card borderColor={borderColor} shadow="md">
          <CardHeader>
            <Heading size="md">API Configuration</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>API Base URL</FormLabel>
                <Input 
                  value="https://personal-ai-agent-backend-production.up.railway.app" 
                  isReadOnly
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  This is configured via environment variables
                </Text>
              </FormControl>
              
              <FormControl>
                <FormLabel>API Key (if needed)</FormLabel>
                <Input type="password" placeholder="Enter API key" />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>
        
        <Card borderColor={borderColor} shadow="md">
          <CardHeader>
            <Heading size="md">Agent Preferences</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Default Agent</FormLabel>
                <Select defaultValue="builder">
                  <option value="builder">Builder Agent</option>
                  <option value="research">Research Agent</option>
                  <option value="memory">Memory Agent</option>
                  <option value="ops">Ops Agent</option>
                </Select>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-delegate" mb="0">
                  Auto-delegate subtasks
                </FormLabel>
                <Switch id="auto-delegate" defaultChecked />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>
        
        <Box textAlign="right">
          <Button colorScheme="blue">Save Settings</Button>
        </Box>
      </VStack>
    </Box>
  );
};

export default SettingsPage;
