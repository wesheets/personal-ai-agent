import React from 'react';
import { 
  Box, 
  Heading, 
  Text, 
  VStack, 
  HStack, 
  Flex, 
  Icon, 
  useColorModeValue,
  Divider,
  Badge
} from '@chakra-ui/react';
import { FiHome, FiInfo, FiAlertCircle } from 'react-icons/fi';

const PageHeader = ({ 
  title, 
  subtitle, 
  icon = FiHome, 
  actions = null, 
  breadcrumbs = null,
  status = null 
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  // Status badge styling
  const getStatusProps = () => {
    switch(status?.type) {
      case 'success':
        return { colorScheme: 'green', icon: null };
      case 'warning':
        return { colorScheme: 'orange', icon: FiAlertCircle };
      case 'error':
        return { colorScheme: 'red', icon: FiAlertCircle };
      case 'info':
        return { colorScheme: 'blue', icon: FiInfo };
      default:
        return null;
    }
  };
  
  const statusProps = status ? getStatusProps() : null;
  
  return (
    <Box 
      mb={6} 
      p={6} 
      bg={bgColor} 
      borderRadius="lg" 
      boxShadow="sm"
      borderWidth="1px"
      borderColor={borderColor}
    >
      {/* Breadcrumbs */}
      {breadcrumbs && (
        <Box mb={3}>
          {breadcrumbs}
        </Box>
      )}
      
      <Flex justifyContent="space-between" alignItems="flex-start">
        <HStack spacing={4} align="flex-start">
          {/* Icon */}
          <Flex
            w={12}
            h={12}
            alignItems="center"
            justifyContent="center"
            borderRadius="md"
            bg={useColorModeValue('blue.100', 'blue.900')}
            color={useColorModeValue('blue.700', 'blue.200')}
          >
            <Icon as={icon} boxSize={6} />
          </Flex>
          
          {/* Title and subtitle */}
          <VStack spacing={1} align="flex-start">
            <HStack>
              <Heading as="h1" size="lg">
                {title}
              </Heading>
              
              {/* Status badge */}
              {status && statusProps && (
                <Badge 
                  colorScheme={statusProps.colorScheme} 
                  variant="subtle"
                  display="flex"
                  alignItems="center"
                  px={2}
                  py={1}
                  borderRadius="full"
                >
                  {statusProps.icon && <Icon as={statusProps.icon} mr={1} boxSize={3} />}
                  {status.text}
                </Badge>
              )}
            </HStack>
            
            {subtitle && (
              <Text color={useColorModeValue('gray.600', 'gray.400')}>
                {subtitle}
              </Text>
            )}
          </VStack>
        </HStack>
        
        {/* Action buttons */}
        {actions && (
          <Box>
            {actions}
          </Box>
        )}
      </Flex>
      
      {/* Optional divider and additional content */}
      {status?.details && (
        <>
          <Divider my={4} />
          <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
            {status.details}
          </Text>
        </>
      )}
    </Box>
  );
};

export default PageHeader;
