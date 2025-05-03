import React from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  HStack, 
  Text, 
  Icon, 
  useColorModeValue,
  Divider,
  Heading,
  Button
} from '@chakra-ui/react';
import { FiPlus, FiFilter, FiGrid, FiList } from 'react-icons/fi';

const ContentLayout = ({ 
  title,
  subtitle,
  actions,
  filters,
  viewToggle = false,
  onViewChange,
  currentView = 'grid',
  children 
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box>
      {/* Header section with title and actions */}
      {(title || actions) && (
        <Flex 
          justifyContent="space-between" 
          alignItems="center" 
          mb={4}
        >
          <Box>
            {title && <Heading as="h2" size="lg">{title}</Heading>}
            {subtitle && (
              <Text color={useColorModeValue('gray.600', 'gray.400')} mt={1}>
                {subtitle}
              </Text>
            )}
          </Box>
          
          <HStack spacing={3}>
            {actions}
          </HStack>
        </Flex>
      )}
      
      {/* Filters and view toggle */}
      {(filters || viewToggle) && (
        <Flex 
          justifyContent="space-between" 
          alignItems="center" 
          mb={4}
          p={4}
          bg={bgColor}
          borderRadius="lg"
          boxShadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Box>
            {filters}
          </Box>
          
          {viewToggle && (
            <HStack spacing={2}>
              <Button
                size="sm"
                leftIcon={<FiGrid />}
                variant={currentView === 'grid' ? 'solid' : 'outline'}
                colorScheme="blue"
                onClick={() => onViewChange && onViewChange('grid')}
              >
                Grid
              </Button>
              <Button
                size="sm"
                leftIcon={<FiList />}
                variant={currentView === 'list' ? 'solid' : 'outline'}
                colorScheme="blue"
                onClick={() => onViewChange && onViewChange('list')}
              >
                List
              </Button>
            </HStack>
          )}
        </Flex>
      )}
      
      {/* Main content */}
      <Box>
        {children}
      </Box>
    </Box>
  );
};

export default ContentLayout;
