import React from 'react';
import {
  Flex,
  Spinner,
  Text,
  Box,
  VStack,
  useColorModeValue,
  Skeleton,
  SkeletonText,
  SkeletonCircle
} from '@chakra-ui/react';

/**
 * LoadingSpinner component
 * 
 * Simple centered spinner with optional text
 */
export const LoadingSpinner = ({ text = 'Loading...', size = 'xl' }) => (
  <Flex 
    justify="center" 
    align="center" 
    direction="column" 
    minH="200px" 
    width="100%"
  >
    <Spinner size={size} thickness="4px" speed="0.65s" mb={4} />
    <Text>{text}</Text>
  </Flex>
);

/**
 * LoadingCard component
 * 
 * Skeleton loading card for list items
 */
export const LoadingCard = ({ count = 1 }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  return (
    <VStack spacing={4} align="stretch" width="100%">
      {Array.from({ length: count }).map((_, index) => (
        <Box 
          key={`loading-card-${index}`}
          p={4} 
          borderWidth="1px" 
          borderRadius="lg" 
          bg={bgColor}
          borderColor={borderColor}
        >
          <Flex justify="space-between" align="center" mb={4}>
            <Skeleton height="24px" width="40%" />
            <SkeletonCircle size="8" />
          </Flex>
          
          <SkeletonText mt="4" noOfLines={3} spacing="4" skeletonHeight="2" />
          
          <Flex mt={6} gap={2}>
            <Skeleton height="32px" width="80px" borderRadius="md" />
            <Skeleton height="32px" width="80px" borderRadius="md" />
            <Skeleton height="32px" width="120px" borderRadius="md" />
          </Flex>
        </Box>
      ))}
    </VStack>
  );
};

/**
 * LoadingGrid component
 * 
 * Grid of skeleton loading cards
 */
export const LoadingGrid = ({ columns = 2, count = 4 }) => (
  <Box 
    display="grid" 
    gridTemplateColumns={{ 
      base: "1fr", 
      md: `repeat(${Math.min(columns, 2)}, 1fr)`, 
      lg: `repeat(${columns}, 1fr)` 
    }}
    gap={4}
    width="100%"
  >
    {Array.from({ length: count }).map((_, index) => (
      <Box 
        key={`loading-grid-item-${index}`}
        p={4} 
        borderWidth="1px" 
        borderRadius="lg" 
        bg={useColorModeValue('white', 'gray.700')}
        borderColor={useColorModeValue('gray.200', 'gray.600')}
      >
        <Skeleton height="24px" width="60%" mb={4} />
        <SkeletonText mt="2" noOfLines={2} spacing="2" skeletonHeight="2" />
      </Box>
    ))}
  </Box>
);

/**
 * LoadingTable component
 * 
 * Skeleton loading table
 */
export const LoadingTable = ({ rows = 5, columns = 4 }) => (
  <Box 
    borderWidth="1px" 
    borderRadius="lg" 
    overflow="hidden"
    bg={useColorModeValue('white', 'gray.700')}
    borderColor={useColorModeValue('gray.200', 'gray.600')}
  >
    {/* Table header */}
    <Flex 
      p={4} 
      borderBottomWidth="1px" 
      borderColor={useColorModeValue('gray.200', 'gray.600')}
      bg={useColorModeValue('gray.50', 'gray.800')}
    >
      {Array.from({ length: columns }).map((_, index) => (
        <Box 
          key={`loading-table-header-${index}`} 
          flex={index === 0 ? 2 : 1}
          pr={4}
        >
          <Skeleton height="20px" width="80%" />
        </Box>
      ))}
    </Flex>
    
    {/* Table rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <Flex 
        key={`loading-table-row-${rowIndex}`}
        p={4} 
        borderBottomWidth={rowIndex < rows - 1 ? "1px" : "0"}
        borderColor={useColorModeValue('gray.200', 'gray.600')}
        align="center"
      >
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Box 
            key={`loading-table-cell-${rowIndex}-${colIndex}`} 
            flex={colIndex === 0 ? 2 : 1}
            pr={4}
          >
            <Skeleton height="16px" width={`${Math.random() * 40 + 60}%`} />
          </Box>
        ))}
      </Flex>
    ))}
  </Box>
);

export default {
  LoadingSpinner,
  LoadingCard,
  LoadingGrid,
  LoadingTable
};
