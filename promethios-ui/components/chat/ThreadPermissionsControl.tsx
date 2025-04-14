import React from 'react';
import { 
  Box, 
  Switch, 
  FormControl, 
  FormLabel, 
  VStack, 
  Text, 
  useColorModeValue,
  HStack,
  Badge
} from '@chakra-ui/react';
import { ThreadPermissions } from '../../models/Message';

interface ThreadPermissionsControlProps {
  threadId: string;
  permissions: ThreadPermissions;
  onUpdatePermissions: (threadId: string, permissions: ThreadPermissions) => void;
}

const ThreadPermissionsControl: React.FC<ThreadPermissionsControlProps> = ({
  threadId,
  permissions,
  onUpdatePermissions
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleToggleExecute = () => {
    const updatedPermissions = {
      ...permissions,
      can_execute: !permissions.can_execute
    };
    onUpdatePermissions(threadId, updatedPermissions);
  };
  
  const handleToggleReflect = () => {
    const updatedPermissions = {
      ...permissions,
      can_reflect: !permissions.can_reflect
    };
    onUpdatePermissions(threadId, updatedPermissions);
  };
  
  return (
    <Box
      p={3}
      borderWidth="1px"
      borderRadius="md"
      borderColor={borderColor}
      bg={bgColor}
      mt={2}
    >
      <Text fontWeight="medium" mb={2}>Thread Permissions</Text>
      
      <VStack align="stretch" spacing={3}>
        <FormControl display="flex" alignItems="center">
          <FormLabel htmlFor="execute-permission" mb="0" fontSize="sm">
            Allow Agent Execution
          </FormLabel>
          <Switch 
            id="execute-permission" 
            isChecked={permissions.can_execute}
            onChange={handleToggleExecute}
            colorScheme="blue"
          />
        </FormControl>
        
        <FormControl display="flex" alignItems="center">
          <FormLabel htmlFor="reflect-permission" mb="0" fontSize="sm">
            Allow Agent Reflection
          </FormLabel>
          <Switch 
            id="reflect-permission" 
            isChecked={permissions.can_reflect}
            onChange={handleToggleReflect}
            colorScheme="purple"
          />
        </FormControl>
        
        <Box>
          <Text fontSize="xs" fontWeight="medium" mb={1}>
            Agents with access:
          </Text>
          <HStack spacing={1} flexWrap="wrap">
            {permissions.agent_ids.map(agentId => (
              <Badge key={agentId} colorScheme="blue" mr={1} mb={1}>
                {agentId}
              </Badge>
            ))}
          </HStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default ThreadPermissionsControl;
