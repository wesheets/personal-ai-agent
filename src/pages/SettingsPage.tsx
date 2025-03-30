import {
  Box,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Button,
  VStack,
  Divider,
  useToast,
  Card,
  CardHeader,
  CardBody,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel
} from '@chakra-ui/react'

const SettingsPage = () => {
  const toast = useToast()
  
  const handleSaveAPISettings = () => {
    // In a real implementation, this would save the API settings
    toast({
      title: 'API Settings saved',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
  }
  
  const handleSaveAgentSettings = () => {
    // In a real implementation, this would save the agent settings
    toast({
      title: 'Agent Settings saved',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
  }
  
  const handleSaveUISettings = () => {
    // In a real implementation, this would save the UI settings
    toast({
      title: 'UI Settings saved',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
  }

  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <Heading as="h1" size="xl" mb={2}>
        Settings
      </Heading>
      <Text fontSize="md" color="gray.600" _dark={{ color: 'gray.400' }} mb={6}>
        Configure your Personal AI Agent System
      </Text>
      
      <Tabs variant="enclosed" colorScheme="brand">
        <TabList>
          <Tab>API Settings</Tab>
          <Tab>Agent Settings</Tab>
          <Tab>UI Settings</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <Card>
              <CardHeader>
                <Heading size="md">API Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <FormControl>
                    <FormLabel>API Base URL</FormLabel>
                    <Input defaultValue="http://localhost:8000" />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>OpenAI API Key</FormLabel>
                    <Input type="password" placeholder="sk-..." />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Claude API Key</FormLabel>
                    <Input type="password" placeholder="sk-..." />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Request Timeout (seconds)</FormLabel>
                    <Input type="number" defaultValue={30} />
                  </FormControl>
                  
                  <Button colorScheme="brand" onClick={handleSaveAPISettings}>
                    Save API Settings
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
          
          <TabPanel>
            <Card>
              <CardHeader>
                <Heading size="md">Agent Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <FormControl>
                    <FormLabel>Default Model</FormLabel>
                    <Select defaultValue="gpt-4">
                      <option value="gpt-4">GPT-4</option>
                      <option value="claude-3">Claude 3</option>
                      <option value="mistral">Mistral</option>
                    </Select>
                  </FormControl>
                  
                  <Divider />
                  
                  <Heading size="sm">Builder Agent Settings</Heading>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Memory</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Auto Orchestrate</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <Divider />
                  
                  <Heading size="sm">Ops Agent Settings</Heading>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Memory</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Auto Orchestrate</FormLabel>
                    <Switch colorScheme="brand" />
                  </FormControl>
                  
                  <Divider />
                  
                  <Heading size="sm">Research Agent Settings</Heading>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Memory</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Auto Orchestrate</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <Divider />
                  
                  <Heading size="sm">Memory Agent Settings</Heading>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Memory</FormLabel>
                    <Switch colorScheme="brand" defaultChecked />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Auto Orchestrate</FormLabel>
                    <Switch colorScheme="brand" />
                  </FormControl>
                  
                  <Button colorScheme="brand" onClick={handleSaveAgentSettings}>
                    Save Agent Settings
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
          
          <TabPanel>
            <Card>
              <CardHeader>
                <Heading size="md">UI Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Dark Mode</FormLabel>
                    <Switch colorScheme="brand" />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Chat Message Display Limit</FormLabel>
                    <Input type="number" defaultValue={50} />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Memory Results Per Page</FormLabel>
                    <Input type="number" defaultValue={10} />
                  </FormControl>
                  
                  <Button colorScheme="brand" onClick={handleSaveUISettings}>
                    Save UI Settings
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}

export default SettingsPage
