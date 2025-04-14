import React from 'react';
import { Box, Flex, Text, useColorModeValue, HStack, VStack, Icon } from '@chakra-ui/react';
import { FiBriefcase, FiUsers, FiLayers, FiShield } from 'react-icons/fi';
import BrandLogo from './BrandLogo';

const BrandHeader = ({ title, subtitle, showFeatures = false, ...props }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.700', 'gray.300');
  const subtitleColor = useColorModeValue('gray.500', 'gray.500');
  
  const features = [
    { icon: FiBriefcase, text: 'Multi-Agent OS' },
    { icon: FiUsers, text: 'User Authentication' },
    { icon: FiLayers, text: 'Memory Management' },
    { icon: FiShield, text: 'Secure & Private' },
  ];
  
  return (
    <Box
      as="header"
      py={6}
      px={8}
      bg={bgColor}
      borderBottomWidth="1px"
      borderColor={borderColor}
      {...props}
    >
      <VStack spacing={4} align="center" maxW="container.lg" mx="auto">
        <BrandLogo size="lg" />
        
        {title && (
          <Text 
            fontSize="2xl" 
            fontWeight="bold" 
            color="brand.600"
            textAlign="center"
          >
            {title}
          </Text>
        )}
        
        {subtitle && (
          <Text 
            fontSize="md" 
            color={subtitleColor}
            textAlign="center"
            maxW="2xl"
          >
            {subtitle}
          </Text>
        )}
        
        {showFeatures && (
          <HStack 
            spacing={8} 
            mt={4} 
            flexWrap="wrap" 
            justify="center"
            display={{ base: 'none', md: 'flex' }}
          >
            {features.map((feature, index) => (
              <HStack key={index} spacing={2}>
                <Icon as={feature.icon} color="brand.500" />
                <Text color={textColor} fontWeight="medium">
                  {feature.text}
                </Text>
              </HStack>
            ))}
          </HStack>
        )}
      </VStack>
    </Box>
  );
};

export default BrandHeader;
