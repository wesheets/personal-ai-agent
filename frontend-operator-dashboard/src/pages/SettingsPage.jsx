import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  Card,
  CardBody,
  SimpleGrid,
  Icon,
  Flex,
  Switch,
  FormControl,
  FormLabel,
  Divider,
  Button,
  useColorMode,
  Badge,
  useToast,
  HStack,
  Tooltip
} from '@chakra-ui/react';
import {
  FiSettings,
  FiUser,
  FiGlobe,
  FiShield,
  FiBell,
  FiInfo,
  FiRefreshCw,
  FiAlertTriangle,
  FiCode,
  FiSave,
  FiRotateCcw
} from 'react-icons/fi';
import { useSettings } from '../context/SettingsContext';

const SettingsPage = () => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const { settings, updateSetting, resetSettings } = useSettings();

  // Local state for settings (to prevent immediate application of some settings)
  const [localSettings, setLocalSettings] = useState(settings);

  // Update local settings when global settings change
  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  // Handle setting change
  const handleSettingChange = (key, value) => {
    setLocalSettings((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  // Apply settings
  const applySettings = () => {
    // Apply each setting
    Object.entries(localSettings).forEach(([key, value]) => {
      updateSetting(key, value);
    });

    // Show success toast
    toast({
      title: 'Settings saved',
      description: 'Your settings have been applied and saved.',
      status: 'success',
      duration: 3000,
      isClosable: true
    });
  };

  // Reset settings
  const handleResetSettings = () => {
    resetSettings();

    // Show success toast
    toast({
      title: 'Settings reset',
      description: 'Your settings have been reset to defaults.',
      status: 'info',
      duration: 3000,
      isClosable: true
    });
  };

  return (
    <Box p={4}>
      <Heading mb={6} size="lg">
        Settings
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        {/* System Settings */}
        <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} boxShadow="md" borderRadius="lg">
          <CardBody>
            <Flex align="center" mb={4}>
              <Icon
                as={FiSettings}
                mr={2}
                boxSize={5}
                color={colorMode === 'light' ? 'blue.500' : 'blue.300'}
              />
              <Heading size="md">System Settings</Heading>
            </Flex>
            <Divider mb={4} />
            <VStack spacing={4} align="stretch">
              {/* Debug Mode Toggle */}
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <FormLabel htmlFor="debug-mode" mb="0">
                    <HStack spacing={2}>
                      <Icon as={FiCode} />
                      <Text>Debug Mode</Text>
                    </HStack>
                  </FormLabel>
                  <Text fontSize="xs" color="gray.500">
                    Enable detailed logging and debug information
                  </Text>
                </Box>
                <Tooltip label="Changes will apply after page refresh">
                  <Switch
                    id="debug-mode"
                    isChecked={localSettings.debugMode}
                    onChange={(e) => handleSettingChange('debugMode', e.target.checked)}
                    colorScheme="blue"
                  />
                </Tooltip>
              </FormControl>

              {/* Auto-refresh Panels Toggle */}
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <FormLabel htmlFor="auto-refresh" mb="0">
                    <HStack spacing={2}>
                      <Icon as={FiRefreshCw} />
                      <Text>Auto-refresh Panels</Text>
                    </HStack>
                  </FormLabel>
                  <Text fontSize="xs" color="gray.500">
                    Automatically refresh data panels
                  </Text>
                </Box>
                <Switch
                  id="auto-refresh"
                  isChecked={localSettings.autoRefreshPanels}
                  onChange={(e) => handleSettingChange('autoRefreshPanels', e.target.checked)}
                  colorScheme="green"
                />
              </FormControl>

              {/* Show Fallback Alerts Toggle */}
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <FormLabel htmlFor="fallback-alerts" mb="0">
                    <HStack spacing={2}>
                      <Icon as={FiAlertTriangle} />
                      <Text>Show Fallback Alerts</Text>
                    </HStack>
                  </FormLabel>
                  <Text fontSize="xs" color="gray.500">
                    Display alerts when memory fallback is active
                  </Text>
                </Box>
                <Switch
                  id="fallback-alerts"
                  isChecked={localSettings.showFallbackAlerts}
                  onChange={(e) => handleSettingChange('showFallbackAlerts', e.target.checked)}
                  colorScheme="yellow"
                />
              </FormControl>

              {/* Save Button */}
              <HStack spacing={2} justify="flex-end" mt={2}>
                <Button
                  leftIcon={<FiRotateCcw />}
                  variant="outline"
                  size="sm"
                  onClick={handleResetSettings}
                >
                  Reset to Defaults
                </Button>
                <Button leftIcon={<FiSave />} colorScheme="blue" size="sm" onClick={applySettings}>
                  Save Settings
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Account Settings */}
        <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} boxShadow="md" borderRadius="lg">
          <CardBody>
            <Flex align="center" mb={4}>
              <Icon
                as={FiUser}
                mr={2}
                boxSize={5}
                color={colorMode === 'light' ? 'blue.500' : 'blue.300'}
              />
              <Heading size="md">Account Settings</Heading>
            </Flex>
            <Divider mb={4} />
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.500">
                Account settings will allow you to manage your profile, authentication, and
                preferences.
              </Text>
              <Badge colorScheme="blue" alignSelf="flex-start">
                Coming Soon
              </Badge>
            </VStack>
          </CardBody>
        </Card>

        {/* API Configuration */}
        <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} boxShadow="md" borderRadius="lg">
          <CardBody>
            <Flex align="center" mb={4}>
              <Icon
                as={FiGlobe}
                mr={2}
                boxSize={5}
                color={colorMode === 'light' ? 'green.500' : 'green.300'}
              />
              <Heading size="md">API Configuration</Heading>
            </Flex>
            <Divider mb={4} />
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.500">
                API configuration will allow you to set up and manage API endpoints and credentials.
              </Text>
              <Badge colorScheme="blue" alignSelf="flex-start">
                Coming Soon
              </Badge>
            </VStack>
          </CardBody>
        </Card>

        {/* Privacy & Security */}
        <Card bg={colorMode === 'light' ? 'white' : 'gray.700'} boxShadow="md" borderRadius="lg">
          <CardBody>
            <Flex align="center" mb={4}>
              <Icon
                as={FiShield}
                mr={2}
                boxSize={5}
                color={colorMode === 'light' ? 'purple.500' : 'purple.300'}
              />
              <Heading size="md">Privacy & Security</Heading>
            </Flex>
            <Divider mb={4} />
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.500">
                Privacy and security settings will allow you to manage data protection and access
                controls.
              </Text>
              <Badge colorScheme="blue" alignSelf="flex-start">
                Coming Soon
              </Badge>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* About Section */}
      <Card
        mt={8}
        bg={colorMode === 'light' ? 'white' : 'gray.700'}
        boxShadow="md"
        borderRadius="lg"
      >
        <CardBody>
          <Flex align="center" mb={4}>
            <Icon
              as={FiInfo}
              mr={2}
              boxSize={5}
              color={colorMode === 'light' ? 'gray.500' : 'gray.300'}
            />
            <Heading size="md">About</Heading>
          </Flex>
          <Divider mb={4} />
          <VStack spacing={4} align="stretch">
            <Text>Promethios OS - Personal AI Agent System</Text>
            <Text fontSize="sm" color="gray.500">
              Version 1.0.0
            </Text>
            <Text fontSize="sm" color="gray.500">
              © 2025 Promethios AI
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
};

export default SettingsPage;
