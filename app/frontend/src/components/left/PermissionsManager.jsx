import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  Icon, 
  VStack,
  HStack,
  Badge,
  Switch,
  FormControl,
  FormLabel,
  useColorModeValue,
  Spinner,
  Tooltip,
  useToast
} from '@chakra-ui/react';
import { FaLock, FaUserShield, FaUserCog, FaUsers, FaExclamationTriangle, FaSync } from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * PermissionsManager Component
 * 
 * Manages system permissions for the current project context.
 * Connected to /api/system/permissions endpoint for permission data and control.
 */
const PermissionsManager = () => {
  const [permissionsExpanded, setPermissionsExpanded] = useState(false);
  const [updatingPermission, setUpdatingPermission] = useState(null);
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const toast = useToast();
  
  // Fetch permissions from API
  const { 
    data: permissionsData, 
    error, 
    loading, 
    refetch 
  } = useFetch('/api/system/permissions', {}, {
    refreshInterval: 30000, // Refresh every 30 seconds
    initialData: {
      permissions: [
        { id: 'memory_write', name: 'Memory Write', enabled: true, critical: true },
        { id: 'agent_execution', name: 'Agent Execution', enabled: true, critical: true },
        { id: 'belief_modification', name: 'Belief Modification', enabled: false, critical: true },
        { id: 'system_rebuild', name: 'System Rebuild', enabled: false, critical: true },
        { id: 'external_api', name: 'External API Access', enabled: true, critical: false },
        { id: 'file_system', name: 'File System Access', enabled: true, critical: false }
      ],
      projectId: 'promethios-core',
      lastUpdated: new Date().toISOString()
    },
    transformResponse: (data) => ({
      permissions: Array.isArray(data.permissions) ? data.permissions : [],
      projectId: data.projectId || 'unknown',
      lastUpdated: data.lastUpdated || new Date().toISOString()
    })
  });
  
  const togglePermission = async (id) => {
    if (!permissionsData || !permissionsData.permissions) return;
    
    const permission = permissionsData.permissions.find(p => p.id === id);
    if (!permission) return;
    
    setUpdatingPermission(id);
    
    try {
      // Call API to update permission
      const response = await fetch('/api/system/permissions/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          permissionId: id, 
          enabled: !permission.enabled,
          projectId: permissionsData.projectId
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update permission: ${response.status}`);
      }
      
      toast({
        title: "Permission updated",
        description: `${permission.name} is now ${!permission.enabled ? 'enabled' : 'disabled'}`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      // Refresh data after permission change
      refetch();
    } catch (err) {
      console.error(`Error updating permission ${id}:`, err);
      
      toast({
        title: "Failed to update permission",
        description: err.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setUpdatingPermission(null);
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Unknown';
    }
  };
  
  return (
    <Box 
      p={4} 
      borderRadius="md" 
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
      position="relative"
    >
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px">
          <Spinner size="sm" color="purple.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px">
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Flex justifyContent="space-between" alignItems="center" mb={3}>
        <HStack>
          <Icon as={FaUserShield} color="purple.500" />
          <Heading size="sm">Permissions</Heading>
        </HStack>
        <Button 
          size="xs" 
          onClick={() => setPermissionsExpanded(!permissionsExpanded)}
          isDisabled={loading || !permissionsData || !permissionsData.permissions}
        >
          {permissionsExpanded ? 'Collapse' : 'Expand'}
        </Button>
      </Flex>
      
      {!permissionsExpanded ? (
        <HStack spacing={2} wrap="wrap">
          {permissionsData && permissionsData.permissions
            .filter(p => p.critical)
            .map(permission => (
              <Badge 
                key={permission.id}
                colorScheme={permission.enabled ? 'green' : 'red'}
                variant="subtle"
                px={2}
                py={1}
                borderRadius="full"
              >
                {permission.name}
              </Badge>
            ))}
        </HStack>
      ) : (
        <VStack align="stretch" spacing={2}>
          {permissionsData && permissionsData.permissions.map(permission => (
            <FormControl 
              key={permission.id} 
              display="flex" 
              alignItems="center" 
              justifyContent="space-between"
              size="sm"
            >
              <FormLabel htmlFor={permission.id} mb={0} fontSize="sm">
                <HStack>
                  <Text>{permission.name}</Text>
                  {permission.critical && (
                    <Badge colorScheme="purple" fontSize="2xs">Critical</Badge>
                  )}
                </HStack>
              </FormLabel>
              <Switch 
                id={permission.id} 
                isChecked={permission.enabled}
                onChange={() => togglePermission(permission.id)}
                colorScheme="green"
                isDisabled={updatingPermission === permission.id}
              />
              {updatingPermission === permission.id && (
                <Spinner size="xs" ml={2} />
              )}
            </FormControl>
          ))}
          
          <Button 
            size="xs" 
            leftIcon={<Icon as={FaUserCog} />} 
            mt={2} 
            colorScheme="purple" 
            variant="outline"
          >
            Advanced Settings
          </Button>
        </VStack>
      )}
      
      <Flex justifyContent="space-between" alignItems="center" mt={2}>
        <Text fontSize="xs" color={textColor}>
          Permissions apply to current project context
        </Text>
        
        {permissionsData && permissionsData.lastUpdated && (
          <Tooltip label={formatTimestamp(permissionsData.lastUpdated)}>
            <Button 
              size="xs" 
              variant="ghost" 
              onClick={() => refetch()} 
              leftIcon={<Icon as={FaSync} />}
              isDisabled={loading}
            >
              Refresh
            </Button>
          </Tooltip>
        )}
      </Flex>
    </Box>
  );
};

export default PermissionsManager;
